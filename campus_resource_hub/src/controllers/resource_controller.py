# AI Contribution: Generated resource controller with search, view, and category features.
from flask import Blueprint, render_template, request, current_app, abort, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from ..models.resource import Resource
from ..models.booking import Booking
from ..models.waitlist import Waitlist
from ..models.review import Review
from ..models.resource_image import ResourceImage
from ..forms import BookingForm, WaitlistForm, ReviewForm
from sqlalchemy import or_, and_, func
from ..extensions import db
from ..data_access import ResourceDAO, BookingDAO, WaitlistDAO, ReviewDAO

resource_bp = Blueprint('resources', __name__, url_prefix='/resources')

# Initialize DAOs
resource_dao = ResourceDAO()
booking_dao = BookingDAO()
waitlist_dao = WaitlistDAO()
review_dao = ReviewDAO()

def get_rating_badges():
    """Calculate top 3 and lowest rated resource IDs for badges.
    Returns tuple: (top_rated_ids list, lowest_rated_id or None)
    Only includes resources that have reviews."""
    # Get all published resources with reviews
    all_published_resources = Resource.query.filter(Resource.status == 'published').all()
    resources_with_reviews = [r for r in all_published_resources if r.review_count() > 0]
    
    if not resources_with_reviews:
        return ([], None)
    
    # Sort by average rating (highest first)
    resources_with_reviews_sorted = sorted(resources_with_reviews, key=lambda r: r.average_rating(), reverse=True)
    
    # Top 3 rated resources (or all if fewer than 3)
    # Only show lowest rated badge if there are at least 2 resources (so there's a comparison)
    top_rated_ids = [r.id for r in resources_with_reviews_sorted[:3]]
    lowest_rated_id = resources_with_reviews_sorted[-1].id if len(resources_with_reviews_sorted) >= 2 else None
    
    return (top_rated_ids, lowest_rated_id)

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
    max_order = db.session.query(func.max(ResourceImage.display_order)).filter_by(resource_id=resource_id).scalar() or 0
    
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

