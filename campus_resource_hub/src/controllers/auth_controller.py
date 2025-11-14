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
        try:
            # Find user by email
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user:
                flash('Invalid email or password. Please try again.', 'danger')
                return render_template('login.html', form=form)
            
            # Check if user has a password hash
            if not user.password_hash:
                flash('Account error: No password set. Please contact an administrator or reset your password.', 'danger')
                return render_template('login.html', form=form)
            
            # Check if user is suspended
            if user.is_suspended:
                flash(f'Your account has been suspended. Reason: {user.suspension_reason or "No reason provided"}', 'danger')
                return render_template('login.html', form=form)
            
            # Check if user is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('login.html', form=form)
            
            # Check if password is correct
            try:
                password_valid = bcrypt.check_password_hash(user.password_hash, form.password.data)
            except Exception as e:
                # Log the error for debugging
                import logging
                logging.error(f"Password check error: {str(e)}")
                flash('Authentication error. Please try again.', 'danger')
                return render_template('login.html', form=form)
            
            if password_valid:
                # Log the user in (remember me checkbox is hidden, so always False)
                login_user(user, remember=False)
                flash(f'Welcome back, {user.first_name or user.username}!', 'success')
                
                # Redirect to dashboard or next page
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.error(f"Login error: {str(e)}", exc_info=True)
            flash('An error occurred during login. Please try again.', 'danger')
    elif request.method == 'POST':
        # Form validation failed
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
        else:
            flash('Please fill in all required fields.', 'danger')
    
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
            role=form.role.data,  # Use selected role from form
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