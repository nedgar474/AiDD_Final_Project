"""Script to add missing columns to the database."""
from src.app import create_app
from src.extensions import db
import sqlite3
import os

app = create_app()

with app.app_context():
    # Get the database URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    
    # Extract the database path
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        # If it's a relative path, it's in the instance folder
        if not os.path.isabs(db_path):
            db_path = os.path.join('instance', db_path)
        
        print(f"Database path: {db_path}")
        
        if os.path.exists(db_path):
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(users)")
            user_cols = [col[1] for col in cursor.fetchall()]
            print(f"Existing user columns: {user_cols}")
            
            # Add missing columns to users table
            if 'is_suspended' not in user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT 0")
                print("Added is_suspended column to users")
            else:
                print("is_suspended column already exists")
                
            if 'suspension_reason' not in user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN suspension_reason TEXT")
                print("Added suspension_reason column to users")
            else:
                print("suspension_reason column already exists")
            
            # Check existing columns in messages table
            cursor.execute("PRAGMA table_info(messages)")
            message_cols = [col[1] for col in cursor.fetchall()]
            print(f"Existing message columns: {message_cols}")
            
            # Add missing columns to messages table
            if 'is_flagged' not in message_cols:
                cursor.execute("ALTER TABLE messages ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
                print("Added is_flagged column to messages")
            else:
                print("is_flagged column already exists")
                
            if 'is_hidden' not in message_cols:
                cursor.execute("ALTER TABLE messages ADD COLUMN is_hidden BOOLEAN DEFAULT 0")
                print("Added is_hidden column to messages")
            else:
                print("is_hidden column already exists")
                
            if 'flag_reason' not in message_cols:
                cursor.execute("ALTER TABLE messages ADD COLUMN flag_reason TEXT")
                print("Added flag_reason column to messages")
            else:
                print("flag_reason column already exists")
            
            conn.commit()
            conn.close()
            print("Database updated successfully!")
        else:
            print(f"Database file not found at {db_path}")
            print("Creating database with all columns...")
            # Create all tables if database doesn't exist
            db.create_all()
            print("Database created with all tables and columns!")
    else:
        print("Not a SQLite database, cannot add columns directly")

