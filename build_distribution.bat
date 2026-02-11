@echo off
setlocal

echo ========================================================
echo      Kelime Oyunu - Dagitim Olusturma Araci v1.5
echo ========================================================
echo.

set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

:: 1. Temizlik
echo [1/3] Eski dosyalar temizleniyor...
if exist "dist\KelimeAvcisi.exe" del "dist\KelimeAvcisi.exe"
if exist "Output\KelimeAvcisiSetup_v1.5.exe" del "Output\KelimeAvcisiSetup_v1.5.exe"
echo Temizlik tamamlandi.
echo.

:: 2. EXE Olusturma (PyInstaller)
echo [2/3] KelimeAvcisi.exe olusturuluyor (PyInstaller)...
python build_installer.py
if %ERRORLEVEL% NEQ 0 (
    echo HATA: PyInstaller islemi basarisiz oldu!
    echo Lutfen hata mesajlarini kontrol edin.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo EXE olusturma basarili!
echo.

:: 3. Kurulum Dosyasi Olusturma (Inno Setup)
echo [3/3] Kurulum dosyasi hazirlaniyor (Inno Setup)...
if not exist "%INNO_SETUP_PATH%" (
    echo HATA: Inno Setup derleyicisi bulunamadi!
    echo Yol: %INNO_SETUP_PATH%
    echo Lutfen Inno Setup 6'nin yuklu oldugundan emin olun.
    pause
    exit /b 1
)

"%INNO_SETUP_PATH%" install_script.iss
if %ERRORLEVEL% NEQ 0 (
    echo HATA: Kurulum dosyasi olusturulamadi!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echoISLEM BASARIYLA TAMAMLANDI!
echo.
echo Olusturulan dosyalar:
if exist "dist\KelimeAvcisi.exe" echo - EXE: dist\KelimeAvcisi.exe
if exist "Output\KelimeAvcisiSetup_v1.5.exe" echo - SETUP: Output\KelimeAvcisiSetup_v1.5.exe
echo ========================================================
echo.
pause