def staff_or_admin_required(f):
    """Decorator to require staff or admin role."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'staff' and current_user.role != 'admin'):
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@resource_bp.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    min_capacity = request.args.get('min_capacity', type=int)
    availability_start = request.args.get('availability_start', '')
    availability_end = request.args.get('availability_end', '')
    sort_by = request.args.get('sort', 'title')  # title, recent, most_booked, top_rated
    
    resources = Resource.query.filter(Resource.status == 'published')
    
    # Keyword search
    if query:
        resources = resources.filter(or_(
            Resource.title.ilike(f'%{query}%'),
            Resource.description.ilike(f'%{query}%')
        ))
    
    # Category filter
    if category:
        resources = resources.filter(Resource.category == category)
    
    # Location filter
    if location:
        resources = resources.filter(Resource.location.ilike(f'%{location}%'))
    
    # Capacity filter (minimum capacity)
    if min_capacity:
        resources = resources.filter(Resource.capacity >= min_capacity)
    
    # Availability date/time filter
    if availability_start and availability_end:
        try:
            start_dt = datetime.strptime(availability_start, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(availability_end, '%Y-%m-%dT%H:%M')
            
            # Get all resources with bookings during this time period
            resources_with_bookings = db.session.query(
                Booking.resource_id,
                func.count(Booking.id).label('booking_count')
            ).filter(
                Booking.status.in_(['pending', 'active']),
                or_(
                    and_(Booking.start_date <= start_dt, Booking.end_date > start_dt),
                    and_(Booking.start_date < end_dt, Booking.end_date >= end_dt),
                    and_(Booking.start_date >= start_dt, Booking.end_date <= end_dt)
                )
            ).group_by(Booking.resource_id).all()
            
            # Determine which resources are unavailable
            unavailable_ids = []
            for resource_id, booking_count in resources_with_bookings:
                resource = Resource.query.get(resource_id)
                if resource and resource.capacity:
                    # Only filter out if resource has capacity and it's been reached
                    if booking_count >= resource.capacity:
                        unavailable_ids.append(resource_id)
                # Resources without capacity are considered unlimited and remain available
            
            # Exclude unavailable resources
            if unavailable_ids:
                resources = resources.filter(~Resource.id.in_(unavailable_ids))
        except ValueError:
            # Invalid date format, ignore availability filter
            pass
    
    # Get all resources before sorting (for calculating stats)
    all_resources = resources.all()
    
    # Eager load images for each resource
    for resource in all_resources:
        resource.images = ResourceImage.query.filter_by(resource_id=resource.id).order_by(ResourceImage.display_order).all()
    
    # Apply sorting
    if sort_by == 'recent':
        resources = sorted(all_resources, key=lambda r: r.created_at, reverse=True)
    elif sort_by == 'most_booked':
        # Sort by booking count (most booked first)
        resources = sorted(all_resources, key=lambda r: r.bookings.filter(
            Booking.status.in_(['active', 'completed'])
        ).count(), reverse=True)
    elif sort_by == 'top_rated':
        # Sort by average rating (highest first)
        resources = sorted(all_resources, key=lambda r: r.average_rating(), reverse=True)
    else:  # default: title
        resources = sorted(all_resources, key=lambda r: r.title)
    
    # Get distinct values for filters
    categories = Resource.query.filter(Resource.status == 'published').with_entities(Resource.category).distinct().all()
    locations = Resource.query.filter(
        Resource.status == 'published',
        Resource.location.isnot(None),
        Resource.location != ''
    ).with_entities(Resource.location).distinct().all()
    
    # Calculate top-rated and lowest-rated badges
    top_rated_ids, lowest_rated_id = get_rating_badges()
    
    return render_template('resources/search.html', 
                         resources=resources,
                         query=query,
                         selected_category=category,
                         categories=categories,
                         location=location,
                         locations=locations,
                         min_capacity=min_capacity,
                         availability_start=availability_start,
                         availability_end=availability_end,
                         sort_by=sort_by,
                         top_rated_ids=top_rated_ids,
                         lowest_rated_id=lowest_rated_id)

@resource_bp.route('/<int:id>')
def view(id):
    resource = Resource.query.get_or_404(id)
    
    # Check if resource is published - if not, only admins can view it
    if resource.status != 'published':
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(404)
    
    # Get page number for reviews pagination
    page = request.args.get('page', 1, type=int)
    
    # Check if the user has any active bookings for this resource
    user_bookings = []
    user_waitlist = None
    user_review = None
    if current_user.is_authenticated:
        # Get all active bookings for this user and resource (allows multiple bookings)
        user_bookings = Booking.query.filter_by(
            user_id=current_user.id,
            resource_id=resource.id,
            status='active'
        ).order_by(Booking.start_date.asc()).all()
        user_waitlist = Waitlist.query.filter_by(
            user_id=current_user.id,
            resource_id=resource.id,
            status='pending'
        ).first()
        user_review = Review.query.filter_by(
            user_id=current_user.id,
            resource_id=resource.id
        ).first()
    
    # Get average rating and review count
    avg_rating = resource.average_rating()
    rating_percentage = resource.rating_percentage()
    review_count = resource.review_count()
    
    # Get paginated reviews (10 per page, ordered by most recent first) - exclude hidden reviews
    reviews_pagination = Review.query.filter_by(
        resource_id=resource.id,
        is_hidden=False
    ).order_by(Review.created_at.desc()).paginate(
        page=page, 
        per_page=10, 
        error_out=False
    )
    
    # Get all images for this resource, ordered by display_order
    resource_images = ResourceImage.query.filter_by(
        resource_id=resource.id
    ).order_by(ResourceImage.display_order).all()
    
    # Calculate top-rated and lowest-rated badges
    top_rated_ids, lowest_rated_id = get_rating_badges()
    
    return render_template('resources/view.html', 
                         resource=resource,
                         user_bookings=user_bookings,
                         user_waitlist=user_waitlist,
                         user_review=user_review,
                         avg_rating=avg_rating,
                         rating_percentage=rating_percentage,
                         review_count=review_count,
                         reviews_pagination=reviews_pagination,
                         reviews=reviews_pagination.items,
                         resource_images=resource_images,
                         top_rated_ids=top_rated_ids,
                         lowest_rated_id=lowest_rated_id)

@resource_bp.route('/category/<category>')
def by_category(category):
    resources = resource_dao.get_by_category(category)
    if not resources:
        abort(404)
    
    # Calculate top-rated and lowest-rated badges
    top_rated_ids, lowest_rated_id = get_rating_badges()
    
    return render_template('resources/by_category.html',
                         category=category,
                         resources=resources,
                         top_rated_ids=top_rated_ids,
                         lowest_rated_id=lowest_rated_id)

def check_time_conflict(resource_id, start_date, end_date, exclude_booking_id=None):
    """Check if there are any conflicting bookings for the given time period using DAL."""
    return booking_dao.check_conflict(resource_id, start_date, end_date, exclude_id=exclude_booking_id)

def check_capacity(resource_id, start_date, end_date):
    """Check if resource capacity is reached during the time period using DAL."""
    resource = resource_dao.get_by_id(resource_id)
    if not resource or not resource.capacity:
        return False
    
    # Get bookings in the time range using DAL
    bookings_in_range = booking_dao.get_by_date_range(start_date, end_date)
    # Filter for this resource and active/pending status
    active_bookings = [b for b in bookings_in_range 
                      if b.resource_id == resource_id 
                      and b.status in ['pending', 'active']]
    
    return len(active_bookings) >= resource.capacity

@resource_bp.route('/<int:id>/book', methods=['GET', 'POST'])
@login_required
def book(id):
    # Check if user is suspended
    if current_user.is_suspended:
        flash('Your account has been suspended. You cannot book resources.', 'danger')
        return redirect(url_for('resources.view', id=id))
    
    resource = resource_dao.get_or_404(id)
    
    # Only published resources can be booked
    if resource.status != 'published':
        flash('This resource is not available for booking.', 'danger')
        return redirect(url_for('resources.search'))
    
    form = BookingForm()
    
    if form.validate_on_submit():
        # Get parsed datetime objects from form validation
        start_date = form.parsed_start_date
        end_date = form.parsed_end_date
        
        # Validate that end date is after start date
        if end_date <= start_date:
            flash('End date must be after start date.', 'danger')
            return render_template('resources/book.html', resource=resource, form=form)
        
        # Check if resource is available
        if not resource.is_available:
            flash('This resource is currently unavailable.', 'danger')
            return render_template('resources/book.html', resource=resource, form=form)
        
        # Check for time conflicts using DAL
        has_conflict = booking_dao.check_conflict(resource.id, start_date, end_date)
        capacity_reached = check_capacity(resource.id, start_date, end_date)
        
        if has_conflict or capacity_reached:
            # Offer waitlist option
            flash('This resource is not available during the requested time. You can join the waitlist.', 'warning')
            return render_template('resources/book.html', 
                                 resource=resource, 
                                 form=form, 
                                 show_waitlist=True,
                                 conflict_reason='time' if has_conflict else 'capacity')
        
        # Determine booking status based on resource approval requirement
        booking_status = 'pending' if resource.requires_approval else 'active'
        
        # Handle recurrence
        recurrence_type = form.recurrence_type.data if form.recurrence_type.data else None
        recurrence_end_date = None
        if recurrence_type and form.parsed_recurrence_end_date:
            recurrence_end_date = form.parsed_recurrence_end_date
        
        # Calculate booking duration
        booking_duration = end_date - start_date
        
        # Create bookings (single or recurring)
        bookings_created = []
        current_start = start_date
        parent_booking_id = None
        
        from datetime import timedelta
        import logging
        
        # Safety limit: prevent creating more than 365 bookings (1 year of daily bookings)
        MAX_RECURRING_BOOKINGS = 365
        iteration_count = 0
        
        # Use no_autoflush to prevent premature database locks during conflict checks
        while iteration_count < MAX_RECURRING_BOOKINGS:
            iteration_count += 1
            
            # Calculate current end date based on duration
            current_end = current_start + booking_duration
            
            # Stop if we've passed the recurrence end date (if set)
            if recurrence_end_date and current_start > recurrence_end_date:
                break
            
            # Check for conflicts for this occurrence (outside no_autoflush to allow queries)
            has_conflict = check_time_conflict(resource.id, current_start, current_end)
            capacity_reached = check_capacity(resource.id, current_start, current_end)
            
            # Only create booking if no conflict and capacity available
            if not has_conflict and not capacity_reached:
                # Use no_autoflush when adding to session to prevent premature locks
                with db.session.no_autoflush:
                    booking = Booking(
                        user_id=current_user.id,
                        resource_id=resource.id,
                        start_date=current_start,
                        end_date=current_end,
                        status=booking_status,
                        notes=form.notes.data if form.notes.data else None,
                        recurrence_type=recurrence_type,
                        recurrence_end_date=recurrence_end_date,
                        parent_booking_id=parent_booking_id
                    )
                    # Also set old columns for backward compatibility
                    booking.start_time = current_start
                    booking.end_time = current_end
                    db.session.add(booking)
                    bookings_created.append(booking)
                    
                    # Set first booking as parent for recurring series
                    if not parent_booking_id and recurrence_type:
                        # Flush to get the ID, but don't commit yet
                        db.session.flush()
                        parent_booking_id = booking.id
                        # Update all previously created bookings with parent ID
                        for prev_booking in bookings_created[:-1]:
                            prev_booking.parent_booking_id = parent_booking_id
            else:
                # If there's a conflict, stop creating more occurrences
                if bookings_created:
                    # Commit what we have so far
                    try:
                        db.session.commit()
                        flash(f'Created {len(bookings_created)} booking(s). Some occurrences were skipped due to conflicts or capacity.', 'warning')
                    except Exception as e:
                        logging.error(f"Error committing bookings: {str(e)}")
                        db.session.rollback()
                        flash('An error occurred while creating the bookings. Please try again.', 'danger')
                        return render_template('resources/book.html', resource=resource, form=form)
                else:
                    db.session.rollback()
                    flash('This resource is not available during the requested time. You can join the waitlist.', 'warning')
                    return render_template('resources/book.html', 
                                         resource=resource, 
                                         form=form, 
                                         show_waitlist=True,
                                         conflict_reason='time' if has_conflict else 'capacity')
                break
            
            # If no recurrence, create only one booking
            if not recurrence_type:
                break
            
            # Calculate next occurrence
            if recurrence_type == 'daily':
                current_start = current_start + timedelta(days=1)
            elif recurrence_type == 'weekly':
                current_start = current_start + timedelta(weeks=1)
            elif recurrence_type == 'monthly':
                # Add approximately one month (30 days)
                current_start = current_start + timedelta(days=30)
            else:
                break
        
        # Safety check: if we hit the limit, warn the user
        if iteration_count >= MAX_RECURRING_BOOKINGS:
            logging.warning(f"Recurring booking creation hit safety limit of {MAX_RECURRING_BOOKINGS} iterations")
            if bookings_created:
                try:
                    db.session.commit()
                    flash(f'Created {len(bookings_created)} booking(s). Recurrence was limited to prevent excessive bookings.', 'warning')
                except Exception as e:
                    logging.error(f"Error committing bookings after limit: {str(e)}")
                    db.session.rollback()
                    flash('An error occurred while creating the bookings. Please try again.', 'danger')
                    return render_template('resources/book.html', resource=resource, form=form)
            else:
                db.session.rollback()
                flash('Unable to create recurring bookings. Please try a shorter recurrence period.', 'danger')
                return render_template('resources/book.html', resource=resource, form=form)
        
        # Commit all bookings at once (only if we have bookings and haven't already committed)
        if bookings_created:
            try:
                db.session.commit()
            except Exception as e:
                logging.error(f"Error committing bookings: {str(e)}")
                db.session.rollback()
                flash('An error occurred while creating the bookings. Please try again.', 'danger')
                return render_template('resources/book.html', resource=resource, form=form)
            
            # Create notifications
            from ..utils.notifications import notify_booking_created, notify_recurring_series_created
            
            if len(bookings_created) > 1:
                # Count skipped bookings (if any were skipped)
                skipped_count = 0  # This would need to be tracked during creation
                notify_recurring_series_created(bookings_created, skipped_count)
                flash(f'Successfully created {len(bookings_created)} recurring bookings!', 'success')
            else:
                notify_booking_created(bookings_created[0])
                flash('Booking request submitted successfully!', 'success')
            return redirect(url_for('resources.view', id=id))
        else:
            # This shouldn't happen, but handle it gracefully
            db.session.rollback()
            flash('No bookings were created. Please check your booking details and try again.', 'warning')
            return render_template('resources/book.html', resource=resource, form=form)
    
    return render_template('resources/book.html', resource=resource, form=form)

@resource_bp.route('/<int:id>/bookings/json')
def bookings_json(id):
    """Return bookings for a resource as JSON for FullCalendar."""
    resource = resource_dao.get_or_404(id)
    
    # Get all bookings for this resource using DAL
    bookings = booking_dao.get_by_resource(resource.id)
    # Filter to only pending/active
    bookings = [b for b in bookings if b.status in ['pending', 'active']]
    
    # Format as FullCalendar events
    events = []
    for booking in bookings:
        events.append({
            'id': booking.id,
            'title': f"{booking.user.username} - {booking.status.title()}",
            'start': booking.start_date.isoformat() if booking.start_date else None,
            'end': booking.end_date.isoformat() if booking.end_date else None,
            'color': '#28a745' if booking.status == 'active' else '#ffc107',
            'extendedProps': {
                'user': booking.user.username,
                'status': booking.status,
                'notes': booking.notes
            }
        })
    
    return jsonify(events)

@resource_bp.route('/new', methods=['GET', 'POST'])
@login_required
@staff_or_admin_required
def create():
    """Create a new resource (staff and admin only)."""
    from ..forms import AdminResourceForm
    from ..models.user import User
    
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
            status=form.status.data if form.status.data else 'draft',
            equipment=form.equipment.data.strip() if form.equipment.data else None
        )
        db.session.add(resource)
        db.session.flush()  # Get the resource ID
        
        # Handle image uploads
        uploaded_files = request.files.getlist('images')
        if uploaded_files and any(f.filename for f in uploaded_files):
            save_uploaded_images(uploaded_files, resource.id)
        
        db.session.commit()
        flash('Resource created successfully!', 'success')
        return redirect(url_for('resources.view', id=resource.id))
    
    return render_template('resources/create.html', form=form)

@resource_bp.route('/<int:id>/review', methods=['GET', 'POST'])
@login_required
def review(id):
    """Create or edit a review for a resource."""
    resource = Resource.query.get_or_404(id)
    
    # Check if user already has a review
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        resource_id=resource.id
    ).first()
    
    form = ReviewForm()
    
    if existing_review:
        # Editing existing review
        if form.validate_on_submit():
            existing_review.rating = form.rating.data
            existing_review.review_text = form.review_text.data
            db.session.commit()
            flash('Review updated successfully!', 'success')
            return redirect(url_for('resources.view', id=resource.id))
        else:
            # Populate form with existing review data
            form.rating.data = existing_review.rating
            form.review_text.data = existing_review.review_text
    else:
        # Creating new review
        if form.validate_on_submit():
            review = Review(
                user_id=current_user.id,
                resource_id=resource.id,
                rating=form.rating.data,
                review_text=form.review_text.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('resources.view', id=resource.id))
    
    return render_template('resources/review.html', 
                         resource=resource, 
                         form=form, 
                         existing_review=existing_review)

@resource_bp.route('/<int:id>/review/delete', methods=['POST'])
@login_required
def delete_review(id):
    """Delete a user's own review."""
    resource = Resource.query.get_or_404(id)
    
    # Find the user's review
    review = Review.query.filter_by(
        user_id=current_user.id,
        resource_id=resource.id
    ).first_or_404()
    
    # Ensure the user owns this review
    if review.user_id != current_user.id:
        flash('You do not have permission to delete this review.', 'danger')
        return redirect(url_for('resources.view', id=resource.id))
    
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('resources.view', id=resource.id))

