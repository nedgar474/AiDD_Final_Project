# AI Contribution: Admin controller with full CRUD operations
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from ..models.user import User
from ..models.resource import Resource
from ..models.booking import Booking
from ..models.message import Message
from ..models.admin_log import AdminLog
from ..models.review import Review
from ..models.resource_image import ResourceImage
from ..models.waitlist import Waitlist
from ..forms import AdminUserForm, AdminResourceForm, AdminBookingForm, AdminWaitlistForm
from ..extensions import db, bcrypt
from sqlalchemy import func, and_

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def staff_or_admin_required(f):
    """Decorator to require staff or admin role."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'staff' and current_user.role != 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(action, target_table=None, details=None):
    """Helper function to log admin and staff actions."""
    if current_user.is_authenticated and (current_user.role == 'admin' or current_user.role == 'staff'):
        log = AdminLog(
            admin_id=current_user.id,
            action=action,
            target_table=target_table,
            details=details
        )
        db.session.add(log)
        db.session.commit()

def allowed_file(filename):
    """Check if file extension is allowed."""
    from flask import current_app
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'gif', 'webp'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_images(files, resource_id):
    """Save uploaded image files and create ResourceImage records."""
    from flask import current_app
    
    if not files:
        return
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Get current max display_order for this resource
    max_order = db.session.query(db.func.max(ResourceImage.display_order)).filter_by(resource_id=resource_id).scalar() or 0
    
    for idx, file in enumerate(files):
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add resource ID and timestamp to make filename unique
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
            name, ext = os.path.splitext(filename)
            unique_filename = f"resource_{resource_id}_{timestamp}_{name}{ext}"
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            
            # Create ResourceImage record
            image = ResourceImage(
                resource_id=resource_id,
                image_path=f"uploads/{unique_filename}",
                display_order=max_order + idx + 1
            )
            db.session.add(image)

@admin_bp.route('/')
@login_required
@staff_or_admin_required
def dashboard():
    """Admin dashboard with statistics."""
    stats = {
        'total_users': User.query.count() if current_user.role == 'admin' else None,
        'total_resources': Resource.query.count(),
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter_by(status='active').count(),
        'pending_bookings': Booking.query.filter_by(status='pending').count(),
        'flagged_messages': Message.query.filter_by(is_flagged=True, is_hidden=False).count() if current_user.role == 'admin' else None
    }
    return render_template('admin/dashboard.html', stats=stats)

# ========== USER MANAGEMENT ==========
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users."""
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user."""
    form = AdminUserForm()
    if form.validate_on_submit():
        # Check if email or username already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Create User')
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Create User')
        
        # Password is required when creating a new user
        if not form.password.data:
            flash('Password is required when creating a new user.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Create User')
        
        user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            department=form.department.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        db.session.add(user)
        db.session.commit()
        log_admin_action('Create user', 'users', f'Created user: {user.username} (ID: {user.id}), Email: {user.email}, Role: {user.role}')
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, title='Create User')

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Edit a user."""
    user = User.query.get_or_404(id)
    form = AdminUserForm(obj=user)
    
    if form.validate_on_submit():
        # Check if email or username is taken by another user
        existing_email = User.query.filter(User.email == form.email.data, User.id != id).first()
        existing_username = User.query.filter(User.username == form.username.data, User.id != id).first()
        
        if existing_email:
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Edit User', user=user)
        if existing_username:
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Edit User', user=user)
        
        user.email = form.email.data
        user.username = form.username.data
        if form.password.data:
            user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.department = form.department.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        db.session.commit()
        log_admin_action('Edit user', 'users', f'Edited user: {user.username} (ID: {user.id})')
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Delete a user."""
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    user_id = user.id
    db.session.delete(user)
    db.session.commit()
    log_admin_action('Delete user', 'users', f'Deleted user: {username} (ID: {user_id})')
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

# ========== RESOURCE MANAGEMENT ==========
@admin_bp.route('/resources')
@login_required
@staff_or_admin_required
def resources():
    """List all resources."""
    resources_list = Resource.query.order_by(Resource.title).all()
    return render_template('admin/resources.html', resources=resources_list)

@admin_bp.route('/resources/new', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def create_resource():
    """Create a new resource."""
    form = AdminResourceForm()
    
    # Populate owner choices
    users = User.query.order_by(User.username).all()
    form.owner_id.choices = [(0, 'None')] + [(user.id, user.username) for user in users]
    # Default to current user
    form.owner_id.data = current_user.id
    
    if form.validate_on_submit():
        resource = Resource(
            title=form.title.data,
            name=form.title.data,  # Set name to title for backward compatibility with database schema
            description=form.description.data,
            category=form.category.data,
            type=form.category.data,  # Set type to category for backward compatibility with database schema
            location=form.location.data,
            image_url=form.image_url.data,
            capacity=int(form.capacity.data) if form.capacity.data else None,
            owner_id=form.owner_id.data if form.owner_id.data and form.owner_id.data != 0 else current_user.id,
            is_available=form.is_available.data,
            is_featured=form.is_featured.data,
            requires_approval=form.requires_approval.data,
            status=form.status.data,
            equipment=form.equipment.data.strip() if form.equipment.data else None
        )
        db.session.add(resource)
        db.session.flush()  # Get the resource ID
        
        # Handle image uploads
        uploaded_files = request.files.getlist('images')
        if uploaded_files and any(f.filename for f in uploaded_files):
            save_uploaded_images(uploaded_files, resource.id)
        
        db.session.commit()
        log_admin_action('Create resource', 'resources', f'Created resource: {resource.title} (ID: {resource.id}), Category: {resource.category}')
        flash('Resource created successfully.', 'success')
        return redirect(url_for('admin.resources'))
    return render_template('admin/resource_form.html', form=form, title='Create Resource')

@admin_bp.route('/resources/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def edit_resource(id):
    """Edit a resource."""
    resource = Resource.query.get_or_404(id)
    
    # Populate owner choices first (before creating form)
    users = User.query.order_by(User.username).all()
    owner_choices = [(0, 'None')] + [(user.id, user.username) for user in users]
    
    form = AdminResourceForm(obj=resource)
    form.owner_id.choices = owner_choices
    
    if form.capacity.data:
        form.capacity.data = str(form.capacity.data)
    
    # Set current owner_id and status if they exist (only for GET requests)
    if request.method == 'GET':
        if resource.owner_id:
            form.owner_id.data = resource.owner_id
        else:
            form.owner_id.data = 0
        # Set status field
        if resource.status:
            form.status.data = resource.status
        else:
            form.status.data = 'draft'
    
    if form.validate_on_submit():
        # Get owner_id from form - handle 0 as None
        owner_id_value = form.owner_id.data
        if owner_id_value == 0 or owner_id_value is None:
            owner_id_value = None
        else:
            owner_id_value = int(owner_id_value)
        
        resource.title = form.title.data
        resource.name = form.title.data  # Update name to match title for backward compatibility
        resource.description = form.description.data
        resource.category = form.category.data
        resource.type = form.category.data  # Update type to match category for backward compatibility
        resource.location = form.location.data
        resource.image_url = form.image_url.data
        resource.capacity = int(form.capacity.data) if form.capacity.data else None
        resource.owner_id = owner_id_value
        resource.is_available = form.is_available.data
        resource.is_featured = form.is_featured.data
        resource.requires_approval = form.requires_approval.data
        resource.status = form.status.data
        resource.equipment = form.equipment.data.strip() if form.equipment.data else None
        
        # Handle new image uploads
        uploaded_files = request.files.getlist('images')
        if uploaded_files and any(f.filename for f in uploaded_files):
            save_uploaded_images(uploaded_files, resource.id)
        
        db.session.commit()
        log_admin_action('Edit resource', 'resources', f'Edited resource: {resource.title} (ID: {resource.id})')
        flash('Resource updated successfully.', 'success')
        return redirect(url_for('admin.resources'))
    
    return render_template('admin/resource_form.html', form=form, title='Edit Resource', resource=resource)

@admin_bp.route('/resources/<int:id>/delete', methods=['POST'])
@login_required
@staff_or_admin_required
def delete_resource(id):
    """Delete a resource."""
    resource = Resource.query.get_or_404(id)
    resource_title = resource.title
    resource_id = resource.id
    db.session.delete(resource)
    db.session.commit()
    log_admin_action('Delete resource', 'resources', f'Deleted resource: {resource_title} (ID: {resource_id})')
    flash('Resource deleted successfully.', 'success')
    return redirect(url_for('admin.resources'))

# ========== BOOKING MANAGEMENT ==========
@admin_bp.route('/bookings')
@login_required
@staff_or_admin_required
def bookings():
    """List all bookings."""
    # Use fresh query to ensure we get latest data
    bookings_list = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings_list)

@admin_bp.route('/bookings/new', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def create_booking():
    """Create a new booking."""
    form = AdminBookingForm()
    # Populate dropdown choices
    form.user_id.choices = [(u.id, f"{u.username} ({u.email})") for u in User.query.order_by(User.username).all()]
    form.resource_id.choices = [(r.id, f"{r.title} - {r.category}") for r in Resource.query.order_by(Resource.title).all()]
    
    if form.validate_on_submit():
        if form.parsed_end_date <= form.parsed_start_date:
            flash('End date must be after start date.', 'danger')
            return render_template('admin/booking_form.html', form=form, title='Create Booking')
        
        booking = Booking(
            user_id=form.user_id.data,
            resource_id=form.resource_id.data,
            start_date=form.parsed_start_date,
            end_date=form.parsed_end_date,
            status=form.status.data,
            notes=form.notes.data
        )
        # Also set old columns for backward compatibility with existing database schema
        booking.start_time = form.parsed_start_date
        booking.end_time = form.parsed_end_date
        db.session.add(booking)
        db.session.commit()
        log_admin_action('Create booking', 'bookings', f'Created booking (ID: {booking.id}) for user ID: {booking.user_id}, resource ID: {booking.resource_id}')
        flash('Booking created successfully.', 'success')
        return redirect(url_for('admin.bookings'))
    return render_template('admin/booking_form.html', form=form, title='Create Booking')

@admin_bp.route('/bookings/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def edit_booking(id):
    """Edit a booking."""
    booking = Booking.query.get_or_404(id)
    form = AdminBookingForm()
    
    # Populate dropdown choices FIRST (before setting data) - ALWAYS do this
    form.user_id.choices = [(u.id, f"{u.username} ({u.email})") for u in User.query.order_by(User.username).all()]
    form.resource_id.choices = [(r.id, f"{r.title} - {r.category}") for r in Resource.query.order_by(Resource.title).all()]
    
    if form.validate_on_submit():
        # Form submitted and validated - update the booking
        if form.parsed_end_date <= form.parsed_start_date:
            flash('End date must be after start date.', 'danger')
            # Re-populate form data for display
            if booking.start_date:
                form.start_date.data = booking.start_date.strftime('%Y-%m-%dT%H:%M')
            if booking.end_date:
                form.end_date.data = booking.end_date.strftime('%Y-%m-%dT%H:%M')
            form.user_id.data = booking.user_id
            form.resource_id.data = booking.resource_id
            valid_statuses = ['pending', 'active', 'completed', 'cancelled']
            booking_status = booking.status if booking.status in valid_statuses else 'pending'
            form.status.data = booking_status
            form.notes.data = booking.notes
            # Populate recurrence fields
            form.recurrence_type.data = booking.recurrence_type if booking.recurrence_type else ''
            if booking.recurrence_end_date:
                form.recurrence_end_date.data = booking.recurrence_end_date.strftime('%Y-%m-%dT%H:%M')
            return render_template('admin/booking_form.html', form=form, title='Edit Booking', booking=booking)
        
        # Store old status for comparison
        old_status = booking.status
        
        # Update booking fields
        booking.user_id = form.user_id.data
        booking.resource_id = form.resource_id.data
        booking.start_date = form.parsed_start_date
        booking.end_date = form.parsed_end_date
        # Also update old columns for backward compatibility
        booking.start_time = form.parsed_start_date
        booking.end_time = form.parsed_end_date
        booking.status = form.status.data
        booking.notes = form.notes.data
        
        # Update recurrence fields
        recurrence_type = form.recurrence_type.data if form.recurrence_type.data else None
        booking.recurrence_type = recurrence_type
        if recurrence_type and form.parsed_recurrence_end_date:
            booking.recurrence_end_date = form.parsed_recurrence_end_date
        elif not recurrence_type:
            booking.recurrence_end_date = None
        
        try:
            db.session.commit()
            # Refresh the booking object to ensure we have the latest data
            db.session.refresh(booking)
            
            # Create notifications for status changes
            from ..utils.notifications import notify_booking_approved, notify_booking_rejected, notify_booking_modified
            
            if old_status != booking.status:
                if old_status == 'pending' and booking.status == 'active':
                    notify_booking_approved(booking)
                elif old_status == 'pending' and booking.status == 'cancelled':
                    notify_booking_rejected(booking)
                else:
                    # Other status changes (modified)
                    changes = [f"Status changed from {old_status} to {booking.status}"]
                    notify_booking_modified(booking, changes)
            
            log_admin_action('Edit booking', 'bookings', f'Edited booking (ID: {booking.id}), Status changed from {old_status} to {booking.status}')
            flash(f'Booking updated successfully. Status changed from {old_status} to {booking.status}', 'success')
            return redirect(url_for('admin.bookings'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating booking: {str(e)}', 'danger')
            # Re-populate form data for display
            if booking.start_date:
                form.start_date.data = booking.start_date.strftime('%Y-%m-%dT%H:%M')
            if booking.end_date:
                form.end_date.data = booking.end_date.strftime('%Y-%m-%dT%H:%M')
            form.user_id.data = booking.user_id
            form.resource_id.data = booking.resource_id
            valid_statuses = ['pending', 'active', 'completed', 'cancelled']
            booking_status = booking.status if booking.status in valid_statuses else 'pending'
            form.status.data = booking_status
            form.notes.data = booking.notes
            # Populate recurrence fields
            form.recurrence_type.data = booking.recurrence_type if booking.recurrence_type else ''
            if booking.recurrence_end_date:
                form.recurrence_end_date.data = booking.recurrence_end_date.strftime('%Y-%m-%dT%H:%M')
            return render_template('admin/booking_form.html', form=form, title='Edit Booking', booking=booking)
    
    # GET request or form not validated - populate form with booking data
    if booking.start_date:
        form.start_date.data = booking.start_date.strftime('%Y-%m-%dT%H:%M')
    if booking.end_date:
        form.end_date.data = booking.end_date.strftime('%Y-%m-%dT%H:%M')
    
    form.user_id.data = booking.user_id
    form.resource_id.data = booking.resource_id
    
    # Handle status - ensure it's a valid choice, default to 'pending' if not
    valid_statuses = ['pending', 'active', 'completed', 'cancelled']
    booking_status = booking.status if booking.status in valid_statuses else 'pending'
    form.status.data = booking_status
    
    form.notes.data = booking.notes
    
    # Populate recurrence fields
    form.recurrence_type.data = booking.recurrence_type if booking.recurrence_type else ''
    if booking.recurrence_end_date:
        form.recurrence_end_date.data = booking.recurrence_end_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('admin/booking_form.html', form=form, title='Edit Booking', booking=booking)

@admin_bp.route('/bookings/<int:id>/delete', methods=['POST'])
@login_required
@staff_or_admin_required
def delete_booking(id):
    """Delete a booking."""
    booking = Booking.query.get_or_404(id)
    booking_id = booking.id
    
    # Create notification before deleting
    from ..utils.notifications import notify_booking_cancelled
    notify_booking_cancelled(booking, cancelled_by_user=False)
    
    db.session.delete(booking)
    db.session.commit()
    log_admin_action('Delete booking', 'bookings', f'Deleted booking (ID: {booking_id})')
    flash('Booking deleted successfully.', 'success')
    return redirect(url_for('admin.bookings'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Reports page with analytics and charts."""
    from collections import defaultdict
    
    # 1. Active Resources by Status
    resources_by_status = db.session.query(
        Resource.status,
        func.count(Resource.id).label('count')
    ).group_by(Resource.status).all()
    # Format status labels (capitalize first letter)
    resources_status_data = {
        'labels': [status.capitalize() if status else 'Unknown' for status, count in resources_by_status],
        'counts': [count for status, count in resources_by_status]
    }
    
    # 2. Total Bookings (Last 30 Days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    bookings_by_date = db.session.query(
        func.date(Booking.created_at).label('date'),
        func.count(Booking.id).label('count')
    ).filter(Booking.created_at >= thirty_days_ago).group_by(func.date(Booking.created_at)).order_by('date').all()
    # func.date() returns a string in SQLite (format: 'YYYY-MM-DD'), so we use it directly
    bookings_timeline_data = {
        'dates': [str(date) for date, _ in bookings_by_date],
        'counts': [count for _, count in bookings_by_date]
    }
    
    # 3. Category Utilization Summary (approved bookings per category)
    category_bookings = db.session.query(
        Resource.category,
        func.count(Booking.id).label('count')
    ).join(Booking, Resource.id == Booking.resource_id).filter(
        Booking.status.in_(['active', 'completed'])
    ).group_by(Resource.category).all()
    category_utilization_data = {
        'categories': [cat for cat, _ in category_bookings],
        'counts': [count for _, count in category_bookings]
    }
    
    # 4. Average Booking Duration per Category
    booking_durations = db.session.query(
        Resource.category,
        func.avg(
            func.julianday(Booking.end_date) - func.julianday(Booking.start_date)
        ).label('avg_days')
    ).join(Booking, Resource.id == Booking.resource_id).filter(
        Booking.status.in_(['active', 'completed']),
        Booking.start_date.isnot(None),
        Booking.end_date.isnot(None)
    ).group_by(Resource.category).all()
    avg_duration_data = {
        'categories': [cat for cat, _ in booking_durations],
        'avg_days': [round(avg_days if avg_days else 0, 2) for _, avg_days in booking_durations]
    }
    
    # 5. Resource Ratings vs. Booking Volume
    resource_stats = db.session.query(
        Resource.id,
        Resource.title,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Booking.id).label('booking_count')
    ).outerjoin(Review, Resource.id == Review.resource_id).outerjoin(
        Booking, Resource.id == Booking.resource_id
    ).group_by(Resource.id, Resource.title).all()
    # Format as array of {x, y} objects for scatter plot
    ratings_vs_bookings_data = [
        {
            'x': round(avg_rating if avg_rating else 0, 2),
            'y': count
        }
        for _, _, avg_rating, count in resource_stats
    ]
    
    # 6. Bookings per User Role
    bookings_by_role = db.session.query(
        User.role,
        func.count(Booking.id).label('count')
    ).join(Booking, User.id == Booking.user_id).group_by(User.role).all()
    bookings_by_role_data = {
        'roles': [role for role, _ in bookings_by_role],
        'counts': [count for _, count in bookings_by_role]
    }
    
    # 7. Booking Status Distribution
    status_distribution = db.session.query(
        Booking.status,
        func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()
    status_distribution_data = {
        'statuses': [status for status, _ in status_distribution],
        'counts': [count for _, count in status_distribution]
    }
    
    # 8. Bookings by Department
    bookings_by_department = db.session.query(
        User.department,
        func.count(Booking.id).label('count')
    ).join(Booking, User.id == Booking.user_id).filter(
        User.department.isnot(None),
        User.department != ''
    ).group_by(User.department).all()
    bookings_by_department_data = {
        'departments': [dept if dept else 'Unknown' for dept, _ in bookings_by_department],
        'counts': [count for _, count in bookings_by_department]
    }
    
    # 9. Resource Usage by Department (bookings per department)
    resource_usage_by_dept = db.session.query(
        User.department,
        func.count(Booking.id).label('booking_count'),
        func.count(func.distinct(Booking.resource_id)).label('resource_count')
    ).join(Booking, User.id == Booking.user_id).filter(
        User.department.isnot(None),
        User.department != '',
        Booking.status.in_(['active', 'completed'])
    ).group_by(User.department).all()
    resource_usage_by_dept_data = {
        'departments': [dept if dept else 'Unknown' for dept, _, _ in resource_usage_by_dept],
        'booking_counts': [count for _, count, _ in resource_usage_by_dept],
        'resource_counts': [res_count for _, _, res_count in resource_usage_by_dept]
    }
    
    # 10. Department Utilization Trends (Last 30 Days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    dept_trends = db.session.query(
        func.date(Booking.created_at).label('date'),
        User.department,
        func.count(Booking.id).label('count')
    ).join(User, Booking.user_id == User.id).filter(
        Booking.created_at >= thirty_days_ago,
        User.department.isnot(None),
        User.department != ''
    ).group_by(func.date(Booking.created_at), User.department).order_by('date', User.department).all()
    
    # Organize by date and department
    dept_trends_by_date = defaultdict(lambda: defaultdict(int))
    all_departments = set()
    all_dates = set()
    for date, dept, count in dept_trends:
        date_str = str(date)
        dept_trends_by_date[date_str][dept] = count
        all_departments.add(dept)
        all_dates.add(date_str)
    
    # Format for Chart.js (line chart with multiple datasets)
    sorted_dates = sorted(all_dates)
    sorted_depts = sorted(all_departments)
    dept_trends_data = {
        'dates': sorted_dates,
        'departments': sorted_depts,
        'datasets': [
            {
                'label': dept,
                'data': [dept_trends_by_date[date].get(dept, 0) for date in sorted_dates]
            }
            for dept in sorted_depts
        ]
    }
    
    # 11. Department vs. Role Cross-Analysis
    dept_role_analysis = db.session.query(
        User.department,
        User.role,
        func.count(Booking.id).label('count')
    ).join(Booking, User.id == Booking.user_id).filter(
        User.department.isnot(None),
        User.department != ''
    ).group_by(User.department, User.role).all()
    
    # Organize by department and role
    dept_role_map = defaultdict(lambda: defaultdict(int))
    dept_role_departments = set()
    dept_role_roles = set()
    for dept, role, count in dept_role_analysis:
        dept_role_map[dept][role] = count
        dept_role_departments.add(dept)
        dept_role_roles.add(role)
    
    sorted_dept_role_depts = sorted(dept_role_departments)
    sorted_dept_role_roles = sorted(dept_role_roles)
    dept_role_data = {
        'departments': sorted_dept_role_depts,
        'roles': sorted_dept_role_roles,
        'datasets': [
            {
                'label': role,
                'data': [dept_role_map[dept].get(role, 0) for dept in sorted_dept_role_depts]
            }
            for role in sorted_dept_role_roles
        ]
    }
    
    return render_template('admin/reports.html',
                         resources_status_data=resources_status_data,
                         bookings_timeline_data=bookings_timeline_data,
                         category_utilization_data=category_utilization_data,
                         avg_duration_data=avg_duration_data,
                         ratings_vs_bookings_data=ratings_vs_bookings_data,
                         bookings_by_role_data=bookings_by_role_data,
                         status_distribution_data=status_distribution_data,
                         bookings_by_department_data=bookings_by_department_data,
                         resource_usage_by_dept_data=resource_usage_by_dept_data,
                         dept_trends_data=dept_trends_data,
                         dept_role_data=dept_role_data)

