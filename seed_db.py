import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from models import User, Profile, Job, Event, Announcement, Feedback

def seed_database():
    app = create_app()
    with app.app_context():
        print("Starting database seeding...")
        
        # Check if already seeded to avoid duplicates
        existing_alumni = User.query.filter_by(role='alumni').count()
        if existing_alumni > 0:
            print(f"Found {existing_alumni} existing alumni. Wiping old seed data...")
            # Delete non-admin users (which cascades to profiles, jobs, events, etc.)
            users_to_delete = User.query.filter(User.role != 'admin').all()
            for u in users_to_delete:
                db.session.delete(u)
            db.session.commit()
            print("Old data wiped.")

        # Ensure Admin exists
        admin = User.query.filter_by(email='admin@aringaranna.edu').first()
        if not admin:
            admin = User(
                name='System Admin',
                email='admin@aringaranna.edu',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                status='Approved'
            )
            db.session.add(admin)
            db.session.commit()

        # 1. Seed Alumni Users
        print("Seeding alumni...")
        alumni_data = [
            {"name": "Priya Sharma", "email": "priya@example.com", "batch": "2018-2021", "dept": "Computer Science", "company": "Google", "role": "Software Engineer", "location": "Bangalore, India", "skills": "Python, React, Cloud"},
            {"name": "Rahul Verma", "email": "rahul@example.com", "batch": "2015-2018", "dept": "Commerce (B.Com)", "company": "Deloitte", "role": "Financial Analyst", "location": "Mumbai, India", "skills": "Excel, Financial Modeling"},
            {"name": "Anita Desai", "email": "anita@example.com", "batch": "2019-2022", "dept": "English", "company": "Penguin Random House", "role": "Editor", "location": "New Delhi, India", "skills": "Copywriting, Editing, SEO"},
            {"name": "Vikram Singh", "email": "vikram@example.com", "batch": "2016-2019", "dept": "Physics", "company": "ISRO", "role": "Research Scientist", "location": "Trivandrum, India", "skills": "Data Analysis, Matlab, Quantum Mechanics"},
            {"name": "Sneha Reddy", "email": "sneha@example.com", "batch": "2020-2023", "dept": "Business Administration (BBA)", "company": "Amazon", "role": "Product Manager", "location": "Hyderabad, India", "skills": "Agile, Jira, Strategy"},
        ]
        
        users = []
        for data in alumni_data:
            user = User(
                name=data['name'],
                email=data['email'],
                password_hash=generate_password_hash('Password@123'),
                role='alumni',
                status='Approved'  # Automatically approved for seeding
            )
            db.session.add(user)
            db.session.flush() # Get user ID
            
            profile = Profile(
                user_id=user.id,
                batch=data['batch'],
                department=data['dept'],
                company=data['company'],
                designation=data['role'],
                location=data['location'],
                skills=data['skills'],
                bio=f"Passionate {data['role']} working at {data['company']}. Always open to mentoring current students."
            )
            db.session.add(profile)
            users.append(user)
            
        db.session.commit()

        # 2. Seed Jobs
        print("Seeding jobs...")
        jobs_data = [
            {"title": "Frontend Developer", "desc": "Looking for a React developer with 2+ years of experience. Remote friendly.", "company": "Google", "location": "Bangalore / Remote", "poster": users[0]},
            {"title": "Investment Banking Analyst", "desc": "Join our fast-paced IB division. Requires strong financial modeling skills.", "company": "Deloitte", "location": "Mumbai", "poster": users[1]},
            {"title": "Content Writer", "desc": "Creative content writer needed for our new digital publication.", "company": "Penguin Random House", "location": "New Delhi", "poster": users[2]}
        ]
        
        for j in jobs_data:
            job = Job(
                title=j['title'],
                description=j['desc'],
                company=j['company'],
                location=j['location'],
                posted_by=j['poster'].id,
                status='Open'
            )
            db.session.add(job)

        # 3. Seed Events
        print("Seeding events...")
        events_data = [
            {"title": "Annual Global Alumni Meet 2027", "desc": "Join us for the biggest networking event of the year! Food, drinks, and keynote speakers.", "date": datetime.now() + timedelta(days=45), "location": "College Main Auditorium"},
            {"title": "Tech Talk: AI in 2027", "desc": "An interactive session on the future of AI and LLMs in enterprise.", "date": datetime.now() + timedelta(days=15), "location": "Virtual (Zoom)"},
            {"title": "Finance Career Fair", "desc": "Connect with top recruiters from banking and consulting firms.", "date": datetime.now() + timedelta(days=30), "location": "Campus Convention Center"}
        ]
        
        for e in events_data:
            event = Event(
                title=e['title'],
                description=e['desc'],
                date=e['date'].date(),
                time=datetime.strptime('18:00', '%H:%M').time(),
                location=e['location'],
                created_by=admin.id
            )
            db.session.add(event)

        # 4. Seed Announcements
        print("Seeding announcements...")
        announcements = [
            {"title": "New Mentorship Program Launched", "content": "We are thrilled to announce the launch of our global alumni mentorship program. Sign up today!", "type": "News", "poster": admin.id},
            {"title": "Campus Renovation Complete", "content": "The new science block is fully operational. Alumni are welcome to visit during the weekend.", "type": "Notice", "poster": admin.id},
            {"title": "Startup Pitch Competition", "content": "Alumni founders can pitch their startups to seed investors next month.", "type": "Event", "poster": admin.id}
        ]
        
        for a in announcements:
            announcement = Announcement(
                title=a['title'],
                content=a['content'],
                type=a['type'],
                posted_by=a['poster']
            )
            db.session.add(announcement)
            
        # 5. Seed Feedback
        print("Seeding feedback...")
        fb = Feedback(
            user_id=users[4].id,
            subject="Great new UI!",
            message="I just love the new glassmorphism design. It feels so premium and easy to use."
        )
        db.session.add(fb)

        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
