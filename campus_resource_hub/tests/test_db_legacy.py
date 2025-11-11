"""Test script to verify database columns exist."""
from src.app import create_app
from src.extensions import db
from src.models.user import User
from src.models.message import Message

app = create_app()

with app.app_context():
    print("Testing database connection...")
    
    # Test User model
    try:
        user = User.query.first()
        if user:
            print(f"[OK] User query successful: {user.username}")
            print(f"[OK] User has is_suspended: {hasattr(user, 'is_suspended')}")
            print(f"[OK] User.is_suspended value: {user.is_suspended}")
            print(f"[OK] User has suspension_reason: {hasattr(user, 'suspension_reason')}")
        else:
            print("No users found in database")
    except Exception as e:
        print(f"[ERROR] User query failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Message model
    try:
        message = Message.query.first()
        if message:
            print(f"[OK] Message query successful: {message.subject}")
            print(f"[OK] Message has is_flagged: {hasattr(message, 'is_flagged')}")
            print(f"[OK] Message has is_hidden: {hasattr(message, 'is_hidden')}")
            print(f"[OK] Message has is_read: {hasattr(message, 'is_read')}")
        else:
            print("No messages found in database")
    except Exception as e:
        print(f"[ERROR] Message query failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nDatabase schema check complete!")