# ========== MESSAGE MANAGEMENT ==========
@admin_bp.route('/messages')
@login_required
@admin_required
def messages():
    """Manage messages - view flagged and all messages."""
    flagged_messages = Message.query.filter_by(is_flagged=True, is_hidden=False).order_by(Message.created_at.desc()).all()
    all_messages = Message.query.order_by(Message.created_at.desc()).limit(50).all()
    return render_template('admin/messages.html', flagged_messages=flagged_messages, all_messages=all_messages)

@admin_bp.route('/messages/<int:id>')
@login_required
@admin_required
def view_message(id):
    """View a message for admin review."""
    message = Message.query.get_or_404(id)
    return render_template('admin/message_view.html', message=message)

@admin_bp.route('/messages/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_message(id):
    """Edit a message."""
    message = Message.query.get_or_404(id)
    
    if request.method == 'POST':
        message.subject = request.form.get('subject', message.subject)
        message.body = request.form.get('body', message.body)
        db.session.commit()
        log_admin_action('Edit message', 'messages', f'Edited message (ID: {message.id}), Subject: {message.subject}')
        flash('Message updated successfully.', 'success')
        return redirect(url_for('admin.view_message', id=id))
    
    return render_template('admin/message_edit.html', message=message)

@admin_bp.route('/messages/<int:id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_message(id):
    """Hide a message."""
    message = Message.query.get_or_404(id)
    message.is_hidden = True
    db.session.commit()
    log_admin_action('Hide message', 'messages', f'Hid message (ID: {message.id}), Subject: {message.subject}')
    flash('Message hidden successfully.', 'success')
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:id>/unflag', methods=['POST'])
@login_required
@admin_required
def unflag_message(id):
    """Unflag a message."""
    message = Message.query.get_or_404(id)
    message.is_flagged = False
    message.flag_reason = None
    db.session.commit()
    log_admin_action('Unflag message', 'messages', f'Unflagged message (ID: {message.id}), Subject: {message.subject}')
    flash('Message unflagged successfully.', 'success')
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_message(id):
    """Delete a message."""
    message = Message.query.get_or_404(id)
    message_id = message.id
    message_subject = message.subject
    db.session.delete(message)
    db.session.commit()
    log_admin_action('Delete message', 'messages', f'Deleted message (ID: {message_id}), Subject: {message_subject}')
    flash('Message deleted successfully.', 'success')
    return redirect(url_for('admin.messages'))

# ========== USER SUSPENSION ==========
@admin_bp.route('/users/<int:id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(id):
    """Suspend a user."""
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot suspend your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    suspension_reason = request.form.get('suspension_reason', '')
    user.is_suspended = True
    user.suspension_reason = suspension_reason if suspension_reason else 'Suspended by administrator'
    db.session.commit()
    log_admin_action('Suspend user', 'users', f'Suspended user: {user.username} (ID: {user.id}). Reason: {suspension_reason or "No reason provided"}')
    flash(f'User {user.username} has been suspended.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:id>/unsuspend', methods=['POST'])
@login_required
@admin_required
def unsuspend_user(id):
    """Unsuspend a user."""
    user = User.query.get_or_404(id)
    user.is_suspended = False
    user.suspension_reason = None
    db.session.commit()
    log_admin_action('Unsuspend user', 'users', f'Unsuspended user: {user.username} (ID: {user.id})')
    flash(f'User {user.username} has been unsuspended.', 'success')
    return redirect(url_for('admin.users'))

# ========== ADMIN LOGS ==========
@admin_bp.route('/logs')
@login_required
@admin_required
def admin_logs():
    """View paginated admin action logs."""
    page = request.args.get('page', 1, type=int)
    logs_pagination = AdminLog.query.order_by(AdminLog.timestamp.desc()).paginate(
        page=page, 
        per_page=20, 
        error_out=False
    )
    return render_template('admin/logs.html', 
                         logs_pagination=logs_pagination,
                         logs=logs_pagination.items)

# ========== REVIEW MANAGEMENT ==========
@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    """List all reviews."""
    reviews_list = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews_list)

@admin_bp.route('/reviews/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_review(id):
    """Edit a review."""
    review = Review.query.get_or_404(id)
    from ..forms import ReviewForm
    form = ReviewForm(obj=review)
    
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.review_text = form.review_text.data
        db.session.commit()
        log_admin_action('Edit review', 'reviews', f'Edited review (ID: {review.id}) for resource ID: {review.resource_id}, Rating: {review.rating}')
        flash('Review updated successfully.', 'success')
        return redirect(url_for('admin.reviews'))
    
    return render_template('admin/review_edit.html', form=form, review=review)

@admin_bp.route('/reviews/<int:id>/hide', methods=['POST'])
@login_required
@admin_required
def hide_review(id):
    """Hide a review."""
    review = Review.query.get_or_404(id)
    review.is_hidden = True
    db.session.commit()
    log_admin_action('Hide review', 'reviews', f'Hid review (ID: {review.id}) for resource ID: {review.resource_id}')
    flash('Review hidden successfully.', 'success')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/reviews/<int:id>/unhide', methods=['POST'])
@login_required
@admin_required
def unhide_review(id):
    """Unhide a review."""
    review = Review.query.get_or_404(id)
    review.is_hidden = False
    db.session.commit()
    log_admin_action('Unhide review', 'reviews', f'Unhid review (ID: {review.id}) for resource ID: {review.resource_id}')
    flash('Review unhidden successfully.', 'success')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/reviews/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(id):
    """Delete a review."""
    review = Review.query.get_or_404(id)
    review_id = review.id
    resource_id = review.resource_id
    db.session.delete(review)
    db.session.commit()
    log_admin_action('Delete review', 'reviews', f'Deleted review (ID: {review_id}) for resource ID: {resource_id}')
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('admin.reviews'))

# Waitlist Management Routes
@admin_bp.route('/waitlists')
@login_required
@staff_or_admin_required
def waitlists():
    """List all waitlist entries."""
    waitlist_entries = Waitlist.query.order_by(Waitlist.created_at.desc()).all()
    return render_template('admin/waitlists.html', waitlists=waitlist_entries)

@admin_bp.route('/waitlists/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def edit_waitlist(id):
    """Edit a waitlist entry."""
    waitlist = Waitlist.query.get_or_404(id)
    form = AdminWaitlistForm()
    
    # Populate dropdown choices FIRST (before setting data)
    form.user_id.choices = [(u.id, f"{u.username} ({u.email})") for u in User.query.order_by(User.username).all()]
    form.resource_id.choices = [(r.id, f"{r.title} - {r.category}") for r in Resource.query.order_by(Resource.title).all()]
    
    if form.validate_on_submit():
        # Form submitted and validated - update the waitlist
        if form.parsed_end_date <= form.parsed_start_date:
            flash('End date must be after start date.', 'danger')
            # Re-populate form data for display
            if waitlist.requested_start_date:
                form.start_date.data = waitlist.requested_start_date.strftime('%Y-%m-%dT%H:%M')
            if waitlist.requested_end_date:
                form.end_date.data = waitlist.requested_end_date.strftime('%Y-%m-%dT%H:%M')
            form.user_id.data = waitlist.user_id
            form.resource_id.data = waitlist.resource_id
            form.status.data = waitlist.status
            form.notes.data = waitlist.notes
            return render_template('admin/waitlist_form.html', form=form, title='Edit Waitlist', waitlist=waitlist)
        
        # Store old status for comparison
        old_status = waitlist.status
        
        # Update waitlist fields
        waitlist.user_id = form.user_id.data
        waitlist.resource_id = form.resource_id.data
        waitlist.requested_start_date = form.parsed_start_date
        waitlist.requested_end_date = form.parsed_end_date
        waitlist.status = form.status.data
        waitlist.notes = form.notes.data
        
        # Update notified_at if status changed to 'notified'
        if form.status.data == 'notified' and old_status != 'notified':
            waitlist.notified_at = datetime.utcnow()
        elif form.status.data != 'notified':
            waitlist.notified_at = None
        
        db.session.commit()
        log_admin_action('Edit waitlist', 'waitlist', f'Edited waitlist (ID: {waitlist.id}) for user ID: {waitlist.user_id}, resource ID: {waitlist.resource_id}, status: {old_status} -> {waitlist.status}')
        flash('Waitlist entry updated successfully.', 'success')
        return redirect(url_for('admin.waitlists'))
    
    # GET request or validation failed - populate form with existing data
    if waitlist.requested_start_date:
        form.start_date.data = waitlist.requested_start_date.strftime('%Y-%m-%dT%H:%M')
    if waitlist.requested_end_date:
        form.end_date.data = waitlist.requested_end_date.strftime('%Y-%m-%dT%H:%M')
    form.user_id.data = waitlist.user_id
    form.resource_id.data = waitlist.resource_id
    form.status.data = waitlist.status
    form.notes.data = waitlist.notes
    
    return render_template('admin/waitlist_form.html', form=form, title='Edit Waitlist', waitlist=waitlist)

@admin_bp.route('/waitlists/<int:id>/delete', methods=['POST'])
@login_required
@staff_or_admin_required
def delete_waitlist(id):
    """Delete a waitlist entry."""
    waitlist = Waitlist.query.get_or_404(id)
    waitlist_id = waitlist.id
    user_id = waitlist.user_id
    resource_id = waitlist.resource_id
    db.session.delete(waitlist)
    db.session.commit()
    log_admin_action('Delete waitlist', 'waitlist', f'Deleted waitlist (ID: {waitlist_id}) for user ID: {user_id}, resource ID: {resource_id}')
    flash('Waitlist entry deleted successfully.', 'success')
    return redirect(url_for('admin.waitlists'))
