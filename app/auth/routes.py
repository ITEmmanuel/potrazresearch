from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create blueprint
bp = Blueprint('auth', __name__)

# Import models and forms after creating the blueprint to avoid circular imports
from ..models import User, db
from ..forms import LoginForm, RegistrationForm

# Import login_manager from the extensions module
from ..extensions import login_manager

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        flash('You have been logged in!', 'success')
        return redirect(next_page or url_for('main.dashboard'))
        
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter((User.email == form.email.data) | 
                                        (User.username == form.username.data)).first()
        if existing_user:
            if existing_user.email == form.email.data:
                flash('Email already registered', 'danger')
            else:
                flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))
            
        # Create new user (initially inactive)
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_active=False  # Admin needs to activate
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! An admin will review your account shortly.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.', 'warning')
    return redirect(url_for('auth.login', next=request.url))
