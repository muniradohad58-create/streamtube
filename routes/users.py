from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Video

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if username and username != current_user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('Username already taken.', 'danger')
                return redirect(url_for('users.profile'))
            current_user.username = username

        if new_password:
            if not current_password or not current_user.check_password(current_password):
                flash('Incorrect current password.', 'danger')
                return redirect(url_for('users.profile'))
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.profile'))

    user_videos = Video.query.filter_by(user_id=current_user.id).order_by(Video.created_at.desc()).all()
    return render_template('users/profile.html', user_videos=user_videos)