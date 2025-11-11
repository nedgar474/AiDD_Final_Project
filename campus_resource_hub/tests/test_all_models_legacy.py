"""Test all models to ensure database schema is correct."""
from src.app import create_app
from src.extensions import db
from src.models.user import User
from src.models.resource import Resource
from src.models.booking import Booking
from src.models.message import Message
from src.models.waitlist import Waitlist

app = create_app()

with app.app_context():
    print("Testing all models...")
    
    # Test User model
    try:
        user = User.query.first()
        print(f"[OK] User model works - found {User.query.count()} users")
    except Exception as e:
        print(f"[ERROR] User model failed: {e}")
    
    # Test Resource model
    try:
        resource = Resource.query.first()
        print(f"[OK] Resource model works - found {Resource.query.count()} resources")
        if resource:
            print(f"  - Resource: {resource.name}, category: {resource.category}, available: {resource.is_available}")
    except Exception as e:
        print(f"[ERROR] Resource model failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Booking model
    try:
        booking = Booking.query.first()
        print(f"[OK] Booking model works - found {Booking.query.count()} bookings")
    except Exception as e:
        print(f"[ERROR] Booking model failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Message model
    try:
        message = Message.query.first()
        print(f"[OK] Message model works - found {Message.query.count()} messages")
    except Exception as e:
        print(f"[ERROR] Message model failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Waitlist model
    try:
        waitlist = Waitlist.query.first()
        print(f"[OK] Waitlist model works - found {Waitlist.query.count()} waitlist entries")
    except Exception as e:
        print(f"[ERROR] Waitlist model failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[OK] All model tests complete!")

