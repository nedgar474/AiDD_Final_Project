"""Quick script to check database schema."""
from src.app import create_app
from src.extensions import db
from sqlalchemy import inspect, text

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    print("=" * 60)
    print("RESOURCES TABLE SCHEMA")
    print("=" * 60)
    cols = inspector.get_columns('resources')
    for col in cols:
        default = col.get('default', 'None')
        if default and hasattr(default, 'arg'):
            default = default.arg
        print(f"{col['name']:20} | nullable={str(col['nullable']):5} | default={str(default)}")
    
    print("\n" + "=" * 60)
    print("BOOKINGS TABLE SCHEMA")
    print("=" * 60)
    cols = inspector.get_columns('bookings')
    for col in cols:
        default = col.get('default', 'None')
        if default and hasattr(default, 'arg'):
            default = default.arg
        print(f"{col['name']:20} | nullable={str(col['nullable']):5} | default={str(default)}")
    
    print("\n" + "=" * 60)
    print("USERS TABLE SCHEMA")
    print("=" * 60)
    cols = inspector.get_columns('users')
    for col in cols:
        default = col.get('default', 'None')
        if default and hasattr(default, 'arg'):
            default = default.arg
        print(f"{col['name']:20} | nullable={str(col['nullable']):5} | default={str(default)}")

