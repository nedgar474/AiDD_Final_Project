"""
Script to check user accounts in the database and diagnose login issues.
"""
import sys
from pathlib import Path

# Add parent directory to path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from campus_resource_hub.src.app import create_app
from campus_resource_hub.src.extensions import db
from campus_resource_hub.src.models.user import User

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("User Account Diagnostic Tool")
    print("=" * 60)
    print()
    
    # Get all users
    users = User.query.all()
    
    if not users:
        print("❌ No users found in the database!")
        print("\nTo create a test user, run: python seed_data.py")
    else:
        print(f"Found {len(users)} user(s) in the database:\n")
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Username: {user.username}")
            print(f"  Role: {user.role}")
            print(f"  Is Active: {user.is_active}")
            print(f"  Is Suspended: {user.is_suspended}")
            if user.is_suspended:
                print(f"  Suspension Reason: {user.suspension_reason}")
            
            # Check password hash
            if user.password_hash:
                print(f"  Password Hash: {'✓ Set' if len(user.password_hash) > 0 else '✗ Empty'}")
                print(f"  Hash Length: {len(user.password_hash)} characters")
            else:
                print(f"  Password Hash: ✗ NOT SET (This will cause login to fail!)")
            
            print()
    
    print("=" * 60)
    print("\nTo reset a user's password, you can:")
    print("1. Use the admin panel (if you have admin access)")
    print("2. Register a new account")
    print("3. Run seed_data.py to create test users with known passwords")
    print("=" * 60)

