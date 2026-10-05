@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo   Aringar Anna College Alumni Management System  
echo             Windows Setup Script                 
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH.
    echo Please install Python 3.10+ and check "Add Python to PATH" during installation.
    pause
    exit /b
)

echo [INFO] Python is installed.
echo.

REM MySQL Configuration
echo [INFO] Checking for MySQL...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MySQL command not found in PATH.
    echo If MySQL is installed, please add its 'bin' folder to your System PATH.
    echo Examples: C:\Program Files\MySQL\MySQL Server 8.0\bin
    echo.
) else (
    echo [INFO] MySQL is detected.
    echo To create the database and user, we need your MySQL root password.
    set /p MYSQL_ROOT_PASS="Enter MySQL root password (leave blank if none): "
    
    echo [INFO] Configuring database 'alumni_db' and user 'alumni_user'...
    if "!MYSQL_ROOT_PASS!"=="" (
        mysql -u root -e "CREATE DATABASE IF NOT EXISTS alumni_db;"
        mysql -u root -e "CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY 'alumni_pass';"
        mysql -u root -e "GRANT ALL PRIVILEGES ON alumni_db.* TO 'alumni_user'@'localhost';"
        mysql -u root -e "FLUSH PRIVILEGES;"
    ) else (
        mysql -u root -p"!MYSQL_ROOT_PASS!" -e "CREATE DATABASE IF NOT EXISTS alumni_db;"
        mysql -u root -p"!MYSQL_ROOT_PASS!" -e "CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY 'alumni_pass';"
        mysql -u root -p"!MYSQL_ROOT_PASS!" -e "GRANT ALL PRIVILEGES ON alumni_db.* TO 'alumni_user'@'localhost';"
        mysql -u root -p"!MYSQL_ROOT_PASS!" -e "FLUSH PRIVILEGES;"
    )
    
    if !errorlevel! neq 0 (
        echo [WARNING] Automatic database configuration failed.
        echo Please manually create database 'alumni_db' and user 'alumni_user' with password 'alumni_pass'.
    ) else (
        echo [SUCCESS] Database configuration successful.
    )
    echo.
)

REM Setup Folders
echo [INFO] Ensuring upload directories exist...
if not exist "static\uploads\profile_pics\" mkdir "static\uploads\profile_pics"
if not exist "static\uploads\event_pics\" mkdir "static\uploads\event_pics"

REM Setup Python Env
echo [INFO] Setting up Python Virtual Environment...
if not exist "venv\" (
    python -m venv venv
)

call venv\Scripts\activate.bat
echo [INFO] Installing required packages...
pip install --upgrade pip >nul
pip install -r requirements.txt

echo.
echo [INFO] Initializing Database Tables...
python init_db.py

echo [INFO] Seeding Database with Mock Data...
python seed_db.py

echo.
echo ===============================================
echo [SUCCESS] Setup Complete!
echo Starting the Flask Application...
echo Access the site at: http://localhost:5000
echo Admin Login: admin@aringaranna.edu / admin123
echo ===============================================
echo.

set FLASK_APP=app.py
set FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=5000

pause
