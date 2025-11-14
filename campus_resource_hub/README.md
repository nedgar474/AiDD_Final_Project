# Campus Resource Hub

A full-stack web application for managing and booking campus resources (study rooms, computer labs, AV equipment, event spaces, etc.). Built with Flask, SQLAlchemy, and Bootstrap 5, featuring an AI-powered Resource Concierge assistant.

**Project Type:** AiDD 2025 Capstone Project  
**Module:** AI Driven Development (AiDD / X501)  
**Instructor:** Prof. Jay Newquist

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Application Architecture](#application-architecture)
- [AI-First Development & Context Pack](#ai-first-development--context-pack)
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
- [Additional Resources](#additional-resources)

---

## Features

### Core Features (Required)

1. **User Management & Authentication**
   - Sign up, sign in, sign out (email + password)
   - Passwords stored hashed (bcrypt)
   - Roles: Student, Staff, Admin with role-based access control

2. **Resource Listings**
   - CRUD operations for resources
   - Fields: title, description, images, category, location, availability rules, owner, capacity, equipment lists
   - Listing lifecycle: draft → published → archived

3. **Search & Filter**
   - Search by keyword, category, location, availability date/time, and capacity
   - Sort options: recent, most booked, top rated

4. **Booking & Scheduling**
   - Calendar-based booking flow with start/end time
   - Recurrence option (daily, weekly, monthly)
   - Conflict detection and capacity checking
   - Approval workflow: automatic for open resources, staff/admin approval for restricted resources

5. **Messaging & Notifications**
   - Email-like messaging system between users
   - Simulated notifications for booking events (created, approved, rejected, cancelled, modified)
   - Notification center with filtering and pagination

6. **Reviews & Ratings**
   - 1-5 star ratings for resources
   - Text reviews with aggregate rating calculations
   - Top-rated badges for highest and lowest rated resources

7. **Admin Panel**
   - Dashboard to manage users, resources, bookings
   - Moderate reviews and flagged messages
   - Analytics reports with 8 comprehensive visualizations
   - Admin action logs

8. **Documentation & Local Runbook**
   - README with setup and run instructions
   - requirements.txt with all dependencies
   - Database migration steps documented

### Advanced Features (Optional)

- **AI Resource Concierge**: OpenAI GPT-4o-mini powered chatbot for natural language resource queries
- **Waitlist System**: Join waitlists for unavailable resources with automatic notifications
- **Calendar Integration**: iCal export and subscription links for external calendar applications
- **Personal Calendar**: Full calendar view of user bookings with multiple view options
- **Analytics Dashboard**: 8 comprehensive reports with Chart.js visualizations

---

## Technology Stack

### Required Baseline

- **Backend**: Python 3.10+ with Flask 2.2.5
- **Database**: SQLite for local development (PostgreSQL optional for deployment)
- **Frontend**: Jinja2 templates (Flask) + Bootstrap 5
- **Auth**: Flask-Login 0.6.2 with Flask-Bcrypt 1.0.1 for password hashing
- **Testing**: pytest 7.4.0 for unit, integration, and end-to-end tests
- **Version Control**: GitHub (branching, PRs required)

### Additional Technologies

- **ORM**: SQLAlchemy 1.4.41
- **Migrations**: Flask-Migrate 4.0.4
- **Forms**: Flask-WTF 1.1.1 (CSRF protection)
- **AI**: OpenAI API (GPT-4o-mini) for Resource Concierge
- **Calendar**: FullCalendar.js for booking interface
- **Visualization**: Chart.js for admin analytics

---

## Application Architecture

The application follows a **Model-View-Controller (MVC) pattern** with a **Data Access Layer (DAL)** to separate presentation, business logic, and data access.

### Architecture Layers

1. **Model Layer** (`src/models/`)
   - SQLAlchemy ORM classes managing all database operations
   - 11 model classes: User, Resource, Booking, Message, Review, Notification, Waitlist, AdminLog, ResourceImage, CalendarSubscription
   - No raw SQL queries; all operations use ORM

2. **View Layer** (`src/views/templates/`)
   - HTML/Jinja2 templates rendering the interface
   - Organized by feature: admin/, bookings/, messages/, notifications/, profile/, resources/
   - Template inheritance with base.html

3. **Controller Layer** (`src/controllers/`)
   - Flask routes (blueprints) coordinating requests and responses
   - 8 blueprints: main_bp, auth_bp, resource_bp, booking_bp, message_bp, admin_bp, profile_bp, notification_bp
   - Decorators for authentication and authorization

4. **Data Access Layer** (`src/data_access/`)
   - Encapsulated database interactions (CRUD methods) in dedicated Python modules/classes
   - 9 DAO classes: UserDAO, ResourceDAO, BookingDAO, MessageDAO, ReviewDAO, NotificationDAO, WaitlistDAO, CalendarSubscriptionDAO
   - Controllers use DAO methods instead of direct ORM queries
   - Ensures controllers do not issue raw SQL

### Folder Structure

```
campus_resource_hub/
├── src/
│   ├── controllers/      # Flask routes and blueprints
│   ├── models/           # ORM classes or schema definitions
│   ├── views/            # HTML/Jinja templates
│   ├── data_access/     # Encapsulated CRUD logic
│   ├── static/           # Static files (CSS, images, uploads)
│   └── ai_features/      # AI Concierge feature
├── tests/                # Test suite
├── migrations/           # Flask-Migrate database migrations
└── docs/                # Documentation
```

---

## AI-First Development & Context Pack

This repository is configured for **AI-assisted and context-aware development** using Cursor AI, GitHub Copilot Agent Mode, and other AI tools. The folder structure helps AI tools understand the project's architecture and generate accurate, contextually relevant code.

### AI-First Folder Structure

#### `.prompt/` Folder
- **`dev_notes.md`**: Log of all AI interactions and outcomes throughout development
- **`golden_prompts.md`**: High-impact prompts and responses that were especially effective

#### `docs/context/` Folder (Context Pack)
This folder system collectively forms the **Context Pack**, a lightweight structure designed to help AI tools ground their reasoning in the project's goals, data, and user context.

- **`APA/`**: Artifacts from Agility, Processes & Automation module
  - BPMN future-state process models, acceptance tests, backlog CSVs
- **`DT/`**: Design Thinking artifacts
  - Personas, journey maps, usability findings
- **`PM/`**: Product Management materials
  - PRDs, OKRs, product strategy briefs, stakeholder maps
- **`shared/`**: Common items
  - Personas, glossary, OKRs shared across modules
- **`AiDD/`**: Project-specific context
  - Final Project Requirements, PRD, ERD diagram, database schema, compliance reports, demo steps

#### `tests/ai_eval/` Folder
- **Optional AI feature validation tests**
- Tests verify AI-generated code follows project patterns
- Validates AI-generated features align with project structure

### AI Integration & Collaboration

The Campus Resource Hub project integrates AI into both the development workflow and application functionality. Throughout development, AI tools (Cursor AI, GitHub Copilot) were used to assist with code generation, documentation, testing, and debugging. All AI interactions are documented in `.prompt/dev_notes.md`, and AI-authored code is marked with attribution comments.

The **Resource Concierge** feature demonstrates context-aware AI integration. This OpenAI GPT-4o-mini powered chatbot uses a Retrieval-Augmented Generation (RAG) approach, referencing materials from `/docs/context/` (including PRDs, personas, acceptance tests, and project documentation) to answer natural language questions about campus resources. The concierge also queries the actual database via the Data Access Layer to provide accurate, real-time information about resource availability and bookings. This implementation showcases how AI can leverage project context to provide meaningful, grounded responses that never fabricate information.

#### Model Context Protocol (MCP) Integration

The project implements **Model Context Protocol (MCP)** to provide a safer, structured interface for AI agents to query the database. MCP enables read-only, secure database access for the AI Concierge feature.

**Key Features:**
- **Read-Only Access**: MCP server provides structured, read-only database queries
- **Role-Based Filtering**: Enforces role-based access control (student, staff, admin)
- **Automatic Fallback**: Falls back to direct DAL access if MCP is unavailable
- **Environment Configuration**: Can be enabled/disabled via `USE_MCP` environment variable (default: enabled)

**MCP Methods:**
- `query_resources` - Search resources by query, role, category
- `get_resource_by_id` - Get specific resource details
- `get_resource_availability` - Check resource availability
- `get_resource_reviews` - Get reviews for a resource
- `get_categories` - List all resource categories

**Implementation Files:**
- `src/ai_features/mcp_server.py` - MCP server implementation
- `src/ai_features/concierge/mcp_client.py` - MCP client wrapper

The AI Concierge automatically uses MCP when available, ensuring secure, structured database access. See `.prompt/dev_notes.md` for detailed implementation notes.

### Ethical Considerations & AI Usage Transparency

**Ethical AI Development Practices:**

The Campus Resource Hub project adheres to ethical AI development principles throughout both the development process and application functionality:

1. **Code Review & Validation**
   - All AI-generated code and documentation was reviewed, tested, and validated before inclusion
   - No AI-generated code was used without human verification and testing
   - All AI-authored code is marked with attribution comments (`# AI Contribution: ...`)

2. **Academic Integrity & Transparency**
   - Comprehensive documentation of all AI interactions in `.prompt/dev_notes.md`
   - Detailed logging of prompts, tools used, and AI-influenced design decisions
   - Full transparency about AI usage as part of academic integrity requirements
   - All AI tools and their contributions are explicitly documented

3. **Data Privacy & Security**
   - AI Concierge uses read-only database access via MCP (Model Context Protocol)
   - Role-based access control ensures users only see information appropriate to their role
   - No user data is sent to external AI services beyond what's necessary for query processing
   - OpenAI API usage is limited to the Resource Concierge feature only

4. **Bias Mitigation**
   - AI responses are grounded in actual database data and project documentation
   - The RAG approach prevents AI from fabricating information
   - Context Pack ensures AI responses align with project requirements and user needs
   - All AI-generated content is validated against project specifications

5. **User Safety**
   - AI Concierge provides helpful guidance but never executes actions on behalf of users
   - All booking and resource management actions require explicit user confirmation
   - Error handling prevents AI from causing system failures or data corruption
   - Rate limiting and caching reduce API costs and prevent abuse

6. **Documentation & Accountability**
   - All AI interactions are logged in `.prompt/dev_notes.md`
   - High-impact prompts and responses are documented in `.prompt/golden_prompts.md`
   - Clear attribution of AI contributions throughout the codebase
   - Regular review of AI-generated code to ensure quality and correctness

**AI Tools Used:**
- **Cursor AI**: Primary development assistant for code generation, refactoring, and debugging
- **GitHub Copilot**: Code completion and suggestion assistance
- **OpenAI GPT-4o-mini**: Resource Concierge chatbot functionality

**AI Contribution Scope:**
- Code generation and scaffolding
- Documentation writing and editing
- Test case generation
- Bug diagnosis and fixes
- Database migration assistance
- UI/UX improvements

All AI contributions were reviewed, tested, and validated by the development team before integration.

### README Requirement

As required by the project specifications, this README describes the folder purpose and AI integration. The Context Pack structure enables AI tools to understand project requirements, user needs, and business context, allowing for more accurate code generation, documentation, and testing assistance.

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
git clone https://github.com/nedgar474/AiDD_Final_Project.git
cd AiDD_Final_Project/campus_resource_hub
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
- Sample resources (study rooms, labs, equipment) **with associated images**
- Sample bookings
- Sample reviews

**Note**: The seed script creates resources with their ResourceImage records linked, so resources will display with image carousels. The image files must exist in `src/static/uploads/` for the images to display properly.

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

As required by the project specifications, the application includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_booking_logic.py
pytest tests/test_data_access.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=src tests/
```

### Test Structure

The test suite includes the following required tests:

1. **Unit Tests for Booking Logic** (`tests/test_booking_logic.py`)
   - Conflict detection tests
   - Status transition tests
   - Booking query tests

2. **Data Access Layer Tests** (`tests/test_data_access.py`)
   - Tests verifying CRUD operations independently from Flask route handlers
   - Tests for all DAO classes (UserDAO, ResourceDAO, BookingDAO, etc.)
   - Ensures DAL properly encapsulates database operations

3. **Integration Tests** (`tests/test_integration.py`)
   - Auth flow test (register → login → access protected route)
   - Booking workflow test (end-to-end scenario demonstrating booking a resource through the UI)
   - Resource management workflow tests

4. **AI Code Evaluation Tests** (`tests/ai_eval/test_ai_generated_features.py`)
   - Tests verifying AI-generated code follows project patterns
   - Validates AI-generated DAL code integration

### Test Configuration

Tests use an in-memory SQLite database and have CSRF protection disabled for easier testing.

### Security Checks

The test suite includes security checks:
- **SQL Injection Protection**: All database queries use SQLAlchemy ORM (parameterized by default)
- **Template Escaping**: Jinja2 automatically escapes template variables to prevent XSS
- **File Upload Sanitization**: Tests verify `secure_filename()` is used for uploads

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
│   │   ├── user.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── message.py
│   │   ├── review.py
│   │   ├── notification.py
│   │   ├── waitlist.py
│   │   ├── admin_log.py
│   │   ├── resource_image.py
│   │   └── calendar_subscription.py
│   ├── controllers/              # Flask blueprints (routes)
│   │   ├── main_controller.py
│   │   ├── auth_controller.py
│   │   ├── resource_controller.py
│   │   ├── booking_controller.py
│   │   ├── message_controller.py
│   │   ├── admin_controller.py
│   │   ├── profile_controller.py
│   │   └── notification_controller.py
│   ├── data_access/              # Data Access Layer (DAO classes)
│   │   ├── base_dao.py
│   │   ├── user_dao.py
│   │   ├── resource_dao.py
│   │   ├── booking_dao.py
│   │   ├── review_dao.py
│   │   ├── message_dao.py
│   │   ├── notification_dao.py
│   │   ├── waitlist_dao.py
│   │   └── calendar_subscription_dao.py
│   ├── views/                    # Jinja2 templates
│   │   └── templates/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── admin/
│   │       ├── bookings/
│   │       ├── messages/
│   │       ├── notifications/
│   │       ├── profile/
│   │       └── resources/
│   ├── static/                   # Static files (CSS, images, uploads)
│   │   ├── css/
│   │   └── uploads/
│   ├── utils/                    # Utility functions
│   │   └── notifications.py
│   └── ai_features/              # AI Concierge feature
│       └── concierge/
│           ├── concierge_controller.py
│           ├── llm_client.py
│           ├── context_retriever.py
│           ├── database_retriever.py
│           ├── query_processor.py
│           ├── response_generator.py
│           ├── booking_proposer.py
│           ├── role_filter.py
│           └── context_summarizer.py
├── migrations/                   # Flask-Migrate database migrations
│   └── versions/                 # Migration version files
├── tests/                        # Test suite
│   ├── test_data_access.py       # DAL unit tests
│   ├── test_integration.py      # Integration tests
│   ├── test_booking_logic.py    # Booking logic unit tests
│   └── ai_eval/                 # AI code evaluation tests
│       └── test_ai_generated_features.py
├── docs/                         # Documentation
│   └── context/                  # Context Pack for AI tools
│       ├── APA/                  # Agility, Processes & Automation artifacts
│       ├── DT/                   # Design Thinking artifacts
│       ├── PM/                   # Product Management materials
│       ├── shared/               # Common items (personas, glossary, OKRs)
│       └── AiDD/                 # Project-specific context
│           ├── Final_Project_Requirements.md
│           ├── PRD.md
│           ├── ERD_Diagram.md
│           ├── database_schema.md
│           ├── REQUIREMENTS_COMPLIANCE_REPORT.md
│           └── ...
├── .prompt/                      # AI development documentation
│   ├── dev_notes.md              # Log of AI interactions and outcomes
│   └── golden_prompts.md         # High-impact prompts and responses
├── instance/                     # Instance-specific files (database, etc.)
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
├── seed_data.py                  # Database seeding script
└── README.md                     # This file
```

### Key Directories

- **`src/models/`**: Database models (User, Resource, Booking, etc.) - Model Layer
- **`src/controllers/`**: Route handlers organized by feature - Controller Layer
- **`src/data_access/`**: Data Access Objects (DAO) for database operations - Data Access Layer
- **`src/views/templates/`**: HTML templates with Jinja2 - View Layer
- **`src/static/`**: Static assets (CSS, JavaScript, uploaded images)
- **`migrations/`**: Database migration scripts
- **`docs/context/`**: Context Pack - Documentation files used by AI tools and Resource Concierge
- **`.prompt/`**: AI development documentation and prompt logs

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
- `GET /admin/reports` - Analytics reports (usage metrics)
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

## Additional Resources

### Documentation

- **Final Project Requirements**: `docs/context/AiDD/Final_Project_Requirements.md`
- **Product Requirements Document (PRD)**: `docs/context/AiDD/PRD.md`
- **Database Schema**: `docs/context/AiDD/database_schema.md`
- **ER Diagram**: `docs/context/AiDD/ERD_Diagram.md` (Mermaid format)
- **Requirements Compliance Report**: `docs/context/AiDD/REQUIREMENTS_COMPLIANCE_REPORT.md`
- **Project Summary**: `docs/context/AiDD/project_summary.md`
- **Demo Steps**: `docs/context/AiDD/Demo_Steps.md`
- **Deployment Guide**: `DEPLOYMENT.md`

### AI Development Documentation

- **AI Development Notes**: `.prompt/dev_notes.md` - Log of all AI interactions and outcomes
- **Golden Prompts**: `.prompt/golden_prompts.md` - High-impact prompts and responses

### Context Pack

The `docs/context/` folder contains the Context Pack, which includes:
- **APA/**: Agility, Processes & Automation artifacts (BPMN models, acceptance tests)
- **DT/**: Design Thinking artifacts (personas, journey maps)
- **PM/**: Product Management materials (PRDs, OKRs)
- **shared/**: Common items (personas, glossary, OKRs)
- **AiDD/**: Project-specific context and documentation

These materials help AI tools understand project requirements, user needs, and business context.

---

## License

This project is part of the AiDD 2025 Capstone Project. See project requirements for licensing information.

---

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

**GitHub Repository**: https://github.com/nedgar474/AiDD_Final_Project
