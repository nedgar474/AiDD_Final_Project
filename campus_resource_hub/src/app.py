# AI Contribution: Generated initial scaffold, verified by team.
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import configuration
from .config import config
from .extensions import db, login_manager, migrate, csrf, bcrypt

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='views/templates',
                static_folder='static')
    app.config.from_object(config[config_name])
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)

    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %I:%M %p')

    @app.template_filter('date')
    def format_date(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d')
    
    # Make csrf_token available as a template function
    @app.template_global()
    def csrf_token():
        """Generate CSRF token for templates."""
        from flask import request, session
        # Ensure we're in a request context
        if hasattr(request, 'csrf_token'):
            return request.csrf_token
        return csrf.generate_csrf()
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .controllers.main_controller import main_bp
    from .controllers.auth_controller import auth_bp
    from .controllers.resource_controller import resource_bp
    from .controllers.booking_controller import booking_bp
    from .controllers.message_controller import message_bp
    from .controllers.admin_controller import admin_bp
    from .controllers.profile_controller import profile_bp
    from .controllers.notification_controller import notification_bp
    from .ai_features.concierge import concierge_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resource_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(concierge_bp)
    
    # Import all models to ensure they're registered with SQLAlchemy
    from .models import User, Resource, Booking, Message, Waitlist, Review, AdminLog, ResourceImage, Notification, CalendarSubscription
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app