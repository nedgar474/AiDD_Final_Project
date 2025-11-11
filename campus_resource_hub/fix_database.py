"""Fix database by ensuring all columns exist in the correct database file."""
from src.app import create_app
from src.extensions import db
import sqlite3
import os

app = create_app()

with app.app_context():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    
    # Extract the database path
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        print(f"Absolute path: {os.path.abspath(db_path)}")
        
        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created directory: {db_dir}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns in users table
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting user columns: {user_cols}")
        
        # Add missing columns to users table
        if 'is_suspended' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT 0")
            print("[OK] Added is_suspended column to users")
        else:
            print("[OK] is_suspended column already exists")
            
        if 'suspension_reason' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN suspension_reason TEXT")
            print("[OK] Added suspension_reason column to users")
        else:
            print("[OK] suspension_reason column already exists")
            
        if 'department' not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN department VARCHAR(100)")
            print("[OK] Added department column to users")
        else:
            print("[OK] department column already exists")
        
        # Check existing columns in bookings table
        cursor.execute("PRAGMA table_info(bookings)")
        booking_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting booking columns: {booking_cols}")
        
        # Add missing columns to bookings table
        if 'recurrence_type' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN recurrence_type VARCHAR(20)")
            print("[OK] Added recurrence_type column to bookings")
        else:
            print("[OK] recurrence_type column already exists")
            
        if 'recurrence_end_date' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN recurrence_end_date DATETIME")
            print("[OK] Added recurrence_end_date column to bookings")
        else:
            print("[OK] recurrence_end_date column already exists")
            
        if 'parent_booking_id' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN parent_booking_id INTEGER")
            print("[OK] Added parent_booking_id column to bookings")
            # Add foreign key constraint if possible (SQLite has limited FK support)
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_parent_booking_id 
                    ON bookings(parent_booking_id)
                """)
                print("[OK] Created index on parent_booking_id")
            except Exception as e:
                print(f"[WARN] Could not create index on parent_booking_id: {e}")
        else:
            print("[OK] parent_booking_id column already exists")
        
        if 'start_date' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN start_date DATETIME")
            print("[OK] Added start_date column to bookings")
            # Migrate data from start_time to start_date if it exists
            if 'start_time' in booking_cols:
                cursor.execute("UPDATE bookings SET start_date = start_time WHERE start_date IS NULL")
                print("[OK] Migrated data from start_time to start_date")
        else:
            print("[OK] start_date column already exists")
            
        if 'end_date' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN end_date DATETIME")
            print("[OK] Added end_date column to bookings")
            # Migrate data from end_time to end_date if it exists
            if 'end_time' in booking_cols:
                cursor.execute("UPDATE bookings SET end_date = end_time WHERE end_date IS NULL")
                print("[OK] Migrated data from end_time to end_date")
        else:
            print("[OK] end_date column already exists")
            
        if 'updated_at' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN updated_at DATETIME")
            print("[OK] Added updated_at column to bookings")
            # Set updated_at to created_at for existing records
            cursor.execute("UPDATE bookings SET updated_at = created_at WHERE updated_at IS NULL")
            print("[OK] Set updated_at for existing bookings")
        else:
            print("[OK] updated_at column already exists")
        
        # Check existing columns in resources table
        cursor.execute("PRAGMA table_info(resources)")
        resource_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting resource columns: {resource_cols}")
        
        # Add missing columns to resources table
        if 'category' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN category VARCHAR(50)")
            print("[OK] Added category column to resources")
            # Migrate data from type to category if it exists
            if 'type' in resource_cols:
                cursor.execute("UPDATE resources SET category = type WHERE category IS NULL")
                print("[OK] Migrated data from type to category")
            else:
                cursor.execute("UPDATE resources SET category = 'General' WHERE category IS NULL")
                print("[OK] Set default category for existing resources")
        else:
            print("[OK] category column already exists")
            
        if 'image_url' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN image_url VARCHAR(255)")
            print("[OK] Added image_url column to resources")
        else:
            print("[OK] image_url column already exists")
            
        if 'is_available' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN is_available BOOLEAN DEFAULT 1")
            print("[OK] Added is_available column to resources")
            # Migrate data from status to is_available if it exists
            if 'status' in resource_cols:
                cursor.execute("UPDATE resources SET is_available = CASE WHEN status = 'available' THEN 1 ELSE 0 END WHERE is_available IS NULL")
                print("[OK] Migrated data from status to is_available")
            else:
                cursor.execute("UPDATE resources SET is_available = 1 WHERE is_available IS NULL")
                print("[OK] Set default is_available for existing resources")
        else:
            print("[OK] is_available column already exists")
            
        if 'is_featured' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN is_featured BOOLEAN DEFAULT 0")
            print("[OK] Added is_featured column to resources")
        else:
            print("[OK] is_featured column already exists")
            
        if 'updated_at' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN updated_at DATETIME")
            print("[OK] Added updated_at column to resources")
            cursor.execute("UPDATE resources SET updated_at = created_at WHERE updated_at IS NULL")
            print("[OK] Set updated_at for existing resources")
        else:
            print("[OK] updated_at column already exists")
            
        if 'requires_approval' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN requires_approval BOOLEAN DEFAULT 0")
            print("[OK] Added requires_approval column to resources")
        else:
            print("[OK] requires_approval column already exists")
        
        # Check if old columns exist and need to be handled
        # Note: SQLite doesn't support dropping columns easily, so we'll just ensure new columns work
        if 'type' in resource_cols and 'category' in resource_cols:
            # Make sure all resources have category set
            cursor.execute("UPDATE resources SET category = type WHERE category IS NULL OR category = ''")
            print("[OK] Ensured all resources have category set")
        
        if 'status' in resource_cols and 'is_available' in resource_cols:
            # Make sure all resources have is_available set
            cursor.execute("UPDATE resources SET is_available = CASE WHEN status = 'available' THEN 1 ELSE 0 END WHERE is_available IS NULL")
            print("[OK] Ensured all resources have is_available set")
        
        # Check if waitlist table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waitlist'")
        waitlist_exists = cursor.fetchone() is not None
        
        if not waitlist_exists:
            print("\n[OK] Creating waitlist table...")
            cursor.execute("""
                CREATE TABLE waitlist (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    resource_id INTEGER NOT NULL,
                    requested_start_date DATETIME NOT NULL,
                    requested_end_date DATETIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    notes TEXT,
                    created_at DATETIME NOT NULL,
                    notified_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(resource_id) REFERENCES resources(id)
                )
            """)
            print("[OK] Waitlist table created")
        else:
            print("\n[OK] Waitlist table already exists")
        
        # Check if reviews table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'")
        reviews_exists = cursor.fetchone() is not None
        
        if not reviews_exists:
            print("\n[OK] Creating reviews table...")
            cursor.execute("""
                CREATE TABLE reviews (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    resource_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    review_text TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(resource_id) REFERENCES resources(id)
                )
            """)
            print("[OK] Reviews table created")
        else:
            print("\n[OK] Reviews table already exists")
        
        # Check existing columns in messages table
        cursor.execute("PRAGMA table_info(messages)")
        message_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting message columns: {message_cols}")
        
        # Add missing columns to messages table
        if 'is_read' not in message_cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT 0")
            print("[OK] Added is_read column to messages")
        else:
            print("[OK] is_read column already exists")
            
        if 'is_flagged' not in message_cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
            print("[OK] Added is_flagged column to messages")
        else:
            print("[OK] is_flagged column already exists")
            
        if 'is_hidden' not in message_cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN is_hidden BOOLEAN DEFAULT 0")
            print("[OK] Added is_hidden column to messages")
        else:
            print("[OK] is_hidden column already exists")
            
        if 'flag_reason' not in message_cols:
            cursor.execute("ALTER TABLE messages ADD COLUMN flag_reason TEXT")
            print("[OK] Added flag_reason column to messages")
        else:
            print("[OK] flag_reason column already exists")
        
        # Check if admin_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_logs'")
        admin_logs_exists = cursor.fetchone() is not None
        
        if not admin_logs_exists:
            cursor.execute("""
                CREATE TABLE admin_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    target_table TEXT,
                    details TEXT,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (admin_id) REFERENCES users(id)
                )
            """)
            print("[OK] Admin_logs table created")
        else:
            print("\n[OK] Admin_logs table already exists")
        
        # Check existing columns in reviews table
        cursor.execute("PRAGMA table_info(reviews)")
        review_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting review columns: {review_cols}")
        
        if 'is_hidden' not in review_cols:
            cursor.execute("ALTER TABLE reviews ADD COLUMN is_hidden BOOLEAN DEFAULT 0")
            print("[OK] Added is_hidden column to reviews")
        else:
            print("[OK] is_hidden column already exists in reviews")
        
        # Check if resource_images table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_images'")
        resource_images_exists = cursor.fetchone() is not None
        
        if not resource_images_exists:
            cursor.execute("""
                CREATE TABLE resource_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id INTEGER NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    display_order INTEGER DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (resource_id) REFERENCES resources(id)
                )
            """)
            print("[OK] Resource_images table created")
        else:
            print("\n[OK] Resource_images table already exists")
        
        # Check if notifications table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        notifications_exists = cursor.fetchone() is not None
        
        if not notifications_exists:
            cursor.execute("""
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    related_booking_id INTEGER,
                    related_resource_id INTEGER,
                    is_read BOOLEAN DEFAULT 0 NOT NULL,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (related_booking_id) REFERENCES bookings(id),
                    FOREIGN KEY (related_resource_id) REFERENCES resources(id)
                )
            """)
            print("[OK] Notifications table created")
        else:
            print("\n[OK] Notifications table already exists")
        
        # Check if owner_id column exists in resources table
        cursor.execute("PRAGMA table_info(resources)")
        resource_cols = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting resource columns: {resource_cols}")
        
        if 'owner_id' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN owner_id INTEGER REFERENCES users(id)")
            print("[OK] Added owner_id column to resources")
        else:
            print("[OK] owner_id column already exists in resources")
        
        # Add title column and migrate from name if needed
        if 'title' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN title VARCHAR(100)")
            print("[OK] Added title column to resources")
            # Migrate data from name to title if name exists
            if 'name' in resource_cols:
                cursor.execute("UPDATE resources SET title = name WHERE title IS NULL OR title = ''")
                print("[OK] Migrated data from name to title")
            else:
                cursor.execute("UPDATE resources SET title = 'Untitled Resource' WHERE title IS NULL OR title = ''")
                print("[OK] Set default title for existing resources")
        else:
            print("[OK] title column already exists in resources")
            # Ensure title is populated from name if title is empty
            if 'name' in resource_cols:
                cursor.execute("UPDATE resources SET title = name WHERE (title IS NULL OR title = '') AND name IS NOT NULL")
                print("[OK] Ensured all resources have title set from name")
        
        # Check if status column exists and update it
        if 'status' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN status VARCHAR(20) DEFAULT 'draft'")
            print("[OK] Added status column to resources")
            # Set existing resources to 'published' by default
            cursor.execute("UPDATE resources SET status = 'published' WHERE status IS NULL OR status = ''")
            print("[OK] Set existing resources to 'published' status")
        else:
            print("[OK] status column already exists in resources")
            # Ensure status has valid values
            cursor.execute("UPDATE resources SET status = 'published' WHERE status IS NULL OR status = '' OR status NOT IN ('draft', 'published', 'archived')")
            print("[OK] Ensured all resources have valid status values")
        
        # Add equipment column if it doesn't exist
        if 'equipment' not in resource_cols:
            cursor.execute("ALTER TABLE resources ADD COLUMN equipment TEXT")
            print("[OK] Added equipment column to resources")
        else:
            print("[OK] equipment column already exists in resources")
        
        conn.commit()
        conn.close()
        print("\n[OK] Database updated successfully!")
    else:
        print("Not a SQLite database, cannot add columns directly")

