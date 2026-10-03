import unittest
from app import create_app
from extensions import db
from models import User, Profile, Job, Event, JobApplication
from extensions import db, bcrypt

from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Create app in testing mode
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Setup dummy users
            # Admin
            self.admin = User(name='Admin Test', email='admin_test@abc.edu', role='admin', status='Approved')
            self.admin.password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
            db.session.add(self.admin)
            
            # Alumni
            self.alumni = User(name='Alumni Test', email='alumni_test@abc.edu', role='alumni', status='Approved')
            self.alumni.password_hash = bcrypt.generate_password_hash('alumni123').decode('utf-8')
            db.session.add(self.alumni)
            

            
            # Pending User
            self.pending = User(name='Pending Test', email='pending@abc.edu', role='alumni', status='Pending')
            self.pending.password_hash = bcrypt.generate_password_hash('pending123').decode('utf-8')
            db.session.add(self.pending)
            
            db.session.commit()
            
            self.admin_id = self.admin.id
            self.alumni_id = self.alumni.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_auth_and_routing(self):
        # Pending user shouldn't be able to login
        res = self.login('pending@abc.edu', 'pending123')
        self.assertIn(b'Your account is pending admin approval.', res.data)
        
        # Admin login
        res = self.login('admin_test@abc.edu', 'admin123')
        self.assertIn(b'Login successful.', res.data)
        
        # Test admin routes
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get('/admin/users')
        self.assertEqual(res.status_code, 200)
        
        res = self.client.get('/admin/reports')
        self.assertEqual(res.status_code, 200)
        self.logout()
        
        # Alumni login
        self.login('alumni_test@abc.edu', 'alumni123')
        # Ensure alumni can't access admin
        res = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Unauthorized access', res.data)
        self.logout()
        self.logout()

    def test_registration(self):
        # Register a new alumni with WEAK password should fail
        res = self.client.post('/auth/register', data={
            'name': 'Registration Test',
            'email': 'regtest@aringaranna.edu',
            'password': 'weak',
            'batch': '2023',
            'department': 'Mechanical Engineering'
        }, follow_redirects=True)
        self.assertIn(b'Password must be at least 8 characters', res.data)

        # Register a new alumni with STRONG password
        res = self.client.post('/auth/register', data={
            'name': 'Registration Test',
            'email': 'regtest@aringaranna.edu',
            'password': 'StrongPassword1',
            'batch': '2023',
            'department': 'Mechanical Engineering',
            'company': 'Auto Corp',
            'designation': 'Engineer',
            'location': 'Detroit, MI',
            'skills': 'CAD, Python',
            'bio': 'New graduate.'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', res.data)
        
        # Verify user and profile in DB
        with self.app.app_context():
            user = User.query.filter_by(email='regtest@aringaranna.edu').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.status, 'Pending')
            self.assertIsNotNone(user.profile)
            self.assertEqual(user.profile.batch, '2023')
            self.assertEqual(user.profile.company, 'Auto Corp')

    def test_admin_crud(self):
        self.login('admin_test@abc.edu', 'admin123')
        
        # Add user
        res = self.client.post('/admin/users/add', data={
            'name': 'New User',
            'email': 'new@abc.edu',
            'password': 'Password123',
            'role': 'alumni',
            'status': 'Approved'
        }, follow_redirects=True)
        self.assertIn(b'New User', res.data)
        
        with self.app.app_context():
            user = User.query.filter_by(email='new@abc.edu').first()
            self.assertIsNotNone(user)
            user_id = user.id
            
        # Edit user
        res = self.client.post(f'/admin/users/{user_id}/edit', data={
            'name': 'Edited User',
            'email': 'edited@abc.edu',
            'role': 'alumni',
            'status': 'Approved'
        }, follow_redirects=True)
        self.assertIn(b'Edited User', res.data)
        
        # Delete user
        res = self.client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
        self.assertIn(b'was successfully deleted', res.data)
        
        with self.app.app_context():
            user = User.query.filter_by(email='edited@abc.edu').first()
            self.assertIsNone(user)

    def test_profile_and_directory(self):
        self.login('alumni_test@abc.edu', 'alumni123')
        
        # Update Profile
        res = self.client.post('/alumni/profile', data={
            'batch': '2020-2023',
            'department': 'Computer Science',
            'company': 'Tech Corp',
            'designation': 'Developer',
            'location': 'New York',
            'skills': 'Python, Flask',
            'bio': 'Test bio'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        # Directory
        res = self.client.get('/alumni/directory')
        self.assertEqual(res.status_code, 200)
        
        # Filter directory
        res = self.client.get('/alumni/directory?batch=2020-2023&department=Computer Science')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Alumni Test', res.data)

    def test_jobs_and_events(self):
        self.login('alumni_test@abc.edu', 'alumni123')
        
        # Create Job
        res = self.client.post('/jobs/post', data={
            'title': 'Test Job',
            'company': 'Test Co',
            'location': 'Remote',
            'description': 'Job desc'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with self.app.app_context():
            job = Job.query.first()
            self.assertIsNotNone(job)
            job_id = job.id
            
        # Create Event
        # NOTE: Only admin can create event, so login as admin first
        self.logout()
        self.login('admin_test@abc.edu', 'admin123')
        res = self.client.post('/events/create', data={
            'title': 'Test Event',
            'date': '2030-01-01',
            'time': '10:00',
            'location': 'Online',
            'description': 'Event desc'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with self.app.app_context():
            event = Event.query.first()
            self.assertIsNotNone(event)
            event_id = event.id
            
        self.logout()
        
        # Alumni applies for job and RSVPs
        self.login('alumni_test@abc.edu', 'alumni123')
        
        # RSVP
        res = self.client.post(f'/events/{event_id}/rsvp', follow_redirects=True)
        self.assertIn(b'Successfully registered', res.data)
        
        # Apply for job
        from io import BytesIO
        data = {
            'cover_letter': 'Test cover letter',
            'resume': (BytesIO(b'dummy pdf data'), 'resume.pdf')
        }
        res = self.client.post(f'/jobs/{job_id}/apply', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
