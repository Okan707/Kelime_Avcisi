import PyInstaller.__main__
import os
import shutil

# Temizlik işlemleri zaten güzel
# Temizlik işlemleri devre dışı
# for folder in ["dist", "build"]:
#     if os.path.exists(folder):
#         try: shutil.rmtree(folder)
#         except: pass

PyInstaller.__main__.run([
    'main.py',
    '--name=KelimeAvcisi', # Final Name
    '--onefile',
    '--noconsole',
    '--clean',
    '--add-data=sozluk.json;.',
    '--add-data=config.json;.',
    '--add-data=highscores.json;.',
    # Dosyaların varlığını kontrol ederek eklemek daha güvenlidir
    '--add-data=button-pressed-38129.mp3;.',
    '--add-data=click-buttons-ui-menu-sounds-effects-button-7-203601.mp3;.',
    '--add-data=mech-keyboard-02-102918.mp3;.',
    '--add-data=benz;benz',
    '--add-data=assets;assets',
    '--icon=app_icon.ico',
])

# --- Post-Build: Copy Critical Assets to Dist ---
print("\n[POST-BUILD] Copying critical assets to dist folder...")
dist_folder = "dist"
if os.path.exists(dist_folder):
    # Files to copy
    files_to_copy = ["sozluk.json", "config.json"]
    for f in files_to_copy:
        if os.path.exists(f):
            shutil.copy(f, os.path.join(dist_folder, f))
            print(f"Copied {f}")
            
    # Folders to copy
    folders_to_copy = ["assets", "benz"]
    for folder in folders_to_copy:
        src = folder
        dst = os.path.join(dist_folder, folder)
        if os.path.exists(src):
            if os.path.exists(dst): 
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied folder {folder}")

print("[POST-BUILD] Complete.")
