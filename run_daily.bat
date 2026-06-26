@echo off
cd /d "%~dp0"
python run_daily.py >> logs\daily.log 2>&1
