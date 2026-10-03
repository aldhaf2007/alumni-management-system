import urllib.request
import urllib.parse
import time
import subprocess
import os

flask_proc = subprocess.Popen(["venv/bin/python", "app.py"])
time.sleep(3)

try:
    print("Testing index...")
    req = urllib.request.Request("http://127.0.0.1:5000/")
    res = urllib.request.urlopen(req)
    print(f"Index: {res.getcode()}")
    
    print("Testing login...")
    data = urllib.parse.urlencode({"email": "admin@aringaranna.edu", "password": "admin123"}).encode()
    req = urllib.request.Request("http://127.0.0.1:5000/auth/login", data=data)
    try:
        res = urllib.request.urlopen(req)
        print(f"Login: {res.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Login error code: {e.code}")
        
    print("Testing register...")
    data = urllib.parse.urlencode({
        "name": "Test User",
        "email": "test@aringaranna.edu",
        "password": "StrongPassword1",
        "batch": "2024",
        "department": "CS"
    }).encode()
    req = urllib.request.Request("http://127.0.0.1:5000/auth/register", data=data)
    try:
        res = urllib.request.urlopen(req)
        print(f"Register: {res.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Register error code: {e.code}")
except Exception as e:
    print(f"Error: {e}")
finally:
    flask_proc.terminate()
