import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
import hashlib
import ctypes.wintypes
import webbrowser
import traceback
import threading
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
import time
from datetime import datetime, timedelta
from scrollable_frame import ScrollableFrame
import sys
import urllib.request
import urllib.error
import zipfile
import shutil
import subprocess
import ssl
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# --- DPI AWARENESS (Fix for High-Res Screens) ---
try:
    from ctypes import windll
    # Try SetProcessDpiAwareness(2) first (Per Monitor Aware V2) - Windows 10/11
    # If fails, fall back to (1) System Aware, then user32.SetProcessDPIAware()
    try:
        windll.shcore.SetProcessDpiAwareness(2) 
    except Exception:
        windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # Use the directory of the script file, not the current working directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- CONFIG MANAGER ---
class ConfigManager:
    """Manages configuration loading from local file and GitHub updates"""
    
    DEFAULT_CONFIG = {
        "version": "1.6",
        "colors_dark": {
            "bg_color": "#1e293b",
            "card_color": "#0f172a",
            "accent_color": "#2dd4bf",
            "text_color": "#f8fafc",
            "input_bg": "#334155",
            "button_color": "#0ea5e9",
            "sub_text_color": "#94a3b8",
            "pink_accent": "#2dd4bf",
            "entry_title_color": "#2dd4bf",
            "definition_card_bg": "#e619e5",
            "red_button": "#ef4444",
            "green_button": "#22c55e"
        },
        "colors_light": {
            "bg_color": "#f1f5f9",
            "card_color": "#ffffff",
            "accent_color": "#0d9488",
            "text_color": "#1e293b",
            "input_bg": "#e2e8f0",
            "button_color": "#0284c7",
            "sub_text_color": "#64748b",
            "pink_accent": "#0d9488",
            "entry_title_color": "#0d9488",
            "definition_card_bg": "#db2777",
            "red_button": "#dc2626",
            "green_button": "#16a34a"
        },
        "colors": {
            "bg_color": "#1e293b",
            "card_color": "#0f172a",
            "accent_color": "#2dd4bf",
            "text_color": "#f8fafc",
            "input_bg": "#334155",
            "button_color": "#0ea5e9",
            "sub_text_color": "#94a3b8",
            "pink_accent": "#2dd4bf",
            "entry_title_color": "#2dd4bf",
            "definition_card_bg": "#e619e5",
            "red_button": "#ef4444",
            "green_button": "#22c55e"
        },
        "sounds": {
            "enabled": True,
            "correct": "button-pressed-38129.mp3",
            "wrong": "click-buttons-ui-menu-sounds-effects-button-7-203601.mp3",
            "next": "mech-keyboard-02-102918.mp3",
            "volume_correct": 1.0,
            "volume_wrong": 1.0,
            "volume_next": 0.5
        },
        "fonts": {
            "main_font_family": "Benz Grotesk Heavy",
            "fallback_font": "Segoe UI",
            "font_file_path": "benz/Benz Grotesk.ttf"
        },
        "game_settings": {
            "timer_duration": 60,
            "levels": [4, 5, 6, 7, 8, 9, 10],
            "score_per_word": 10,
            "hint_penalty": 1
        },
        "ui_text": {
            "app_title": "Kelime Avcısı",
            "welcome_title": "KELİME AVCISI",
            "name_placeholder": "ADINIZ - SOYADINIZ",
            "start_button": "OYUNA BAŞLA",
            "hint_button": "HARF İSTE",
            "submit_button": "CEVAPLA",
            "next_button": "SIRADAKİ KELİME",
            "finish_button": "OYUNU BİTİR"
        },
        "ui_design": {
            "entry_title_font_size": 144,
            "card_height": 180,
            "stats_bar_padding": 15,
            "button_width": 200,
            "button_height": 50,
            "rounded_radius": 25
        },
        "update_check": {
            "enabled": True,
            "config_url": "https://raw.githubusercontent.com/Okan707/Kelime_Oyunu/main/config.json",
            "main_py_url": "https://raw.githubusercontent.com/Okan707/Kelime_Oyunu/main/main.py",
            "sozluk_url": "https://raw.githubusercontent.com/Okan707/Kelime_Oyunu/main/sozluk.json",
            "release_url": "https://api.github.com/repos/Okan707/Kelime_Oyunu/releases/latest"
        },
        "display_settings": {
            "custom_scale": None,
            "resolution": "fullscreen",
            "fullscreen": True,
            "theme": "dark"
        }
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = "config.json"
        self.load_local_config()
        
    def load_local_config(self):
        """Load configuration from local file"""
        try:
            # 1. First look in AppData (persistent location)
            appdata_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'KelimeOyunu')
            appdata_config = os.path.join(appdata_dir, self.config_file)
            
            # 2. Then look in resource path (default installation location)
            bundled_config = resource_path(self.config_file)
            
            config_to_load = None
            if os.path.exists(appdata_config):
                config_to_load = appdata_config
                print(f"[CONFIG] Loading persistent config from AppData: {config_to_load}")
            elif os.path.exists(bundled_config):
                config_to_load = bundled_config
                print(f"[CONFIG] Loading bundled config: {config_to_load}")
            
            if config_to_load:
                with open(config_to_load, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Deep merge with default config
                    self._deep_merge(self.config, loaded_config)
                    print(f"[CONFIG] Version: {self.config.get('version', 'unknown')}")
            else:
                print(f"[CONFIG] Config file not found, using defaults")
            
            # Apply theme palette to the active 'colors' config
            theme = self.config.get("display_settings", {}).get("theme", "dark")
            palette_key = "colors_light" if theme == "light" else "colors_dark"
            if palette_key in self.config:
                self.config["colors"] = self.config[palette_key].copy()
                print(f"[CONFIG] Applied theme palette: {theme}")

            # --- VERSION MIGRATION CHECK ---
            local_version = self.config.get("version", "0.0.0")
            default_version = self.DEFAULT_CONFIG.get("version", "0.0.0")
            
            if local_version != default_version:
                print(f"[CONFIG] Version mismatch detected: Local({local_version}) != Default({default_version}). Updating...")
                self.config["version"] = default_version
                
                # If we loaded from AppData, update it right there
                if config_to_load == appdata_config:
                    try:
                         with open(appdata_config, 'w', encoding='utf-8') as f:
                            json.dump(self.config, f, ensure_ascii=False, indent=2)
                         print(f"[CONFIG] Successfully updated version in: {appdata_config}")
                    except Exception as e:
                         print(f"[CONFIG] Failed to save version update: {e}")
                
        except Exception as e:
            print(f"[CONFIG] Failed to load local config: {e}")
            # Use default config
            
    def _deep_merge(self, base, update):
        """Recursively merge update dict into base dict"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, section, key=None, default=None):
        """Helper to get config values safely"""
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
                
    def update_from_github(self, callback=None):
        """Download latest config from GitHub (non-blocking)"""
        def download():
            try:
                print(f"[CONFIG] Checking GitHub for config updates...")
                
                if not self.config.get("update_check", {}).get("enabled", True):
                    print(f"[CONFIG] Auto-update is disabled")
                    return
                    
                url = self.config.get("update_check", {}).get("config_url")
                if url:
                    url = f"{url}?t={int(time.time())}"
                if not url:
                    print(f"[CONFIG] No update URL configured")
                    return
                
                print(f"[CONFIG] Downloading from: {url[:60]}...")
                
                # Download with timeout and SSL bypass
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                    content = response.read().decode('utf-8')
                    new_config = json.loads(content)
                    
                    # Check version
                    current_version = self.config.get("version", "0.0.0")
                    new_version = new_config.get("version", "0.0.0")
                    
                    print(f"[CONFIG] Current version: {current_version}")
                    print(f"[CONFIG] GitHub version: {new_version}")
                    
                    # Merge new config
                    # Merge new config but PROTECT user settings
                    # List of keys that should NOT be overwritten by remote defaults
                    protected_keys = ["sounds", "display_settings", "game_settings"]
                    for key in protected_keys:
                        if key in new_config:
                            del new_config[key]
                            
                    self._deep_merge(self.config, new_config)
                    
                    # Save to persistent AppData location
                    appdata_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'KelimeOyunu')
                    if not os.path.exists(appdata_dir):
                        os.makedirs(appdata_dir)
                    
                    config_path = os.path.join(appdata_dir, self.config_file)
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, ensure_ascii=False, indent=2)
                    
                    print(f"[CONFIG] Config updated and saved to persistent storage: {config_path}")
                    print(f"[CONFIG] Restart required for changes to take effect!")
                    
                    if callback:
                        callback(True, new_version)
                    
                    # If version is higher, we can auto-trigger the full update or let user decide
                    # For now, auto-update is just for manual check to be safer
                        
            except Exception as e:
                print(f"[CONFIG] Update from GitHub failed: {e}")
                import traceback
                traceback.print_exc()
                if callback:
                    callback(False, str(e))
        
        # Run in background thread
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
        
    def check_for_updates_manual(self, callback=None):
        """Manually check for updates via GitHub Releases"""
        def check():
            try:
                print(f"[CONFIG] Manual update check started (GitHub Releases)...")
                
                release_url = self.get("update_check", "release_url")
                if not release_url:
                    if callback: 
                        callback({
                            "success": False, 
                            "message": "Güncelleştirme URL'si yapılandırılmamış."
                        })
                    return

                # fetch latest release
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(release_url, headers={'User-Agent': 'KelimeOyunu/1.0'})
                with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                    content = response.read().decode('utf-8')
                    release_data = json.loads(content)
                    
                    latest_tag = release_data.get("tag_name", "").lstrip("v")
                    current_version = self.config.get("version", "0.0.0")
                    
                    print(f"[UPDATE] Current: {current_version}, Latest: {latest_tag}")
                    
                    if latest_tag > current_version:
                        # Find EXE asset
                        assets = release_data.get("assets", [])
                        exe_asset = next((a for a in assets if a["name"].lower().endswith(".exe")), None)
                        
                        if exe_asset:
                            # Store pending update info
                            self.pending_update_url = exe_asset["browser_download_url"]
                            self.pending_update_filename = exe_asset["name"]
                            
                            if callback:
                                callback({
                                    "success": True,
                                    "update_available": True,
                                    "current_version": current_version,
                                    "new_version": latest_tag,
                                    "message": "Yeni versiyon bulundu!"
                                })
                        else:
                            if callback: 
                                callback({
                                    "success": False, 
                                    "message": "Güncelleme bulundu ancak kurulum dosyası eksik."
                                })
                    else:
                        print(f"[UPDATE] App is up to date.")
                        if callback: 
                            callback({
                                "success": True, 
                                "update_available": False,
                                "current_version": current_version,
                                "message": "Uygulamanız güncel."
                            })
                        
            except Exception as e:
                print(f"[UPDATE] Check failed: {e}")
                if callback: 
                    callback({
                        "success": False, 
                        "message": f"Hata: {str(e)}"
                    })
        
        threading.Thread(target=check, daemon=True).start()

    def trigger_full_update(self, callback=None):
        """Bridge to start the full download and apply process"""
        if hasattr(self, 'pending_update_url') and self.pending_update_url:
            self.download_and_install_update(self.pending_update_url, self.pending_update_filename, callback)
        else:
            if callback: callback(False, "Güncelleme bilgisi bulunamadı.")

    def download_and_install_update(self, download_url, filename, callback=None):
        """Downloads the installer and runs it"""
        def process():
            try:
                appdata_dir, temp_dir = self._get_update_dirs()
                if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                
                installer_path = os.path.join(temp_dir, filename)
                print(f"[UPDATE] Downloading installer to {installer_path}...")
                
                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(download_url, headers={'User-Agent': 'KelimeOyunu/1.0'})
                with urllib.request.urlopen(req, timeout=120, context=ctx) as response:
                    with open(installer_path, 'wb') as f:
                        shutil.copyfileobj(response, f)
                        
                print(f"[UPDATE] Download complete. Launching installer...")
                
                if callback:
                    callback(True, "İndirme tamamlandı. Kurulum başlatılıyor...")

                # Create a small batch script to run installer and kill this app
                updater_bat = os.path.join(temp_dir, "run_update.bat")
                
                lines = [
                    "@echo off",
                    "echo Guncelleme baslatiliyor...",
                    f"timeout /t 2 /nobreak > nul",
                    f"start \"\" \"{installer_path}\" /SILENT", # Try silent install if supported, or normal
                    "del \"%~f0\"" 
                ]
                
                with open(updater_bat, "w") as f:
                    f.write("\n".join(lines))
                    
                subprocess.Popen([updater_bat], shell=True)
                os._exit(0)
                
            except Exception as e:
                print(f"[UPDATE] Install failed: {e}")
                if callback:
                    callback(False, f"Kurulum hatası: {str(e)}")

        threading.Thread(target=process, daemon=True).start()

    def _get_update_dirs(self):
        """Get directories used for update process"""
        appdata_dir = os.path.join(os.getenv('APPDATA', os.getenv('LOCALAPPDATA', os.path.expanduser('~'))), 'KelimeOyunu')
        temp_update_dir = os.path.join(appdata_dir, "_update_temp")
        return appdata_dir, temp_update_dir

# --- GLOBAL CONFIG INSTANCE ---
config = ConfigManager()

# --- STYLE CONSTANTS (with config fallback) ---
BG_COLOR = config.get("colors", "bg_color", default="#1e293b")
CARD_COLOR = config.get("colors", "card_color", default="#0f172a")
ACCENT_COLOR = config.get("colors", "accent_color", default="#2dd4bf")
TEXT_COLOR = config.get("colors", "text_color", default="#f8fafc")
INPUT_BG = config.get("colors", "input_bg", default="#334155")
BUTTON_COLOR = config.get("colors", "button_color", default="#0ea5e9")
SUB_TEXT_COLOR = config.get("colors", "sub_text_color", default="#94a3b8")
UPDATE_URL = "https://raw.githubusercontent.com/Okan707/Kelime_Oyunu/main/main.py"
PINK_ACCENT = config.get("colors", "pink_accent", default="#ec4899")
DEFINITION_CARD_BG = config.get("colors", "definition_card_bg", default="#e619e5")
API_URL = config.get("network", "api_url", default="http://localhost:5000")

# --- NETWORK MANAGER ---
class NetworkManager:
    """Handles communication with the game server (Jsonbin.io Integration)"""
    def __init__(self):
        # Jsonbin.io Configuration
        self.api_key = "$2a$10$efDp30ZwzbwZpEe/u8B33ObccCeT7lVjfEfG5XAybeOlmiGHmkIIW"
        self.score_bin_id = "6973d78c43b1c97be9450373"
        self.user_bin_id = "6973da39d0ea881f408071c0"
        
        self.base_url = "https://api.jsonbin.io/v3/b"
        self.api_url = API_URL # For compatibility
        self.headers = {
            "X-Master-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _request(self, url, method="GET", data=None, retries=3, delay=1):
        for attempt in range(retries):
            try:
                body = json.dumps(data).encode('utf-8') if data else None
                req = urllib.request.Request(url, data=body, headers=self.headers, method=method)
                ctx = ssl._create_unverified_context()
                
                with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                    return json.loads(response.read().decode('utf-8'))
            except Exception as e:
                print(f"[NETWORK] Error (Attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2 # Exponential backoff
                else:
                    return None

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        try:
            username = username.strip().upper()
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                return {"success": False, "message": "Kullanıcı verileri alınamadı."}
            
            users = res["record"].get("users", [])
            hashed_pw = self._hash_password(password)
            
            for user in users:
                if user["username"] == username:
                    if user["password"] == hashed_pw:
                        return {
                            "success": True, 
                            "user_id": user.get("id", random.randint(1000, 9999)), 
                            "username": user["username"],
                            "profile": user # Return full user object
                        }
                    else:
                        return {"success": False, "message": "Şifre hatalı."}
            
            return {"success": False, "message": "Kullanıcı bulunamadı."}
        except Exception as e:
            return {"success": False, "message": str(e)}
        
    def register(self, username, password, fullname, birth_date, gender, school, class_level, security_question="", security_answer=""):
        try:
            username = username.strip().upper()
            # 1. Fetch current users
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                return {"success": False, "message": "Sunucu bağlantı hatası."}
            
            users = res["record"].get("users", [])
            
            # 2. Check if user exists
            if any(u["username"] == username for u in users):
                return {"success": False, "message": "Bu kullanıcı adı zaten alınmış."}
            
            # 3. Add new user
            new_user = {
                "id": int(time.time()),
                "username": username,
                "password": self._hash_password(password),
                "created_at": str(datetime.now()),
                "fullname": fullname,
                "birth_date": birth_date,
                "gender": gender,
                "school": school,
                "class_level": class_level,
                "security_question": security_question,
                "security_answer": security_answer
            }
            users.append(new_user)
            
            # 4. Update bin
            update_res = self._request(f"{self.base_url}/{self.user_bin_id}", method="PUT", data={"users": users})
            if update_res:
                return {"success": True, "message": "Kayıt başarılı! Şimdi giriş yapabilirsiniz."}
            return {"success": False, "message": "Kayıt sırasında hata oluştu."}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
        
    def submit_score(self, user_id, username, score, time_str, timestamp, school="-", fullname="-", class_level="-", gender="-", avatar_id="1"):
        try:
            # 1. Fetch current scores
            res = self._request(f"{self.base_url}/{self.score_bin_id}/latest", method="GET")
            scores = []
            if res and "record" in res:
                scores = res["record"].get("skorlar", [])
            
            # 2. Add new record
            new_entry = {
                "ad": username,
                "puan": score,
                "sure": time_str,
                "timestamp": timestamp,
                "okul": school,
                "fullname": fullname,
                "class_level": class_level,
                "gender": gender,
                "avatar_id": avatar_id
            }
            scores.append(new_entry)
            
            # 3. Sort and limit to top 100 (Increased from 20 for better filtering)
            scores.sort(key=lambda x: x['puan'], reverse=True)
            scores = scores[:100]
            
            # 4. Update the bin
            payload = {"skorlar": scores}
            update_res = self._request(f"{self.base_url}/{self.score_bin_id}", method="PUT", data=payload)
            
            if update_res:
                return {"success": True, "message": "Skor başarıyla yüklendi!"}
            return {"success": False, "message": "Skor yüklenemedi."}
        except Exception as e:
            print(f"[NETWORK] Score submit failed: {e}")
            return {"success": False, "message": str(e)}
        
    def get_scores(self, period="all"):
        try:
            res = self._request(f"{self.base_url}/{self.score_bin_id}/latest", method="GET")
            if res and "record" in res:
                raw_scores = res["record"].get("skorlar", [])
                
                # Filter by period client-side
                now = datetime.now()
                start_ts = 0
                if period == "daily":
                    start_ts = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                elif period == "weekly":
                    start_ts = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                elif period == "monthly":
                    start_ts = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
                
                mapped = []
                for s in raw_scores:
                    ts = s.get("timestamp", 0)
                    if ts >= start_ts:
                        mapped.append({
                            "name": s.get("ad", "Bilinmeyen"),
                            "score": s.get("puan", 0),
                            "time": s.get("sure", "--:--"),
                            "timestamp": ts,
                            "school": s.get("okul", "-"),
                            "fullname": s.get("fullname", "-"),
                            "class_level": s.get("class_level", "-"),
                            "gender": s.get("gender", "-"),
                            "avatar_id": s.get("avatar_id", "1")
                        })
                
                # 2. Sort filtered results by score descending
                mapped.sort(key=lambda x: x['score'], reverse=True)
                
                return {"success": True, "scores": mapped}
            return {"success": False, "message": "Skorlar alınamadı."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_score(self, username, timestamp):
        try:
            # 1. Fetch current scores
            res = self._request(f"{self.base_url}/{self.score_bin_id}/latest", method="GET")
            scores = []
            if res and "record" in res:
                scores = res["record"].get("skorlar", [])
            
            # 2. Filter out the specific score
            # Using timestamp as unique identifier mostly, but checking username too for safety
            original_len = len(scores)
            new_scores = [s for s in scores if not (s.get("ad") == username and s.get("timestamp") == timestamp)]
            
            if len(new_scores) == original_len:
                return {"success": False, "message": "Skor bulunamadı veya zaten silinmiş."}

            # 3. Update the bin
            payload = {"skorlar": new_scores}
            update_res = self._request(f"{self.base_url}/{self.score_bin_id}", method="PUT", data=payload)
            
            if update_res:
                return {"success": True, "message": "Skor başarıyla silindi."}
            return {"success": False, "message": "Silme işlemi başarısız."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_all_users(self):
        try:
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if res and "record" in res:
                 users = res["record"].get("users", [])
                 return {"success": True, "users": users}
            return {"success": False, "message": "Kullanıcı listesi alınamadı."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_user(self, username_to_delete):
        try:
            # 1. DELETE USER
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                 return {"success": False, "message": "Veri okunamadı."}
            
            users = res["record"].get("users", [])
            original_count = len(users)
            new_users = [u for u in users if u.get("username") != username_to_delete]
            
            if len(new_users) == original_count:
                 return {"success": False, "message": "Kullanıcı bulunamadı."}
            
            # Update Users Bin
            self._request(f"{self.base_url}/{self.user_bin_id}", method="PUT", data={"users": new_users})
            
            # 2. DELETE SCORES
            s_res = self._request(f"{self.base_url}/{self.score_bin_id}/latest", method="GET")
            if s_res and "record" in s_res:
                scores = s_res["record"].get("skorlar", [])
                # Filter out scores belonging to this user
                # Score object uses 'ad' for username
                new_scores = [s for s in scores if s.get("ad") != username_to_delete]
                
                if len(new_scores) != len(scores):
                     self._request(f"{self.base_url}/{self.score_bin_id}", method="PUT", data={"skorlar": new_scores})
            
            return {"success": True, "message": f"Kullanıcı '{username_to_delete}' ve ilişkili veriler silindi."}

        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_user_profile(self, username, profile_data):
        """Updates user profile data in the cloud"""
        try:
            # 1. Fetch current users
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                return {"success": False, "message": "Sunucu bağlantı hatası."}
            
            users = res["record"].get("users", [])
            
            # 2. Find and update user
            user_found = False
            for user in users:
                if user.get("username") == username:
                    # Update fields
                    for key, value in profile_data.items():
                        user[key] = value
                    user_found = True
                    break
            
            if not user_found:
                return {"success": False, "message": "Kullanıcı bulunamadı."}
            
            # 3. Push updates
            update_res = self._request(f"{self.base_url}/{self.user_bin_id}", method="PUT", data={"users": users})
            
            if update_res:
                return {"success": True, "message": "Profil güncellendi."}
            return {"success": False, "message": "Profil güncellenemedi."}
            
        except Exception as e:
            print(f"[NETWORK] Profile update failed: {e}")
            return {"success": False, "message": str(e)}


    def get_user_by_username(self, username):
        try:
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                return None
            
            users = res["record"].get("users", [])
            for u in users:
                if u["username"] == username:
                    return u
            return None
        except:
            return None

    def reset_password(self, username, new_password):
        try:
            # 1. Fetch current users
            res = self._request(f"{self.base_url}/{self.user_bin_id}/latest", method="GET")
            if not res or "record" not in res:
                return {"success": False, "message": "Sunucu bağlantı hatası."}
            
            users = res["record"].get("users", [])
            
            # 2. Find and update user
            user_found = False
            for u in users:
                if u["username"] == username:
                    u["password"] = self._hash_password(new_password)
                    user_found = True
                    break
            
            if not user_found:
                return {"success": False, "message": "Kullanıcı bulunamadı."}
            
            # 3. Update bin
            update_res = self._request(f"{self.base_url}/{self.user_bin_id}", method="PUT", data={"users": users})
            if update_res:
                return {"success": True, "message": "Şifre başarıyla güncellendi."}
            return {"success": False, "message": "Güncelleme sırasında hata oluştu."}
            
        except Exception as e:
            return {"success": False, "message": str(e)}


# --- FONT LOADING ---
def load_custom_font(font_path):
    if os.path.exists(font_path):
        res = ctypes.windll.gdi32.AddFontResourceW(font_path)
        return res > 0
    return False

FONT_FAMILY = config.get("fonts", "main_font_family", default="Benz Grotesk Heavy")


# Avatar Definitions
AVATARS = {
    "1": {"icon": "🎯", "color": "#ef4444", "name": "Avcı"},
    "2": {"icon": "🧭", "color": "#3b82f6", "name": "Kaşif"},
    "3": {"icon": "🚀", "color": "#a855f7", "name": "Hızlı"},
    "4": {"icon": "⭐", "color": "#eab308", "name": "Yıldız"},
    "5": {"icon": "📚", "color": "#22c55e", "name": "Bilgin"},
    "6": {"icon": "👑", "color": "#ec4899", "name": "Kral"},
    "7": {"icon": "⚡", "color": "#f97316", "name": "Enerjik"}
}

class WordGameApp:

    def __init__(self, root):
        self.root = root
        self.root.title(config.get("ui_text", "app_title", default="Kelime Oyunu"))
        self.root.state('zoomed')  # Maximized on Windows
        self.root.geometry("1200x800") # Larger fallback
        self.root.configure(bg=BG_COLOR)
        
        # --- SCALING MECHANISM ---
        # Baseline resolution is 1920x1080
        # We try to detect the screen resolution from Tkinter
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # --- UNIVERSAL SCALING FIX (WITH MANUAL OVERRIDE) ---
        # 1. Check for manual override in config
        custom_scale = config.get("display_settings", "custom_scale", default=None)
        
        if custom_scale is not None:
             try:
                 self.scale_factor = float(custom_scale)
                 print(f"[DISPLAY] Using manual scale factor: {self.scale_factor}")
             except:
                 self.scale_factor = 1.0
        else:
            # 2. Auto-detect if no manual override
            # Baseline resolution is 1920x1080
            # We calculate scaling relative to 1920x1080.
            self.scale_factor = min(screen_w / 1920, screen_h / 1080)
            
            # We only apply a floor if it's extremely small, but keep it low 
            # enough to fit on 640px wide logical screens (300% on 1080p).
            if self.scale_factor < 0.35: self.scale_factor = 0.35
            
            print(f"[DISPLAY] Auto-detected scale factor: {self.scale_factor:.2f}")

        # --- WINDOW MODE & RESOLUTION ---
        # --- WINDOW MODE & RESOLUTION ---
        # User Request: Always start in "Windowed Fullscreen" (Maximized Window)
        # We override config settings to enforce this on startup.
        self.root.state('zoomed')
        self.root.attributes('-fullscreen', False)
        
        # Update config to reflect this state so Settings menu is consistent
        # (Optional, but good practice if Settings reads from config immediately)
        # config.set("display_settings", "fullscreen", False)


        # Start Window Controls
        self.root.after(100, self.create_window_controls)


        
        def s(val):
            """Scales a pixel value"""
            if isinstance(val, (int, float)):
                return int(val * self.scale_factor)
            return val
            
        self.s = s

        
        # Check for config updates from GitHub (non-blocking)
        config.update_from_github()
        
        # Load Custom Font
        font_yolu = resource_path("benz/Benz Grotesk.ttf")
        
        if load_custom_font(font_yolu):
            from tkinter import font as tkfont
            families = tkfont.families()
            match = [f for f in families if f.startswith("Benz")]
            self.font_main = match[0] if match else config.get("fonts", "fallback_font", default="Segoe UI")
        else:
            self.font_main = config.get("fonts", "fallback_font", default="Segoe UI")

        # --- GLOBAL FONT APPLICATION ---
        try:
             from tkinter import font as tkfont
             default_font = tkfont.nametofont("TkDefaultFont")
             default_font.configure(family=self.font_main, size=12)
             
             text_font = tkfont.nametofont("TkTextFont")
             text_font.configure(family=self.font_main, size=12)
             
             menu_font = tkfont.nametofont("TkMenuFont")
             menu_font.configure(family=self.font_main, size=12)
             
             # Apply to all future widgets that don't specify a font
             self.root.option_add("*Font", f"{{{self.font_main}}} 12")
        except Exception as e:
            print(f"Font configuration error: {e}")

        # --- TTK STYLE CONFIGURATION ---
        # Configure ComboBox to match Entry field background color
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization
        style.configure('TCombobox', 
                       fieldbackground=INPUT_BG,  # Background of the entry part
                       background=INPUT_BG,        # Background of the dropdown button
                       foreground=TEXT_COLOR,      # Text color
                       borderwidth=0,
                       relief='flat')
        style.map('TCombobox',
                 fieldbackground=[('readonly', INPUT_BG)],
                 selectbackground=[('readonly', INPUT_BG)],
                 selectforeground=[('readonly', TEXT_COLOR)])

        self.network = NetworkManager()
        self.current_user = None # {id, username}
        self.username = ""
        
        # Try to load session
        session = self.load_session()
        if session:
            self.current_user = session
            self.username = session.get('username', '')

        self.dictionary = {}
        self.current_word_data = None
        self.levels = config.get("game_settings", "levels", default=[4, 5, 6, 7, 8, 9, 10])
        self.level_idx = 0
        self.used_words = set()
        
        # Scoring Factors
        self.total_score = 0
        self.potential_score = 0
        self.revealed_indices = []
        self.time_left = config.get("game_settings", "timer_duration", default=60)
        self.timer_id = None
        self.game_start_time = None
        self.transitioning = False # State lock
        
        # Initialize Audio
        try:
            if PYGAME_AVAILABLE and config.get("sounds", "enabled", default=True):
                pygame.mixer.init()
                self.sound_enabled = True
            else:
                self.sound_enabled = False
            
            self.sounds = {}
            # Always call load_sounds to prepare MCI aliases for fallback
            self.load_sounds()
        except:
            self.log_debug("Sound initialization issue")
            # If pygame failed, we still want to try MCI if on Windows
            self.sounds = {}
            if os.name == 'nt':
                self.load_sounds()
            self.sound_enabled = False
        
        # Load dictionary
        self.load_dictionary()
        
        # Main Container
        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(expand=True, fill="both")
        
        # Global Error Handler
        self.root.report_callback_exception = self.handle_exception
        
        # Exit Handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial Cleanup
        self.cleanup_scores()
        
        # Show Entry Screen
        self.reset_game()

    def create_modern_control_button(self, parent, type="close", cmd=None):
        """Creates a modern, transparent canvas-based window control button"""
        size = self.s(40)
        canvas = tk.Canvas(parent, width=size, height=size, bg=parent['bg'], highlightthickness=0, cursor="hand2")
        
        # Internal state
        canvas.type = type
        canvas.icon_color = "white"
        canvas.normal_bg = parent['bg']
        canvas.hover_bg = "#ef4444" if type == "close" else "#475569"
        
        def render(state="normal"):
            canvas.delete("all")
            bg = canvas.hover_bg if state == "hover" else canvas.normal_bg
            
            # Subtle rounded background on hover
            if state == "hover":
                r = size // 4
                self.draw_rounded_rect(canvas, 1, 1, size-2, size-2, r, bg)
            
            # Draw Icons
            cx, cy = size // 2, size // 2
            offset = size // 5 # even smaller/more elegant
            
            if canvas.type == "close":
                canvas.create_line(cx-offset, cy-offset, cx+offset, cy+offset, fill=canvas.icon_color, width=self.s(1.5), capstyle="round")
                canvas.create_line(cx+offset, cy-offset, cx-offset, cy+offset, fill=canvas.icon_color, width=self.s(1.5), capstyle="round")
            else:
                canvas.create_line(cx-offset, cy, cx+offset, cy, fill=canvas.icon_color, width=self.s(1.5), capstyle="round")

        def update_colors(bg_color, icon_color):
            canvas.normal_bg = bg_color
            canvas.icon_color = icon_color
            canvas.config(bg=bg_color)
            render("normal")

        canvas.update_colors = update_colors

        def on_enter(e): render("hover")
        def on_leave(e): render("normal")
        def on_click(e):
            if cmd: self.root.after(50, cmd)

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", on_click)
        
        render("normal")
        return canvas

    def create_window_controls(self):
        """Creates modern top-right window controls (Minimize, Close)"""
        if not self.root.attributes("-fullscreen"):
            return

        try:
            if hasattr(self, 'win_controls_frame') and self.win_controls_frame.winfo_exists():
                self.win_controls_frame.lift()
                return

            self.win_controls_frame = tk.Frame(self.root, bg=BG_COLOR)
            self.win_controls_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-self.s(15), y=self.s(15))
            
            def on_minimize(): self.root.state('iconic')
            def on_close(): self.root.quit()

            # Create Buttons
            self.min_btn_canvas = self.create_modern_control_button(self.win_controls_frame, type="min", cmd=on_minimize)
            self.min_btn_canvas.pack(side="left", padx=2)

            self.close_btn_canvas = self.create_modern_control_button(self.win_controls_frame, type="close", cmd=on_close)
            self.close_btn_canvas.pack(side="left", padx=2)
            
            def get_brightness(hex_color):
                """Rough brightness calculation to determine icon color"""
                if not hex_color or not hex_color.startswith("#"): return 255
                try:
                    hex_color = hex_color.lstrip('#')
                    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    return (r * 0.299 + g * 0.587 + b * 0.114)
                except: return 255

            def refresh_controls():
                if hasattr(self, 'win_controls_frame') and self.win_controls_frame.winfo_exists():
                    try:
                        current_bg = BG_COLOR
                        
                        # PRIORITY 1: State-based hard fallbacks for full-bleed headers
                        if self.current_screen == "game":
                            current_bg = ACCENT_COLOR
                        elif self.current_screen == "leaderboard":
                            current_bg = DEFINITION_CARD_BG
                        else:
                            # PRIORITY 2: Intelligent background sampling
                            sample_x = self.root.winfo_width() - self.s(120) 
                            sample_y = self.s(10)
                            widget = self.root.winfo_containing(sample_x, sample_y)
                            if widget:
                                 current_bg = widget.cget('bg')
                        
                        # Determine icon color based on brightness
                        brightness = get_brightness(current_bg)
                        icon_color = "white" if brightness < 150 else "#1e293b"
                        
                        if self.win_controls_frame.cget('bg') != current_bg or self.min_btn_canvas.icon_color != icon_color:
                            self.win_controls_frame.config(bg=current_bg)
                            self.min_btn_canvas.update_colors(current_bg, icon_color)
                            self.close_btn_canvas.update_colors(current_bg, icon_color)
                            
                    except: pass
                    
                    self.win_controls_frame.lift()
                    self.root.after(300, refresh_controls) # Slightly faster refresh
            
            refresh_controls()
            
        except Exception as e:
            print(f"Window controls error: {e}")

    def load_dictionary(self):
        try:
            # 1. Try bundled resource path (standard PyInstaller location)
            json_path = resource_path("sozluk.json")
            
            # 2. Fallback: If not found in bundle, check next to the executable
            if not os.path.exists(json_path):
                json_path = os.path.join(os.path.dirname(sys.executable), "sozluk.json")
            
            # 3. Last Resort: Current working directory
            if not os.path.exists(json_path):
                json_path = os.path.join(os.getcwd(), "sozluk.json")

            with open(json_path, "r", encoding="utf-8") as f:
                self.dictionary = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"sozluk.json yüklenemedi.\nAranan Yol: {json_path}\nHata: {e}")
            self.root.destroy()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        messagebox.showerror("Kritik Hata", f"Beklenmedik bir hata oluştu:\n{error_msg}")

    def clear_container(self):
        try:
            # Efficiently destroy all children
            for widget in self.container.winfo_children():
                widget.destroy()
            # Removed update_idletasks to avoid stutter during rapid transitions
        except:
            pass

        
    def draw_rounded_rect(self, canvas, x, y, w, h, r, color, tag="rect"):
        canvas.create_oval(x, y, x+r, y+r, fill=color, outline=color, tags=tag)
        canvas.create_oval(x+w-r, y, x+w, y+r, fill=color, outline=color, tags=tag)
        canvas.create_oval(x, y+h-r, x+r, y+h, fill=color, outline=color, tags=tag)
        canvas.create_oval(x+w-r, y+h-r, x+w, y+h, fill=color, outline=color, tags=tag)
        canvas.create_rectangle(x+r/2, y, x+w-r/2, y+h, fill=color, outline=color, tags=tag)
        canvas.create_rectangle(x, y+r/2, x+w, y+h-r/2, fill=color, outline=color, tags=tag)

    def create_rounded_button(self, parent, text, cmd, width=200, height=50, bg=ACCENT_COLOR, fg=BG_COLOR, radius=25, font_size=12):
        # Scale inputs
        width = self.s(width)
        height = self.s(height)
        radius = self.s(radius)
        font_size = self.s(font_size)
        
        # Increased canvas height slightly to accommodate shadows and lift effect
        canvas = tk.Canvas(parent, width=width, height=height+self.s(10), bg=parent['bg'], highlightthickness=0, cursor="hand2")

        
        canvas.button_bg = bg
        canvas.button_fg = fg
        canvas.button_cmd = cmd
        canvas.text_val = text # Store text
        canvas.is_enabled = True
        canvas.state = "normal" # normal, hover, pressed

        def render():
            canvas.delete("all")
            offset_y = 5 
            shadow_offset = 8
            
            if not canvas.is_enabled:
                btn_color = INPUT_BG
                text_color = SUB_TEXT_COLOR
            elif canvas.state == "hover":
                offset_y = 2 
                shadow_offset = 10
                # Preserve original colors but apply the 'lift' effect for interaction
                btn_color = canvas.button_bg
                text_color = canvas.button_fg
            elif canvas.state == "pressed":
                offset_y = 8 
                shadow_offset = 5
                btn_color = canvas.button_bg
                text_color = canvas.button_fg
            else:
                offset_y = 5
                shadow_offset = 8
                btn_color = canvas.button_bg
                text_color = canvas.button_fg

            shadow_color = "#0f172a" 
            self.draw_rounded_rect(canvas, 2, shadow_offset, width-2, height, radius, shadow_color, tag="shadow")
            self.draw_rounded_rect(canvas, 0, offset_y, width, height, radius, btn_color, tag="btn_shape")
            
            if canvas.state == "hover" and radius > 0:
                canvas.create_oval(10, offset_y + 5, width-10, offset_y + 15, fill="white", stipple="gray25", outline="")

            canvas.create_text(width/2, height/2 + offset_y, text=canvas.text_val, fill=text_color, font=(self.font_main, font_size, "bold"), tag="btn_text")


        canvas.last_props = None
        def trigger_render():
            current_props = (canvas.state, canvas.is_enabled, canvas.text_val, canvas.button_bg, canvas.button_fg)
            if canvas.last_props == current_props:
                return
            canvas.last_props = current_props
            render()

        def set_text(new_text):
            if canvas.text_val != new_text:
                canvas.text_val = new_text
                trigger_render()
            
        canvas.set_text = set_text

        def on_enter(e):
            if canvas.is_enabled:
                canvas.state = "hover"
                trigger_render()
            
        def on_leave(e):
            if canvas.is_enabled:
                canvas.state = "normal"
                trigger_render()
            
        def on_press(e):
            if canvas.is_enabled:
                canvas.state = "pressed"
                trigger_render()

        def on_release(e):
            if canvas.is_enabled and canvas.state == "pressed":
                canvas.state = "hover"
                trigger_render()
                if not getattr(self, 'transitioning', False):
                    self.play_game_sound("next")
                    self.root.after(50, canvas.button_cmd)

        def set_state(state, new_bg=None, new_fg=None):
            if new_bg: canvas.button_bg = new_bg
            if new_fg: canvas.button_fg = new_fg
            canvas.is_enabled = (state != "disabled")
            canvas.config(cursor="hand2" if canvas.is_enabled else "arrow")
            canvas.state = "normal"
            render()

        canvas.set_state = set_state
        render() # Initial draw
        
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        return canvas

    def show_entry_screen(self):
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        
        # Logo
        theme = config.get("display_settings", "theme", default="dark")
        
        # DEBUG LOGGING
        try:
            debug_log_path = os.path.join(os.getcwd(), "debug_logo.txt")
            with open(debug_log_path, "a") as logf:
                logf.write(f"\n--- LOGO DEBUG {datetime.now()} ---\n")
                logf.write(f"Theme: {theme}\n")
                logf.write(f"PILLOW_AVAILABLE: {PILLOW_AVAILABLE}\n")
        except Exception as e:
            print(f"Logging failed: {e}")

        # Explicitly choose logo based on theme
        # Use v11 logo (Flood Fill + Soft Edge)
        icon_name = "logo_dark_v11.png" if theme == "dark" else "logo_light.png"
        logo_path = resource_path(os.path.join("assets", icon_name))
        
        try:
            with open(debug_log_path, "a") as logf:
                logf.write(f"Target Logo Name: {icon_name}\n")
                logf.write(f"Target Path: {logo_path}\n")
                logf.write(f"Path Exists: {os.path.exists(logo_path)}\n")
        except: pass

        # Fallback logic: If specific theme logo missing, try the other one
        if not os.path.exists(logo_path):
            alt_icon = "logo_light.png" if theme == "dark" else "logo_dark.png"
            alt_path = resource_path(os.path.join("assets", alt_icon))
            if os.path.exists(alt_path):
                logo_path = alt_path
                try:
                    with open(debug_log_path, "a") as logf:
                        logf.write(f"Fallback to Alt Path: {alt_path}\n")
                except: pass

        try:
            if PILLOW_AVAILABLE and os.path.exists(logo_path):
                img = Image.open(logo_path).convert("RGBA")
                # Scale to fit reasonable width
                # Scale to fit reasonable width
                base_width = 2000 # Adjusted to intermediate size (User Feedback: 2400 was too big)
                
                try:
                    with open(debug_log_path, "a") as logf:
                        logf.write(f"Resizing with Base Width: {base_width}\n")
                except: pass

                target_width = self.s(base_width)
                ratio = target_width / float(img.size[0])
                target_height = int(float(img.size[1]) * ratio)
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img) # Keep reference
                
                logo_lbl = tk.Label(frame, image=self.logo_img, bg=BG_COLOR)
                logo_lbl.pack(pady=(self.s(30), self.s(50)))
                try:
                    with open(debug_log_path, "a") as logf:
                        logf.write("Logo Packed (Pillow)\n")
                except: pass
            
            elif os.path.exists(logo_path):
                # Fallback to standard PhotoImage if Pillow not available
                self.logo_img = tk.PhotoImage(file=logo_path)
                logo_lbl = tk.Label(frame, image=self.logo_img, bg=BG_COLOR)
                logo_lbl.pack(pady=(self.s(30), self.s(50)))
                try:
                    with open(debug_log_path, "a") as logf:
                        logf.write("Logo Packed (Standard PhotoImage)\n")
                except: pass
                
            else:
                # Fallback to Text if NO logo found
                try:
                    with open(debug_log_path, "a") as logf:
                        logf.write("NO LOGO FOUND - Raising Error\n")
                except: pass
                raise FileNotFoundError(f"Logo not found at {logo_path}")

        except Exception as e:
            try:
                with open(debug_log_path, "a") as logf:
                    logf.write(f"EXCEPTION: {e}\n")
            except: pass
            print(f"Logo load error: {e}")
            welcome_title = config.get("ui_text", "welcome_title", default="KELİME OYUNU")
            tk.Label(frame, text=welcome_title, font=(self.font_main, self.s(84), "bold"), 
                     fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(self.s(30), self.s(50)))
        
        # Auth State Logic
        if self.current_user:
            # LOGGED IN VIEW
            # Identity Container (Top-Left)
            id_frame = tk.Frame(self.container, bg=BG_COLOR)
            id_frame.place(relx=0.02, rely=0.02, anchor="nw")
            
            # Username
            u_label = tk.Label(id_frame, text=self.current_user['username'], 
                     font=(self.font_main, self.s(12)), 
                     fg="#e619e5", bg=BG_COLOR, cursor="hand2")
            u_label.pack(side="left")
            u_label.bind("<Button-1>", lambda e: self.show_profile_screen())
            
            # Rank (Next to username, No Icon)
            stats = self.get_user_stats(self.current_user['username'])
            tk.Label(id_frame, text=stats['rank'], 
                     font=(self.font_main, self.s(12), "bold"), 
                     fg="#fbbf24", bg=BG_COLOR).pack(side="left", padx=(10, 0))
            
            self.create_rounded_button(frame, "OYUNA BAŞLA", self.start_game_as_user, 
                                     width=280, height=60, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=self.s(20))
                                     
            # Removed "ÇIKIŞ YAP" button as per user request
                                     
        else:
            # GUEST / LOGIN VIEW
            btn_frame = tk.Frame(frame, bg=BG_COLOR)
            btn_frame.pack(pady=self.s(30))
            
            self.create_rounded_button(btn_frame, "GİRİŞ YAP", self.show_login_screen, 
                                     width=220, height=60, bg=ACCENT_COLOR, fg=BG_COLOR).pack(side="left", padx=10)
                                     
            self.create_rounded_button(btn_frame, "KAYIT OL", self.show_register_screen, 
                                     width=220, height=60, bg="#db2777", fg="white").pack(side="left", padx=10)
            
            # Guest Option
            tk.Label(frame, text="veya", font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(pady=self.s(10))
            
            self.create_rounded_button(frame, "MİSAFİR OLARAK OYNA", self.show_guest_input, 
                                     width=300, height=50, bg=BG_COLOR, fg=SUB_TEXT_COLOR, radius=15).pack()

        # Links Footer
        self._create_footer_links()

    def _create_footer_links(self):
        # Update Check Link (Left Corner)
        update_frame = tk.Frame(self.container, bg=BG_COLOR)
        update_frame.place(relx=0.02, rely=0.98, anchor="sw")
        
        settings_link = tk.Label(update_frame, text="Ayarlar", font=(self.font_main, self.s(12)), 
                               fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        settings_link.pack(side="left", padx=self.s(15))
        settings_link.bind("<Button-1>", lambda e: self.show_settings_menu())

        # Admin Link
        if getattr(self, 'current_user', None) and str(self.current_user.get('username', '')).upper() == "OKAN707":
             admin_link = tk.Label(update_frame, text="Tüm Üyeler", font=(self.font_main, self.s(12)), 
                                  fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
             admin_link.pack(side="left", padx=self.s(15))
             admin_link.bind("<Button-1>", lambda e: self.show_admin_users_screen())

        # Update link moved to Settings Menu as requested
        
        # Other Links (Right Corner)
        links_frame = tk.Frame(self.container, bg=BG_COLOR)
        links_frame.place(relx=0.98, rely=0.98, anchor="se")

        # Settings Link Removed from here (Moved to left)
        # settings_link = tk.Label(links_frame, text="Ayarlar"...

        lb_link = tk.Label(links_frame, text="Puan Durumu", font=(self.font_main, self.s(12)), 
                           fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        lb_link.pack(side="left", padx=self.s(15))
        lb_link.bind("<Button-1>", lambda e: self.show_leaderboard(source="entry"))
        
        contact_link = tk.Label(links_frame, text="İletişim", font=(self.font_main, self.s(12)), 
                             fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        contact_link.pack(side="left", padx=self.s(15))
        contact_link.bind("<Button-1>", lambda e: self.show_contact())

        about_link = tk.Label(links_frame, text="Hakkında", font=(self.font_main, self.s(12)), 
                           fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        about_link.pack(side="left", padx=self.s(15))
        about_link.bind("<Button-1>", lambda e: self.show_about())

        if self.current_user:
            logout_link = tk.Label(links_frame, text="Çıkış", font=(self.font_main, self.s(12), "bold"), 
                               fg="#ef4444", bg=BG_COLOR, cursor="hand2")
            logout_link.pack(side="left", padx=(self.s(15), 0))
            logout_link.bind("<Button-1>", lambda e: self.logout())

    def show_guest_input(self):
        self.current_screen = "guest_login"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        
        tk.Label(frame, text="MİSAFİR GİRİŞİ", font=(self.font_main, self.s(36), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(self.s(30), self.s(50)))

        entry_strip = tk.Frame(frame, bg=INPUT_BG, height=self.s(90))
        entry_strip.pack_propagate(False)
        entry_strip.pack(pady=self.s(10), fill="x")

        placeholder = "ADINIZ - SOYADINIZ"
        self.name_entry = tk.Entry(entry_strip, font=(self.font_main, self.s(36), "bold"), bg=INPUT_BG, fg=SUB_TEXT_COLOR, 
                                  insertbackground="white", relief="flat", justify="center", bd=0)
        self.name_entry.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        self.name_entry.insert(0, placeholder)
        
        # ... (Focus bindings kept inline or reused) ...
        self.name_entry.bind("<FocusIn>", lambda e: self.entry_focus_in(self.name_entry, placeholder))
        self.name_entry.bind("<FocusOut>", lambda e: self.entry_focus_out(self.name_entry, placeholder))
        self.name_entry.bind("<Return>", self.handle_enter_key)
        
        self.start_btn = self.create_rounded_button(frame, "OYUNA BAŞLA", self.handle_start, width=280, height=60)
        self.start_btn.pack(pady=self.s(40))
        
        # Back Button (Matching other screens' style)
        back_container = tk.Frame(self.container, bg=BG_COLOR)
        back_container.place(relx=0.5, rely=0.92, anchor="center")
        
        self.create_rounded_button(back_container, "GERİ DÖN", self.show_entry_screen, width=200, height=50, bg="#ef4444", fg="white").pack()    
        # Removed old settings/exit buttons from here, now in links
        pass

    def show_login_screen(self):
        self.current_screen = "login"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="GİRİŞ YAP", font=(self.font_main, self.s(48), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(30)))
                 
        # Username
        tk.Label(frame, text="KULLANICI ADI", font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
        u_entry = tk.Entry(frame, font=(self.font_main, self.s(18)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center")
        u_entry.pack(pady=(5, 15), ipady=10, fill="x")
        u_entry.focus_set()
        
        # Password
        tk.Label(frame, text="ŞİFRE", font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
        p_entry = tk.Entry(frame, font=(self.font_main, self.s(18)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center", show="*")
        p_entry.pack(pady=(5, 30), ipady=10, fill="x")
        
        def submit_login():
            u = u_entry.get().strip()
            p = p_entry.get().strip()
            if not u or not p:
                messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun.")
                return
            
            res = self.network.login(u, p)
            if res.get("success"):
                self.current_user = {"id": res["user_id"], "username": res["username"]}
                self.username = res["username"]
                
                # SYNC: Update local profile with cloud data
                cloud_profile = res.get("profile", {})
                # Filter out sensitive or system fields if necessary, or just save relevant ones
                # We want to keep local logic consistent, so we match keys used in get_profile_data
                profile_to_save = {
                    "fullname": cloud_profile.get("fullname", ""),
                    "birthdate": cloud_profile.get("birth_date", "") or cloud_profile.get("birthdate", ""),
                    "gender": cloud_profile.get("gender", ""),
                    "school": cloud_profile.get("school", ""),
                    "class_level": cloud_profile.get("class_level", ""),
                    "avatar_id": cloud_profile.get("avatar_id", "1")
                }
                self.save_profile_data(self.username, profile_to_save, push_to_cloud=False) # Don't push back what we just got
                
                self.save_session(self.current_user) # Persist Login
                self.show_entry_screen()
            else:
                messagebox.showerror("Hata", res.get("message", "Giriş başarısız."))

        self.create_rounded_button(frame, "GİRİŞ YAP", submit_login, width=250, height=60).pack(pady=10)
        
        self.create_rounded_button(frame, "GERİ DÖN", self.show_entry_screen, width=250, height=50, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack(pady=(0, 20))

        # Forgot Password Link (Moved to bottom)
        forgot_link = tk.Label(frame, text="Şifremi Unuttum?", font=(self.font_main, self.s(12)), 
                              fg=TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        forgot_link.pack(pady=5)
        forgot_link.bind("<Button-1>", lambda e: self.show_forgot_password())

    def show_forgot_password(self):
        """Multi-step password recovery: Username → Birth Date → Security Question → New Password"""
        self.current_screen = "forgot_password"
        self.clear_container()
        
        # State variables for multi-step process
        self.fp_step = 1
        self.fp_username = ""
        self.fp_user_data = None
        
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = tk.Label(frame, text="ŞİFRE KURTARMA", font=(self.font_main, self.s(36), "bold"), 
                              fg=ACCENT_COLOR, bg=BG_COLOR)
        title_label.pack(pady=(0, self.s(20)))
        
        # Step indicator
        step_label = tk.Label(frame, text="", font=(self.font_main, self.s(14)), 
                             fg=SUB_TEXT_COLOR, bg=BG_COLOR)
        step_label.pack(pady=(0, self.s(30)))
        
        # Content frame (will be updated for each step)
        content_frame = tk.Frame(frame, bg=BG_COLOR)
        content_frame.pack(fill="both", expand=True)
        
        def show_step_1():
            """Step 1: Username Entry"""
            self.fp_step = 1
            step_label.config(text="Adım 1/4: Kullanıcı Adınızı Girin")
            
            # Clear content
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            tk.Label(content_frame, text="KULLANICI ADI", font=(self.font_main, self.s(14)), 
                    fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            username_entry = tk.Entry(content_frame, font=(self.font_main, self.s(18)), 
                                     bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center")
            username_entry.pack(pady=(5, 20), ipady=10, fill="x")
            username_entry.focus_set()
            
            def verify_username():
                username = username_entry.get().strip().upper()
                if not username:
                    messagebox.showwarning("Hata", "Lütfen kullanıcı adınızı girin.")
                    return
                
                # Check if user exists
                user_data = self.network.get_user_by_username(username)
                if not user_data:
                    messagebox.showerror("Hata", "Bu kullanıcı adı bulunamadı.")
                    return
                
                self.fp_username = username
                self.fp_user_data = user_data
                show_step_2()
            
            self.create_rounded_button(content_frame, "DEVAM ET", verify_username, 
                                      width=250, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=10)
        
        def show_step_2():
            """Step 2: Birth Date Verification"""
            self.fp_step = 2
            step_label.config(text="Adım 2/4: Doğum Tarihinizi Doğrulayın")
            
            # Clear content
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            tk.Label(content_frame, text=f"Kullanıcı: {self.fp_username}", 
                    font=(self.font_main, self.s(14), "bold"), 
                    fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, 20))
            
            tk.Label(content_frame, text="DOĞUM TARİHİ (GG.AA.YYYY)", 
                    font=(self.font_main, self.s(14)), 
                    fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            dob_entry = tk.Entry(content_frame, font=(self.font_main, self.s(18)), 
                                bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center")
            dob_entry.pack(pady=(5, 20), ipady=10, fill="x")
            dob_entry.focus_set()
            
            def verify_dob():
                dob = dob_entry.get().strip()
                if not dob:
                    messagebox.showwarning("Hata", "Lütfen doğum tarihinizi girin.")
                    return
                
                # Check multiple potential keys for birth date
                stored_dob = self.fp_user_data.get("birth_date", "").strip()
                if not stored_dob:
                    stored_dob = self.fp_user_data.get("birthdate", "").strip()
                
                # Debug Logging
                print(f"[DEBUG] Password Recovery - User Data Keys: {list(self.fp_user_data.keys())}")
                print(f"[DEBUG] Stored DOB: '{stored_dob}'")

                # Normalization helper to handle DD.MM.YYYY, D.M.YYYY, DD/MM/YYYY etc.
                def normalize_date(d):
                    try:
                        # Replace common separators with dot
                        d = d.replace("/", ".").replace("-", ".")
                        parts = d.split(".")
                        if len(parts) == 3:
                            # Pad day and month with zeros (e.g. 1 -> 01)
                            return f"{int(parts[0]):02d}.{int(parts[1]):02d}.{parts[2]}"
                    except:
                        pass
                    return d

                normalized_input = normalize_date(dob)
                normalized_stored = normalize_date(stored_dob)
                
                if normalized_input != normalized_stored:
                    msg = f"Doğum tarihi eşleşmiyor!\nSistemdeki: '{stored_dob}'"
                    if not stored_dob:
                        msg = "Bu hesap için doğum tarihi kayıtlı değil."
                    messagebox.showerror("Hata", msg)
                    return
                
                # Check if user has security question
                if not self.fp_user_data.get("security_question"):
                    messagebox.showerror("Hata", 
                                       "Bu hesap için güvenlik sorusu tanımlanmamış.\\n" +
                                       "Lütfen yöneticinizle iletişime geçin.")
                    return
                
                show_step_3()
            
            self.create_rounded_button(content_frame, "DEVAM ET", verify_dob, 
                                      width=250, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=10)
            self.create_rounded_button(content_frame, "GERİ", show_step_1, 
                                      width=250, height=40, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack()
        
        def show_step_3():
            """Step 3: Security Question Verification"""
            self.fp_step = 3
            step_label.config(text="Adım 3/4: Güvenlik Sorusunu Cevaplayın")
            
            # Clear content
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            tk.Label(content_frame, text=f"Kullanıcı: {self.fp_username}", 
                    font=(self.font_main, self.s(14), "bold"), 
                    fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, 20))
            
            # Display security question
            security_q = self.fp_user_data.get("security_question", "")
            tk.Label(content_frame, text=security_q, 
                    font=(self.font_main, self.s(16)), 
                    fg=TEXT_COLOR, bg=BG_COLOR, wraplength=400).pack(pady=(0, 10))
            
            tk.Label(content_frame, text="CEVABINIZ", 
                    font=(self.font_main, self.s(14)), 
                    fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            answer_entry = tk.Entry(content_frame, font=(self.font_main, self.s(18)), 
                                   bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center")
            answer_entry.pack(pady=(5, 20), ipady=10, fill="x")
            answer_entry.focus_set()
            
            def verify_answer():
                answer = answer_entry.get().strip()
                if not answer:
                    messagebox.showwarning("Hata", "Lütfen cevabınızı girin.")
                    return
                
                correct_answer = self.fp_user_data.get("security_answer", "")
                if answer.lower() != correct_answer.lower():
                    messagebox.showerror("Hata", "Güvenlik sorusu cevabı yanlış!")
                    return
                
                show_step_4()
            
            self.create_rounded_button(content_frame, "DEVAM ET", verify_answer, 
                                      width=250, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=10)
            self.create_rounded_button(content_frame, "GERİ", show_step_2, 
                                      width=250, height=40, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack()
        
        def show_step_4():
            """Step 4: New Password Entry"""
            self.fp_step = 4
            step_label.config(text="Adım 4/4: Yeni Şifrenizi Belirleyin")
            
            # Clear content
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            tk.Label(content_frame, text="YENİ ŞİFRE", 
                    font=(self.font_main, self.s(14)), 
                    fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            new_pass_entry = tk.Entry(content_frame, font=(self.font_main, self.s(18)), 
                                     bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center", show="*")
            new_pass_entry.pack(pady=(5, 15), ipady=10, fill="x")
            new_pass_entry.focus_set()
            
            tk.Label(content_frame, text="YENİ ŞİFRE (TEKRAR)", 
                    font=(self.font_main, self.s(14)), 
                    fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            confirm_pass_entry = tk.Entry(content_frame, font=(self.font_main, self.s(18)), 
                                         bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center", show="*")
            confirm_pass_entry.pack(pady=(5, 20), ipady=10, fill="x")
            
            def reset_password():
                new_pass = new_pass_entry.get().strip()
                confirm_pass = confirm_pass_entry.get().strip()
                
                if not new_pass or not confirm_pass:
                    messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun.")
                    return
                
                if new_pass != confirm_pass:
                    messagebox.showerror("Hata", "Şifreler eşleşmiyor!")
                    return
                
                if len(new_pass) < 4:
                    messagebox.showwarning("Hata", "Şifre en az 4 karakter olmalıdır.")
                    return
                
                # Reset password via backend
                res = self.network.reset_password(self.fp_username, new_pass)
                if res.get("success"):
                    messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi!\\nŞimdi giriş yapabilirsiniz.")
                    self.show_login_screen()
                else:
                    messagebox.showerror("Hata", res.get("message", "Şifre sıfırlama başarısız."))
            
            self.create_rounded_button(content_frame, "ŞİFREYİ DEĞİŞTİR", reset_password, 
                                      width=250, height=50, bg="#22c55e", fg="white").pack(pady=10)
            self.create_rounded_button(content_frame, "GERİ", show_step_3, 
                                      width=250, height=40, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack()
        
        # Start with step 1
        show_step_1()
        
        # Back to login button (bottom)
        back_container = tk.Frame(self.container, bg=BG_COLOR)
        back_container.place(relx=0.5, rely=0.92, anchor="center")
        self.create_rounded_button(back_container, "GİRİŞE DÖN", self.show_login_screen, 
                                   width=200, height=50, bg="#ef4444", fg="white").pack()

    def show_register_screen(self):
        self.current_screen = "register"
        self.clear_container()
        
        # Main container frame - centered
        # Increased size to fit everything, removed fixed size to allow autosizing with padding
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        tk.Label(frame, text="KAYIT OL", font=(self.font_main, self.s(32), "bold"), 
                 fg="#ec4899", bg=BG_COLOR).pack(pady=(0, 20))

        # Helper to create inputs with slightly tighter spacing
        def create_input(label_text, is_password=False):
            # Container for each field to keep them tidy
            field_frame = tk.Frame(frame, bg=BG_COLOR)
            field_frame.pack(fill="x", pady=2)
            
            tk.Label(field_frame, text=label_text, font=(self.font_main, self.s(11)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            entry = tk.Entry(field_frame, font=(self.font_main, self.s(13)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center", show="*" if is_password else "")
            entry.pack(ipady=6, fill="x")
            return entry
        
        # Helper to create dropdown
        def create_dropdown(label_text, values):
            field_frame = tk.Frame(frame, bg=BG_COLOR)
            field_frame.pack(fill="x", pady=2)
            
            tk.Label(field_frame, text=label_text, font=(self.font_main, self.s(11)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
            combo = ttk.Combobox(field_frame, values=values, state="readonly", font=(self.font_main, self.s(13)), justify="center")
            combo.pack(ipady=6, fill="x")
            return combo

        # Grid-like layout using pack? No, vertical stack is fine if compact.
        # Or maybe two columns? User said "alt alta" (one under another).
        # We will stick to one column but compact.
        
        u_entry = create_input("KULLANICI ADI *")
        p_entry = create_input("ŞİFRE *", is_password=True)
        p_confirm_entry = create_input("ŞİFRE (TEKRAR) *", is_password=True)
        fullname_entry = create_input("AD - SOYAD *")
        dob_entry = create_input("DOĞUM TARİHİ (GG.AA.YYYY) *")
        
        # Gender Dropdown (ERKEK/KIZ)
        gender_combo = create_dropdown("CİNSİYET *", ["ERKEK", "KIZ"])
        
        # School Dropdown (Previously registered schools + "Yeni okul ekle")
        # Get list of previously registered schools from profiles
        schools_set = set()
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "profiles.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    all_profiles = json.load(f)
                    for username, profile in all_profiles.items():
                        school = profile.get("school", "").strip()
                        if school and school != "-":
                            schools_set.add(school)
        except:
            pass
        
        school_list = sorted(list(schools_set)) + ["Yeni okul ekle"]
        school_combo = create_dropdown("OKUL *", school_list)
        
        # Make ComboBox editable when "Yeni okul ekle" is selected
        def on_school_change(event):
            if school_combo.get() == "Yeni okul ekle":
                school_combo.config(state="normal")
                school_combo.set("")  # Clear the text
                school_combo.focus()
            else:
                school_combo.config(state="readonly")
        
        school_combo.bind("<<ComboboxSelected>>", on_school_change)
        
        class_entry = create_input("SINIF *")
        
        # Security Question for Password Recovery
        security_questions = [
            "İlk evcil hayvanınızın adı neydi?",
            "En sevdiğiniz yemek hangisidir?",
            "İlk okulunuzun adı neydi?",
            "En sevdiğiniz renk nedir?",
            "Doğduğunuz şehir neresidir?",
            "En sevdiğiniz çizgi film kahramanı kim?",
            "En sevdiğiniz ders hangisi?",
            "En iyi arkadaşınızın adı ne?",
            "Hangi takımı tutuyorsunuz?",
            "Büyüyünce ne olmak istersiniz?"
        ]
        security_q_combo = create_dropdown("GÜVENLİK SORUSU *", security_questions)
        security_a_entry = create_input("GÜVENLİK SORUSU CEVABI *")

        def submit_register():
            u = u_entry.get().strip()
            p = p_entry.get().strip()
            p_conf = p_confirm_entry.get().strip()
            fullname = fullname_entry.get().strip()
            dob = dob_entry.get().strip()
            gender = gender_combo.get().strip()
            
            # Get school value directly from ComboBox
            school = school_combo.get().strip()
            
            class_lvl = class_entry.get().strip()
            
            # Get security question and answer
            security_q = security_q_combo.get().strip()
            security_a = security_a_entry.get().strip()

            if not all([u, p, p_conf, fullname, dob, gender, school, class_lvl, security_q, security_a]):
                messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun.")
                return
            
            if " " in u:
                messagebox.showwarning("Hata", "Kullanıcı adı boşluk içeremez!")
                return
            
            if p != p_conf:
                messagebox.showerror("Hata", "Şifreler eşleşmiyor!")
                return
            
            # Convert gender to E/K for backend compatibility
            gender_code = "E" if gender == "ERKEK" else "K"

            res = self.network.register(u, p, fullname, dob, gender_code, school, class_lvl, security_q, security_a)
            if res.get("success"):
                messagebox.showinfo("Başarılı", "Kayıt başarılı! Lütfen giriş yapın.")
                self.show_login_screen()
            else:
                messagebox.showerror("Hata", res.get("message", "Kayıt başarısız."))

        # Buttons
        self.create_rounded_button(frame, "KAYIT OL", submit_register, width=400, height=45, bg="#db2777", fg="white").pack(pady=(20, 10), padx=self.s(30))
        self.create_rounded_button(frame, "GERİ DÖN", self.show_entry_screen, width=400, height=40, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack(padx=self.s(30))
    
    def logout(self):
        self.current_user = None
        self.username = ""
        self.clear_session() # Remove session file
        self.show_entry_screen()
        
    def start_game_as_user(self):
        self.username = self.current_user['username']
        self._reset_game_state()
        self.show_game_screen()
        self.game_start_time = time.time()
        
    def entry_focus_in(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT_COLOR)
            
    def entry_focus_out(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=SUB_TEXT_COLOR)

    def show_contact(self):
        self.current_screen = "contact"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        # Match game screen content structure
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        
        tk.Label(frame, text="İLETİŞİM", font=(self.font_main, self.s(48), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(30)))
        
        contact_intro = (
            "Görüş, öneri veya destek için X ve Instagram üzerinden\n"
            "bizimle iletişime geçebilirsiniz:"
        )
        
        tk.Label(frame, text=contact_intro, font=(self.font_main, self.s(20)), 
                 fg=TEXT_COLOR, bg=BG_COLOR, justify="center").pack(pady=(self.s(20), 0))
                 
        tk.Label(frame, text="@okan707 - OKAN BAYINDIR", font=(self.font_main, self.s(24), "bold"), 
                 fg="#ec4899", bg=BG_COLOR, justify="center").pack(pady=(self.s(10), self.s(20)))

        # GitHub Link (User Request)
        tk.Label(frame, text="Diğer uygulamalar için Github:", font=(self.font_main, self.s(20)), 
                 fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(self.s(10), 0))
                 
        gh_lbl = tk.Label(frame, text="www.github.com/Okan707", font=(self.font_main, self.s(24), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR, cursor="hand2")
        gh_lbl.pack(pady=(0, self.s(20)))
        gh_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Okan707"))

            
        # Back Button (Matching leaderboard style and position)
        back_container = tk.Frame(self.container, bg=BG_COLOR)
        back_container.place(relx=0.5, rely=0.92, anchor="center")
        
        self.create_rounded_button(back_container, "GERİ DÖN", self.show_entry_screen, width=200, height=50, bg="#ef4444", fg="white").pack()

    def show_about(self):
        self.current_screen = "about"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(frame, text="HAKKINDA", font=(self.font_main, self.s(48), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(30)))

        
        scroll = ScrollableFrame(frame, bg=BG_COLOR)
        scroll.pack(fill="both", expand=True)
        content = scroll.scrollable_frame
        
        # Modular text parts to allow for bold/normal mix
        sections = [
            ("Kelime Avcısı ile Türkçenin Zirvesine Tırmanmaya Hazır Mısın?", True),
            ("Merhaba Kelime Avcısı! Kelimelerin büyülü dünyasına adım atmaya hazır mısın? \"Kelime Avcısı\", sadece bir oyun değil, aynı zamanda zihnini keskinleştirecek bir bilgi yarışması!", False),
            ("Nasıl Oynanır?", True),
            ("Oyunumuz, senin adınla başlıyor. Giriş ekranında ismini yaz ve maceraya atıl! Karşına Türkçemizin en seçkin kelimeleri çıkacak. Ama dikkat et, kelimeleri sana doğrudan vermiyoruz; önce anlamlarını okuyacak, sonra gizli kelimeyi bulmaya çalışacaksın.\n\nKlavye Kısayolları:\n• ENTER: Oyunu Başlat / Cevapla / Sıradaki Soru\n• BOŞLUK (SPACE): Harf İste", False),
            ("Kurallar Basit, Heyecan Yüksek:", False),
            ("Basitten Zora", True),
            ("Isınma turları 4 harfli kelimelerle başlar. Sen ustalaştıkça kelimeler uzar ve 10 harfe kadar çıkar.", False),
            ("Puan Sistemi", True),
            ("Kelimelerin uzunluğu arttıkça kazanacağın puan da artar:\n• 4 Harfli: 100 Puan\n• 5 Harfli: 125 Puan\n• 6 Harfli: 150 Puan\n• 7 Harfli: 175 Puan\n• 8 Harfli: 200 Puan\n• 9 Harfli: 225 Puan\n• 10 Harfli: 250 Puan", False),
            ("Süre ve Strateji", True),
            ("Ayarlar menüsünden seçeceğin oyun süresi, kazancını katlar:\n• 30 Saniye (Zor): 2.5 Kat Puan!\n• 45 Saniye (Orta): 1.5 Kat Puan!\n• 60 Saniye (Standart): 1.0 Kat Puan!\n\nUnutma; kısa sürede hızlı düşünmek seni liderlik tablosunda çok daha yukarılara taşır!", False),
            ("Harf İste ve Risk", True),
            ("Eğer cevabı bulamazsan \"Harf İste\" butonunu kullanabilirsin. Her harf isteği, seçtiğin süre çarpanına göre puanını 25 puan (taban) düşürür. Eğer kelimenin tüm harflerini açarsan, o kelimeden 0 puan alırsın!", False),
            ("Hedef", True),
            ("En az ipucu ile en yüksek puanı toplayıp, Türkçenin ustası olduğunu kanıtlamak!", False),
            ("Seviye ve Rütbe Sistemi", True),
            ("Puanına göre kazanabileceğin rütbeler:\n• Yeni Çaylak: 0 - 50.000 Puan\n• Meraklı Oyuncu: 50.001 - 250.000 Puan\n• Kelime Avcısı: 250.001 - 1.000.000 Puan\n• Kelime Üstadı: 1.000.000+ Puan", False),
            ("Neden Kelime Avcısı?", True),
            ("Okulda öğrendiğin konuları pekiştirmek, \"Dilimizin Zenginlikleri\"ni keşfetmek ve kelime hazineni geliştirmek hiç bu kadar eğlenceli olmamıştı. Hem yarış hem öğren!", False),
            ("Hazırsan etkileşimli tahtanın başına geç, Kelime Avcısı başlıyor!", False)
        ]
        
        for text, is_bold in sections:
            font_style = (self.font_main, self.s(18), "bold") if is_bold else (self.font_main, self.s(16))
            pady_val = (self.s(20), self.s(5)) if is_bold else (0, self.s(15))
            # Use pink color for bold headers to make them more eye-catching
            fg_color = "#ec4899" if is_bold else TEXT_COLOR
            
            lbl = tk.Label(content, text=text, font=font_style, 
                           fg=fg_color, bg=BG_COLOR, justify="left", wraplength=self.s(750))
            lbl.pack(anchor="nw", padx=self.s(20), pady=pady_val)

            
        scroll.update_scroll()
        
        # Back Button (Matching leaderboard style and position)
        back_container = tk.Frame(self.container, bg=BG_COLOR)
        back_container.place(relx=0.5, rely=0.92, anchor="center")
        
        self.create_rounded_button(back_container, "GERİ DÖN", self.show_entry_screen, width=200, height=50, bg="#ef4444", fg="white").pack()

    def show_settings_menu(self):
        self.current_screen = "settings"
        self.clear_container()
        
        # Center Container (Card Style)
        # Using theme-aware CARD_COLOR for the card effect
        card_bg = CARD_COLOR
            
        card_frame = tk.Frame(self.container, bg=card_bg)
        card_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=1.0)
        
        # Add Scrollable Frame for settings content
        scroll = ScrollableFrame(card_frame, bg=card_bg)
        scroll.pack(fill="both", expand=True)
        inner_frame = scroll.scrollable_frame
        
        # Horizontal padding via a wrapper in inner_frame for better aesthetics
        content_wrapper = tk.Frame(inner_frame, bg=card_bg, padx=self.s(80), pady=self.s(40))
        content_wrapper.pack(fill="both", expand=True)
        inner_frame = content_wrapper # Override for easier grid usage

        # Header
        tk.Label(inner_frame, text="AYARLAR", font=(self.font_main, self.s(36), "bold"), 
                 fg=TEXT_COLOR, bg=card_bg).grid(row=0, column=0, columnspan=2, pady=(0, self.s(30)))

        # Configure Grid Weights for Symmetry
        inner_frame.columnconfigure(0, weight=1)
        inner_frame.columnconfigure(1, weight=1)

        # --- Section 1: GÖRÜNÜM ---
        tk.Label(inner_frame, text="GÖRÜNÜM", font=(self.font_main, self.s(14), "bold"), 
                 fg=ACCENT_COLOR, bg=card_bg).grid(row=1, column=0, sticky="w", pady=(10, 5))
                 
        tk.Frame(inner_frame, height=2, bg=ACCENT_COLOR).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Scale
        tk.Label(inner_frame, text="Arayüz Ölçeği:", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=3, column=0, sticky="w", pady=10)
                 
        scale_var = tk.DoubleVar(value=self.scale_factor)
        # Scale Container for alignment
        scale_frame = tk.Frame(inner_frame, bg=card_bg)
        scale_frame.grid(row=3, column=1, sticky="e", pady=10)
        
        scale_slider = tk.Scale(scale_frame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", 
                                variable=scale_var, bg=card_bg, fg=TEXT_COLOR, 
                                activebackground=ACCENT_COLOR, highlightthickness=0, length=self.s(200)) # Slightly shorter for fit
        scale_slider.pack(side="left")
        
        # Label removed per user request (slider has built-in value)
        # val_lbl = tk.Label(scale_frame, text=f"{self.scale_factor:.1f}x", font=(self.font_main, 14, "bold"), fg=TEXT_COLOR, bg=card_bg)
        # val_lbl.pack(side="left", padx=(10, 0))
        # scale_slider.config(command=lambda v: val_lbl.config(text=f"{float(v):.1f}x"))

        # Resolution
        tk.Label(inner_frame, text="Çözünürlük:", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=4, column=0, sticky="w", pady=10)
                 
        res_options = {
            "Tam Ekran": "fullscreen",
            "2560x1440": "2560x1440",
            "1920x1080": "1920x1080",
            "1600x900": "1600x900", 
            "1536x864": "1536x864",
            "1440x900": "1440x900",
            "1366x768": "1366x768",
            "1280x720": "1280x720",
            "1024x768": "1024x768"
        }
        reverse_res_options = {v: k for k, v in res_options.items()}
        
        current_res = config.get("display_settings", "resolution")
        is_full = config.get("display_settings", "fullscreen")
        init_res_val = "Tam Ekran"
        if not is_full and current_res in reverse_res_options:
            init_res_val = reverse_res_options[current_res]
            
        res_dropdown = ttk.Combobox(inner_frame, values=list(res_options.keys()), state="readonly", font=(self.font_main, self.s(12)), width=18)
        res_dropdown.set(init_res_val)
        res_dropdown.grid(row=4, column=1, sticky="e", pady=10) # Right Aligned

        # Theme Mode
        tk.Label(inner_frame, text="Görünüm Modu:", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=5, column=0, sticky="w", pady=10)
                 
        theme_options = {"Karanlık": "dark", "Aydınlık": "light"}
        reverse_theme_options = {v: k for k, v in theme_options.items()}
        current_theme = config.get("display_settings", "theme", default="dark")
        
        theme_dropdown = ttk.Combobox(inner_frame, values=list(theme_options.keys()), state="readonly", font=(self.font_main, self.s(12)), width=18)
        theme_dropdown.set(reverse_theme_options.get(current_theme, "Karanlık"))
        theme_dropdown.grid(row=5, column=1, sticky="e", pady=10) # Right Aligned

        # --- Section 2: OYUN & SES ---
        tk.Label(inner_frame, text="OYUN & SES", font=(self.font_main, self.s(14), "bold"), 
                 fg=ACCENT_COLOR, bg=card_bg).grid(row=6, column=0, sticky="w", pady=(20, 5))
        tk.Frame(inner_frame, height=2, bg=ACCENT_COLOR).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Sound Toggle
        tk.Label(inner_frame, text="Ses Efektleri:", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=8, column=0, sticky="w", pady=10)
                 
        sound_var = tk.BooleanVar(value=config.get("sounds", "enabled", default=True))
        
        sound_btn_frame = tk.Frame(inner_frame, bg=card_bg, cursor="hand2")
        sound_btn_frame.grid(row=8, column=1, sticky="e", pady=10) # Right Aligned
        
        s_text = tk.Label(sound_btn_frame, text="AÇIK", font=(self.font_main, self.s(12), "bold"), bg=card_bg, fg="#22c55e")
        s_text.pack(side="left", padx=5)
        s_icon = tk.Label(sound_btn_frame, text="🔊", font=(self.font_main, self.s(20)), bg=card_bg, fg=TEXT_COLOR)
        s_icon.pack(side="left") # Icon on right side for "Control" look? Or keep icon left? Keeping icon right fits 'Right Align' vibe.
        
        # Original: Icon Left, Text Right. 
        # New Right Aligned: Maybe Text Left, Icon Right? 
        # Let's keep Icon Left for familiarity but align the whole block Right.
        
        def toggle_s():
            sound_var.set(not sound_var.get())
            if sound_var.get():
                s_icon.config(text="🔊", fg=TEXT_COLOR)
                s_text.config(text="AÇIK", fg="#22c55e")
            else:
                s_icon.config(text="🔇", fg=SUB_TEXT_COLOR)
                s_text.config(text="KAPALI", fg="#ef4444")
        
        sound_btn_frame.bind("<Button-1>", lambda e: toggle_s())
        s_icon.bind("<Button-1>", lambda e: toggle_s())
        s_text.bind("<Button-1>", lambda e: toggle_s())
        
        # Init state
        if not sound_var.get():
            s_icon.config(text="🔇", fg=SUB_TEXT_COLOR)
            s_text.config(text="KAPALI", fg="#ef4444")

        # Timer
        tk.Label(inner_frame, text="Süre (Saniye):", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=9, column=0, sticky="w", pady=10)
        
        timer_var = tk.IntVar(value=config.get("game_settings", "timer_duration", default=60))
        # Updated width to 18 to match other dropdowns
        timer_combo = ttk.Combobox(inner_frame, values=[30, 45, 60], state="readonly", font=(self.font_main, self.s(12)), width=18)
        timer_combo.set(timer_var.get())
        timer_combo.grid(row=9, column=1, sticky="e", pady=10) # Right Aligned

        # --- Section 3: SİSTEM ---
        tk.Label(inner_frame, text="SİSTEM", font=(self.font_main, self.s(14), "bold"), 
                 fg=ACCENT_COLOR, bg=card_bg).grid(row=10, column=0, sticky="w", pady=(20, 5))
        tk.Frame(inner_frame, height=2, bg=ACCENT_COLOR).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Update Check
        tk.Label(inner_frame, text="Versiyon:", font=(self.font_main, self.s(16)), 
                 fg=SUB_TEXT_COLOR, bg=card_bg).grid(row=12, column=0, sticky="w", pady=10)
        
        tk.Label(inner_frame, text=config.get("version", default="1.4"), font=(self.font_main, self.s(16), "bold"), 
                 fg=TEXT_COLOR, bg=card_bg).grid(row=12, column=1, sticky="e", pady=10)
        
        # GitHub Link Row (User Request: Text + Button)
        # GitHub Link Row (User Request: Split Alignment)
        # Left Text
        tk.Label(inner_frame, text="Güncelleştirmeyi elle kontrol etmek için", 
                 font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=card_bg)\
                 .grid(row=13, column=0, sticky="w", pady=(10, 30))
                 
        # Right Button
        self.create_rounded_button(inner_frame, "TIKLAYINIZ", lambda: webbrowser.open("https://github.com/Okan707/Kelime_Avcisi"),
                                 width=120, height=35, bg=ACCENT_COLOR, fg=BG_COLOR, radius=10, font_size=10)\
                                 .grid(row=13, column=1, sticky="e", pady=(10, 30))

        
        # --- FOOTER ACTIONS ---
        def save():
            # Logic similar to before
            new_s = scale_var.get()
            sel_res_name = res_dropdown.get()
            res_val = res_options.get(sel_res_name, "fullscreen")
            full = (res_val == "fullscreen")
            
            config.config["display_settings"]["custom_scale"] = new_s
            config.config["display_settings"]["resolution"] = res_val
            config.config["display_settings"]["fullscreen"] = full
            config.config["display_settings"]["theme"] = theme_options.get(theme_dropdown.get(), "dark")
            config.config["sounds"]["enabled"] = sound_var.get()
            try:
                config.config["game_settings"]["timer_duration"] = int(timer_combo.get())
            except: pass
            
            # Save
            appdata_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'KelimeOyunu')
            if not os.path.exists(appdata_dir): os.makedirs(appdata_dir)
            with open(os.path.join(appdata_dir, "config.json"), 'w', encoding='utf-8') as f:
                json.dump(config.config, f, ensure_ascii=False, indent=2)
                
            if messagebox.askyesno("Yeniden Başlat", "Değişikliklerin geçerli olması için yeniden başlatılsın mı?"):
                self.root.destroy()
                import sys
                if getattr(sys, 'frozen', False):
                    application_path = os.path.dirname(sys.executable)
                    exe_path = sys.executable
                else:
                    application_path = os.getcwd()
                    exe_path = sys.executable

                # FIX: restart using subprocess with sanitized environment
                # This prevents the new process from inheriting the dying _MEI folder path
                
                try:
                    # Create a copy of the environment
                    new_env = os.environ.copy()
                    
                    # Remove PyInstaller internal variables
                    if '_MEIPASS2' in new_env:
                        del new_env['_MEIPASS2']
                    if 'PYINSTALLER_STRICT_UNPACK_MODE' in new_env:
                        del new_env['PYINSTALLER_STRICT_UNPACK_MODE']
                        
                    # Launch the new process
                    print(f"Restarting... Executable: {exe_path}, CWD: {application_path}")
                    subprocess.Popen([exe_path], cwd=application_path, env=new_env)
                    
                except Exception as e:
                    print(f"Direct restart failed: {e}")
                    messagebox.showerror("Hata", f"Yeniden başlatma başarısız oldu:\n{e}\nLütfen uygulamayı manuel olarak kapatıp açın.")
                
                # Force exit immediately
                self.root.quit()
                os._exit(0)

                # Force exit immediately
                os._exit(0)

        action_frame = tk.Frame(inner_frame, bg=card_bg)
        # Moved to row=14 to avoid collision with GitHub link at row=13
        # Increased pady to (60, 20) to push it down further as requested
        action_frame.grid(row=14, column=0, columnspan=2, pady=(60, 20))
        
        self.create_rounded_button(action_frame, "KAYDET VE BAŞLAT", save, width=220, height=50, bg="#22c55e", fg="white", font_size=12).pack(side="left", padx=10)
        self.create_rounded_button(action_frame, "İPTAL", self.show_entry_screen, width=120, height=50, bg="#64748b", fg="white", font_size=12).pack(side="left", padx=10)
        
        # Ensure scrollregion is updated
        self.root.after(100, scroll.update_scroll)

    def get_short_path_name(self, long_name):
        """Gets the short path name of a file system path for MCI compatibility."""
        if os.name != 'nt': return long_name
        try:
            output_buf_size = 0
            while True:
                output_buf = ctypes.create_unicode_buffer(output_buf_size)
                needed = ctypes.windll.kernel32.GetShortPathNameW(long_name, output_buf, output_buf_size)
                if output_buf_size >= needed:
                    return output_buf.value
                output_buf_size = needed
        except:
            return long_name

    def load_sounds(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Get sound files from config
            sound_files = {
                "correct": config.get("sounds", "correct", default="button-pressed-38129.mp3"),
                "wrong": config.get("sounds", "wrong", default="click-buttons-ui-menu-sounds-effects-button-7-203601.mp3"),
                "next": config.get("sounds", "next", default="mech-keyboard-02-102918.mp3")
            }
            for key, filename in sound_files.items():
                path = resource_path(filename)
                if os.path.exists(path):
                    # print(f"DEBUG: Found sound file: {path}")
                    if self.sound_enabled:
                        self.sounds[key] = pygame.mixer.Sound(path)
                    
                    if os.name == 'nt':
                        try:
                            # Use short paths for MCI to avoid issues with spaces or unicode
                            short_path = self.get_short_path_name(path)
                            alias = f"game_{key}"
                            ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0) # Close if already open
                            cmd = f'open "{short_path}" alias {alias}' # Use quotes for path
                            ctypes.windll.winmm.mciSendStringW(cmd, None, 0, 0)
                        except Exception as mci_e:
                            self.log_debug(f"MCI open error for {key}: {mci_e}")
                            # If MCI fails, ensure pygame is still the primary method if enabled
                            if self.sound_enabled and key not in self.sounds:
                                self.sounds[key] = pygame.mixer.Sound(path)
        except Exception as e:
            self.log_debug(f"Error pre-loading sounds: {e}")
            self.sound_enabled = False

    def log_debug(self, msg):
        # Disabled for performance. Re-enable only for troubleshooting.
        pass
    
    def check_updates(self):
        """Handler for manual update check button"""
        # Show loading screen
        self.clear_container()
        tk.Label(self.container, text="GÜNCELLEŞTİRMELER KONTROL EDİLİYOR...", font=(self.font_main, self.s(36), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.5, anchor="center")
        
        def on_update_result(result):
            # This callback runs in background thread, so use after to safely update UI
            self.root.after(0, lambda: self.show_update_screen(result))
        
        # Start the check
        config.check_for_updates_manual(callback=on_update_result)
    
    def start_full_update(self):
        """Starts the full download and apply process"""
        # Show a "Downloading..." overlay or message
        self.clear_container()
        tk.Label(self.container, text="GÜNCELLEŞTİRME İNDİRİLİYOR...", font=(self.font_main, self.s(36), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(self.container, text="Lütfen bekleyin, işlem tamamlandığında uygulama yeniden başlatılacak.", 
                 font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.5, anchor="center")
        
        def on_complete(success, message):
            if not success:
                self.root.after(0, lambda: messagebox.showerror("Hata", message))
                self.root.after(0, self.show_entry_screen)
        
        config.trigger_full_update(callback=on_complete)

    def show_update_screen(self, result):
        """Show update check result in a full screen page"""
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        
        success = result.get("success", False)
        update_available = result.get("update_available", False)
        message = result.get("message", "")
        current_ver = result.get("current_version", "?.?.?")
        new_ver = result.get("new_version", "?.?.?")

        # Title
        title_text = "GÜNCELLEŞTİRME MEVCUT" if update_available else ("SONUÇ" if success else "HATA")
        if not update_available and success:
             title_text = "UYGULAMANIZ GÜNCEL"
             
        title_color = ACCENT_COLOR if success else "#ef4444"
        
        tk.Label(frame, text=title_text, font=(self.font_main, self.s(48), "bold"), 
                 fg=title_color, bg=BG_COLOR).pack(pady=(0, self.s(30)))
        
        if update_available:
            # Version Comparison
            ver_frame = tk.Frame(frame, bg=BG_COLOR)
            ver_frame.pack(pady=self.s(20))
            
            tk.Label(ver_frame, text=f"ŞU ANKİ VERSİYON: {current_ver}", font=(self.font_main, self.s(24)), 
                     fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(pady=5)
            
            tk.Label(ver_frame, text="⬇", font=(self.font_main, self.s(24)), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=5)
            
            tk.Label(ver_frame, text=f"YENİ VERSİYON: {new_ver}", font=(self.font_main, self.s(24), "bold"), 
                     fg="#22c55e", bg=BG_COLOR).pack(pady=5)
                     
            tk.Label(frame, text="Güncelleştirmeyi şimdi indirip uygulamak istiyor musunuz?", 
                     font=(self.font_main, self.s(18)), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=self.s(30))
            
            # Action Buttons
            btn_frame = tk.Frame(frame, bg=BG_COLOR)
            btn_frame.pack(pady=self.s(20))
            
            self.create_rounded_button(btn_frame, "GÜNCELLE", self.start_full_update, 
                                     width=250, height=60, bg=ACCENT_COLOR, fg=BG_COLOR).pack(side="left", padx=10)
                                     
            self.create_rounded_button(btn_frame, "DAHA SONRA", self.show_entry_screen, 
                                     width=250, height=60, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack(side="left", padx=10)
                                     
        else:
            # Info Message
            msg_color = TEXT_COLOR if success else "#ef4444"
            icon = "✅" if success else "❌"
            
            tk.Label(frame, text=f"{icon}\n{message}", font=(self.font_main, self.s(24)), 
                     fg=msg_color, bg=BG_COLOR, justify="center").pack(pady=self.s(40))
            
            # Back Button
            self.create_rounded_button(frame, "GERİ DÖN", self.show_entry_screen, 
                                     width=250, height=60, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack(pady=self.s(40))


    def handle_start(self):
        self.log_debug("--- handle_start started ---")
        if self.transitioning:
            self.log_debug("handle_start: Already transitioning, aborting.")
            return
        
        try:
            if not hasattr(self, 'name_entry') or not self.name_entry.winfo_exists():
                self.log_debug("handle_start: name_entry missing or destroyed.")
                return
                
            name = self.name_entry.get().strip()
            placeholder = "ADINIZ - SOYADINIZ"
            if not name or name == placeholder:
                self.log_debug("handle_start: Invalid name.")
                messagebox.showwarning("Uyarı", "Lütfen adınızı giriniz.")
                return
            
            self.log_debug(f"handle_start: Starting game for {name}")
            self._reset_game_state() # Fresh start for every player
            self.transitioning = True
            self.username = self.tr_upper(name)  # Force uppercase
            self.game_start_time = time.time()
            self.show_game_screen()
            self.transitioning = False
            self.log_debug("handle_start: Completed successfully.")
        except Exception as e:
            self.transitioning = False
            error_msg = traceback.format_exc()
            self.log_debug(f"handle_start ERROR: {error_msg}")
            messagebox.showerror("Hata", f"Ciddi bir hata oluştu:\n{error_msg}")

    def show_game_screen(self):
        self.current_screen = "game"
        self.log_debug("show_game_screen: Starting...")
        self.clear_container()
        
        # Stats Bar - Now full width and turquoise with even distribution
        stats_frame = tk.Frame(self.container, bg=ACCENT_COLOR, pady=self.s(15))

        stats_frame.pack(side="top", fill="x")
        
        # Configure grid for 4 even columns
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1, uniform="stats")

        # 1. Username (Grid Col 0)
        user_container = tk.Frame(stats_frame, bg=ACCENT_COLOR)
        user_container.grid(row=0, column=0, sticky="nsew")
        tk.Label(user_container, text=self.tr_upper(self.username), font=(self.font_main, self.s(15), "bold"), fg="white", bg=ACCENT_COLOR).pack()

        # 2. Timer (Grid Col 1)
        timer_container = tk.Frame(stats_frame, bg=ACCENT_COLOR)
        timer_container.grid(row=0, column=1, sticky="nsew")
        self.timer_label = tk.Label(timer_container, text="01:00", font=(self.font_main, self.s(15), "bold"), fg="white", bg=ACCENT_COLOR)
        self.timer_label.pack(expand=True)

        # 3. Potential Score (Grid Col 2)
        pot_container = tk.Frame(stats_frame, bg=ACCENT_COLOR)
        pot_container.grid(row=0, column=2, sticky="nsew")
        self.pot_score_label = tk.Label(pot_container, text="", font=(self.font_main, self.s(16), "bold"), fg="white", bg=ACCENT_COLOR)
        self.pot_score_label.pack(expand=True)

        # 4. Total Score (Grid Col 3)
        score_container = tk.Frame(stats_frame, bg=ACCENT_COLOR)
        score_container.grid(row=0, column=3, sticky="nsew")
        tk.Label(score_container, text="PUAN: ", font=(self.font_main, self.s(15), "bold"), fg="black", bg=ACCENT_COLOR).pack(side="left", expand=True, anchor="e")
        self.total_score_label = tk.Label(score_container, text=str(self.total_score), font=(self.font_main, self.s(15), "bold"), fg="white", bg=ACCENT_COLOR)

        self.total_score_label.pack(side="left", expand=True, anchor="w")

        self.game_frame = tk.Frame(self.container, bg=BG_COLOR)
        self.game_frame.pack(expand=True, fill="both")
        
        # Content frame centered inside the remaining game_frame space
        self.content_center = tk.Frame(self.game_frame, bg=BG_COLOR)
        self.content_center.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)
        
        # Definition Card - Adaptive Height to prevent cut-off
        CARD_BG = config.get("colors", "definition_card_bg", default="#e619e5")
        # Removed fixed height and pack_propagate(False) to allow growth
        self.card = tk.Frame(self.container, bg=CARD_BG)
        self.card.pack(after=stats_frame, fill="x")
        
        # Check if we should use a smaller wrap length for interactive boards
        dynamic_wrap = int(self.root.winfo_screenwidth() * 0.9)
        
        self.def_label = tk.Label(self.card, text="", wraplength=dynamic_wrap, font=(self.font_main, self.s(20)), 
                                  fg=TEXT_COLOR, bg=CARD_BG, justify="center")

        # Use pack with padding instead of place to allow card to grow with content
        self.def_label.pack(pady=self.s(30), padx=self.s(20), expand=True)
        
        # Placeholder
        self.placeholder_label = tk.Label(self.content_center, text="", font=(self.font_main, self.s(88), "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        self.placeholder_label.pack(pady=self.s(20))
        
        # Answer Entry - Stretched full width
        self.ans_entry = tk.Entry(self.content_center, font=(self.font_main, self.s(20)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", justify="center")
        self.ans_entry.pack(pady=self.s(10), ipady=self.s(12), fill="x")

        self.ans_entry.bind("<Return>", self.handle_enter_key)
        self.ans_entry.focus_set()

        # Global Return binding for cases where focus is not in entry but next/finish is enabled
        self.root.bind("<Return>", self.handle_enter_key)
        self.root.bind("<space>", self.handle_space_key)

        # Button Frame (Horizontal)
        btn_frame = tk.Frame(self.content_center, bg=BG_COLOR)
        btn_frame.pack(pady=30)
        
        # Hint Button (Red)
        hint_text = config.get("ui_text", "hint_button", default="HARF İSTE")
        red_color = config.get("colors", "red_button", default="#ef4444")
        self.hint_btn = self.create_rounded_button(btn_frame, hint_text, self.get_hint, width=160, height=50, bg=red_color, fg=TEXT_COLOR)
        self.hint_btn.pack(side="left", padx=10)
        
        # Submit Button (Green)
        submit_text = config.get("ui_text", "submit_button", default="CEVAPLA")
        green_color = config.get("colors", "green_button", default="#22c55e")
        self.submit_btn = self.create_rounded_button(btn_frame, submit_text, self.check_answer, width=160, height=50, bg=green_color, fg=BG_COLOR)
        self.submit_btn.pack(side="left", padx=10)

        # Navigation Frame (Bottom)
        nav_frame = tk.Frame(self.content_center, bg=BG_COLOR)
        nav_frame.pack(pady=(20, 0), fill="x")
        
        # Back Button (Left Arrow) - Aligned Left
        # Using a simple < arrow, theme compatible
        # Made square (50x50) as requested, with sharp corners (radius=0)
        self.back_btn = self.create_rounded_button(nav_frame, "❮", self.handle_back, width=50, height=50, bg=INPUT_BG, fg=SUB_TEXT_COLOR, radius=0)
        self.back_btn.place(relx=0, rely=0.5, anchor="w")
        
        # Next Question Button (Sıradaki Kelime) - Centered
        next_text = config.get("ui_text", "next_button", default="SIRADAKİ KELİME")
        self.next_btn = self.create_rounded_button(nav_frame, next_text, self.next_question, width=220, height=50, bg=INPUT_BG, fg=SUB_TEXT_COLOR)
        self.next_btn.set_state("disabled")
        self.next_btn.pack(side="top") # inner pack centers it by default since frame fills x but pack defaults side top
        
        self.next_question()

    def handle_back(self):
        self._reset_game_state()
        self.show_entry_screen()

    def get_hint(self):
        # Sound is already played by the button click
        word = self.current_word_data['kelime']
        hidden_indices = [i for i in range(len(word)) if i not in self.revealed_indices]
        
        if hidden_indices and self.potential_score > 0:
            idx = random.choice(hidden_indices)
            self.revealed_indices.append(idx)
            
            # KURAL: Her harf istemi -25 puan (Taban)
            self.potential_score = max(0, self.potential_score - 25)
                
            # KURAL: Tüm harfler açıldığında puan 0 olur.
            if not [i for i in range(len(word)) if i not in self.revealed_indices]:
                self.potential_score = 0
                
            self.update_ui()
            
            # Check if all letters revealed (0 points left)
            if not [i for i in range(len(word)) if i not in self.revealed_indices]:
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
                self.hint_btn.set_state("disabled")
                self.submit_btn.set_state("disabled")
                
                # Dynamic Button Text
                if self.level_idx >= len(self.levels):
                    self.next_btn.set_text("OYUNU BİTİR")
                    new_bg = "#ef4444"
                else:
                    self.next_btn.set_text("SIRADAKİ KELİME")
                    new_bg = ACCENT_COLOR
                    
                self.next_btn.set_state("normal", new_bg, BG_COLOR) # Highlight next button

    def update_ui(self):
        if not hasattr(self, 'placeholder_label'):
            return
        word = self.current_word_data['kelime']
        display = ""
        for i, char in enumerate(word):
            if i in self.revealed_indices:
                display += char + " "
            else:
                display += "_ "
        self.placeholder_label.config(text=display.strip())
        self.pot_score_label.config(text=str(self.potential_score))
        self.total_score_label.config(text=str(self.total_score))

    def next_question(self):
        self.log_debug("next_question: Starting...")
        # Sound omitted here as it's typically triggered by a button click
        if self.level_idx >= len(self.levels):
            self.log_debug("next_question: Game finished, showing summary.")
            self.show_summary_screen()
            return

        current_level = self.levels[self.level_idx]
        cat_key = f"{current_level}_harf"
        self.log_debug(f"next_question: Loading level {current_level}")
        
        if self.dictionary is None or not self.dictionary:
            messagebox.showerror("Hata", "Sözlük verisi yüklenemedi!")
            return

        available_words = [w for w in self.dictionary.get(cat_key, []) if w.get('kelime') not in self.used_words]
        self.log_debug(f"next_question: Found {len(available_words)} available words")
        
        if not available_words:
            # Fallback if a category is somehow empty
            self.level_idx += 1
            self.next_question()
            return

        self.current_word_data = random.choice(available_words)
        self.used_words.add(self.current_word_data['kelime'])
        
        # Yeni Puanlama Sistemi:
        # 4 harfli: 100, 5 harfli: 125, 6 harfli: 150... 10 harfli: 250
        # 30s -> 2.5x, 45s -> 1.5x, 60s -> 1.0x
        duration = config.get("game_settings", "timer_duration", default=60)
        multiplier = 1.0
        if duration == 30:
            multiplier = 2.5
        elif duration == 45:
            multiplier = 1.5
            
        word_len = len(self.current_word_data['kelime'])
        self.potential_score = word_len * 25
        
        self.revealed_indices = []
        self.hint_btn.set_state("normal")
        self.submit_btn.set_state("normal")
        
        # Dynamic Button Text (Immediate update for this level)
        # If this is the last level (index len - 1), show "OYUNU BİTİR"
        if self.level_idx == len(self.levels) - 1:
            self.next_btn.set_text("OYUNU BİTİR")
        else:
            self.next_btn.set_text("SIRADAKİ KELİME")
            
        self.next_btn.set_state("disabled")
        
        # Start Countdown
        # Start Countdown
        duration = config.get("game_settings", "timer_duration", default=60)
        self.start_timer(duration)
        
        self.def_label.config(text=self.current_word_data['tanim'])
        self.ans_entry.delete(0, tk.END)
        self.ans_entry.config(bg=INPUT_BG)
        self.update_ui()
        
        # Prepare index for next question
        self.level_idx += 1

    def handle_enter_key(self, event=None):
        """Unified 'Enter' key handler for Start, Submit and Next Word actions."""
        # Safety check: ensure game UI is active
        # Handle Entry Screen Start
        if hasattr(self, 'start_btn') and self.start_btn.winfo_exists():
            if self.start_btn.is_enabled:
                self.handle_start()
                return "break"

        if not hasattr(self, 'submit_btn') or not hasattr(self, 'next_btn'):
            return
            
        # 1. If Submit button is enabled, check answer
        if self.submit_btn.is_enabled:
            self.check_answer()
            return "break" # Stop event propagation
            
        # 2. Else if Next/Finish button is enabled, go to next question
        elif self.next_btn.is_enabled:
            self.next_question()
            return "break"

    def handle_space_key(self, event=None):
        """Handler for Space key to trigger Hint."""
        # Only work in game screen when hint button exists
        if hasattr(self, 'hint_btn') and self.hint_btn.winfo_exists():
            # Check if button is enabled (it might be disabled if time is up or already answered)
            if self.hint_btn.is_enabled:
                self.get_hint()
                return "break"

    def tr_upper(self, text):
        # Turkish-aware uppercase conversion
        text = text.replace('i', 'İ').replace('ı', 'I')
        return text.upper()

    def get_user_data_dir(self):
        """Returns the directory for user data (highscores)."""
        # Save to %LOCALAPPDATA%/KelimeOyunu to ensure write permissions
        app_data = os.getenv('LOCALAPPDATA')
        if not app_data:
            app_data = os.path.expanduser("~") # Fallback to user home
            
        data_dir = os.path.join(app_data, "KelimeOyunu")
        
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
            except Exception as e:
                self.log_debug(f"Error creating data dir: {e}")
                # Fallback to local dir if creation fails (rare)
                return os.path.dirname(os.path.abspath(__file__))
                
        return data_dir

    def load_scores(self):
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "highscores.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.log_debug(f"Error loading scores: {e}")
            # Try fallback to internal resource if external file doesn't exist yet
            try:
                path = resource_path("highscores.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
            except:
                pass
        return []

    def save_score(self, score_data):
        # 1. Save locally (always)
        scores = self.load_scores()
        
        # Duplicate Prevention Check
        # Check if a score with same name, score and very close timestamp exists
        is_duplicate = False
        current_ts = score_data['timestamp']
        for s in scores:
            if (s.get('name') == score_data['name'] and 
                s.get('score') == score_data['score'] and 
                abs(s.get('timestamp', 0) - current_ts) < 5.0): # 5 second buffer for duplicates
                is_duplicate = True
                break
        
        if is_duplicate:
            self.log_debug("Ignoring duplicate score submission.")
            return

        scores.append(score_data)
        scores.sort(key=lambda x: (-x['score'], x['timestamp']))
        
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "highscores.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
            self.cleanup_scores()
        except Exception as e:
            self.log_debug(f"Error saving score locally: {e}")
            
        # 2. Push to server (if logged in)
        if self.current_user:
            # Get School Info (Safe access)
            p_data = self.get_profile_data(self.current_user['username'])
            school_info = p_data.get("school", "-")
            if not school_info: school_info = "-"
            
            fullname = p_data.get("fullname", "-")
            class_level = p_data.get("class_level", "-")
            gender = p_data.get("gender", "-")
            avatar_id = p_data.get("avatar_id", "1")

            threading.Thread(target=lambda: self.network.submit_score(
                self.current_user['id'], 
                self.current_user['username'], 
                score_data['score'], 
                score_data['time'], 
                score_data['timestamp'],
                school_info,
                fullname,
                class_level,
                gender,
                avatar_id
            ), daemon=True).start()




    def load_session(self):
        """Load session data from local JSON"""
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "session.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def save_session(self, data):
        """Save session data to local JSON"""
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "session.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_debug(f"Error saving session: {e}")

    def clear_session(self):
        """Delete session file"""
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "session.json")
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            self.log_debug(f"Error clearing session: {e}")

    def cleanup_scores(self):
        """Removes scores that don't fall into the top ranks of any category."""
        scores = self.load_scores()
        if not scores: return

        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        
        # Start of week (Monday)
        start_of_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        
        # Start of month
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()

        # 1. Identify which scores to keep for each category
        def get_top(data, start_ts, limit):
            filtered = [s for s in data if s.get('timestamp', 0) >= start_ts]
            filtered.sort(key=lambda x: x['score'], reverse=True)
            return filtered[:limit]

        keep_daily = get_top(scores, start_of_day, 20)
        keep_weekly = get_top(scores, start_of_week, 15)
        keep_monthly = get_top(scores, start_of_month, 15)
        
        # All time
        all_time_sorted = sorted(scores, key=lambda x: x['score'], reverse=True)
        keep_all_time = all_time_sorted[:15]

        # 2. Use a characteristic tuple as a key to identify unique entries
        def get_key(s): return (s.get('timestamp'), s.get('name'), s.get('score'))
        
        keep_keys = set()
        for s in keep_daily + keep_weekly + keep_monthly + keep_all_time:
            keep_keys.add(get_key(s))

        # 3. Filter the original list
        new_scores = [s for s in scores if get_key(s) in keep_keys]
        
        # Sort by score desc, then timestamp
        new_scores.sort(key=lambda x: (-x['score'], x['timestamp']))

        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "highscores.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(new_scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_debug(f"Error during score cleanup: {e}")

    def get_profile_data(self, username):
        """Load extended profile data from local JSON"""
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "profiles.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    profiles = json.load(f)
                    return profiles.get(username, {})
        except Exception:
            pass
        return {}

    def save_profile_data(self, username, data, push_to_cloud=True):
        """Save extended profile data to local JSON"""
        try:
            base_dir = self.get_user_data_dir()
            path = os.path.join(base_dir, "profiles.json")
            profiles = {}
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    profiles = json.load(f)
            
            profiles[username] = data
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
                
            # CLOUD SYNC
            if push_to_cloud and self.current_user:
                threading.Thread(target=lambda: self.network.update_user_profile(username, data), daemon=True).start()
                
            return True
        except Exception as e:
            self.log_debug(f"Error saving profile: {e}")
            return False

    def play_game_sound(self, sound_type="correct"):
        """Plays game sounds using the fastest available method (non-blocking)."""
        def _play():
            try:
                # Check Global Sound Config
                if not config.get("sounds", "enabled", default=True):
                    return

                # Get volume from config
                volume_key = f"volume_{sound_type}"
                volume = config.get("sounds", volume_key, default=1.0)

                # 1. Try Pygame (already non-blocking)
                if self.sound_enabled and sound_type in self.sounds:
                    try:
                        sound_obj = self.sounds[sound_type]
                        sound_obj.set_volume(volume)
                        sound_obj.play()
                        return
                    except:
                        pass

                # 2. Fallback to MCI (Windows)
                if os.name == 'nt':
                    try:
                        # Use the pre-opened alias if available, or open and play
                        alias = f"game_{sound_type}"
                        mci = ctypes.windll.winmm.mciSendStringW
                        
                        # Set volume
                        mci_vol = int(volume * 1000)
                        mci(f"setaudio {alias} volume to {mci_vol}", None, 0, 0)
                        
                        # Play from beginning. If it fails, maybe it wasn't opened?
                        res = mci(f"play {alias} from 0", None, 0, 0)
                        
                        if res != 0:
                            filename = {
                                "correct": "button-pressed-38129.mp3",
                                "wrong": "click-buttons-ui-menu-sounds-effects-button-7-203601.mp3",
                                "next": "mech-keyboard-02-102918.mp3"
                            }.get(sound_type, "mech-keyboard-02-102918.mp3")
                            path = resource_path(filename)
                            short_path = self.get_short_path_name(path)
                            
                            # Use a temporary alias for this fallback
                            temp_alias = f"tmp_{sound_type}_{int(time.time()*100)}"
                            mci(f'open "{short_path}" alias {temp_alias}', None, 0, 0)
                            mci(f"setaudio {temp_alias} volume to {mci_vol}", None, 0, 0)
                            mci(f"play {temp_alias} wait", None, 0, 0)
                            mci(f"close {temp_alias}", None, 0, 0)
                    except:
                        pass
            except:
                pass

        threading.Thread(target=_play, daemon=True).start()


    def start_timer(self, seconds):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = seconds
        self.update_timer()

    def update_timer(self):
        mins, secs = divmod(self.time_left, 60)
        timer_text = f"{mins:02d}:{secs:02d}"
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            self.timer_label.config(text=timer_text)
            
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.handle_timeout()

    def handle_timeout(self):
        self.log_debug("handle_timeout: Time is up!")
        self.play_game_sound("wrong")
        self.potential_score = 0
        word = self.current_word_data['kelime']
        self.revealed_indices = list(range(len(word)))
        self.update_ui()
        
        self.ans_entry.delete(0, tk.END)
        self.ans_entry.insert(0, word)
        self.ans_entry.config(bg="#ef4444")
        
        self.submit_btn.set_state("disabled")
        self.hint_btn.set_state("disabled")
        
        # Dynamic Button Text
        if self.level_idx >= len(self.levels):
            self.next_btn.set_text("OYUNU BİTİR")
            new_bg = "#ef4444"
        else:
            self.next_btn.set_text("SIRADAKİ KELİME")
            new_bg = ACCENT_COLOR
            
        self.next_btn.set_state("normal", new_bg, BG_COLOR)
        
        messagebox.showwarning("Süre Doldu", f"Süreniz bitti! Doğru cevap: {word}")

    def check_answer(self):
        user_ans = self.tr_upper(self.ans_entry.get().strip())
        correct_ans = self.tr_upper(self.current_word_data['kelime'])
        
        if user_ans == correct_ans:
            if not self.next_btn.is_enabled: # Only score once
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
                self.play_game_sound()
                
                # Süre Çarpanını Uygula
                duration = config.get("game_settings", "timer_duration", default=60)
                multiplier = 1.0
                if duration == 30: multiplier = 2.5
                elif duration == 45: multiplier = 1.5
                
                earned_points = round(self.potential_score * multiplier)
                self.total_score += earned_points
            
                # Reveal all letters when correct
                word = self.current_word_data['kelime']
                self.revealed_indices = list(range(len(word)))
                
                self.update_ui()
            
            self.ans_entry.config(bg="#22c55e") # Emerald Green for correct
            self.submit_btn.set_state("disabled")
            self.hint_btn.set_state("disabled")
            
            # Dynamic Button Text
            if self.level_idx >= len(self.levels):
                self.next_btn.set_text("OYUNU BİTİR")
                new_bg = "#ef4444"
            else:
                self.next_btn.set_text("SIRADAKİ KELİME")
                new_bg = ACCENT_COLOR
                
            self.next_btn.set_state("normal", new_bg, BG_COLOR) # Enable manual next
        else:
            self.play_game_sound("wrong")
            self.ans_entry.config(bg="#ef4444") # Red for wrong
        def reset_entry_color():
            if hasattr(self, 'ans_entry') and self.ans_entry.winfo_exists():
                self.ans_entry.config(bg=INPUT_BG)
        
        self.root.after(400, reset_entry_color)

    def show_summary_screen(self):
        self.current_screen = "summary"
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.clear_container()  # Restored clearing of previous widgets
        
        frame = tk.Frame(self.container, bg=BG_COLOR)
        # Lowered frame position to 0.60 since title is removed from it
        frame.place(relx=0.5, rely=0.60, anchor="center", relwidth=1.0)
        
        # Calculate duration
        duration_str = "00:00"
        timestamp = time.time()
        if self.game_start_time:
            duration = int(timestamp - self.game_start_time)
            mins, secs = divmod(duration, 60)
            duration_str = f"{mins:02d}:{secs:02d}"
            
        # Save Score
        # Save Score (One-time check)
        if not getattr(self, 'score_saved', False):
            self.save_score({
                'name': self.username,
                'score': self.total_score,
                'timestamp': timestamp,
                'time': duration_str
            })
            self.score_saved = True
            
        # Independent Title Positioning (Directly on container)
        # Placed at rely=0.20 to be "higher" as requested
        tk.Label(self.container, text="OYUN BİTTİ", font=(self.font_main, self.s(144), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.20, anchor="center")
                 
        # Show New Rank/Stats
        stats = self.get_user_stats(self.username)
        tk.Label(self.container, text=f"🎖 {stats['rank']}", font=(self.font_main, self.s(24)), 
                 fg="#fbbf24", bg=BG_COLOR).place(relx=0.5, rely=0.32, anchor="center")
        
        # Name Display with Thick Pink Strip (Matching Definition Card)
        CARD_BG = DEFINITION_CARD_BG
        name_container = tk.Frame(frame, bg=CARD_BG, height=self.s(90)) # Thinner strip
        name_container.pack_propagate(False) # Force size
        name_container.pack(pady=(self.s(50), 0), fill="x") # Increased top padding to move strips down
        
        tk.Label(name_container, text=self.tr_upper(self.username), font=(self.font_main, self.s(36), "bold"), 
                 fg=TEXT_COLOR, bg=CARD_BG).place(relx=0.5, rely=0.5, anchor="center")
        
        # Score Display with Thick Turquoise Strip (Matching Name Strip)
        score_container = tk.Frame(frame, bg=ACCENT_COLOR, height=self.s(90)) # Thinner strip
        score_container.pack_propagate(False) # Force size
        score_container.pack(pady=(0, 0), fill="x") # No padding between strips
        
        # Removed "PUAN:" prefix, showing only the number
        score_msg = str(self.total_score)
        tk.Label(score_container, text=score_msg, font=(self.font_main, self.s(36), "bold"), 
                 fg=TEXT_COLOR, bg=ACCENT_COLOR).place(relx=0.5, rely=0.5, anchor="center")

        # Time Display with Thick Blue Strip (Matching other strips)
        TIME_BG = "#3b82f6"
        time_container = tk.Frame(frame, bg=TIME_BG, height=self.s(90)) # Thinner strip
        time_container.pack_propagate(False)
        time_container.pack(pady=(0, 0), fill="x") # Removed padding to keep strips tight
        
        # Display just the time value (mm:ss) as requested
        tk.Label(time_container, text=duration_str, font=(self.font_main, self.s(36), "bold"), 
                 fg=TEXT_COLOR, bg=TIME_BG).place(relx=0.5, rely=0.5, anchor="center")


        # Buttons Side-by-Side
        btn_frame = tk.Frame(frame, bg=BG_COLOR)
        # Adjusted padding to compensate for strip movement (80 -> 50)
        btn_frame.pack(pady=(50, 20))
        
        btn1 = self.create_rounded_button(btn_frame, "TEKRAR OYNA", self.reset_game, width=220, height=50)
        btn1.pack(side="left", padx=10)
        
        btn2 = self.create_rounded_button(btn_frame, "PUAN TABLOSU", lambda: self.show_leaderboard("summary"), width=220, height=50, bg=DEFINITION_CARD_BG)
        btn2.pack(side="left", padx=10)


    def get_user_stats(self, username):
        """Calculate stats for the profile screen"""
        scores = self.load_scores()
        user_scores = [s for s in scores if s.get('name') == username]
        
        total_score = sum(s.get('score', 0) for s in user_scores)
        games_played = len(user_scores)
        best_score = max((s.get('score', 0) for s in user_scores), default=0)
        
        # Calculate approximate "Words Hunted" based on score
        words_hunted = int(total_score / 100) 
        
        # Success Rate (Fake for now)
        success_rate = 95 if games_played > 0 else 0
        
        # Calculate Rank
        rank = "Yeni Çaylak"
        if total_score > 1000000: rank = "Kelime Üstadı"
        elif total_score > 250000: rank = "Kelime Avcısı"
        elif total_score > 50000: rank = "Meraklı Oyuncu"

        # Admin Override
        if username.upper() == "OKAN707":
            rank = "Kelime Üstadı"

        return {
            "total_score": total_score,
            "games_played": games_played,
            "best_score": best_score,
            "words_hunted": words_hunted,
            "success_rate": success_rate,
            "rank": rank
        }

    def show_profile_screen(self):
        self.current_screen = "profile"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
        
        # --- LEFT PANEL (Identity) ---
        left_panel = tk.Frame(frame, bg=BG_COLOR)
        left_panel.place(relx=0.25, rely=0.5, anchor="center", relwidth=0.4) # Increased width share

        # 1. Avatar (Centered)
        canvas = tk.Canvas(left_panel, width=self.s(160), height=self.s(160), bg=BG_COLOR, highlightthickness=0)
        canvas.pack(pady=(0, self.s(15)))
        
        # Get Avatar Data
        p_data = self.get_profile_data(self.current_user['username'])
        avatar_id = p_data.get("avatar_id", "1")
        av_data = AVATARS.get(avatar_id, AVATARS["1"])
        
        # Draw concentric circles
        canvas.create_oval(self.s(5), self.s(5), self.s(155), self.s(155), outline=ACCENT_COLOR, width=2) # Outer ring
        canvas.create_oval(self.s(15), self.s(15), self.s(145), self.s(145), fill=av_data["color"], outline="", width=0) # Inner bg (Avatar Color)
        
        # Draw Icon instead of initial
        canvas.create_text(self.s(80), self.s(80), text=av_data["icon"], font=("Segoe UI Emoji", self.s(64)), fill=BG_COLOR)
        
        # 2. Username (Centered)
        tk.Label(left_panel, text=self.tr_upper(self.current_user['username']), font=(self.font_main, self.s(40), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(5)))
                 
        # 3. Title/Rank (Centered, with Icon)
        stats = self.get_user_stats(self.current_user['username'])
        rank = stats['rank']
            
        tk.Label(left_panel, text=f"🎖 {rank}", font=(self.font_main, self.s(18)), 
                 fg="#fbbf24", bg=BG_COLOR).pack(pady=(0, self.s(30)))

        # 4. Extended Info (Grid Layout for perfect alignment)
        p_data = self.get_profile_data(self.current_user['username'])
        
        info_container = tk.Frame(left_panel, bg=BG_COLOR)
        info_container.pack() # Pack centered
        
        # Define fields to show
        fields = [
            ("Adı Soyadı:", p_data.get("fullname", "-")),
            ("Doğum Tarihi:", p_data.get("birthdate", "-")),
            ("Cinsiyet:", p_data.get("gender", "-")),
            ("Okulu:", p_data.get("school", "-")),
            ("Sınıfı:", p_data.get("class_level", "-"))
        ]

        for i, (label, value) in enumerate(fields):
            # Value only (Left Aligned for cleanliness)
            val_label = tk.Label(info_container, text=value, font=(self.font_main, self.s(14)), 
                     fg=TEXT_COLOR, bg=BG_COLOR, anchor="w", justify="left")
            val_label.grid(row=i, column=0, padx=0, pady=4, sticky="w")
        
        # --- STATS \u0026 ACTIONS PANEL (Symmetric 2x2 Grid) ---
        side_panel = tk.Frame(frame, bg=BG_COLOR)
        side_panel.place(relx=0.65, rely=0.5, anchor="center")
        
        def create_stat_box(parent, title, value):
            box = tk.Frame(parent, bg=INPUT_BG, width=self.s(280), height=self.s(180))
            box.pack_propagate(False)
            
            # Use a centered sub-container for labels to ensure vertical symmetry
            content = tk.Frame(box, bg=INPUT_BG)
            content.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(content, text=value, font=(self.font_main, self.s(48), "bold"), fg=TEXT_COLOR, bg=INPUT_BG).pack()
            tk.Label(content, text=title, font=(self.font_main, self.s(16)), fg=SUB_TEXT_COLOR, bg=INPUT_BG).pack()
            return box

        # Grid Column Configuration for Symmetry
        side_panel.columnconfigure(0, weight=1, pad=20)
        side_panel.columnconfigure(1, weight=1, pad=20)

        # Row 0: Stats (Side-by-Side)
        create_stat_box(side_panel, "Toplam Puan", f"{stats['total_score']:,}").grid(row=0, column=0, pady=10)
        create_stat_box(side_panel, "En İyi Skor", f"{stats['best_score']:,}").grid(row=0, column=1, pady=10)

        # Row 1: Buttons (Correspondingly below stats for symmetry)
        # GERİ DÖN under Toplam Puan (0,0 -> 1,0)
        self.create_rounded_button(side_panel, "GERİ DÖN", self.show_entry_screen, 
                                 width=self.s(280), height=self.s(60), bg=BG_COLOR, fg=SUB_TEXT_COLOR).grid(row=1, column=0, pady=10)
        
        # PROFİLİ DÜZENLE under En İyi Skor (0,1 -> 1,1)
        self.create_rounded_button(side_panel, "PROFİLİ DÜZENLE", self.show_edit_profile, 
                                 width=self.s(280), height=self.s(60), bg=INPUT_BG, fg=TEXT_COLOR).grid(row=1, column=1, pady=10)

    def show_edit_profile(self):
        self.current_screen = "edit_profile"
        self.clear_container()
        frame = tk.Frame(self.container, bg=BG_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Title
        tk.Label(frame, text="PROFİLİ DÜZENLE", font=(self.font_main, self.s(32), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, 20))

        content_frame = tk.Frame(frame, bg=BG_COLOR)
        content_frame.pack(fill="both", expand=True)
        
        # Left: Personal Info
        left_col = tk.Frame(content_frame, bg=BG_COLOR)
        left_col.pack(side="left", fill="both", expand=True, padx=20)
        
        tk.Label(left_col, text="Kişisel Bilgiler", font=(self.font_main, self.s(18), "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=10, anchor="w")
        
        p_data = self.get_profile_data(self.current_user['username'])
        entries = {}
        
        # --- Avatar Selection ---
        tk.Label(left_col, text="Profil Resmi Seçin", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,5))
        
        avatar_frame = tk.Frame(left_col, bg=BG_COLOR)
        avatar_frame.pack(fill="x", pady=(0, 15))
        
        self.selected_avatar_var = tk.StringVar(value=p_data.get("avatar_id", "1"))
        
        def select_avatar(aid):
            self.selected_avatar_var.set(aid)
            # Visual update
            for child in avatar_frame.winfo_children():
                # Checking tag to identify buttons
                if hasattr(child, "avatar_id"):
                     is_sel = (child.avatar_id == aid)
                     # Add border if selected
                     child.config(highlightbackground=ACCENT_COLOR if is_sel else BG_COLOR, highlightthickness=2 if is_sel else 0)

        for aid, data in AVATARS.items():
            # Circular frame acting as cached button
            # We use a button or canvas. Let's use Label with binding for custom look
            
            # Container for highlight border
            cont = tk.Frame(avatar_frame, bg=BG_COLOR, width=50, height=50)
            cont.pack(side="left", padx=5)
            cont.avatar_id = aid
            
            # Canvas
            cv = tk.Canvas(cont, width=46, height=46, bg=BG_COLOR, highlightthickness=0, cursor="hand2")
            cv.pack(padx=2, pady=2)
            
            cv.create_oval(2, 2, 44, 44, fill=data["color"], outline="")
            cv.create_text(23, 23, text=data["icon"], font=("Segoe UI Emoji", 20))
            
            cv.bind("<Button-1>", lambda e, x=aid: select_avatar(x))
            
        # Initial visual update
        self.root.after(100, lambda: select_avatar(self.selected_avatar_var.get()))

        def add_field(parent, label, key):
            tk.Label(parent, text=label, font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,0))
            e = tk.Entry(parent, font=(self.font_main, self.s(14)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat")
            e.pack(fill="x", ipady=5, pady=(0, 10))
            e.insert(0, p_data.get(key, ""))
            entries[key] = e
            
        add_field(left_col, "Adı Soyadı", "fullname")
        add_field(left_col, "Doğum Tarihi (GG.AA.YYYY)", "birthdate")
        add_field(left_col, "Cinsiyet (E/K)", "gender")
        add_field(left_col, "Okulu", "school")
        add_field(left_col, "Sınıfı", "class_level")
        
        # Right: Password Change
        right_col = tk.Frame(content_frame, bg=BG_COLOR)
        right_col.pack(side="right", fill="both", expand=True, padx=20)
        
        tk.Label(right_col, text="Şifre Değiştir", font=(self.font_main, self.s(18), "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=10, anchor="w")
        
        tk.Label(right_col, text="Eski Şifre", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,0))
        old_pass = tk.Entry(right_col, font=(self.font_main, self.s(14)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", show="*")
        old_pass.pack(fill="x", ipady=5, pady=(0, 10))
        tk.Label(right_col, text="Yeni Şifre", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,0))
        new_pass = tk.Entry(right_col, font=(self.font_main, self.s(14)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat", show="*")
        new_pass.pack(fill="x", ipady=5, pady=(0, 20))

        # --- Security Question Management (Inline) ---
        tk.Label(right_col, text="Güvenlik Sorusu", font=(self.font_main, self.s(16), "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(10, 5), anchor="w")
        
        # Fetch latest data
        latest_user_data = self.network.get_user_by_username(self.current_user.get('username', ''))
        current_sec_q = ""
        current_sec_a = ""
        if latest_user_data:
            current_sec_q = latest_user_data.get("security_question", "")
            current_sec_a = latest_user_data.get("security_answer", "") # Also fetch answer to pre-fill

        # Security Questions List
        security_questions = [
            "İlk evcil hayvanınızın adı neydi?",
            "En sevdiğiniz yemek hangisidir?",
            "İlk okulunuzun adı neydi?",
            "En sevdiğiniz renk nedir?",
            "Doğduğunuz şehir neresidir?",
            "En sevdiğiniz çizgi film kahramanı kim?",
            "En sevdiğiniz ders hangisi?",
            "En iyi arkadaşınızın adı ne?",
            "Hangi takımı tutuyorsunuz?",
            "Büyüyünce ne olmak istersiniz?"
        ]
        
        # Dropdown for Question
        tk.Label(right_col, text="Soru Seçin", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,0))
        
        sec_q_var = tk.StringVar()
        sec_q_combo = ttk.Combobox(right_col, textvariable=sec_q_var, values=security_questions, state="readonly", font=(self.font_main, self.s(12)))
        sec_q_combo.pack(fill="x", ipady=5, pady=(0, 10))
        
        if current_sec_q and current_sec_q in security_questions:
            sec_q_combo.set(current_sec_q)
        else:
            sec_q_combo.set("Seçiniz...")

        # Entry for Answer
        tk.Label(right_col, text="Cevap", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(5,0))
        sec_a_entry = tk.Entry(right_col, font=(self.font_main, self.s(14)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat")
        sec_a_entry.pack(fill="x", ipady=5, pady=(0, 10))
        
        # Pre-fill answer if available
        if current_sec_a:
            sec_a_entry.insert(0, current_sec_a)

        # Validation/Interactivity: Enable answer only if question selected?
        # Actually, simplest is to just let them type. 
        # But user asked: "güvenlik sorusu seçilince yazılabilir alan aktifleşsin"
        
        def on_q_select(event=None): # event=None for initial call
            if sec_q_combo.get() and sec_q_combo.get() != "Seçiniz...":
                sec_a_entry.config(state="normal", bg=INPUT_BG)
            else:
                sec_a_entry.config(state="disabled", bg=BG_COLOR) # Dimmed
                
        sec_q_combo.bind("<<ComboboxSelected>>", on_q_select)
        
        # Initial State
        on_q_select() # Call once to set initial state based on pre-filled question

        # Actions
        btn_frame = tk.Frame(frame, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        def save_all():
            # 1. Save Profile Data Locally
            data_to_save = {k: v.get().strip() for k, v in entries.items()}
            data_to_save["avatar_id"] = self.selected_avatar_var.get()
            
            # 2. Handle Security Question Update
            q_val = sec_q_combo.get()
            a_val = sec_a_entry.get().strip()
            
            # Only update if a valid question is selected AND an answer is provided
            # OR if strictly changing question
            if q_val and q_val != "Seçiniz..." and a_val:
                data_to_save["security_question"] = q_val
                data_to_save["security_answer"] = a_val
            elif q_val == "Seçiniz..." and not a_val: # If both are empty/default, clear them
                data_to_save["security_question"] = ""
                data_to_save["security_answer"] = ""
            # If question is selected but answer is empty, don't save (or warn?)
            # For now, if q is selected but a is empty, it won't be saved.
            
            self.save_profile_data(self.current_user['username'], data_to_save)
            
            # 3. Change Password (if filled)
            op = old_pass.get().strip()
            np = new_pass.get().strip()
            
            if op and np:
                # Call server endpoint
                url = f"{self.network.api_url}/auth/change-password"
                try:
                    payload = {
                        "username": self.current_user['username'], 
                        "old_password": op, 
                        "new_password": np
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                               headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req) as response:
                        res = json.load(response)
                        if not res.get("success"):
                            messagebox.showerror("Hata", f"Şifre hatası: {res.get('message')}")
                            return # Don't exit screen
                except Exception as e:
                    messagebox.showerror("Hata", f"Bağlantı hatası: {e}")
                    return

            # Success - Transition immediately
            self.show_profile_screen()

        self.create_rounded_button(btn_frame, "KAYDET", save_all, width=200, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(side="left", padx=10)
        self.create_rounded_button(btn_frame, "İPTAL", self.show_profile_screen, width=150, height=50, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack(side="left", padx=10)

    def show_leaderboard(self, source="summary"):
        self.current_screen = "leaderboard"
        self.transitioning = False 
        self.clear_container()
        
        lb_frame = tk.Frame(self.container, bg=BG_COLOR)
        lb_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)
        
        # Header
        header_strip = tk.Frame(lb_frame, bg=DEFINITION_CARD_BG, height=self.s(100))
        header_strip.pack_propagate(False)
        header_strip.pack(fill="x", pady=(0, self.s(10)))
        
        tk.Label(header_strip, text="PUAN TABLOSU", font=(self.font_main, self.s(48), "bold"), 
                 fg=TEXT_COLOR, bg=DEFINITION_CARD_BG).place(relx=0.5, rely=0.5, anchor="center")

        # --- SCOPE TABS (YEREL / GENEL) ---
        scope_frame = tk.Frame(lb_frame, bg=BG_COLOR)
        scope_frame.pack(pady=(0, 10))
        
        self.leaderboard_scope = getattr(self, 'leaderboard_scope', 'local') # Default to local, remember last choice if possible? No, reset is fine.
        # Actually let's use a default if not set
        if not hasattr(self, 'leaderboard_scope'): self.leaderboard_scope = 'local'

        self.scope_buttons = {}
        
        def set_scope(scope):
            self.leaderboard_scope = scope
            # Redraw scope buttons
            for s, btn in self.scope_buttons.items():
                is_sel = (s == scope)
                c = "#ec4899" if is_sel else INPUT_BG # Pink for selected scope
                fg = "white" if is_sel else SUB_TEXT_COLOR
                if hasattr(btn, 'set_state'): # Ensure we use the exposed method
                     # We need to access the set_state method wrapper we made? 
                     # Actually create_rounded_button returns the canvas which has the method attached
                     btn.set_state(btn.state, c, fg)
            
            # Reload data
            self.load_leaderboard_data(self.current_filter)

        for text, scope in [("YEREL", "local"), ("GENEL", "global")]:
            is_selected = (scope == self.leaderboard_scope)
            bg_c = "#ec4899" if is_selected else INPUT_BG
            fg_c = "white" if is_selected else SUB_TEXT_COLOR
            
            btn = self.create_rounded_button(scope_frame, text, lambda s=scope: set_scope(s), 
                                           width=300, height=50, bg=bg_c, fg=fg_c, radius=15)
            btn.pack(side="left", padx=10)
            self.scope_buttons[scope] = btn

        # --- FILTERS ---
        filter_frame = tk.Frame(lb_frame, bg=BG_COLOR)
        filter_frame.pack(pady=(0, 20))
        
        filters = [("GÜNLÜK", "GÜNLÜK"), ("HAFTALIK", "HAFTALIK"), ("AYLIK", "AYLIK"), ("TÜM ZAMANLAR", "TÜM ZAMANLAR")]
        self.current_filter = "GÜNLÜK" 
        
        self.filter_buttons = {}
        
        for text, key in filters:
            is_selected = (key == self.current_filter)
            btn_bg = ACCENT_COLOR if is_selected else INPUT_BG
            btn_fg = BG_COLOR if is_selected else SUB_TEXT_COLOR
            
            # Mapping key to period string for server if needed
            btn = self.create_rounded_button(filter_frame, text, lambda k=key: self.load_leaderboard_data(k), 
                                           width=180, height=45, bg=btn_bg, fg=btn_fg, radius=15)
            btn.pack(side="left", padx=10)
            self.filter_buttons[key] = btn

        # List Area
        list_container = tk.Frame(lb_frame, bg=BG_COLOR)
        list_container.pack(expand=True, fill="both", padx=100, pady=(0, 100))
        
        self.score_scroll = ScrollableFrame(list_container, bg=BG_COLOR)
        self.score_scroll.pack(expand=True, fill="both")
        self.leaderboard_content = self.score_scroll.scrollable_frame
        
        # Back Button
        back_cmd = self.show_summary_screen if source == "summary" else self.show_entry_screen
        back_container = tk.Frame(lb_frame, bg=BG_COLOR)
        back_container.place(relx=0.5, rely=0.92, anchor="center")
        self.create_rounded_button(back_container, "GERİ DÖN", back_cmd, width=200, height=50, bg="#ef4444", fg="white").pack()
        
        self.load_leaderboard_data("GÜNLÜK")

    def load_leaderboard_data(self, filter_key):
        self.current_filter = filter_key
        
        # Update Filter Buttons
        for key, btn in self.filter_buttons.items():
             is_selected = (key == self.current_filter)
             new_bg = ACCENT_COLOR if is_selected else INPUT_BG
             new_fg = BG_COLOR if is_selected else SUB_TEXT_COLOR
             if hasattr(btn, 'set_state'):
                 btn.set_state(btn.state, new_bg, new_fg)

        # Clear List
        for widget in self.leaderboard_content.winfo_children():
            widget.destroy()
            
        def render_scores(scores):
            # Normalize and render
            if not scores:
                tk.Label(self.leaderboard_content, text="Henüz kayıtlı skor yok.", 
                         font=(self.font_main, self.s(20)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(pady=self.s(50))
                return

            # Optimization: Load all profiles once
            all_profiles = {}
            try:
                base_dir = self.get_user_data_dir()
                path = os.path.join(base_dir, "profiles.json")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        all_profiles = json.load(f)
            except: pass

            for idx, item in enumerate(scores):
                # Map server fields to local fields if needed
                # Server: username, time_str. Local: name, time.
                data = item.copy()
                if 'username' in data and 'name' not in data: data['name'] = data['username']
                if 'time_str' in data and 'time' not in data: data['time'] = data['time_str']
                
                # Enrich with Class Level (Fetched from Profile)
                # Enrich with Class Level (Fetched from Profile)
                uname = data.get('name')
                if uname and uname in all_profiles:
                     p = all_profiles[uname]
                     # Only overwrite if local profile has a valid class level
                     if p.get('class_level') and p.get('class_level') != "-":
                        data['class_level'] = p['class_level']
                
                try:
                    # Only allow deleting if scope is local OR user is admin
                    is_admin = (self.current_user and self.current_user['username'].upper() == 'OKAN707')
                    allow_delete = (self.leaderboard_scope == 'local') or is_admin
                    
                    self.create_score_strip(self.leaderboard_content, idx + 1, data, allow_delete)
                except Exception as e:
                    print(f"Error rendering score: {e}")
            
            self.score_scroll.update_scroll()

        # Fetch Data
        if self.leaderboard_scope == 'local':
            scores = self.load_scores()
            # Clean
            valid_scores = [s for s in scores if isinstance(s, dict) and 'score' in s]
            # Helper function to convert time string (MM:SS) to seconds for sorting
            def time_to_seconds(time_str):
                try:
                    parts = str(time_str).split(':')
                    return int(parts[0]) * 60 + int(parts[1])
                except:
                    return 999999  # Invalid time goes to end
            
            # Sort by score (descending), then by time (ascending) for tied scores
            valid_scores.sort(key=lambda x: (-x['score'], time_to_seconds(x.get('time', '99:99'))))
            
            # Filter
            now = datetime.now()
            start_ts = 0
            if filter_key == "GÜNLÜK":
                start_ts = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            elif filter_key == "HAFTALIK":
                start_ts = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            elif filter_key == "AYLIK":
                start_ts = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp()
            
            filtered = [s for s in valid_scores if s.get('timestamp', 0) >= start_ts]
            
            # Backfill/Update data from local profiles
            # This ensures that if the user changes their avatar/name, it updates in the leaderboard view (for themselves/local users)
            for s in filtered:
                p_data = self.get_profile_data(s.get('name'))
                if p_data:
                    # Always sync Avatar to current selection
                    if 'avatar_id' in p_data:
                        s['avatar_id'] = p_data['avatar_id']
                    
                    # Backfill Fullname if missing
                    if ('fullname' not in s or s['fullname'] == "-") and p_data.get('fullname'):
                        s['fullname'] = p_data['fullname']
                        
            # Use same limits as server
            render_scores(filtered[:20])
            
        else: # GLOBAL
            # Map filter key to server period
            period_map = {
                "GÜNLÜK": "daily",
                "HAFTALIK": "weekly",
                "AYLIK": "monthly",
                "TÜM ZAMANLAR": "all"
            }
            period = period_map.get(filter_key, "all")
            
            # Run in thread to prevent freezing
            # Run in thread to prevent freezing
            def fetch():
                res = self.network.get_scores(period)
                if res.get("success"):
                    scores = res.get("scores", [])
                    
                    # Backfill/Update data from local profiles
                    # Important for Global Scoreboard to correct local user's avatar immediately
                    for s in scores:
                        p_data = self.get_profile_data(s.get('name'))
                        if p_data:
                            # Always sync Avatar to current selection
                            if 'avatar_id' in p_data:
                                s['avatar_id'] = p_data['avatar_id']
                            
                            # Backfill Fullname if missing
                            if ('fullname' not in s or s['fullname'] == "-") and p_data.get('fullname'):
                                s['fullname'] = p_data['fullname']

                    self.root.after(0, lambda: render_scores(scores))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Hata", "Sunucuya bağlanılamadı."))
            
            threading.Thread(target=fetch, daemon=True).start()

    def create_score_strip(self, parent, rank, data, allow_delete=True):
        # Colors based on Rank
        strip_bg = INPUT_BG
        rank_fg = SUB_TEXT_COLOR
        
        if rank == 1:
            rank_fg = "#3b82f6" # Blue
        elif rank == 2:
            rank_fg = "#ca8a04" # Dark Yellow/Gold (Readable on dark bg)
        elif rank == 3:
            rank_fg = "#22c55e" # Green
        elif rank == 4:
            rank_fg = "#a855f7" # Purple
        elif rank == 5:
            rank_fg = "#ef4444" # Red
            
        # Strip Container
        strip = tk.Frame(parent, bg=strip_bg, height=self.s(80))
        strip.pack_propagate(False)
        strip.pack(fill="x", pady=self.s(5))
        
        # Rank (Number only, no hash)
        tk.Label(strip, text=str(rank), font=(self.font_main, self.s(24), "bold"), 
                 fg=rank_fg, bg=strip_bg, width=4).pack(side="left", padx=(self.s(20), self.s(10)))
                 
        # Avatar/Icon Placeholder (Optional circle)
        # canvas = tk.Canvas(strip, width=self.s(50), height=self.s(50), bg=strip_bg, highlightthickness=0)
        # canvas.pack(side="left", padx=self.s(10))
        # self.draw_rounded_rect(canvas, 0, 0, self.s(50), self.s(50), self.s(25), rank_fg)
        
        # Name (Display Full Name if available, check length)
        display_name = data.get('fullname', '-')
        if not display_name or display_name == "-":
            display_name = self.tr_upper(data['name']) # Fallback to username
            
        # Truncate if too long (approx 25 chars)
        if len(display_name) > 25:
             display_name = display_name[:22] + "..."
             
        name_lbl = tk.Label(strip, text=display_name, font=(self.font_main, self.s(20), "bold"), 
                 fg=TEXT_COLOR, bg=strip_bg, cursor="hand2")
        name_lbl.pack(side="left", padx=self.s(20))
        
        # Click to show profile
        name_lbl.bind("<Button-1>", lambda e: self.show_player_profile(data))

        # Score Column (Far right, fixed width)
        # Using a fixed container ensures precise column alignment regardless of text length
        score_col = tk.Frame(strip, bg=strip_bg, width=self.s(240), height=self.s(80))
        score_col.pack_propagate(False)
        score_col.pack(side="right", padx=(self.s(10), self.s(40))) # 40px from window edge
        
        tk.Label(score_col, text=f"{data['score']} PUAN", font=(self.font_main, self.s(24), "bold"), 
                 fg=ACCENT_COLOR, bg=strip_bg).place(relx=1.0, rely=0.5, anchor="e")

        # Date column removed - date now shown only in profile dialog

        # Time Column (Left of Date, fixed width)
        time_col = tk.Frame(strip, bg=strip_bg, width=self.s(100), height=self.s(80))
        time_col.pack_propagate(False)
        time_col.pack(side="right", padx=(self.s(80), 0))
        
        time_val = data.get('time', "00:00")
        tk.Label(time_col, text=time_val, font=(self.font_main, self.s(16), "bold"), 
                 fg=SUB_TEXT_COLOR, bg=strip_bg).place(relx=1.0, rely=0.5, anchor="e")

        # Class Level Column (Replaces School)
        # On small screens, we reduce width
        class_width = 400
        if self.root.winfo_screenwidth() < 1200:
            class_width = 250
        if self.root.winfo_screenwidth() < 800:
            class_width = 150
            
        class_col = tk.Frame(strip, bg=strip_bg, width=self.s(class_width), height=self.s(80))
        class_col.pack_propagate(False)
        class_col.pack(side="right", padx=(self.s(80), 0))
        
        class_val = data.get('class_level', "-")
        # Truncate if too long (unlikely for class level but good for safety)
        max_chars = 35 if class_width >= 400 else 18
        if len(str(class_val)) > max_chars: 
            class_val = str(class_val)[:max_chars-3] + "..."
            
        tk.Label(class_col, text=class_val, font=(self.font_main, self.s(16), "bold"), 
                 fg=SUB_TEXT_COLOR, bg=strip_bg).place(relx=1.0, rely=0.5, anchor="e")


        # Bind Right Click (Delete) for all parts of the strip
        def on_right_click(event):
            self.delete_score(data)
            
        # Recursive binding for all widgets within the strip
        def bind_recursive(widget):
            widget.bind("<Button-3>", on_right_click, add="+")
            for child in widget.winfo_children():
                bind_recursive(child)

        if allow_delete:
            bind_recursive(strip)

    def show_admin_users_screen(self):
        self.current_screen = "admin_users"
        self.clear_container()
        
        # Header
        tk.Label(self.container, text="TÜM ÜYELER (ADMIN)", font=(self.font_main, self.s(32), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=20)
        
        # Scrollable List
        list_container = tk.Frame(self.container, bg=BG_COLOR)
        list_container.pack(fill="both", expand=True, padx=50, pady=(0, 20))
        
        list_scroll = ScrollableFrame(list_container, bg=BG_COLOR)
        list_scroll.pack(fill="both", expand=True)
        content = list_scroll.scrollable_frame
        
        # Fetch Users
        res = self.network.get_all_users()
        if not res.get("success"):
            tk.Label(content, text=res.get("message"), fg="#ef4444", bg=BG_COLOR).pack(pady=20)
        else:
            users = res.get("users", [])
            if not users:
                 tk.Label(content, text="Hiç üye yok.", fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(pady=20)

            # Fetch Scores for Profile View
            scores_res = self.network.get_scores()
            user_scores = {}
            if scores_res and scores_res.get("success"):
                all_scores = scores_res.get("scores", [])
                for s in all_scores:
                    uname = s.get("name") # 'name' is keyed from get_scores()
                    puan = s.get("score", 0)
                    if uname:
                        user_scores[uname] = user_scores.get(uname, 0) + int(puan)

            for i, u in enumerate(users):
                row = tk.Frame(content, bg=INPUT_BG, height=self.s(60))
                row.pack(fill="x", pady=2, padx=10)
                
                username = u.get("username", "Bilinmeyen")
                fullname = u.get("fullname", "").strip()
                display_text = f"{i+1}. {fullname if fullname else username}"
                
                # Prepare data for profile view (show_player_profile expects 'name')
                profile_data = u.copy()
                profile_data['name'] = username
                # Inject total score
                profile_data['score'] = user_scores.get(username, 0)
                
                def open_profile(e, d=profile_data):
                    self.show_player_profile(d)
                
                # Wrapper frame for clickability (if row itself doesn't work well due to children)
                # Actually binding row and label is enough usually.
                
                # Username/Fullname Label
                lbl = tk.Label(row, text=display_text, font=(self.font_main, self.s(16)), 
                         fg=TEXT_COLOR, bg=INPUT_BG, width=30, anchor="w", cursor="hand2")
                lbl.pack(side="left", padx=20, pady=10)
                
                # Bind click to view profile
                row.bind("<Button-1>", open_profile)
                lbl.bind("<Button-1>", open_profile)
                
                # Delete Button
                # Don't allow self-deletion
                if username != "OKAN707": # Hardcoded protection for main admin
                    self.create_rounded_button(row, "SİL", lambda x=username: self.confirm_delete_user(x), 
                                              width=80, height=35, bg="#ef4444", fg="white", font_size=10).pack(side="right", padx=20, pady=5)

        # Back Button
        self.create_rounded_button(self.container, "GERİ DÖN", self.show_entry_screen, 
                                  width=200, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=20)

    def confirm_delete_user(self, username):
        if messagebox.askyesno("Kullanıcı Sil", f"'{username}' kullanıcısını ve tüm verilerini silmek istediğinize emin misiniz?"):
            res = self.network.delete_user(username)
            messagebox.showinfo("Bilgi", res.get("message"))
            if res.get("success"):
                self.show_admin_users_screen() # Refresh list


    def show_player_profile(self, data):
        """Displays a modal popup with player details."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Oyuncu Profili")
        
        # Bigger sizing as requested
        width = self.s(750)
        height = self.s(550)
        
        # Center the dialog
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        # ROUNDED WINDOW TRICK
        transparent_key = "#000001"
        dialog.configure(bg=transparent_key)
        dialog.attributes("-transparentcolor", transparent_key)
        dialog.overrideredirect(True)
        dialog.attributes("-topmost", True)
        
        # Background Canvas
        bg_canvas = tk.Canvas(dialog, width=width, height=height, bg=transparent_key, highlightthickness=0)
        bg_canvas.pack(fill="both", expand=True)
        
        # Rounded Border
        # Rounded Border
        self.draw_rounded_rect(bg_canvas, 2, 2, width-2, height-2, 25, ACCENT_COLOR)
        # Background
        self.draw_rounded_rect(bg_canvas, 4, 4, width-6, height-6, 23, BG_COLOR)
        
        # Content Frame (Centered, padded)
        content = tk.Frame(bg_canvas, bg=BG_COLOR)
        content.place(relx=0.5, rely=0.5, anchor="center", width=width-40, height=height-40)

        # Close Button (Top Right of Content or Canvas?)
        # Better in content or manually drawn on canvas. Let's put it in content.
        close_btn = tk.Label(content, text="✕", font=(self.font_main, self.s(20)), fg=SUB_TEXT_COLOR, bg=BG_COLOR, cursor="hand2")
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=10, y=-10) # Offset slightly
        close_btn.bind("<Button-1>", lambda e: dialog.destroy())
        
        # Avatar Area
        canvas = tk.Canvas(content, width=self.s(120), height=self.s(120), bg=BG_COLOR, highlightthickness=0)
        canvas.pack(pady=(self.s(30), self.s(10)))
        
        # Use Avatar ID from data if available
        avatar_id = data.get("avatar_id", "1")
        av_data = AVATARS.get(avatar_id, AVATARS["1"])
        
        # Fix: Inner circle must be smaller/concentric with outer ring and fit in 120x120 canvas
        # Canvas: 120x120
        # Outer: 5,5 to 115,115 (Size 110)
        # Inner: 10,10 to 110,110 (Size 100)
        canvas.create_oval(self.s(5), self.s(5), self.s(115), self.s(115), outline=ACCENT_COLOR, width=2)
        canvas.create_oval(self.s(10), self.s(10), self.s(110), self.s(110), fill=av_data["color"], outline="", width=0)
        canvas.create_text(self.s(60), self.s(60), text=av_data["icon"], font=("Segoe UI Emoji", self.s(48)), fill=BG_COLOR)
        
        # Username
        tk.Label(content, text=data.get('name', 'Bilinmiyor'), font=(self.font_main, self.s(32), "bold"), 
                 fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(20)))
                 
        # Info Grid
        info_frame = tk.Frame(content, bg=BG_COLOR)
        info_frame.pack(pady=10)
        
        fields = [
            ("Adı Soyadı:", data.get('fullname', '-')),
            ("Okulu:", data.get('school', '-')),
            ("Sınıfı:", data.get('class_level', '-')),
            ("Cinsiyet:", data.get('gender', '-')),
            ("Tarih:", datetime.fromtimestamp(data.get('timestamp', 0)).strftime("%d.%m.%Y") if data.get('timestamp') else "-"),
            ("Puan:", f"{data.get('score', 0)}")
        ]
        
        for i, (label, val) in enumerate(fields):
            tk.Label(info_frame, text=label, font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR, anchor="e", width=15).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Label(info_frame, text=val, font=(self.font_main, self.s(14), "bold"), fg=TEXT_COLOR, bg=BG_COLOR, anchor="w").grid(row=i, column=1, sticky="w", padx=5, pady=2)
            
        # --- Security Question Management (Only for own profile) ---
        current_username = str(getattr(self, "username", "")).strip().upper()
        # Leaderboard data might use 'name' or 'username' depending on source
        raw_view_username = data.get("username", data.get("name", ""))
        view_username = str(raw_view_username).strip().upper()
        
        print(f"[DEBUG] Profile View - Current: '{current_username}', View: '{view_username}' (Raw: '{raw_view_username}')")
        
        if current_username and view_username and current_username == view_username:
            # Fetch full user data to get security info
            full_user_data = self.network.get_user_by_username(current_username)
            
            if full_user_data:
                sec_q = full_user_data.get("security_question", "")
                
                manage_frame = tk.Frame(content, bg=BG_COLOR)
                manage_frame.pack(pady=10)
                
                if not sec_q:
                    # No security question set
                    tk.Label(manage_frame, text="⚠️ Güvenlik sorusu ayarlanmamış!", 
                            font=(self.font_main, self.s(12)), fg="#ef4444", bg=BG_COLOR).pack()
                    
                    self.create_rounded_button(manage_frame, "Güvenlik Sorusu Oluştur", 
                                              lambda: [dialog.destroy(), self.open_security_question_dialog(full_user_data)], 
                                              width=220, height=40, bg=ACCENT_COLOR, fg=BG_COLOR, font_size=12).pack(pady=5)
                else:
                    # Security question exists
                    tk.Label(manage_frame, text="Güvenlik Sorusu:", 
                            font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack()
                    tk.Label(manage_frame, text=sec_q, 
                            font=(self.font_main, self.s(12), "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack()
                    
                    self.create_rounded_button(manage_frame, "Değiştir", 
                                              lambda: [dialog.destroy(), self.open_security_question_dialog(full_user_data)], 
                                              width=150, height=35, bg=INPUT_BG, fg=TEXT_COLOR, font_size=11).pack(pady=5)

        # OK Button
        self.create_rounded_button(content, "KAPAT", dialog.destroy, width=200, height=50, bg=ACCENT_COLOR, fg=BG_COLOR, font_size=14).pack(side="bottom", pady=20)

        dialog.grab_set()

    def open_security_question_dialog(self, user_data):
        """Dialog to set or update security question"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Güvenlik Sorusu")
        
        width = self.s(500)
        height = self.s(450)
        
        # Center the dialog
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="GÜVENLİK SORUSU", font=(self.font_main, self.s(24), "bold"), 
                fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=20)
        
        content = tk.Frame(dialog, bg=BG_COLOR, padx=20)
        content.pack(fill="both", expand=True)
        
        # Security Questions List (Matches Register)
        security_questions = [
            "İlk evcil hayvanınızın adı neydi?",
            "En sevdiğiniz yemek hangisidir?",
            "İlk okulunuzun adı neydi?",
            "En sevdiğiniz renk nedir?",
            "Doğduğunuz şehir neresidir?",
            "En sevdiğiniz çizgi film kahramanı kim?",
            "En sevdiğiniz ders hangisi?",
            "En iyi arkadaşınızın adı ne?",
            "Hangi takımı tutuyorsunuz?",
            "Büyüyünce ne olmak istersiniz?"
        ]
        
        tk.Label(content, text="SORU SEÇİN", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
        q_combo = ttk.Combobox(content, values=security_questions, state="readonly", font=(self.font_main, self.s(12)))
        q_combo.pack(fill="x", pady=(5, 15))
        
        # Pre-select if exists
        current_q = user_data.get("security_question", "")
        if current_q in security_questions:
            q_combo.set(current_q)
        else:
            if security_questions: q_combo.current(0)
            
        tk.Label(content, text="CEVAP", font=(self.font_main, self.s(12)), fg=SUB_TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
        a_entry = tk.Entry(content, font=(self.font_main, self.s(14)), bg=INPUT_BG, fg=TEXT_COLOR, relief="flat")
        a_entry.pack(fill="x", pady=(5, 20), ipady=5)
        
        def save_security_info():
            q = q_combo.get()
            a = a_entry.get().strip()
            
            if not q or not a:
                messagebox.showwarning("Hata", "Lütfen soru ve cevap girin.")
                return
            
            # Update via NetworkManager
            username = user_data.get("username")
            update_data = {
                "security_question": q,
                "security_answer": a
            }
            
            res = self.network.update_user_profile(username, update_data)
            if res.get("success"):
                messagebox.showinfo("Başarılı", "Güvenlik sorusu güncellendi!")
                dialog.destroy()
                # Re-open profile to see changes
                updated_user = self.network.get_user_by_username(username)
                if updated_user:
                    self.show_player_profile(updated_user)
            else:
                messagebox.showerror("Hata", res.get("message", "Güncelleme başarısız."))
        
        self.create_rounded_button(content, "KAYDET", save_security_info, width=200, height=50, bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=20)
        self.create_rounded_button(content, "İPTAL", dialog.destroy, width=200, height=40, bg=BG_COLOR, fg=SUB_TEXT_COLOR).pack()

    def show_custom_confirmation(self, title, message, on_confirm):
        # Create a modern modal dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        
        # Dimensions
        width, height = 500, 350
        
        # Center the dialog
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        
        x = root_x + (root_w - width) // 2
        y = root_y + (root_h - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # ROUNDED WINDOW TRICK (Windows Only)
        # 1. Set a unique transparent color key
        transparent_key = "#000001" 
        dialog.configure(bg=transparent_key)
        dialog.attributes("-transparentcolor", transparent_key)
        dialog.overrideredirect(True) 
        dialog.attributes("-topmost", True)
        
        # 2. Draw Rounded Background on Canvas
        bg_canvas = tk.Canvas(dialog, width=width, height=height, bg=transparent_key, highlightthickness=0)
        bg_canvas.pack(fill="both", expand=True)
        
        # Draw with slight border
        # Rounded Border
        self.draw_rounded_rect(bg_canvas, 2, 2, width-2, height-2, 25, ACCENT_COLOR) # Border using Full + Color
        # Background
        self.draw_rounded_rect(bg_canvas, 4, 4, width-6, height-6, 23, BG_COLOR)     # Inner Background
        
        # 3. Content Frame (Centered, slightly smaller to avoid corner overlap)
        # Using place to center it inside the canvas
        content = tk.Frame(bg_canvas, bg=BG_COLOR)
        content.place(relx=0.5, rely=0.5, anchor="center", width=width-40, height=height-40)

        
        # Icon/Title
        tk.Label(content, text="⚠", font=(self.font_main, self.s(30)), fg="#ef4444", bg=BG_COLOR).pack(pady=(self.s(10), 0))
        tk.Label(content, text=title, font=(self.font_main, self.s(20), "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(0, self.s(10)))
        
        # Message
        tk.Label(content, text=message, font=(self.font_main, self.s(14)), fg=SUB_TEXT_COLOR, bg=BG_COLOR, wraplength=self.s(420)).pack(pady=self.s(10))
        
        # Buttons
        btn_frame = tk.Frame(content, bg=BG_COLOR, height=self.s(80))
        btn_frame.pack_propagate(False)
        btn_frame.pack(side="bottom", pady=self.s(10), fill="x")
        
        # Center buttons inside btn_frame
        inner_btn_frame = tk.Frame(btn_frame, bg=BG_COLOR)
        inner_btn_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        def do_confirm():
            dialog.destroy()
            on_confirm()
            
        def do_cancel():
            dialog.destroy()
            
        # Buttons
        btn_yes = self.create_rounded_button(inner_btn_frame, "EVET", do_confirm, width=160, height=45, bg="#ef4444", fg="white", font_size=16)
        btn_yes.pack(side="left", padx=self.s(10))
        
        btn_no = self.create_rounded_button(inner_btn_frame, "HAYIR", do_cancel, width=160, height=45, bg="#64748b", fg="white", font_size=16)
        btn_no.pack(side="left", padx=self.s(10))

        dialog.grab_set()


    def delete_score(self, score_data):
        def perform_delete():
            try:
                if self.leaderboard_scope == 'global':
                    # Server Delete
                    target_user = score_data.get('name') 
                    target_ts = score_data.get('timestamp')
                    
                    def run_del():
                        res = self.network.delete_score(target_user, target_ts)
                        self.root.after(0, lambda: self.handle_delete_result(res))
                        
                    threading.Thread(target=run_del, daemon=True).start()
                    
                else:
                    # Local Delete
                    base_dir = self.get_user_data_dir()
                    path = os.path.join(base_dir, "highscores.json")
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            scores = json.load(f)
                        
                        original_len = len(scores)
                        new_scores = []
                        target_ts = score_data.get('timestamp')
                        target_name = score_data.get('name')
                        
                        for s in scores:
                            if s.get('timestamp') == target_ts and s.get('name') == target_name:
                                continue
                            new_scores.append(s)
                        
                        if len(new_scores) < original_len:
                            with open(path, "w", encoding="utf-8") as f:
                                json.dump(new_scores, f, ensure_ascii=False, indent=2)
                            
                            self.load_leaderboard_data(self.current_filter)
            except Exception as e:
                self.log_debug(f"Error deleting score: {e}")
        
        self.show_custom_confirmation("SKOR SİLİNSİN Mİ?", 
                                    f"'{score_data.get('name')}' adlı oyuncunun {score_data.get('score')} puanlık skorunu silmek istiyor musunuz?", 
                                    perform_delete)

    def handle_delete_result(self, res):
        if res.get("success"):
            # Refresh leaderboard
            self.load_leaderboard_data(self.current_filter)
        else:
            messagebox.showerror("Hata", res.get("message", "Silme işlemi başarısız."))

    def _reset_game_state(self):
        """Centralized method to reset game state for a new player or restart.
        Ensures score and levels are cleared, but used words remain persistent in session."""
        # self.used_words.clear() # Keeping it persistent across games in the same session
        self.level_idx = 0
        self.total_score = 0
        self.potential_score = 0
        self.revealed_indices = []
        self.time_left = config.get("game_settings", "timer_duration", default=60)
        self.current_word_data = None
        self.score_saved = False
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except:
                pass
            self.timer_id = None

    def reset_game(self):
        # Full reset for "Play Again" or Initial Start
        self._reset_game_state()
        self.show_entry_screen()

    def on_closing(self):
        # Stop timer if active
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except:
                pass
        
        # Shutdown pygame if used
        try:
            if os.name == 'nt':
                # Close all MCI aliases
                ctypes.windll.winmm.mciSendStringW("close all", None, 0, 0)

            if PYGAME_AVAILABLE:
                pygame.mixer.quit()
                pygame.quit()
        except:
            pass
            
        self.root.destroy()
        # Full exit to ensure no hanging processes
        os._exit(0)

if __name__ == "__main__":
    # Enable DPI Awareness for sharp text on high-DPI displays
    try:
        from ctypes import windll
        try:
            windll.shcore.SetProcessDpiAwareness(2) 
        except Exception:
            windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            windll.user32.SetProcessDPIAware()
        except:
            pass

    root = tk.Tk()
    app = WordGameApp(root)
    root.mainloop()
