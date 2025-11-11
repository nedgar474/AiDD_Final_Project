"""
Script to add calendar_subscriptions table to the database.
Run this script to add the subscription token table for iCal subscription links.
"""
import sqlite3
import os
from pathlib import Path

# Get database path
basedir = Path(__file__).parent
db_path = basedir / 'instance' / 'campus_resource_hub.db'

if not db_path.exists():
    print(f"Database not found at {db_path}")
    print("Please run the application first to create the database.")
    exit(1)

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar_subscriptions'")
if cursor.fetchone():
    print("Table 'calendar_subscriptions' already exists. Skipping creation.")
else:
    print("Creating 'calendar_subscriptions' table...")
    cursor.execute("""
        CREATE TABLE calendar_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token VARCHAR(64) NOT NULL UNIQUE,
            created_at DATETIME NOT NULL,
            last_accessed_at DATETIME,
            access_count INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            expires_at DATETIME,
            status_filter VARCHAR(20),
            start_date DATETIME,
            end_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create index on token for faster lookups
    cursor.execute("CREATE INDEX idx_calendar_subscriptions_token ON calendar_subscriptions(token)")
    
    # Create index on user_id for faster queries
    cursor.execute("CREATE INDEX idx_calendar_subscriptions_user_id ON calendar_subscriptions(user_id)")
    
    conn.commit()
    print("Table 'calendar_subscriptions' created successfully!")
    print("Indexes created successfully!")

conn.close()
print("Database update complete!")

