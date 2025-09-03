from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

# Create blueprint
bp = Blueprint('admin', __name__)

# Import models after creating the blueprint to avoid circular imports
from ..models import User, db

@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get all users except the current admin
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin/dashboard.html', users=users)

@bp.route('/user/toggle/<int:user_id>')
@login_required
def toggle_user(user_id):
    if user_id == current_user.id:
        flash('You cannot modify your own account status.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/user/make_admin/<int:user_id>')
@login_required
def make_admin(user_id):
    if user_id == current_user.id:
        flash('You cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    
    flash(f'User {user.username} has been granted admin privileges.', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/user/remove_admin/<int:user_id>')
@login_required
def remove_admin(user_id):
    if user_id == current_user.id:
        flash('You cannot remove your own admin privileges.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.is_admin = False
    db.session.commit()
    
    flash(f'Admin privileges have been removed from {user.username}.', 'success')
    return redirect(url_for('admin.dashboard'))

@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.dashboard'))
