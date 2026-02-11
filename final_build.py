import subprocess
import sys
import os

def build():
    print("--- FINAL BUILD ATTEMPT ---")
    
    # Try directory cleanup only if possible (don't crash)
    if os.path.exists("dist"):
        try:
            import shutil
            shutil.rmtree("dist")
            print("Cleaned dist")
        except:
            print("Could not clean dist (locked?)")

    # Command 1: Python module approach (safest)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=KelimeOyunu_FINAL_V2",
        "--icon=app_icon.ico",
        "--clean",
        "--add-data=sozluk.json;.",
        "--add-data=config.json;.",
        "--add-data=highscores.json;.",
        "--add-data=benz;benz",
        "--add-data=assets;assets",
        "main.py"
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        # Use shell=True to bypass some path issues on Windows
        ret = subprocess.call(cmd, shell=True)
        print(f"Return Code: {ret}")
        
        if ret != 0:
            print("Usage failed... trying direct command...")
            subprocess.call("pyinstaller main.py", shell=True)
            
    except Exception as e:
        print(f"Subprocess failed: {e}")

    if os.path.exists("dist/KelimeOyunu_FINAL_V2.exe"):
        print("SUCCESS: File created.")
    else:
        print("FAILURE: No file found.")

if __name__ == "__main__":
    build()
