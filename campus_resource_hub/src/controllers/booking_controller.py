# AI Contribution: Generated initial scaffold, verified by team.
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from ..models.booking import Booking
from ..models.waitlist import Waitlist
from ..extensions import db, csrf
from ..data_access import BookingDAO, WaitlistDAO, CalendarSubscriptionDAO
try:
    from icalendar import Calendar, Event
    ICALENDAR_AVAILABLE = True
except ImportError as e:
    Calendar = None
    Event = None
    ICALENDAR_AVAILABLE = False
    import logging
    logging.warning(f"icalendar package not available: {e}")

booking_bp = Blueprint('booking', __name__, url_prefix='/bookings')

# Initialize DAOs
booking_dao = BookingDAO()
waitlist_dao = WaitlistDAO()
subscription_dao = CalendarSubscriptionDAO()

@booking_bp.route('/')
@login_required
def list():
    """Display user's bookings."""
    # Get all bookings for the current user using DAL
    bookings = booking_dao.get_by_user(current_user.id)
    # Get all waitlist entries for the current user using DAL
    waitlist_entries = waitlist_dao.get_by_user(current_user.id, status='pending')
    return render_template('bookings/list.html', bookings=bookings, waitlist_entries=waitlist_entries)

@booking_bp.route('/<int:id>')
@login_required
def details(id):
    """Display booking details."""
    booking = booking_dao.get_or_404(id)
    
    # Ensure the booking belongs to the current user (unless admin)
    if booking.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
    
    return render_template('bookings/details.html', booking=booking)

@booking_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel a booking."""
    booking = booking_dao.get_or_404(id)
    
    # Ensure the booking belongs to the current user
    if booking.user_id != current_user.id:
        abort(403)
    
    # Check if booking is already cancelled or completed
    if booking.status == 'cancelled':
        flash('This booking is already cancelled.', 'warning')
        return redirect(url_for('booking.details', id=id))
    
    if booking.status == 'completed':
        flash('Cannot cancel a completed booking.', 'warning')
        return redirect(url_for('booking.details', id=id))
    
    try:
        # Cancel the booking
        booking_dao.update_status(id, 'cancelled')
        
        # If this is a recurring booking, cancel all child bookings
        if booking.recurrence_type:
            # This is a parent booking - cancel all children
            child_bookings = booking_dao.get_recurring_children(id)
            for child in child_bookings:
                if child.status not in ['cancelled', 'completed']:
                    booking_dao.update_status(child.id, 'cancelled')
                    # Send notification for each cancelled child booking
                    from ..utils.notifications import notify_booking_cancelled
                    notify_booking_cancelled(child, cancelled_by_user=True)
        elif booking.parent_booking_id:
            # This is a child booking - cancel it and potentially notify about the series
            pass  # Already handled above
        
        # Send notification
        from ..utils.notifications import notify_booking_cancelled
        notify_booking_cancelled(booking, cancelled_by_user=True)
        
        flash('Booking cancelled successfully.', 'success')
        return redirect(url_for('booking.details', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while cancelling the booking: {str(e)}', 'error')
        return redirect(url_for('booking.details', id=id))

@booking_bp.route('/waitlist/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_waitlist(id):
    """Cancel a waitlist entry."""
    waitlist_entry = waitlist_dao.get_or_404(id)
    
    if waitlist_entry.user_id != current_user.id:
        abort(403)
    
    waitlist_dao.update_status(id, 'cancelled')
    flash('Waitlist entry cancelled.', 'success')
    return redirect(url_for('booking.list'))

@booking_bp.route('/calendar')
@login_required
def calendar():
    """Display personal calendar view of all user bookings."""
    return render_template('bookings/calendar.html')

@booking_bp.route('/calendar/json')
@login_required
def calendar_json():
    """Return user's bookings as JSON for FullCalendar."""
    # Get filter parameters
    status_filter = request.args.get('status', '')
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    
    # Get bookings using DAL
    if start_date and end_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            bookings = booking_dao.get_by_date_range(start_dt, end_dt, user_id=current_user.id)
        except ValueError:
            # Invalid date format, get all user bookings
            bookings = booking_dao.get_by_user(current_user.id, status=status_filter)
    else:
        bookings = booking_dao.get_by_user(current_user.id, status=status_filter)
    
    # Format as FullCalendar events
    events = []
    for booking in bookings:
        # Determine color based on status
        color_map = {
            'active': '#28a745',
            'pending': '#ffc107',
            'completed': '#17a2b8',
            'cancelled': '#dc3545'
        }
        color = color_map.get(booking.status, '#6c757d')
        
        events.append({
            'id': booking.id,
            'title': f"{booking.resource.title} - {booking.status.title()}",
            'start': booking.start_date.isoformat() if booking.start_date else None,
            'end': booking.end_date.isoformat() if booking.end_date else None,
            'color': color,
            'textColor': '#ffffff',
            'extendedProps': {
                'resource_id': booking.resource_id,
                'resource_title': booking.resource.title,
                'resource_category': booking.resource.category,
                'resource_location': booking.resource.location or '',
                'status': booking.status,
                'notes': booking.notes or 'No notes'
            }
        })
    
    return jsonify(events)

