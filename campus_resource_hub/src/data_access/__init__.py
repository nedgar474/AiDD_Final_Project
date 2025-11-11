"""
Data Access Layer (DAL) for Campus Resource Hub.

This module provides encapsulated database operations, ensuring controllers
do not issue raw SQL and maintaining separation of concerns.
"""
from .user_dao import UserDAO
from .resource_dao import ResourceDAO
from .booking_dao import BookingDAO
from .message_dao import MessageDAO
from .waitlist_dao import WaitlistDAO
from .review_dao import ReviewDAO
from .notification_dao import NotificationDAO
from .calendar_subscription_dao import CalendarSubscriptionDAO

__all__ = [
    'UserDAO',
    'ResourceDAO',
    'BookingDAO',
    'MessageDAO',
    'WaitlistDAO',
    'ReviewDAO',
    'NotificationDAO',
    'CalendarSubscriptionDAO'
]

