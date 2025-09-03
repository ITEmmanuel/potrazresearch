import os
from datetime import timedelta

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration
    @staticmethod
    def get_database_uri():
        # Priority: Environment variable > MySQL > SQLite fallback
        if os.environ.get('DATABASE_URL'):
            return os.environ.get('DATABASE_URL')
        
        # MySQL configuration
        mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
        mysql_port = os.environ.get('MYSQL_PORT', '3306')
        mysql_user = os.environ.get('MYSQL_USER', 'root')
        mysql_password = os.environ.get('MYSQL_PASSWORD', '')
        mysql_database = os.environ.get('MYSQL_DATABASE', 'potplag')
        
        # If MySQL credentials are provided, use MySQL
        if mysql_user and mysql_database and mysql_password:
            # Use PyMySQL as the MySQL driver
            return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"
        
        # Fallback to SQLite for development
        return 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    DOWNLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Plagiarism checker settings
    CSV_OUTPUT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'results.csv')
    
    # Admin credentials
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'  # Change this in production
    
    # Flask-Login settings
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    
    # Create upload and download directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Email configuration (for password reset, etc.)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Admin configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    
    # Application settings
    DOCUMENTS_PER_PAGE = 10
    
    # Plagiarism checker settings
    PLAGIARISM_THRESHOLD = 20  # Percentage
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
