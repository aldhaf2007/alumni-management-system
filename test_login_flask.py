from app import create_app
from extensions import db
from models import User
from flask_bcrypt import Bcrypt

app = create_app()
with app.app_context():
    # Attempt to query the admin user
    try:
        user = User.query.filter_by(email='admin@abc.edu').first()
        if user:
            print(f"User found: {user.name}, role: {user.role}, password hash starts with: {user.password_hash[:10] if user.password_hash else 'None'}")
        else:
            print("Admin user not found.")
    except Exception as e:
        print(f"Error querying user: {e}")
        
    client = app.test_client()
    try:
        response = client.post('/auth/login', data={'email': 'admin@abc.edu', 'password': 'admin123'})
        print(f"Login Response Status: {response.status_code}")
        if response.status_code == 500:
            print("Login failed with 500")
            print(response.get_data(as_text=True)[:500])
        elif response.status_code == 302:
            print(f"Redirecting to: {response.headers.get('Location')}")
            # Follow redirect to dashboard
            dashboard_response = client.get(response.headers.get('Location'))
            print(f"Dashboard Response Status: {dashboard_response.status_code}")
            if dashboard_response.status_code == 500:
                print("Dashboard failed with 500")
                print(dashboard_response.get_data(as_text=True)[:500])
            else:
                print("Dashboard loaded successfully.")
    except Exception as e:
        print(f"Exception during request: {e}")
