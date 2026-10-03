from app import create_app
from extensions import db, bcrypt
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

app = create_app(TestConfig)
with app.app_context():
    db.create_all()
    client = app.test_client()
    
    # Try registering
    res = client.post('/auth/register', data={
        'name': 'Bob',
        'email': 'bob@bob.com',
        'password': 'StrongPassword1',
        'batch': '2024',
        'department': 'CS'
    })
    print(f"Register status: {res.status_code}")
    if res.status_code == 500:
        print(res.data.decode('utf-8'))
        
    # Try admin dashboard
    from models import User
    hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(name='Admin', email='admin@a.com', password_hash=hashed_pw, role='admin', status='Approved')
    db.session.add(admin)
    db.session.commit()
    
    res = client.post('/auth/login', data={'email': 'admin@a.com', 'password': 'admin123'}, follow_redirects=True)
    print(f"Login status: {res.status_code}")
    if res.status_code == 500:
        print(res.data.decode('utf-8'))
        
    res = client.get('/admin/dashboard')
    print(f"Admin Dashboard status: {res.status_code}")
    if res.status_code == 500:
        print(res.data.decode('utf-8'))
        
    # Let's also check reports
    res = client.get('/admin/reports')
    print(f"Admin Reports status: {res.status_code}")
    if res.status_code == 500:
        print(res.data.decode('utf-8'))
