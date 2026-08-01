@echo off
echo Starting Alumni Management System...
call venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
pause