@resource_bp.route('/<int:id>/waitlist', methods=['GET', 'POST'])
@login_required
def join_waitlist(id):
    """Join waitlist for a resource."""
    # Check if user is suspended
    if current_user.is_suspended:
        flash('Your account has been suspended. You cannot join waitlists.', 'danger')
        return redirect(url_for('resources.view', id=id))
    
    resource = resource_dao.get_or_404(id)
    
    # Only published resources can have waitlists
    if resource.status != 'published':
        flash('This resource is not available for waitlist.', 'danger')
        return redirect(url_for('resources.search'))
    
    form = WaitlistForm()
    
    if form.validate_on_submit():
        start_date = form.parsed_start_date
        end_date = form.parsed_end_date
        
        if end_date <= start_date:
            flash('End date must be after start date.', 'danger')
            return render_template('resources/waitlist.html', resource=resource, form=form)
        
        # Check if user is already on waitlist for this time period using DAL
        existing = waitlist_dao.check_existing(
            current_user.id,
            resource.id,
            start_date,
            end_date
        )
        
        if existing:
            flash('You are already on the waitlist for this time period.', 'info')
            return redirect(url_for('resources.view', id=id))
        
        # Create waitlist entry using DAL
        waitlist_entry = waitlist_dao.create(
            user_id=current_user.id,
            resource_id=resource.id,
            requested_start_date=start_date,
            requested_end_date=end_date,
            notes=form.notes.data if form.notes.data else None,
            status='pending'
        )
        
        flash('You have been added to the waitlist. You will be notified when the resource becomes available.', 'success')
        return redirect(url_for('resources.view', id=id))
    
    return render_template('resources/waitlist.html', resource=resource, form=form)