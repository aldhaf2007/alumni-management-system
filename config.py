import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-for-alumni-portal'
    # Strictly use MySQL database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://alumni_user:alumni_pass@localhost/alumni_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads/resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB limit
