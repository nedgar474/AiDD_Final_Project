"""Fix resources table to handle old type column constraint."""
from src.app import create_app
from src.extensions import db
import sqlite3

app = create_app()

with app.app_context():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update all existing resources to have type = category
    cursor.execute("UPDATE resources SET type = category WHERE type IS NULL OR type = ''")
    print(f"Updated {cursor.rowcount} resources with type from category")
    
    # Also ensure status is set
    cursor.execute("UPDATE resources SET status = CASE WHEN is_available = 1 THEN 'available' ELSE 'unavailable' END WHERE status IS NULL OR status = ''")
    print(f"Updated {cursor.rowcount} resources with status from is_available")
    
    conn.commit()
    conn.close()
    print("Resource table fixed!")

