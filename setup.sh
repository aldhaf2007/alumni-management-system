#!/bin/bash
echo "==============================================="
echo "Alumni Management System - Linux Setup"
echo "==============================================="

echo "[INFO] Checking for MySQL Server..."
if ! command -v mysql &> /dev/null; then
    echo "[INFO] MySQL could not be found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y mysql-server
        SERVICE_NAME="mysql"
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y community-mysql-server
        SERVICE_NAME="mysqld"
    elif command -v yum &> /dev/null; then
        sudo yum install -y mysql-server
        SERVICE_NAME="mysqld"
    else
        echo "[ERROR] Unsupported package manager. Please install MySQL manually."
        exit 1
    fi
else
    echo "[INFO] MySQL is already installed."
    if systemctl list-units --full -all | grep -Fq "mysqld.service"; then
        SERVICE_NAME="mysqld"
    else
        SERVICE_NAME="mysql"
    fi
fi

echo "[INFO] Ensuring MySQL service is running..."
sudo systemctl start $SERVICE_NAME
sudo systemctl enable $SERVICE_NAME

echo "[INFO] Configuring MySQL Database..."
# Create database and user
sudo mysql -e "CREATE DATABASE IF NOT EXISTS alumni_db;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY 'alumni_pass';"
sudo mysql -e "GRANT ALL PRIVILEGES ON alumni_db.* TO 'alumni_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "[INFO] Setting up Python Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[INFO] Initializing Database (Creating tables)..."
python init_db.py

echo "[INFO] Starting Flask Application..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
