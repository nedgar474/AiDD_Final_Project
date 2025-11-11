"""
Notification utility functions for creating simulated notifications.
"""
from datetime import datetime
from ..models.notification import Notification
from ..models.booking import Booking
from ..models.resource import Resource
from ..extensions import db

def create_notification(user_id, notification_type, title, message, booking_id=None, resource_id=None):
    """
    Create a notification for a user.
    
    Args:
        user_id: ID of the user to notify
        notification_type: Type of notification (booking_created, booking_approved, etc.)
        title: Notification title
        message: Notification message
        booking_id: Optional related booking ID
        resource_id: Optional related resource ID
    
    Returns:
        Created Notification object
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_booking_id=booking_id,
        related_resource_id=resource_id,
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def notify_booking_created(booking):
    """Notify user when a booking is created."""
    resource = booking.resource
    status_text = "pending approval" if booking.status == 'pending' else "confirmed"
    
    title = f"Booking {status_text.title()}: {resource.title}"
    message = f"Your booking for {resource.title} has been created.\n\n"
    message += f"Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Status: {booking.status.title()}\n"
    
    if booking.recurrence_type:
        message += f"\nRecurrence: {booking.recurrence_type.title()}"
        if booking.recurrence_end_date:
            message += f" until {booking.recurrence_end_date.strftime('%Y-%m-%d %I:%M %p')}"
    
    if booking.status == 'pending':
        message += "\n\nYour booking is pending approval. You will be notified once it's reviewed."
    
    create_notification(
        user_id=booking.user_id,
        notification_type='booking_created',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )
    
    # Notify resource owner if different from requester
    if resource.owner_id and resource.owner_id != booking.user_id:
        owner_title = f"New Booking Request: {resource.title}"
        owner_message = f"A new booking has been requested for your resource: {resource.title}\n\n"
        owner_message += f"Requester: {booking.user.username}\n"
        owner_message += f"Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
        owner_message += f"End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
        owner_message += f"Status: {booking.status.title()}"
        
        create_notification(
            user_id=resource.owner_id,
            notification_type='owner_notified',
            title=owner_title,
            message=owner_message,
            booking_id=booking.id,
            resource_id=resource.id
        )

def notify_booking_approved(booking):
    """Notify user when a booking is approved."""
    resource = booking.resource
    title = f"Booking Approved: {resource.title}"
    message = f"Your booking for {resource.title} has been approved!\n\n"
    message += f"Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Status: Active"
    
    create_notification(
        user_id=booking.user_id,
        notification_type='booking_approved',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )

def notify_booking_rejected(booking, reason=None):
    """Notify user when a booking is rejected."""
    resource = booking.resource
    title = f"Booking Rejected: {resource.title}"
    message = f"Your booking request for {resource.title} has been rejected.\n\n"
    message += f"Requested Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Requested End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    
    if reason:
        message += f"\nReason: {reason}\n"
    
    message += "\nYou may try booking a different time slot or resource."
    
    create_notification(
        user_id=booking.user_id,
        notification_type='booking_rejected',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )

def notify_booking_cancelled(booking, cancelled_by_user=True):
    """Notify users when a booking is cancelled."""
    resource = booking.resource
    title = f"Booking Cancelled: {resource.title}"
    
    if cancelled_by_user:
        message = f"Your booking for {resource.title} has been cancelled.\n\n"
    else:
        message = f"Your booking for {resource.title} has been cancelled by an administrator.\n\n"
    
    message += f"Original Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Original End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}"
    
    create_notification(
        user_id=booking.user_id,
        notification_type='booking_cancelled',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )
    
    # Notify resource owner if different from requester
    if resource.owner_id and resource.owner_id != booking.user_id:
        owner_title = f"Booking Cancelled: {resource.title}"
        owner_message = f"A booking for your resource {resource.title} has been cancelled.\n\n"
        owner_message += f"Requester: {booking.user.username}\n"
        owner_message += f"Original Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
        owner_message += f"Original End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}"
        
        create_notification(
            user_id=resource.owner_id,
            notification_type='booking_cancelled',
            title=owner_title,
            message=owner_message,
            booking_id=booking.id,
            resource_id=resource.id
        )

def notify_booking_modified(booking, changes=None):
    """Notify users when a booking is modified."""
    resource = booking.resource
    title = f"Booking Modified: {resource.title}"
    message = f"Your booking for {resource.title} has been updated.\n\n"
    
    if changes:
        message += "Changes:\n"
        for change in changes:
            message += f"- {change}\n"
        message += "\n"
    
    message += f"Updated Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Updated End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    message += f"Status: {booking.status.title()}"
    
    create_notification(
        user_id=booking.user_id,
        notification_type='booking_modified',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )
    
    # Notify resource owner if different from requester
    if resource.owner_id and resource.owner_id != booking.user_id:
        owner_title = f"Booking Modified: {resource.title}"
        owner_message = f"A booking for your resource {resource.title} has been modified.\n\n"
        owner_message += f"Requester: {booking.user.username}\n"
        owner_message += f"Updated Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
        owner_message += f"Updated End: {booking.end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
        owner_message += f"Status: {booking.status.title()}"
        
        create_notification(
            user_id=resource.owner_id,
            notification_type='booking_modified',
            title=owner_title,
            message=owner_message,
            booking_id=booking.id,
            resource_id=resource.id
        )

def notify_recurring_series_created(bookings, skipped_count=0):
    """Notify user when a recurring booking series is created."""
    if not bookings:
        return
    
    booking = bookings[0]
    resource = booking.resource
    title = f"Recurring Booking Series Created: {resource.title}"
    message = f"Your recurring booking series for {resource.title} has been created.\n\n"
    message += f"Recurrence: {booking.recurrence_type.title()}\n"
    message += f"Series Start: {booking.start_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    
    if booking.recurrence_end_date:
        message += f"Series End: {booking.recurrence_end_date.strftime('%Y-%m-%d %I:%M %p')}\n"
    
    message += f"Total Bookings Created: {len(bookings)}\n"
    
    if skipped_count > 0:
        message += f"\nNote: {skipped_count} occurrence(s) were skipped due to conflicts or capacity."
    
    create_notification(
        user_id=booking.user_id,
        notification_type='recurring_series',
        title=title,
        message=message,
        booking_id=booking.id,
        resource_id=resource.id
    )

def notify_waitlist_available(waitlist_entry):
    """Notify user when a resource becomes available from waitlist."""
    resource = waitlist_entry.resource
    title = f"Resource Available: {resource.title}"
    message = f"The resource {resource.title} is now available!\n\n"
    message += f"You requested: {waitlist_entry.requested_start_date.strftime('%Y-%m-%d %I:%M %p')} to {waitlist_entry.requested_end_date.strftime('%Y-%m-%d %I:%M %p')}\n\n"
    message += "Please book the resource soon as availability may be limited."
    
    create_notification(
        user_id=waitlist_entry.user_id,
        notification_type='waitlist_available',
        title=title,
        message=message,
        resource_id=resource.id
    )

