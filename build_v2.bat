@echo off
echo Building Kelime Oyunu (Fixed Sounds)...
python -m PyInstaller main.py --name=KelimeOyunu --onefile --noconsole --clean ^
 --add-data "sozluk.json;." ^
 --add-data "config.json;." ^
 --add-data "highscores.json;." ^
 --add-data "benz;benz" ^
 --add-data "assets;assets" ^
 --add-data "button-pressed-38129.mp3;." ^
 --add-data "click-buttons-ui-menu-sounds-effects-button-7-203601.mp3;." ^
 --add-data "mech-keyboard-02-102918.mp3;." ^
 --icon="app_icon.ico"
echo Build Complete.
