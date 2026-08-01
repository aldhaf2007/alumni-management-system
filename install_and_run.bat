@echo off
echo ===============================================
echo Alumni Management System - Windows Setup
echo ===============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH.
    echo Please install Python from https://www.python.org/downloads/ and try again.
    pause
    exit /b
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing required dependencies...
pip install -r requirements.txt

echo [INFO] Starting the Flask server...
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

pause
