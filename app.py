from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.alumni import alumni_bp
    from routes.public import public_bp
    from routes.events import events_bp
    from routes.jobs import jobs_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(alumni_bp, url_prefix='/alumni')
    app.register_blueprint(events_bp)
    app.register_blueprint(jobs_bp)

    with app.app_context():
        db.create_all()
        from models import User
        if not User.query.first():
            from seed_db import seed_database
            seed_database(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
