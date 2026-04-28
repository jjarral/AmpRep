@echo off
echo Starting Ampoulex...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python run.py
pause