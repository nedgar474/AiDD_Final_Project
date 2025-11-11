from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models.notification import Notification
from ..models.booking import Booking
from ..extensions import db, csrf

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

@notification_bp.route('/')
@login_required
def list():
    """Display user's notifications."""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')  # all, unread, read
    
    query = Notification.query.filter_by(user_id=current_user.id)
    
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'read':
        query = query.filter_by(is_read=True)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    # Get unread count
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template('notifications/list.html',
                         notifications=notifications,
                         notifications_list=notifications.items,
                         filter_type=filter_type,
                         unread_count=unread_count)

@notification_bp.route('/<int:id>/read', methods=['POST'])
@csrf.exempt
@login_required
def mark_as_read(id):
    """Mark a notification as read."""
    notification = Notification.query.get_or_404(id)
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True, 'is_read': True})

@notification_bp.route('/<int:id>/unread', methods=['POST'])
@csrf.exempt
@login_required
def mark_as_unread(id):
    """Mark a notification as unread."""
    notification = Notification.query.get_or_404(id)
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = False
    db.session.commit()
    
    return jsonify({'success': True, 'is_read': False})

@notification_bp.route('/mark-all-read', methods=['POST'])
@csrf.exempt
@login_required
def mark_all_read():
    """Mark all notifications as read for current user."""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'success': True})

@notification_bp.route('/<int:id>/delete', methods=['POST'])
@csrf.exempt
@login_required
def delete(id):
    """Delete a notification."""
    notification = Notification.query.get_or_404(id)
    
    # Ensure the notification belongs to the current user
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@notification_bp.route('/unread-count')
@login_required
def unread_count():
    """Get unread notification count (for AJAX)."""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})

