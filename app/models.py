import os
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    documents = db.relationship('Document', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='processing')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Additional fields for plagiarism results
    similarity_score_value = db.Column(db.Float, default=0.0)
    ai_percentage = db.Column(db.Float, default=0.0)
    word_count = db.Column(db.Integer, default=0)
    report_path = db.Column(db.String(255), nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    # Computed/alias properties for template and route compatibility
    @property
    def filepath(self):
        return self.path

    @filepath.setter
    def filepath(self, value):
        self.path = value

    @property
    def file_size(self):
        try:
            return os.path.getsize(self.path)
        except OSError:
            return 0

    @property
    def similarity_score(self):
        return self.similarity_score_value or 0.0
    
    @similarity_score.setter
    def similarity_score(self, value):
        self.similarity_score_value = value
    
    @property
    def formatted_size(self):
        """Return human-readable file size"""
        try:
            size = self.file_size
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0 or unit == 'TB':
                    return f"{size:.0f} {unit}" if unit == 'B' else f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} TB"
        except:
            return "0 B"
    
    @property
    def file_type(self):
        """Return file extension/type"""
        try:
            return os.path.splitext(self.original_filename)[1].upper().replace('.', '')
        except:
            return 'Unknown'

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
