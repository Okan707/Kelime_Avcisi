@echo off
echo Starting update... > cmd_log.txt
python update_dark_logo_only.py >> cmd_log.txt 2>&1
echo Done. >> cmd_log.txt
