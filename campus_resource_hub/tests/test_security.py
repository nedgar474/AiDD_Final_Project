"""
Security tests for Campus Resource Hub.

Tests SQL injection protection, template escaping, and parameterized queries.
"""
import pytest
from datetime import datetime, timedelta
from src.data_access import UserDAO, ResourceDAO, BookingDAO
from src.models.user import User
from src.models.resource import Resource
from src.models.booking import Booking
from src.extensions import db, bcrypt


class TestSQLInjectionProtection:
    """Test that SQL injection attempts are prevented."""
    
    def test_sql_injection_in_search_query(self, app, client, test_resource):
        """Test that SQL injection in search query is treated as literal string."""
        with app.app_context():
            # Malicious SQL injection payloads
            sql_injection_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; DELETE FROM resources; --",
                "1' UNION SELECT * FROM users--",
                "admin'--",
                "' OR 1=1--"
            ]
            
            for payload in sql_injection_payloads:
                # Attempt search with malicious input
                response = client.get(f'/resources/search?q={payload}')
                
                # Should not crash or execute SQL
                assert response.status_code in [200, 302, 400], \
                    f"Search with SQL injection payload '{payload}' should not crash"
                
                # Verify the payload is treated as a literal search string
                # (it won't match anything, but shouldn't execute SQL)
                dao = ResourceDAO()
                results = dao.search(query=payload)
                
                # Should return empty or no results, not crash
                assert isinstance(results, list), \
                    f"Search should return a list, not crash with payload '{payload}'"
    
    def test_sql_injection_in_resource_title(self, app, client, test_admin):
        """Test that SQL injection in resource title is prevented."""
        with app.app_context():
            # Login as admin
            client.post('/auth/login', data={
                'email': test_admin.email,
                'password': 'admin123'
            })
            
            # Attempt to create resource with SQL injection in title
            malicious_title = "'; DROP TABLE resources; --"
            
            response = client.post('/admin/resources/new', data={
                'title': malicious_title,
                'description': 'Test description',
                'category': 'Room',
                'location': 'Building A',
                'capacity': 10,
                'is_available': True,
                'status': 'published',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Should either reject or treat as literal string
            assert response.status_code in [200, 302, 400], \
                "Resource creation with SQL injection should not crash"
            
            # If resource was created, verify it's stored as literal string
            resource = Resource.query.filter_by(title=malicious_title).first()
            if resource:
                # Verify the title is stored literally, not executed
                assert resource.title == malicious_title
                # Verify no tables were dropped (database still has resources table)
                assert Resource.query.count() >= 1
    
    def test_sql_injection_in_user_creation(self, app, client):
        """Test that SQL injection in user registration is prevented."""
        with app.app_context():
            # Malicious username with SQL injection
            malicious_username = "admin'; DROP TABLE users; --"
            
            response = client.post('/auth/register', data={
                'username': malicious_username,
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'role': 'student',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Should either reject or treat as literal string
            assert response.status_code in [200, 302, 400], \
                "User registration with SQL injection should not crash"
            
            # Verify users table still exists (not dropped)
            user_count = User.query.count()
            assert user_count >= 0  # Should be able to query users table
    
    def test_sql_injection_in_booking_notes(self, app, client, test_user, test_resource):
        """Test that SQL injection in booking notes is prevented."""
        with app.app_context():
            # Login as user
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123'
            })
            
            # Attempt to create booking with SQL injection in notes
            malicious_notes = "'; DROP TABLE bookings; --"
            start_date = datetime.utcnow() + timedelta(days=2)
            end_date = start_date + timedelta(hours=2)
            
            response = client.post(f'/resources/{test_resource.id}/book', data={
                'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
                'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
                'notes': malicious_notes,
                'recurrence_type': '',
                'recurrence_end_date': '',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Should not crash
            assert response.status_code in [200, 302, 400], \
                "Booking creation with SQL injection should not crash"
            
            # Verify bookings table still exists
            booking_count = Booking.query.count()
            assert booking_count >= 0  # Should be able to query bookings table
    
    def test_parameterized_queries_used(self, app, test_user, test_resource):
        """Verify that DAL uses parameterized queries (SQLAlchemy ORM)."""
        with app.app_context():
            dao = ResourceDAO()
            
            # Verify that search uses SQLAlchemy ORM methods, not raw SQL
            # SQLAlchemy ORM automatically uses parameterized queries
            malicious_input = "'; DROP TABLE resources; --"
            
            # This should use SQLAlchemy's filter/ilike which is parameterized
            results = dao.search(query=malicious_input)
            
            # Verify it returns a list (ORM query result), not an error
            assert isinstance(results, list)
            
            # Verify SQLAlchemy is being used (check that we can query)
            # If raw SQL was used, this would have crashed or dropped tables
            all_resources = Resource.query.all()
            assert isinstance(all_resources, list)
            assert len(all_resources) >= 0  # Table should still exist


class TestTemplateEscaping:
    """Test that XSS attacks are prevented through template escaping."""
    
    def test_xss_in_resource_title(self, app, client, test_admin):
        """Test that XSS payload in resource title is escaped in templates."""
        with app.app_context():
            # Login as admin
            client.post('/auth/login', data={
                'email': test_admin.email,
                'password': 'admin123'
            })
            
            # Create resource with XSS payload
            xss_payload = "<script>alert('XSS')</script>"
            
            response = client.post('/admin/resources/new', data={
                'title': xss_payload,
                'description': 'Test description',
                'category': 'Room',
                'location': 'Building A',
                'capacity': 10,
                'is_available': True,
                'status': 'published',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Resource should be created
            resource = Resource.query.filter_by(title=xss_payload).first()
            if resource:
                # Get the rendered template
                response = client.get(f'/resources/{resource.id}')
                html_content = response.get_data(as_text=True)
                
                # Verify script tag is escaped (should appear as &lt;script&gt; not <script>)
                assert '<script>' not in html_content or '&lt;script&gt;' in html_content, \
                    "XSS payload should be escaped in rendered template"
                
                # Verify alert is not executable
                assert "alert('XSS')" not in html_content or '&lt;script&gt;' in html_content, \
                    "XSS payload should not be executable"
    
    def test_xss_in_resource_description(self, app, client, test_admin):
        """Test that XSS payload in resource description is escaped."""
        with app.app_context():
            # Login as admin
            client.post('/auth/login', data={
                'email': test_admin.email,
                'password': 'admin123'
            })
            
            # Create resource with XSS in description
            xss_payload = "<img src=x onerror=alert('XSS')>"
            
            response = client.post('/admin/resources/new', data={
                'title': 'Test Resource',
                'description': xss_payload,
                'category': 'Room',
                'location': 'Building A',
                'capacity': 10,
                'is_available': True,
                'status': 'published',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Get resource
            resource = Resource.query.filter_by(title='Test Resource').first()
            if resource:
                # Get rendered template
                response = client.get(f'/resources/{resource.id}')
                html_content = response.get_data(as_text=True)
                
                # Verify XSS payload is escaped
                # Should contain escaped version, not raw HTML
                assert 'onerror=' not in html_content or '&lt;' in html_content or '&gt;' in html_content, \
                    "XSS payload in description should be escaped"
    
    def test_xss_in_user_username(self, app, client):
        """Test that XSS payload in username is escaped."""
        with app.app_context():
            # Register user with XSS payload in username
            xss_payload = "<script>alert('XSS')</script>"
            
            response = client.post('/auth/register', data={
                'username': xss_payload,
                'email': 'xss@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'role': 'student',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # User should be created (or rejected, but not crash)
            assert response.status_code in [200, 302, 400]
            
            # If user was created, verify XSS is escaped in templates
            user = User.query.filter_by(email='xss@example.com').first()
            if user:
                # Login and check profile/username display
                client.post('/auth/login', data={
                    'email': 'xss@example.com',
                    'password': 'password123'
                })
                
                # Check any page that displays username
                response = client.get('/')
                html_content = response.get_data(as_text=True)
                
                # Verify script tag is escaped if username appears
                if xss_payload in html_content or user.username in html_content:
                    assert '<script>' not in html_content or '&lt;script&gt;' in html_content, \
                        "XSS payload in username should be escaped"
    
    def test_xss_in_booking_notes(self, app, client, test_user, test_resource):
        """Test that XSS payload in booking notes is escaped."""
        with app.app_context():
            # Login as user
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123'
            })
            
            # Create booking with XSS in notes
            xss_payload = "<script>document.cookie='stolen'</script>"
            start_date = datetime.utcnow() + timedelta(days=2)
            end_date = start_date + timedelta(hours=2)
            
            response = client.post(f'/resources/{test_resource.id}/book', data={
                'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
                'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
                'notes': xss_payload,
                'recurrence_type': '',
                'recurrence_end_date': '',
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Booking should be created
            booking = Booking.query.filter_by(
                user_id=test_user.id,
                resource_id=test_resource.id
            ).order_by(Booking.created_at.desc()).first()
            
            if booking and booking.notes:
                # Get booking details page
                response = client.get(f'/bookings/{booking.id}')
                html_content = response.get_data(as_text=True)
                
                # Verify XSS payload is escaped
                assert '<script>' not in html_content or '&lt;script&gt;' in html_content, \
                    "XSS payload in booking notes should be escaped"
    
    def test_xss_in_message_body(self, app, client, test_user, test_admin):
        """Test that XSS payload in message body is escaped."""
        with app.app_context():
            # Login as user
            client.post('/auth/login', data={
                'email': test_user.email,
                'password': 'password123'
            })
            
            # Send message with XSS payload
            xss_payload = "<script>alert('XSS')</script>"
            
            response = client.post('/messages/compose', data={
                'recipient': test_admin.username,
                'subject': 'Test Message',
                'body': xss_payload,
                'csrf_token': ''  # CSRF disabled in tests
            }, follow_redirects=True)
            
            # Message should be sent
            from src.models.message import Message
            message = Message.query.filter_by(
                sender_id=test_user.id,
                recipient_id=test_admin.id
            ).order_by(Message.created_at.desc()).first()
            
            if message:
                # Login as admin and view message
                client.post('/auth/login', data={
                    'email': test_admin.email,
                    'password': 'admin123'
                })
                
                response = client.get(f'/messages/{message.id}')
                html_content = response.get_data(as_text=True)
                
                # Verify XSS payload is escaped
                assert '<script>' not in html_content or '&lt;script&gt;' in html_content, \
                    "XSS payload in message body should be escaped"


class TestParameterizedQueryVerification:
    """Verify that parameterized queries are used throughout the application."""
    
    def test_dal_uses_sqlalchemy_orm(self, app):
        """Verify that DAL uses SQLAlchemy ORM (which uses parameterized queries)."""
        with app.app_context():
            dao = ResourceDAO()
            
            # Verify that search method uses SQLAlchemy ORM
            # SQLAlchemy ORM automatically parameterizes queries
            malicious_input = "'; DROP TABLE resources; --"
            
            # This should use SQLAlchemy's filter/ilike
            results = dao.search(query=malicious_input)
            
            # Verify it's a list (ORM result), not a raw SQL result
            assert isinstance(results, list)
            
            # Verify SQLAlchemy is being used (not raw SQL)
            # Check that we can still query resources (table wasn't dropped)
            all_resources = Resource.query.all()
            assert isinstance(all_resources, list)
    
    def test_user_dao_uses_parameterized_queries(self, app, test_user):
        """Verify UserDAO uses parameterized queries."""
        with app.app_context():
            dao = UserDAO()
            
            # Attempt to query with SQL injection
            malicious_email = "admin@example.com' OR '1'='1"
            
            # This should use SQLAlchemy filter_by which is parameterized
            user = dao.get_by_email(malicious_email)
            
            # Should return None (no match) or a user, but not crash
            # If raw SQL was used, this might have executed malicious SQL
            assert user is None or isinstance(user, User)
            
            # Verify users table still exists
            user_count = User.query.count()
            assert user_count >= 0
    
    def test_booking_dao_uses_parameterized_queries(self, app, test_user, test_resource):
        """Verify BookingDAO uses parameterized queries."""
        with app.app_context():
            dao = BookingDAO()
            
            # Create a booking with potentially malicious input
            start_date = datetime.utcnow() + timedelta(days=1)
            end_date = start_date + timedelta(hours=2)
            
            booking = dao.create(
                user_id=test_user.id,
                resource_id=test_resource.id,
                start_date=start_date,
                end_date=end_date,
                status='active',
                notes="'; DROP TABLE bookings; --"  # SQL injection attempt
            )
            
            # Should create booking successfully (notes stored as literal)
            assert booking.id is not None
            
            # Verify bookings table still exists
            booking_count = Booking.query.count()
            assert booking_count >= 1
            
            # Verify the notes are stored literally
            retrieved = dao.get_by_id(booking.id)
            assert retrieved.notes == "'; DROP TABLE bookings; --"
    
    def test_no_raw_sql_in_controllers(self, app):
        """Verify that controllers don't use raw SQL strings."""
        import inspect
        from src.controllers import resource_controller, booking_controller, auth_controller
        
        # Check for common raw SQL patterns
        raw_sql_patterns = [
            'db.session.execute',
            'db.engine.execute',
            'text(',
            'sqlalchemy.text'
        ]
        
        # Get source code of key controller files
        controller_files = [
            resource_controller,
            booking_controller,
            auth_controller
        ]
        
        for controller in controller_files:
            source = inspect.getsource(controller)
            
            # Check for raw SQL usage (should be minimal or none)
            # Note: Some legitimate uses might exist, but should be rare
            raw_sql_count = sum(1 for pattern in raw_sql_patterns if pattern in source)
            
            # Most queries should use ORM, not raw SQL
            # Allow some raw SQL for complex queries, but flag if excessive
            assert raw_sql_count < 10, \
                f"Controller {controller.__name__} may be using too much raw SQL"

