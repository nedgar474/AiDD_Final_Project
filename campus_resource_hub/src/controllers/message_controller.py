from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models.message import Message
from ..models.user import User
from ..extensions import db, csrf
from ..forms import MessageForm

message_bp = Blueprint('message', __name__, url_prefix='/messages')

@message_bp.route('/')
@login_required
def inbox():
    """Display user's message inbox."""
    messages = Message.query.filter_by(recipient_id=current_user.id, is_hidden=False).order_by(Message.created_at.desc()).all()
    return render_template('messages/inbox.html', messages=messages)

@message_bp.route('/sent')
@login_required
def sent():
    """Display user's sent messages."""
    messages = Message.query.filter_by(sender_id=current_user.id, is_hidden=False).order_by(Message.created_at.desc()).all()
    return render_template('messages/sent.html', messages=messages)

@message_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose and send a message."""
    # Check if user is suspended
    if current_user.is_suspended:
        flash('Your account has been suspended. You cannot send messages.', 'danger')
        return redirect(url_for('message.inbox'))
    
    form = MessageForm()
    if form.validate_on_submit():
        # Find recipient by username or email
        recipient = User.query.filter((User.username == form.recipient.data) | (User.email == form.recipient.data)).first()
        if not recipient:
            flash('Recipient not found. Please check the username or email.', 'danger')
            return render_template('messages/compose.html', form=form)
        
        if recipient.is_suspended:
            flash('The recipient account has been suspended.', 'danger')
            return render_template('messages/compose.html', form=form)

        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            subject=form.subject.data,
            body=form.body.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully.', 'success')
        return redirect(url_for('message.sent'))
    return render_template('messages/compose.html', form=form)

@message_bp.route('/<int:id>')
@login_required
def view(id):
    """View a single message and mark as read if recipient."""
    message = Message.query.get_or_404(id)
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        # Not authorized to view this message
        flash('You are not authorized to view this message.', 'danger')
        return redirect(url_for('message.inbox'))
    if message.recipient_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    return render_template('messages/view.html', message=message)

@message_bp.route('/<int:id>/flag', methods=['POST'])
@login_required
def flag_message(id):
    """Flag a message for admin review."""
    message = Message.query.get_or_404(id)
    if message.recipient_id != current_user.id and message.sender_id != current_user.id:
        flash('You are not authorized to flag this message.', 'danger')
        return redirect(url_for('message.inbox'))
    
    flag_reason = request.form.get('flag_reason', '')
    message.is_flagged = True
    message.flag_reason = flag_reason if flag_reason else 'Flagged by user'
    db.session.commit()
    flash('Message has been flagged for admin review.', 'success')
    return redirect(url_for('message.view', id=id))

@message_bp.route('/send', methods=['POST'])
@csrf.exempt
@login_required
def send_message():
    """Send a message via AJAX (for modal form)."""
    # Check if user is suspended
    if current_user.is_suspended:
        return jsonify({'success': False, 'error': 'Your account has been suspended. You cannot send messages.'}), 403
    
    # Get form data from JSON
    data = request.get_json()
    recipient_username = data.get('recipient', '').strip()
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    
    # Validate required fields
    if not recipient_username or not subject or not body:
        return jsonify({'success': False, 'error': 'All fields are required.'}), 400
    
    # Find recipient by username or email
    recipient = User.query.filter((User.username == recipient_username) | (User.email == recipient_username)).first()
    if not recipient:
        return jsonify({'success': False, 'error': 'Recipient not found. Please check the username or email.'}), 404
    
    if recipient.is_suspended:
        return jsonify({'success': False, 'error': 'The recipient account has been suspended.'}), 403
    
    # Create message
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient.id,
        subject=subject,
        body=body
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Message sent successfully!'})