@booking_bp.route('/export/ical')
@login_required
def export_ical():
    """Export user's bookings as iCal file."""
    if not ICALENDAR_AVAILABLE:
        flash('iCal export is not available. Please install icalendar package and restart the application.', 'error')
        return redirect(url_for('booking.calendar'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Get bookings using DAL
    if start_date_str and end_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            bookings = booking_dao.get_by_date_range(start_dt, end_dt, user_id=current_user.id)
        except ValueError:
            bookings = booking_dao.get_by_user(current_user.id, status=status_filter)
    elif start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_dt = datetime.utcnow() + timedelta(days=365)  # Default to 1 year ahead
            bookings = booking_dao.get_by_date_range(start_dt, end_dt, user_id=current_user.id)
        except ValueError:
            bookings = booking_dao.get_by_user(current_user.id, status=status_filter)
    else:
        bookings = booking_dao.get_by_user(current_user.id, status=status_filter)
    
    # Create iCal calendar
    cal = Calendar()
    cal.add('prodid', '-//Campus Resource Hub//Booking Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('X-WR-CALNAME', f'{current_user.username}\'s Bookings')
    cal.add('X-WR-CALDESC', 'Bookings from Campus Resource Hub')
    cal.add('X-WR-TIMEZONE', 'UTC')
    
    # Add each booking as an event
    for booking in bookings:
        event = Event()
        event.add('uid', f'booking-{booking.id}@campus-resource-hub')
        event.add('summary', f'{booking.resource.title} - {booking.status.title()}')
        
        # Description with booking details
        description = f"Resource: {booking.resource.title}\n"
        description += f"Category: {booking.resource.category}\n"
        if booking.resource.location:
            description += f"Location: {booking.resource.location}\n"
        description += f"Status: {booking.status.title()}\n"
        if booking.notes:
            description += f"Notes: {booking.notes}\n"
        description += f"Booking ID: {booking.id}"
        
        event.add('description', description)
        
        # Start and end times (convert to UTC if needed)
        if booking.start_date:
            start_utc = booking.start_date
            if start_utc.tzinfo is None:
                start_utc = start_utc.replace(tzinfo=timezone.utc)
            event.add('dtstart', start_utc)
        
        if booking.end_date:
            end_utc = booking.end_date
            if end_utc.tzinfo is None:
                end_utc = end_utc.replace(tzinfo=timezone.utc)
            event.add('dtend', end_utc)
        
        # Location
        if booking.resource.location:
            event.add('location', booking.resource.location)
        
        # Status
        status_map = {
            'active': 'CONFIRMED',
            'pending': 'TENTATIVE',
            'completed': 'CONFIRMED',
            'cancelled': 'CANCELLED'
        }
        event.add('status', status_map.get(booking.status, 'CONFIRMED'))
        
        # Recurrence rule if applicable
        if booking.recurrence_type and booking.recurrence_end_date:
            freq_map = {
                'daily': 'DAILY',
                'weekly': 'WEEKLY',
                'monthly': 'MONTHLY'
            }
            freq = freq_map.get(booking.recurrence_type, 'WEEKLY')
            until = booking.recurrence_end_date
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            event.add('rrule', {
                'FREQ': freq,
                'UNTIL': until
            })
        
        # Last modified
        if booking.updated_at:
            last_modified = booking.updated_at
            if last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)
            event.add('last-modified', last_modified)
        elif booking.created_at:
            created = booking.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            event.add('last-modified', created)
        
        # Organizer (user)
        event.add('organizer', f'MAILTO:{current_user.email}')
        
        cal.add_component(event)
    
    # Generate iCal file
    ical_content = cal.to_ical()
    
    # Create response
    response = Response(ical_content, mimetype='text/calendar')
    response.headers['Content-Disposition'] = f'attachment; filename="bookings_{current_user.username}_{datetime.now().strftime("%Y%m%d")}.ics"'
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    
    return response

def generate_ical_calendar(user, bookings):
    """Helper function to generate iCal calendar from bookings."""
    if Calendar is None or Event is None:
        return None
    
    cal = Calendar()
    cal.add('prodid', '-//Campus Resource Hub//Booking Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('X-WR-CALNAME', f'{user.username}\'s Bookings')
    cal.add('X-WR-CALDESC', 'Bookings from Campus Resource Hub')
    cal.add('X-WR-TIMEZONE', 'UTC')
    cal.add('REFRESH-INTERVAL;VALUE=DURATION', 'PT12H')  # Refresh every 12 hours
    cal.add('X-PUBLISHED-TTL', 'PT12H')  # Publish TTL of 12 hours
    
    for booking in bookings:
        event = Event()
        event.add('uid', f'booking-{booking.id}@campus-resource-hub')
        event.add('summary', f'{booking.resource.title} - {booking.status.title()}')
        
        description = f"Resource: {booking.resource.title}\n"
        description += f"Category: {booking.resource.category}\n"
        if booking.resource.location:
            description += f"Location: {booking.resource.location}\n"
        description += f"Status: {booking.status.title()}\n"
        if booking.notes:
            description += f"Notes: {booking.notes}\n"
        description += f"Booking ID: {booking.id}"
        
        event.add('description', description)
        
        if booking.start_date:
            start_utc = booking.start_date
            if start_utc.tzinfo is None:
                start_utc = start_utc.replace(tzinfo=timezone.utc)
            event.add('dtstart', start_utc)
        
        if booking.end_date:
            end_utc = booking.end_date
            if end_utc.tzinfo is None:
                end_utc = end_utc.replace(tzinfo=timezone.utc)
            event.add('dtend', end_utc)
        
        if booking.resource.location:
            event.add('location', booking.resource.location)
        
        status_map = {
            'active': 'CONFIRMED',
            'pending': 'TENTATIVE',
            'completed': 'CONFIRMED',
            'cancelled': 'CANCELLED'
        }
        event.add('status', status_map.get(booking.status, 'CONFIRMED'))
        
        if booking.recurrence_type and booking.recurrence_end_date:
            freq_map = {
                'daily': 'DAILY',
                'weekly': 'WEEKLY',
                'monthly': 'MONTHLY'
            }
            freq = freq_map.get(booking.recurrence_type, 'WEEKLY')
            until = booking.recurrence_end_date
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            event.add('rrule', {
                'FREQ': freq,
                'UNTIL': until
            })
        
        if booking.updated_at:
            last_modified = booking.updated_at
            if last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)
            event.add('last-modified', last_modified)
        elif booking.created_at:
            created = booking.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            event.add('last-modified', created)
        
        event.add('organizer', f'MAILTO:{user.email}')
        
        cal.add_component(event)
    
    return cal

