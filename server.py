from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os
import datetime
import time

app = Flask(__name__)
DB_FILE = "kelime_oyunu.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
        # Scores table
        c.execute('''CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username TEXT,
                        score INTEGER,
                        time_str TEXT,
                        timestamp REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
        
        # Schema Migration: Add school column if not exists

            
        conn.commit()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def tr_upper(text):
    if not text:
        return text
    # Turkish-aware uppercase conversion
    return text.replace('i', 'İ').replace('ı', 'I').upper()

@app.route('/')
def home():
    return "Kelime Oyunu Server is Running!"

import re

# ... (Previous imports kept if needed, but 're' is new)
RESERVED_NAMES = {"ADMIN", "MODERATOR", "DESTEK", "SYSTEM", "GAMEMASTER", "YONETICI", "ROOT"}
PROFANITY_LIST = {"KUFUR1", "KUFUR2", "BADWORD"} # Placeholder list - Extend as needed

def validate_username(username):
    # 1. Length Check
    if not (3 <= len(username) <= 20):
        return False, "Kullanıcı adı 3 ile 20 karakter arasında olmalıdır."
    
    # 2. Allowed Characters (Alphanumeric + Underscore)
    if not re.match(r"^[a-zA-Z0-9_ğüşıöçĞÜŞİÖÇ]+$", username):
        return False, "Kullanıcı adı sadece harf, rakam ve alt çizgi (_) içerebilir."
    
    upper_username = tr_upper(username)
    
    # 3. Reserved Words
    if any(reserved in upper_username for reserved in RESERVED_NAMES):
        return False, "Bu kullanıcı adı kullanılamaz (Rezerve edilmiş)."
        
    # 4. Profanity Filter (Basic containment check)
    if any(bad in upper_username for bad in PROFANITY_LIST):
        return False, "Kullanıcı adı uygunsuz ifadeler içeremez."
        
    # 5. PII Protection (Basic Phone Number check: looks for 12+ digits)
    digit_count = sum(c.isdigit() for c in username)
    if digit_count > 11:
        return False, "Kullanıcı adı çok fazla rakam içeremez (Telefon no vb.)."

    return True, None

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Kullanıcı adı ve şifre gereklidir."}), 400
    
    username = username.strip()
    
    # Run Validation
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400
        
    final_username = tr_upper(username) # Store uppercase for consistency
    
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                      (final_username, hash_password(password)))
            conn.commit()
            return jsonify({"success": True, "message": "Kayıt başarılı! Lütfen giriş yapın."})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Bu kullanıcı adı zaten alınmış."}), 409
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Eksik bilgi."}), 400
        
    username = tr_upper(username.strip())
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", 
                  (username, hash_password(password)))
        user = c.fetchone()
        
        if user:
            return jsonify({
                "success": True, 
                "message": "Giriş başarılı.",
                "user_id": user[0],
                "username": user[1]
            })
        else:
            return jsonify({"success": False, "message": "Kullanıcı adı veya şifre hatalı."}), 401

@app.route('/auth/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not all([username, old_password, new_password]):
        return jsonify({"success": False, "message": "Eksik bilgi."}), 400
        
    username = tr_upper(username.strip())
    
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # Verify old password first
        c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", 
                  (username, hash_password(old_password)))
        user = c.fetchone()
        
        if not user:
             return jsonify({"success": False, "message": "Eski şifre hatalı."}), 401
             
        # Update to new password
        c.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                  (hash_password(new_password), user[0]))
        conn.commit()
        
        return jsonify({"success": True, "message": "Şifre başarıyla değiştirildi."})

@app.route('/scores', methods=['POST'])
def add_score():
    data = request.json
    # Validation
    required = ['user_id', 'username', 'score', 'time_str', 'timestamp']
    if not all(k in data for k in required):
        return jsonify({"success": False, "message": "Eksik veri"}), 400
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            # Deduplication Check: Check if a score with same user_id, score and very close timestamp exists
            c.execute("SELECT id FROM scores WHERE user_id = ? AND score = ? AND abs(timestamp - ?) < 5.0", 
                      (data['user_id'], data['score'], data['timestamp']))
            if c.fetchone():
                return jsonify({"success": True, "message": "Skor zaten kaydedilmiş (kopya)."})

            c.execute('''INSERT INTO scores (user_id, username, score, time_str, timestamp) 
                         VALUES (?, ?, ?, ?, ?)''',
                      (data['user_id'], data['username'], data['score'], data['time_str'], data['timestamp']))
            conn.commit()
            return jsonify({"success": True, "message": "Skor kaydedildi."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/scores', methods=['GET'])
def get_scores():
    period = request.args.get('period', 'all') # daily, weekly, monthly, all
    limit = int(request.args.get('limit', 50))
    
    now = datetime.datetime.now()
    start_ts = 0
    
    if period == 'daily':
        start_ts = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    elif period == 'weekly':
        start_ts = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    elif period == 'monthly':
        start_ts = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
        
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            query = "SELECT username, score, time_str, timestamp FROM scores WHERE timestamp >= ? ORDER BY score DESC, timestamp ASC LIMIT ?"
            c.execute(query, (start_ts, limit))
            rows = c.fetchall()
            
            scores = [dict(row) for row in rows]
            return jsonify({"success": True, "scores": scores})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            query = "SELECT id, username, created_at FROM users ORDER BY created_at DESC"
            c.execute(query)
            rows = c.fetchall()
            users = [dict(row) for row in rows]
            return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            
            # Delete scores associated with user first
            c.execute("DELETE FROM scores WHERE user_id = ?", (user_id,))
            
            # Delete user
            c.execute("DELETE FROM users WHERE id = ?", (user_id,))
            deleted = c.rowcount
            
            conn.commit()
            
            if deleted > 0:
                return jsonify({"success": True, "message": "Kullanıcı ve ilişkili veriler silindi."})
            else:
                return jsonify({"success": False, "message": "Kullanıcı bulunamadı."}), 404
                
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so others can connect
    app.run(host='0.0.0.0', port=5000, debug=True)
