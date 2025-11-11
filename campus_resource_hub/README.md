# Campus Resource Hub

A full-stack web application for managing and booking campus resources (study rooms, computer labs, AV equipment, event spaces, etc.). Built with Flask, SQLAlchemy, and Bootstrap 5, featuring an AI-powered Resource Concierge assistant.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Features
- **User Management**: Registration, authentication, role-based access (Student, Staff, Admin)
- **Resource Management**: CRUD operations for resources with lifecycle (draft/published/archived)
- **Advanced Search**: Keyword, category, location, capacity, and availability-based filtering
- **Booking System**: Calendar-based booking with conflict detection, recurrence, and approval workflows
- **Messaging**: User-to-user messaging with admin moderation
- **Reviews & Ratings**: 1-5 star ratings with text reviews and aggregate calculations
- **Notifications**: Simulated notification system for booking events
- **Admin Dashboard**: Full CRUD operations, analytics, and content moderation

### Advanced Features
- **AI Resource Concierge**: OpenAI GPT-4o-mini powered chatbot for natural language resource queries
- **Waitlist System**: Join waitlists for unavailable resources with automatic notifications
- **Calendar Integration**: iCal export and subscription links for calendar applications
- **Image Carousel**: Multiple images per resource with auto-advance
- **Recurrence Support**: Daily, weekly, and monthly recurring bookings
- **Personal Calendar**: Full calendar view of user bookings with multiple view options
- **Analytics Dashboard**: 8 comprehensive reports with Chart.js visualizations

---

## Technology Stack

### Backend
- **Python 3.10+**
- **Flask 2.2.5** - Web framework
- **SQLAlchemy 1.4.41** - ORM
- **Flask-Migrate 4.0.4** - Database migrations
- **Flask-Login 0.6.2** - Authentication
- **Flask-WTF 1.1.1** - Form handling and CSRF protection
- **Flask-Bcrypt 1.0.1** - Password hashing
- **OpenAI API** - AI Concierge (GPT-4o-mini)

### Database
- **SQLite** - Development (default)
- **PostgreSQL** - Production (optional)

### Frontend
- **Jinja2** - Template engine
- **Bootstrap 5** - UI framework
- **FullCalendar.js** - Calendar interface
- **Chart.js** - Data visualization

### Development Tools
- **pytest 7.4.0** - Testing framework
- **python-dotenv 1.0.0** - Environment variable management

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Git** (for version control)
- **OpenAI API Key** (for Resource Concierge feature - optional but recommended)

### Checking Python Version

```bash
python --version
# or
python3 --version
```

You should see Python 3.10 or higher.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd campus_resource_hub
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including Flask, SQLAlchemy, and other dependencies.

### 4. Set Up Environment Variables

Create a `.env` file in the `campus_resource_hub` directory:

```bash
# Copy the example file (if it exists)
cp .env.example .env
```

Or create a new `.env` file with the following content:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration (optional - defaults to SQLite)
# DATABASE_URL=sqlite:///instance/campus_resource_hub.db