@booking_bp.route('/subscription/generate', methods=['POST'])
@csrf.exempt
@login_required
def generate_subscription():
    """Generate a new subscription token for the current user."""
    try:
        if not ICALENDAR_AVAILABLE:
            return jsonify({'success': False, 'error': 'iCal export is not available'}), 400
        
        from ..models.calendar_subscription import CalendarSubscription
        
        # Get filter parameters from request
        status_filter = request.json.get('status_filter') if request.is_json else request.form.get('status_filter')
        start_date_str = request.json.get('start_date') if request.is_json else request.form.get('start_date')
        end_date_str = request.json.get('end_date') if request.is_json else request.form.get('end_date')
        
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Create subscription token
        subscription = CalendarSubscription.create_for_user(
            user_id=current_user.id,
            status_filter=status_filter if status_filter else None,
            start_date=start_date,
            end_date=end_date
        )
        
        # Generate subscription URL
        subscription_url = url_for('booking.subscription_ical', token=subscription.token, _external=True)
        
        return jsonify({
            'success': True,
            'token': subscription.token,
            'subscription_url': subscription_url,
            'created_at': subscription.created_at.isoformat()
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error generating subscription: {error_msg}'}), 500

@booking_bp.route('/subscription/revoke', methods=['POST'])
@csrf.exempt
@login_required
def revoke_subscription():
    """Revoke the current user's subscription token."""
    subscription = subscription_dao.get_active_by_user(current_user.id)
    
    if subscription:
        subscription.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscription revoked successfully'})
    
    return jsonify({'success': False, 'error': 'No active subscription found'}), 404

@booking_bp.route('/subscription/status', methods=['GET'])
@login_required
def subscription_status():
    """Get the current user's subscription status."""
    subscription = subscription_dao.get_active_by_user(current_user.id)
    
    if subscription and subscription.is_valid():
        subscription_url = url_for('booking.subscription_ical', token=subscription.token, _external=True)
        return jsonify({
            'has_subscription': True,
            'subscription_url': subscription_url,
            'created_at': subscription.created_at.isoformat(),
            'last_accessed_at': subscription.last_accessed_at.isoformat() if subscription.last_accessed_at else None,
            'access_count': subscription.access_count,
            'status_filter': subscription.status_filter,
            'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        })
    
    return jsonify({'has_subscription': False})

@booking_bp.route('/subscription/<token>.ics')
def subscription_ical(token):
    """Return iCal data for a subscription token (public endpoint)."""
    if not ICALENDAR_AVAILABLE:
        return Response('iCal export is not available', status=503, mimetype='text/plain')
    
    from ..models.user import User
    
    # Find subscription by token using DAL
    subscription = subscription_dao.get_by_token(token)
    
    if not subscription or not subscription.is_valid():
        return Response('Invalid or expired subscription', status=404, mimetype='text/plain')
    
    # Record access using DAL
    subscription_dao.record_access(subscription.id)
    
    # Get user
    user = subscription.user
    
    # Get bookings using DAL with subscription filters
    if subscription.start_date and subscription.end_date:
        bookings = booking_dao.get_by_date_range(
            subscription.start_date,
            subscription.end_date,
            user_id=user.id
        )
    elif subscription.start_date:
        from datetime import datetime, timedelta
        end_date = datetime.utcnow() + timedelta(days=365)
        bookings = booking_dao.get_by_date_range(
            subscription.start_date,
            end_date,
            user_id=user.id
        )
    else:
        bookings = booking_dao.get_by_user(user.id, status=subscription.status_filter)
    
    # Apply status filter if needed (for cases without date range)
    if subscription.status_filter and not (subscription.start_date or subscription.end_date):
        bookings = [b for b in bookings if b.status == subscription.status_filter]
    
    # Generate iCal calendar
    cal = generate_ical_calendar(user, bookings)
    
    if not cal:
        return Response('Error generating calendar', status=500, mimetype='text/plain')
    
    ical_content = cal.to_ical()
    
    # Create response with appropriate headers for subscription
    response = Response(ical_content, mimetype='text/calendar')
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    response.headers['Cache-Control'] = 'public, max-age=43200'  # Cache for 12 hours
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response