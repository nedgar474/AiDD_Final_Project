# Test Suite for Campus Resource Hub

This directory contains the comprehensive test suite for the Campus Resource Hub application.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── test_data_access.py            # Unit tests for Data Access Layer (DAL)
├── test_booking_logic.py         # Unit tests for booking business logic
├── test_integration.py            # Integration tests for complete workflows
├── test_booking_legacy.py         # Legacy booking tests (migrated)
├── test_db_legacy.py              # Legacy database tests (migrated)
├── test_all_models_legacy.py     # Legacy model tests (migrated)
└── ai_eval/                       # AI evaluation tests
    ├── __init__.py
    └── test_ai_generated_features.py
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_data_access.py
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Run only unit tests:
```bash
pytest tests/test_data_access.py tests/test_booking_logic.py
```

### Run only integration tests:
```bash
pytest tests/test_integration.py
```

### Run AI evaluation tests:
```bash
pytest tests/ai_eval/
```

## Test Categories

### 1. Data Access Layer Tests (`test_data_access.py`)
Tests verify that:
- DAL classes properly encapsulate database operations
- CRUD operations work correctly
- Query methods return expected results
- No direct ORM queries are needed in controllers

### 2. Business Logic Tests (`test_booking_logic.py`)
Tests verify:
- Booking conflict detection
- Status transitions
- Date range queries
- Capacity checking

### 3. Integration Tests (`test_integration.py`)
Tests verify complete workflows:
- User registration and login
- Booking creation
- Resource management
- End-to-end user journeys

### 4. AI Evaluation Tests (`ai_eval/test_ai_generated_features.py`)
Tests verify:
- AI-generated code follows project patterns
- Consistency across DAL implementations
- Code quality standards

## Fixtures

The `conftest.py` file provides reusable fixtures:
- `app`: Flask application instance
- `client`: Test client for making requests
- `test_user`: Sample user for testing
- `test_admin`: Sample admin user
- `test_resource`: Sample resource
- `test_booking`: Sample booking

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage of business logic
- **Integration Tests**: All major user workflows
- **DAL Tests**: 100% coverage of data access methods

## Notes

- Tests use a temporary SQLite database that is created and destroyed for each test session
- CSRF protection is disabled in test configuration for easier testing
- All tests run in isolated database transactions

