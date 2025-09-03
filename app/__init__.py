import os
from flask import Flask
from config import Config
from datetime import datetime

# Import extensions
from .extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload and download directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_DIR'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # Register blueprints
    from .auth.routes import bp as auth_bp
    from .main.routes import bp as main_bp
    from .admin.routes import bp as admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Import models here to avoid circular imports
    from .models import User, Document

    # Add template filters
    from .utils.document_utils import file_modified_time, extract_number
    app.jinja_env.filters['file_modified_time'] = file_modified_time
    app.jinja_env.filters['extract_number'] = extract_number

    def filesizeformat(value):
        try:
            value = int(value or 0)
        except (TypeError, ValueError):
            value = 0
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if value < 1024.0 or unit == 'TB':
                return f"{value:.0f} {unit}" if unit == 'B' else f"{value:.2f} {unit}"
            value /= 1024.0
        return f"{value:.2f} TB"

    app.jinja_env.filters['filesizeformat'] = filesizeformat

    # Inject current time into templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_email = app.config.get('ADMIN_EMAIL')
        admin_password = app.config.get('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(
                    username='admin',
                    email=admin_email,
                    is_admin=True,
                    is_active=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()

    return app

from app import models
