import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-for-alumni-portal'
    # Use MySQL if configured, otherwise fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///alumni.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads/resumes')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB limit
