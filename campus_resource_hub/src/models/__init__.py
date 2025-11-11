# AI Contribution: Generated initial scaffold, verified by team.
from ..extensions import db

# Import all models to ensure they're registered with SQLAlchemy
from .user import User
from .resource import Resource
from .booking import Booking
from .message import Message
from .waitlist import Waitlist
from .review import Review
from .admin_log import AdminLog
from .resource_image import ResourceImage
from .notification import Notification
from .calendar_subscription import CalendarSubscription

__all__ = ['db', 'User', 'Resource', 'Booking', 'Message', 'Waitlist', 'Review', 'AdminLog', 'ResourceImage', 'Notification', 'CalendarSubscription']