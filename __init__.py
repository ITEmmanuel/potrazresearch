from flask import Flask
from config import Config
from extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.auth import auth as auth_blueprint
    from app.main import main as main_blueprint
    from app.admin import admin as admin_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        from extensions import User
        admin = User.query.filter_by(email=app.config.get('ADMIN_EMAIL', 'admin@example.com')).first()
        if not admin:
            admin = User(
                username='admin',
                email=app.config.get('ADMIN_EMAIL', 'admin@example.com'),
                is_admin=True,
                is_active=True
            )
            admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()

    return app
