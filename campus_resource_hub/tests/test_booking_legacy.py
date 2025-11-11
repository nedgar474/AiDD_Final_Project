"""Test script to verify booking queries work."""
from src.app import create_app
from src.extensions import db
from src.models.booking import Booking

app = create_app()

with app.app_context():
    print("Testing booking queries...")
    
    try:
        # Test query that was failing
        bookings = Booking.query.filter_by(user_id=1, status='active').all()
        print(f"[OK] Query successful - found {len(bookings)} active bookings")
        
        # Test individual booking
        booking = Booking.query.first()
        if booking:
            print(f"[OK] Booking query successful: ID {booking.id}")
            print(f"[OK] Has start_date: {hasattr(booking, 'start_date')}")
            print(f"[OK] Has end_date: {hasattr(booking, 'end_date')}")
            if hasattr(booking, 'start_date') and booking.start_date:
                print(f"[OK] start_date value: {booking.start_date}")
            if hasattr(booking, 'end_date') and booking.end_date:
                print(f"[OK] end_date value: {booking.end_date}")
        else:
            print("No bookings found in database")
    except Exception as e:
        print(f"[ERROR] Booking query failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nBooking test complete!")

