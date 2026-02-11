
@echo off
echo Cleaning up...

:: Folders
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Output rmdir /s /q Output
if exist __pycache__ rmdir /s /q __pycache__
if exist _internal rmdir /s /q _internal
if exist mock_app rmdir /s /q mock_app
if exist mock_source rmdir /s /q mock_source
if exist test_appdata rmdir /s /q test_appdata

:: Files
if exist cmd_log.txt del /q cmd_log.txt
if exist update_log.txt del /q update_log.txt
if exist debug_logo.txt del /q debug_logo.txt
if exist forgot_password_method.txt del /q forgot_password_method.txt

:: Specific Scripts (Explicit list to be safe)
if exist convert_icon.py del /q convert_icon.py
if exist force_theme_sync.py del /q force_theme_sync.py
if exist logo_fix_processor.py del /q logo_fix_processor.py
if exist migrate_users.py del /q migrate_users.py
if exist restore_dict.py del /q restore_dict.py
if exist update_dark_logo_only.py del /q update_dark_logo_only.py
if exist verify_updater.py del /q verify_updater.py
if exist wipe_scores.py del /q wipe_scores.py

:: Patterns
del /q analyze_*.py
del /q check_*.py
del /q clean_*.py
del /q create_assets_*.py
del /q deploy_*.py
del /q fix_*.py
del /q process_*.py
del /q test_*.py
del /q *.spec

:: Delete python cleanup script if it exists
if exist cleanup_project.py del /q cleanup_project.py

echo Cleanup complete.
