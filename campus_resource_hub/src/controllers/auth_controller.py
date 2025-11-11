# AI Contribution: Generated initial scaffold, verified by team.
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from ..forms import LoginForm, RegistrationForm
from ..extensions import bcrypt, db
from ..models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('login.html', form=form)
            
            # Log the user in
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.first_name or user.username}!', 'success')
            
            # Redirect to dashboard or next page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('An account with this email already exists. Please use a different email or log in.', 'danger')
            return render_template('register.html', form=form)
        
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('This username is already taken. Please choose a different username.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            first_name=form.first_name.data if form.first_name.data else None,
            last_name=form.last_name.data if form.last_name.data else None,
            department=form.department.data if form.department.data else None,
            role='student',  # Default role for new registrations
            is_active=True,
            is_suspended=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in automatically
        login_user(user)
        flash(f'Account created successfully! Welcome, {user.first_name or user.username}!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))