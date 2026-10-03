@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo Alumni Management System - Windows Setup
echo ===============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH.
    pause
    exit /b
)

echo [INFO] Checking for MySQL...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] MySQL is not installed or not in PATH.
    echo [INFO] Attempting to install MySQL via winget...
    winget install -e --id Oracle.MySQL --accept-source-agreements --accept-package-agreements
    
    echo [INFO] Adding MySQL to PATH for this session...
    set "PATH=%PATH%;C:\Program Files\MySQL\MySQL Server 8.0\bin;C:\Program Files\MySQL\MySQL Server 8.4\bin"
)

echo [INFO] Attempting to create database and user...
echo [INFO] Note: If your MySQL root user has a password, this step might fail.
mysql -u root -e "CREATE DATABASE IF NOT EXISTS alumni_db;"
mysql -u root -e "CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY 'alumni_pass';"
mysql -u root -e "GRANT ALL PRIVILEGES ON alumni_db.* TO 'alumni_user'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"

if %errorlevel% neq 0 (
    echo [WARNING] MySQL database creation failed or requires password.
    echo Please manually create the 'alumni_db' and user 'alumni_user' with password 'alumni_pass'.
)

REM Setup Python Env
echo [INFO] Setting up Python Environment...
if not exist "venv\" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo [INFO] Initializing Database (Creating tables)...
python init_db.py

echo [INFO] Starting Flask Application...
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

pause