# OpenAI API Configuration (required for Resource Concierge)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Important**: 
- Replace `your-secret-key-here-change-in-production` with a secure random string
- Replace `your-openai-api-key-here` with your actual OpenAI API key (get one at https://platform.openai.com/api-keys)
- The `.env` file is in `.gitignore` and will not be committed to version control

---

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | No | SQLite in `instance/` folder |
| `OPENAI_API_KEY` | OpenAI API key for Resource Concierge | No* | None |
| `OPENAI_MODEL` | OpenAI model to use | No | `gpt-4o-mini` |

*Required if you want to use the Resource Concierge feature. The application will run without it, but the chatbot will not be available.

### Configuration Files

- **`src/config.py`**: Application configuration classes
- **`.env`**: Environment variables (not in version control)
- **`instance/`**: Database files and instance-specific data

---

## Database Setup

### Option 1: Automatic Setup (Recommended for First-Time Setup)

The application will automatically create database tables when you first run it:

```bash
python run.py
```

This will create the SQLite database file at `instance/campus_resource_hub.db` with all required tables.

### Option 2: Using Flask-Migrate (Recommended for Development and Production)

Flask-Migrate provides version-controlled database migrations. This is the recommended approach for managing schema changes.

#### Check Migration Status

First, check if migrations are already initialized and view current status:

```bash
# Check current database revision
flask db current

# View migration history
flask db history
```

#### Initialize Migrations (First Time Only - Already Done)

If migrations haven't been initialized (they already are in this project):

```bash
flask db init
```

This creates the `migrations/` directory structure. **Note**: This is already done in this project, so you typically won't need to run this.

#### Create a New Migration

When you modify database models (in `src/models/`), create a migration:

```bash
flask db migrate -m "Description of changes"
```

**Example**:
```bash
flask db migrate -m "Add department field to users table"
```

This will:
1. Compare current models to the database state
2. Generate a migration script in `migrations/versions/`
3. Include the description you provided

**Important**: Always review the generated migration file in `migrations/versions/` before applying it!

#### Apply Migrations

To apply pending migrations to the database:

```bash
flask db upgrade
```

This applies all migrations that haven't been applied yet.

**Apply to specific revision**:
```bash
flask db upgrade head  # Apply all pending migrations
flask db upgrade <revision>  # Apply to specific revision
```

#### Rollback Migrations

To roll back the last migration:

```bash
flask db downgrade
```

**Roll back to specific revision**:
```bash
flask db downgrade -1  # Roll back one migration
flask db downgrade <revision>  # Roll back to specific revision
```

#### Viewing Migration Information

```bash
# See current database revision
flask db current

# View all migrations (past and future)
flask db history

# View detailed information about a specific revision
flask db show <revision>
```

#### Migration Best Practices

1. **Always review migrations** before applying them
2. **Test migrations** on a copy of production data first
3. **Commit migration files** to version control
4. **Use descriptive messages** when creating migrations
5. **One logical change per migration** when possible
6. **Backup before migrating** in production environments
7. **Test the downgrade path** to ensure reversibility

#### Troubleshooting Migrations

**Database Out of Sync**:
```bash
# Check current revision
flask db current

# View migration history
flask db history

# Apply all pending migrations
flask db upgrade head
```

**Migration Conflicts**:
- Review the migration files in `migrations/versions/`
- Check for manual database changes
- Resolve conflicts manually if needed
- Create a new migration to sync state

**Fresh Start (Development Only)**:
```bash
# Delete the database
rm instance/campus_resource_hub.db  # Linux/macOS
del instance\campus_resource_hub.db  # Windows

# Recreate from migrations
flask db upgrade

# Or recreate from models
python -c "from src.app import create_app; from src.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

**⚠️ Warning**: This will delete all data! Only use in development.

For more detailed migration documentation, see `migrations/README`.

### Option 3: Manual Database Creation

If you prefer to create tables manually:

```python
from src.app import create_app
from src.extensions import db

app = create_app('development')
with app.app_context():
    db.create_all()
```

### Seeding the Database

To populate the database with test data:

```bash
python seed_data.py
```

This creates:
- Sample users (admin, staff, students)
- Sample resources (study rooms, labs, equipment)
- Sample bookings
- Sample reviews

**Default Admin Credentials** (from seed data):
- Email: `admin@example.com`
- Password: `admin123`

**Note**: Change the admin password immediately in production!

---

## Running the Application

### Development Mode

```bash
python run.py
```

The application will start on `http://localhost:5000` (or `http://127.0.0.1:5000`).

### Using Flask CLI

```bash
flask run
```

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

Or set environment variables:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
python run.py
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_booking_logic.py

# Run with coverage
pytest --cov=src tests/
```

### Test Structure

- **`tests/test_data_access.py`**: Data Access Layer tests
- **`tests/test_integration.py`**: Integration tests
- **`tests/test_booking_logic.py`**: Booking logic tests
- **`tests/ai_eval/test_ai_generated_features.py`**: AI code evaluation tests

### Test Configuration

Tests use an in-memory SQLite database and have CSRF protection disabled for easier testing.

---

## Project Structure

```
campus_resource_hub/
├── src/                          # Application source code
│   ├── app.py                    # Flask application factory
│   ├── config.py                 # Configuration classes
│   ├── extensions.py             # Flask extensions initialization
│   ├── forms.py                  # WTForms form definitions
│   ├── models/                   # SQLAlchemy ORM models
│   ├── controllers/              # Flask blueprints (routes)
│   ├── data_access/              # Data Access Layer (DAO classes)
│   ├── views/                    # Jinja2 templates
│   │   └── templates/
│   ├── static/                   # Static files (CSS, images, uploads)
│   ├── utils/                    # Utility functions
│   └── ai_features/              # AI Concierge feature
│       └── concierge/
├── migrations/                   # Flask-Migrate database migrations
│   └── versions/                 # Migration version files
├── tests/                        # Test suite
├── docs/                         # Documentation
│   └── context/                  # Context files for AI Concierge
├── instance/                     # Instance-specific files (database, etc.)
├── .prompt/                      # AI development documentation
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── seed_data.py                  # Database seeding script
└── README.md                     # This file
```

### Key Directories

- **`src/models/`**: Database models (User, Resource, Booking, etc.)
- **`src/controllers/`**: Route handlers organized by feature
- **`src/data_access/`**: Data Access Objects (DAO) for database operations
- **`src/views/templates/`**: HTML templates with Jinja2
- **`src/static/`**: Static assets (CSS, JavaScript, uploaded images)
- **`migrations/`**: Database migration scripts
- **`docs/context/`**: Documentation files used by AI Concierge

---

## API Documentation

### Main Routes

#### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/register` - Registration page
- `POST /auth/register` - Process registration
- `GET /auth/logout` - Logout

#### Resources
- `GET /resources/search` - Search and filter resources
- `GET /resources/<id>` - View resource details
- `GET /resources/<id>/book` - Book a resource
- `POST /resources/<id>/book` - Process booking
- `GET /resources/category/<category>` - Browse by category
- `GET /resources/new` - Create resource (staff/admin)
- `POST /resources/new` - Process resource creation

#### Bookings
- `GET /bookings` - View user's bookings
- `GET /bookings/<id>` - View booking details
- `GET /bookings/calendar` - Personal calendar view
- `GET /bookings/export/ical` - Export bookings to iCal
- `POST /bookings/subscription/generate` - Generate iCal subscription link

#### Messages
- `GET /messages` - Inbox
- `GET /messages/sent` - Sent messages
- `GET /messages/compose` - Compose message
- `POST /messages/send` - Send message
- `GET /messages/<id>` - View message

#### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/resources` - Resource management
- `GET /admin/bookings` - Booking management
- `GET /admin/reports` - Analytics reports
- `GET /admin/logs` - Admin action logs

#### AI Concierge
- `POST /concierge/query` - Process user query
- `GET /concierge/health` - Check AI service availability

---

## Deployment

### Production Checklist

1. **Environment Variables**
   - Set `SECRET_KEY` to a secure random string
   - Set `DATABASE_URL` to production database
   - Set `OPENAI_API_KEY` if using Resource Concierge
   - Set `FLASK_ENV=production`

2. **Database**
   - Use PostgreSQL for production (recommended)
   - Run migrations: `flask db upgrade`
   - Seed initial data if needed

3. **Static Files**
   - Configure web server to serve static files
   - Set up proper file upload directory permissions

4. **Security**
   - Use HTTPS
   - Set secure session cookies
   - Configure CORS if needed
   - Review CSRF settings

5. **WSGI Server**
   - Use Gunicorn, uWSGI, or similar
   - Configure reverse proxy (Nginx, Apache)

See `DEPLOYMENT.md` for detailed deployment instructions.

---

## Troubleshooting

### Common Issues

#### Database Errors

**Issue**: `OperationalError: no such column`
- **Solution**: Run database migrations: `flask db upgrade`
- Or manually create tables: `python -c "from src.app import create_app; from src.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"`

#### Import Errors

**Issue**: `ModuleNotFoundError`
- **Solution**: Ensure virtual environment is activated and dependencies are installed: `pip install -r requirements.txt`

#### OpenAI API Errors

**Issue**: Resource Concierge not working
- **Solution**: 
  1. Check that `OPENAI_API_KEY` is set in `.env` file
  2. Verify API key is valid
  3. Check internet connection
  4. Review error logs in Flask console

#### Port Already in Use

**Issue**: `Address already in use`
- **Solution**: 
  - Use a different port: `flask run --port 5001`
  - Or kill the process using port 5000

### Getting Help

- Check the logs in the Flask console for error messages
- Review the `docs/context/AiDD/` folder for detailed documentation
- Check `REQUIREMENTS_COMPLIANCE_REPORT.md` for feature documentation

---

## Contributing

### Development Workflow

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Write/update tests
4. Run tests: `pytest`
5. Commit changes: `git commit -m "Description"`
6. Push to branch: `git push origin feature-name`
7. Create a Pull Request

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex logic

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

---

## License

This project is part of the AiDD 2025 Capstone Project. See project requirements for licensing information.

---

## Additional Resources

- **Database Schema**: See `docs/context/AiDD/database_schema.md`
- **Project Summary**: See `docs/context/AiDD/project_summary.md`
- **Requirements Compliance**: See `docs/context/AiDD/REQUIREMENTS_COMPLIANCE_REPORT.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **AI Concierge Setup**: See `docs/context/AiDD/development_options.md`

---

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

