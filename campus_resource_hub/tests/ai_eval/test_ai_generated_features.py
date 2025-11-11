"""
AI Evaluation Tests for AI-Generated Features

These tests validate that AI-generated code follows project patterns,
maintains consistency, and meets quality standards.
"""
import pytest
from src.data_access import BaseDAO
from src.models.user import User


class TestAIGeneratedCodeQuality:
    """Test quality and consistency of AI-generated code."""
    
    def test_dal_follows_base_pattern(self, app):
        """Test that DAL classes follow the BaseDAO pattern."""
        with app.app_context():
            from src.data_access import UserDAO, ResourceDAO, BookingDAO
            
            # All DAOs should inherit from BaseDAO
            assert issubclass(UserDAO, BaseDAO)
            assert issubclass(ResourceDAO, BaseDAO)
            assert issubclass(BookingDAO, BaseDAO)
            
            # All DAOs should have model_class attribute
            user_dao = UserDAO()
            assert hasattr(user_dao, 'model_class')
            assert user_dao.model_class == User
    
    def test_dal_methods_consistent_naming(self, app):
        """Test that DAL methods follow consistent naming conventions."""
        with app.app_context():
            from src.data_access import UserDAO, BookingDAO
            
            user_dao = UserDAO()
            booking_dao = BookingDAO()
            
            # Common methods should exist
            assert hasattr(user_dao, 'get_by_id')
            assert hasattr(user_dao, 'create')
            assert hasattr(user_dao, 'update')
            assert hasattr(user_dao, 'delete')
            
            assert hasattr(booking_dao, 'get_by_id')
            assert hasattr(booking_dao, 'create')
            assert hasattr(booking_dao, 'update')
            assert hasattr(booking_dao, 'delete')
    
    def test_controllers_import_dal(self, app):
        """Test that controllers properly import and use DAL."""
        # This is a structural test - verifies the pattern
        import src.controllers.booking_controller as booking_ctrl
        
        # Should import DAOs
        assert hasattr(booking_ctrl, 'booking_dao')
        assert hasattr(booking_ctrl, 'waitlist_dao')
        assert hasattr(booking_ctrl, 'subscription_dao')

