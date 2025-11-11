# AI Contribution: User profile controller
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db, bcrypt
from ..models.user import User
from ..forms import ProfileForm, PasswordChangeForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view_profile():
    return render_template('profile/view.html')

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check if username is taken by someone else
        if form.username.data != current_user.username:
            existing = User.query.filter_by(username=form.username.data).first()
            if existing:
                flash('Username is already taken.', 'danger')
                return render_template('profile/edit.html', form=form)
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.department = form.department.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.view_profile'))
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('profile/password.html', form=form)
        current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('profile.view_profile'))
    return render_template('profile/password.html', form=form)
