"""
Seed script to populate the database with test data.
Run this script to add sample users, resources, and bookings to the database.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the current directory to Python path
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

from src.app import create_app
from src.extensions import db, bcrypt
from src.models import User, Resource, Booking, ResourceImage

def create_users():
    """Create test users with different roles."""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@campus.edu',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin'
        },
        {
            'username': 'student1',
            'email': 'student1@campus.edu',
            'password': 'student123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'student'
        },
        {
            'username': 'student2',
            'email': 'student2@campus.edu',
            'password': 'student123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'student'
        },
        {
            'username': 'staff1',
            'email': 'staff1@campus.edu',
            'password': 'staff123',
            'first_name': 'Dr. Robert',
            'last_name': 'Johnson',
            'role': 'staff'
        },
        {
            'username': 'staff2',
            'email': 'staff2@campus.edu',
            'password': 'staff123',
            'first_name': 'Dr. Sarah',
            'last_name': 'Williams',
            'role': 'staff'
        },
        {
            'username': 'student3',
            'email': 'student3@campus.edu',
            'password': 'student123',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'role': 'student'
        }
    ]
    
    users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            users.append(existing_user)
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=bcrypt.generate_password_hash(user_data['password']).decode('utf-8'),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            is_active=True
        )
        db.session.add(user)
        users.append(user)
        print(f"Created user: {user_data['username']} ({user_data['role']})")
    
    return users

def create_resources():
    """Create test resources (rooms, equipment, etc.) with their images."""
    resources_data = [
        {
            'title': 'Main Library Study Room A',
            'description': 'Quiet study room with whiteboard and projector. Perfect for group study sessions.',
            'category': 'Study Room',
            'location': 'Library, Floor 2, Room 201',
            'capacity': 6,
            'is_available': True,
            'is_featured': True,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_3_20251112_044448_028747_IMG_1981.jpg',
                'uploads/resource_3_20251112_044448_028747_IMG_1982.jpg'
            ]
        },
        {
            'title': 'Main Library Study Room B',
            'description': 'Quiet study room with comfortable seating. Ideal for individual or small group study.',
            'category': 'Study Room',
            'location': 'Library, Floor 2, Room 202',
            'capacity': 4,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_4_20251112_044514_740008_IMG_1972.jpg',
                'uploads/resource_4_20251112_044514_744029_IMG_1973.jpg'
            ]
        },
        {
            'title': 'Computer Lab 1',
            'description': 'Fully equipped computer lab with 30 workstations. Software includes Microsoft Office, Adobe Creative Suite, and development tools.',
            'category': 'Computer Lab',
            'location': 'Science Building, Floor 1, Room 101',
            'capacity': 30,
            'is_available': True,
            'is_featured': True,
            'status': 'published',
            'equipment': 'Computers, Mice, Computer Mice',
            'images': [
                'uploads/resource_5_20251112_043748_252361_IMG_1986.jpg',
                'uploads/resource_5_20251112_043748_254372_IMG_1987.jpg'
            ]
        },
        {
            'title': 'Computer Lab 2',
            'description': 'Computer lab with 20 workstations. Available for general use and workshops.',
            'category': 'Computer Lab',
            'location': 'Science Building, Floor 1, Room 102',
            'capacity': 20,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_6_20251112_043824_460447_IMG_1988.jpg',
                'uploads/resource_6_20251112_043824_464508_IMG_1989.jpg'
            ]
        },
        {
            'title': 'Conference Room Alpha',
            'description': 'Large conference room with video conferencing capabilities. Perfect for presentations and meetings.',
            'category': 'Conference Room',
            'location': 'Administration Building, Floor 3, Room 301',
            'capacity': 20,
            'is_available': True,
            'is_featured': True,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_7_20251109_232315_226579_IDO_IU-Hodge-Hall_CollabRoom_8165_2880-860x550.webp',
                'uploads/resource_7_20251112_044358_936065_IMG_1984.jpg',
                'uploads/resource_7_20251112_044358_936065_IMG_1985.jpg'
            ]
        },
        {
            'title': 'Conference Room Beta',
            'description': 'Medium-sized conference room with projector and whiteboard.',
            'category': 'Conference Room',
            'location': 'Administration Building, Floor 3, Room 302',
            'capacity': 12,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_8_20251112_044413_102023_IMG_1977.jpg'
            ]
        },
        {
            'title': 'Projector Set A',
            'description': 'Portable projector with screen and cables. Suitable for presentations and events.',
            'category': 'Equipment',
            'location': 'Equipment Storage, Room 105',
            'capacity': None,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_9_20251112_044719_564700_projector.webp'
            ]
        },
        {
            'title': 'Laptop Cart',
            'description': 'Mobile cart with 15 laptops. Available for classroom use.',
            'category': 'Equipment',
            'location': 'IT Services, Room 205',
            'capacity': 15,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_10_20251112_044936_524708_cart.webp'
            ]
        },
        {
            'title': 'Gymnasium Court 1',
            'description': 'Full-size basketball court. Available for sports activities and events.',
            'category': 'Sports Facility',
            'location': 'Recreation Center, Main Floor',
            'capacity': 50,
            'is_available': True,
            'is_featured': True,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_11_20251112_044428_688183_IMG_1956.jpg',
                'uploads/resource_11_20251112_044428_688183_IMG_1957.jpg'
            ]
        },
        {
            'title': 'Music Practice Room',
            'description': 'Soundproof practice room with piano. Available for music students.',
            'category': 'Practice Room',
            'location': 'Arts Building, Floor 2, Room 208',
            'capacity': 3,
            'is_available': True,
            'is_featured': False,
            'status': 'published',
            'equipment': None,
            'images': [
                'uploads/resource_12_20251112_044540_465413_IMG_1974.jpg',
                'uploads/resource_12_20251112_044540_475988_IMG_1980.jpg'
            ]
        }
    ]
    
    resources = []
    for resource_data in resources_data:
        # Check if resource already exists
        existing_resource = Resource.query.filter_by(title=resource_data['title']).first()
        if existing_resource:
            print(f"Resource {resource_data['title']} already exists, skipping...")
            resources.append(existing_resource)
            continue
        
        # Use raw SQL to insert with all columns including old ones
        # This is needed because the database still has old columns with NOT NULL constraints
        from sqlalchemy import text
        status_value = resource_data.get('status', 'published')
        type_value = resource_data.get('category', 'General')
        
        result = db.session.execute(
            text("""
                INSERT INTO resources (title, name, description, category, type, location, image_url, capacity, 
                                      is_available, is_featured, requires_approval, status, equipment, created_at, updated_at)
                VALUES (:title, :title, :description, :category, :type, :location, :image_url, :capacity,
                        :is_available, :is_featured, :requires_approval, :status, :equipment, :created_at, :updated_at)
            """),
            {
                'title': resource_data['title'],
                'description': resource_data.get('description'),
                'category': resource_data.get('category', 'General'),
                'type': type_value,
                'location': resource_data.get('location'),
                'image_url': resource_data.get('image_url'),
                'capacity': resource_data.get('capacity'),
                'is_available': 1 if resource_data.get('is_available', True) else 0,
                'is_featured': 1 if resource_data.get('is_featured', False) else 0,
                'requires_approval': 1 if resource_data.get('requires_approval', False) else 0,
                'status': status_value,
                'equipment': resource_data.get('equipment'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )
        db.session.flush()
        
        # Get the created resource
        resource = Resource.query.filter_by(title=resource_data['title']).first()
        
        # Create ResourceImage records for this resource
        images = resource_data.get('images', [])
        if images:
            for idx, image_path in enumerate(images, start=1):
                # Check if image record already exists
                existing_image = ResourceImage.query.filter_by(
                    resource_id=resource.id,
                    image_path=image_path
                ).first()
                
                if not existing_image:
                    image = ResourceImage(
                        resource_id=resource.id,
                        image_path=image_path,
                        display_order=idx
                    )
                    db.session.add(image)
                    print(f"  Added image {idx}: {image_path}")
                else:
                    print(f"  Image already exists: {image_path}")
        
        resources.append(resource)
        print(f"Created resource: {resource_data['title']} with {len(images)} image(s)")
    
    return resources

def create_bookings(users, resources):
    """Create test bookings."""
    # Only create bookings if we have users and resources
    if not users or not resources:
        print("No users or resources available, skipping bookings...")
        return
    
    # Get some specific users and resources
    student1 = next((u for u in users if u.username == 'student1'), None)
    student2 = next((u for u in users if u.username == 'student2'), None)
    staff1 = next((u for u in users if u.username == 'staff1'), None)
    staff2 = next((u for u in users if u.username == 'staff2'), None)
    
    study_room_a = next((r for r in resources if 'Study Room A' in r.title), None)
    study_room_b = next((r for r in resources if 'Study Room B' in r.title), None)
    computer_lab_1 = next((r for r in resources if 'Computer Lab 1' in r.title), None)
    conference_alpha = next((r for r in resources if 'Conference Room Alpha' in r.title), None)
    gym_court = next((r for r in resources if 'Gymnasium Court' in r.title), None)
    
    now = datetime.utcnow()
    
    bookings_data = [
        # Past completed booking
        {
            'user': student1,
            'resource': study_room_a,
            'start_date': now - timedelta(days=5, hours=10),
            'end_date': now - timedelta(days=5, hours=12),
            'status': 'completed',
            'notes': 'Group study session for midterm exam'
        },
        # Active booking (happening now)
        {
            'user': student2,
            'resource': computer_lab_1,
            'start_date': now - timedelta(hours=1),
            'end_date': now + timedelta(hours=2),
            'status': 'active',
            'notes': 'Working on programming assignment'
        },
        # Upcoming pending booking
        {
            'user': staff1,
            'resource': conference_alpha,
            'start_date': now + timedelta(days=1, hours=10),
            'end_date': now + timedelta(days=1, hours=12),
            'status': 'pending',
            'notes': 'Department meeting'
        },
        # Another upcoming booking
        {
            'user': student1,
            'resource': study_room_b,
            'start_date': now + timedelta(days=2, hours=14),
            'end_date': now + timedelta(days=2, hours=16),
            'status': 'pending',
            'notes': 'Project group meeting'
        },
        # Cancelled booking
        {
            'user': staff2,
            'resource': gym_court,
            'start_date': now + timedelta(days=3, hours=18),
            'end_date': now + timedelta(days=3, hours=20),
            'status': 'cancelled',
            'notes': 'Event cancelled due to scheduling conflict'
        }
    ]
    
    bookings_created = 0
    for booking_data in bookings_data:
        if not booking_data['user'] or not booking_data['resource']:
            continue
        
        # Use raw SQL to insert with all columns including old ones
        from sqlalchemy import text
        db.session.execute(
            text("""
                INSERT INTO bookings (user_id, resource_id, start_date, end_date, start_time, end_time,
                                      status, notes, created_at, updated_at)
                VALUES (:user_id, :resource_id, :start_date, :end_date, :start_time, :end_time,
                        :status, :notes, :created_at, :updated_at)
            """),
            {
                'user_id': booking_data['user'].id,
                'resource_id': booking_data['resource'].id,
                'start_date': booking_data['start_date'],
                'end_date': booking_data['end_date'],
                'start_time': booking_data['start_date'],  # Also set old column
                'end_time': booking_data['end_date'],      # Also set old column
                'status': booking_data['status'],
                'notes': booking_data.get('notes'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )
        db.session.flush()
        bookings_created += 1
        print(f"Created booking: {booking_data['user'].username} -> {booking_data['resource'].name} ({booking_data['status']})")
    
    if bookings_created > 0:
        print(f"Created {bookings_created} bookings")
    else:
        print("No bookings created (missing users or resources)")

def seed_database():
    """Main function to seed the database."""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 50)
        print("Starting database seeding...")
        print("=" * 50)
        
        # Create all tables if they don't exist
        db.create_all()
        
        # Create users
        print("\n--- Creating Users ---")
        users = create_users()
        
        # Create resources
        print("\n--- Creating Resources ---")
        resources = create_resources()
        
        # Create bookings
        print("\n--- Creating Bookings ---")
        create_bookings(users, resources)
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 50)
            print("Database seeding completed successfully!")
            print("=" * 50)
            print("\nTest accounts created:")
            print("  Admin: admin / admin123")
            print("  Student: student1 / student123")
            print("  Staff: staff1 / staff123")
            print("\nAll passwords are the same as the username role (e.g., admin123, student123, staff123)")
        except Exception as e:
            db.session.rollback()
            print(f"\nError occurred: {e}")
            raise

if __name__ == '__main__':
    seed_database()

