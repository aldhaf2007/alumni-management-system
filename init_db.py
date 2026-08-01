from app import create_app
from extensions import db, bcrypt
from models import User

app = create_app()
with app.app_context():
    db.create_all()
    # Create admin if not exists
    if not User.query.filter_by(email='admin@abc.edu').first():
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(name='System Admin', email='admin@abc.edu', password_hash=hashed_pw, role='admin', status='Approved')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin already exists.")
