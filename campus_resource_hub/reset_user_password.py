"""
Script to reset a user's password.
Usage: python reset_user_password.py <email> <new_password>
"""
import sys
from pathlib import Path

# Add parent directory to path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from campus_resource_hub.src.app import create_app
from campus_resource_hub.src.extensions import db, bcrypt
from campus_resource_hub.src.models.user import User

if len(sys.argv) < 3:
    print("Usage: python reset_user_password.py <email> <new_password>")
    print("Example: python reset_user_password.py admin@example.com newpassword123")
    sys.exit(1)

email = sys.argv[1]
new_password = sys.argv[2]

app = create_app('development')

with app.app_context():
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"❌ User with email '{email}' not found!")
        sys.exit(1)
    
    # Generate new password hash
    new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Update user
    user.password_hash = new_hash
    db.session.commit()
    
    print(f"✓ Password reset successfully for user: {user.email}")
    print(f"  Username: {user.username}")
    print(f"  New password: {new_password}")
    print("\nYou can now log in with this password.")

