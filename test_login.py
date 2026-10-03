import requests
s = requests.Session()
r = s.post('http://127.0.0.1:5000/auth/login', data={'email': 'admin@abc.edu', 'password': 'admin123'})
print(r.status_code)
print(r.text[:500])
