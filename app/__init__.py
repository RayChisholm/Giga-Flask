from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='default'):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.admin import admin_bp
    from app.tools import tools_bp

    # Import jobs blueprint (routes will be imported automatically)
    from app.jobs import jobs_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

    # Initialize Celery with Flask app context
    # Deferred to avoid circular imports during initialization
    try:
        from celery_app import init_celery
        init_celery(app)
    except Exception:
        # Celery initialization can fail during Flask CLI operations
        pass

    # Create instance folder if it doesn't exist
    import os
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
