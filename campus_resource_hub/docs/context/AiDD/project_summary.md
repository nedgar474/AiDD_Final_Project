# Campus Resource Hub - Project Summary

## Executive Overview

The Campus Resource Hub is a full-stack web application that enables university departments, student organizations, and individuals to list, share, and reserve campus resources. The system supports comprehensive search capabilities, calendar-based booking with conflict detection, role-based access control, user messaging, reviews and ratings, and administrative management tools. The application includes an AI-powered Resource Concierge assistant that helps users find and book resources through natural language queries.

**Project Type**: Capstone project for AiDD 2025 (AI-Driven Development)
**Status**: Production-ready implementation with all core features and advanced optional features
**Architecture**: Model-View-Controller (MVC) with Data Access Layer (DAL)

---

## Application Architecture

### Technology Stack

**Backend**:
- Python 3.10+ with Flask 2.2.5
- SQLAlchemy 1.4.41 (ORM)
- Flask-Migrate 4.0.4 (database migrations)
- Flask-Login 0.6.2 (authentication)
- Flask-WTF 1.1.1 (form handling and CSRF protection)
- Flask-Bcrypt 1.0.1 (password hashing)
- OpenAI API (GPT-4o-mini) for AI Concierge

**Database**:
- SQLite for local development
- PostgreSQL optional for production deployment

**Frontend**:
- Jinja2 templates (server-side rendering)
- Bootstrap 5 (responsive UI framework)
- FullCalendar.js (calendar interface)
- Chart.js (data visualization for admin reports)
- Custom CSS and JavaScript

**AI Features**:
- OpenAI GPT-4o-mini for Resource Concierge
- Retrieval-Augmented Generation (RAG) approach
- Model Context Protocol (MCP) integration for secure database access
- Document context from `/docs/context/` markdown files
- Database context via Data Access Layer or MCP
- Rate limit handling and caching for API efficiency

### Project Structure

```
campus_resource_hub/
├── src/
│   ├── app.py                    # Flask application factory
│   ├── config.py                 # Configuration settings
│   ├── extensions.py             # Flask extension initialization
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
│   ├── data_access/              # Data Access Layer (DAL)
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
│   │       ├── dashboard.html
│   │       ├── resources/
│   │       ├── bookings/
│   │       ├── messages/
│   │       ├── admin/
│   │       └── ...
│   ├── static/                   # Static assets
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
├── docs/
│   └── context/                  # Context files for AI Concierge
│       └── AiDD/
├── migrations/                   # Flask-Migrate database migrations
├── tests/                        # Test suite
├── .prompt/                      # AI development documentation
│   ├── dev_notes.md
│   └── golden_prompts.md
└── requirements.txt
```

### Design Patterns

1. **MVC Architecture**: Clear separation of Models, Views, and Controllers
2. **Data Access Layer (DAL)**: Encapsulated database operations in DAO classes
3. **Blueprint Pattern**: Modular route organization
4. **Factory Pattern**: Flask application factory (`create_app()`)
5. **Repository Pattern**: DAO classes abstract database access

---

## Database Schema

### Core Tables (10 total)

1. **users**: User accounts, authentication, roles, suspension status
2. **resources**: Bookable resources with lifecycle status (draft/published/archived)
3. **bookings**: Reservations with recurrence support and status tracking
4. **messages**: User-to-user messaging with flagging and moderation
5. **reviews**: Resource ratings (1-5 stars) and text reviews
6. **notifications**: Simulated notification system for booking events
7. **waitlist**: Waitlist entries for unavailable resources
8. **admin_logs**: Audit trail of all administrative actions
9. **resource_images**: Multiple images per resource (carousel support)
10. **calendar_subscriptions**: iCal subscription tokens for calendar integration

### Key Relationships

- **User → Resources**: One-to-many (users can own multiple resources)
- **User → Bookings**: One-to-many (users can have multiple bookings)
- **Resource → Bookings**: One-to-many (resources can have multiple bookings)
- **Resource → Reviews**: One-to-many (resources can have multiple reviews)
- **Booking → Booking**: Self-referential (for recurring booking series)
- **User → Messages**: One-to-many (as sender and recipient)

See `database_schema.md` for complete schema documentation.

---

## User Roles and Permissions

### Student Role
- **Can**: View published resources, create bookings, leave reviews, send/receive messages, view own bookings
- **Cannot**: Create resources, access admin dashboard, view draft/archived resources
- **Restrictions**: Suspended students cannot book resources or send messages

### Staff Role
- **Can**: All student permissions, plus:
  - Create/edit resources
  - View all resources (including drafts)
  - Access limited administrative dashboard (resource and booking management only)
  - Manage resources and bookings through admin interface
- **Cannot**: 
  - Manage users or user accounts
  - Moderate messages or reviews
  - View admin logs or analytics reports
  - Access full admin dashboard features

### Admin Role
- **Can**: All staff permissions, plus:
  - Full CRUD operations on users, resources, bookings
  - User suspension/unsuspension
  - Message moderation (flag, hide, edit, delete)
  - Review moderation (edit, hide, delete)
  - View admin logs and reports
  - Access administrative dashboard with analytics

---

## Core Features

### 1. User Management & Authentication

**Features**:
- User registration with email and password
- Login/logout functionality
- Password hashing with Bcrypt
- Role-based access control (student, staff, admin)
- User profile management (view, edit, change password)
- User suspension system (prevents booking and messaging)
- Department field for user organization

**Routes**:
- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/profile` - View profile
- `/profile/edit` - Edit profile
- `/profile/password` - Change password

### 2. Resource Management

**Features**:
- Full CRUD operations for resources
- Resource fields: title, description, category, location, capacity, equipment list, owner
- Multiple images per resource (carousel display with auto-advance)
- Resource lifecycle: draft → published → archived
- Approval workflow: `requires_approval` flag determines if bookings need approval
- Resource status visibility: Only published resources visible to students
- Equipment lists as comma-separated text field
- Resource ownership assignment

**Routes**:
- `/resources/search` - Search and filter resources
- `/resources/<id>` - View resource details
- `/resources/<id>/book` - Book a resource
- `/resources/new` - Create resource (staff/admin)
- `/resources/category/<category>` - Browse by category
- `/admin/resources` - Admin resource management

### 3. Search & Filter

**Search Capabilities**:
- Keyword search (title and description)
- Category filter (dropdown)
- Location filter (text input with partial matching)
- Capacity filter (minimum capacity)
- Availability date/time filter (checks conflicts and capacity)
- Sort options:
  - Title (A-Z)
  - Most Recent
  - Most Booked
  - Top Rated

**Implementation**: SQLAlchemy queries with `ilike` for case-insensitive matching, conflict detection for availability filtering

### 4. Booking & Scheduling

**Features**:
- Calendar-based booking interface (FullCalendar.js)
- Three-click selection system (start, end, clear)
- Start/end date and time selection
- Recurrence options: daily, weekly, monthly with end date
- Conflict detection (time overlap and capacity checking)
- Booking approval workflow:
  - Automatic approval if `resource.requires_approval = False`
  - Pending approval if `resource.requires_approval = True`
- Booking statuses: pending, active, completed, cancelled
- Waitlist feature for unavailable resources
- Personal calendar page with multiple view options (day, week, month, list)
- iCal export for personal bookings
- iCal subscription links for calendar integration

**Routes**:
- `/resources/<id>/book` - Book a resource
- `/bookings` - View user's bookings
- `/bookings/<id>` - View booking details
- `/bookings/calendar` - Personal calendar view
- `/bookings/export/ical` - Export bookings to iCal
- `/bookings/subscription/generate` - Generate subscription link
- `/resources/<id>/waitlist` - Join waitlist

### 5. Messaging System

**Features**:
- User-to-user messaging (email-like, not threaded)
- Inbox, Sent, and Compose views
- Message flagging for admin review
- Read/unread status tracking
- Message moderation (admin can edit, hide, delete)
- "Message Owner" button on resource pages (modal)
- AJAX message sending without page reload
- Users can send messages to themselves

**Routes**:
- `/messages` - Inbox
- `/messages/sent` - Sent messages
- `/messages/compose` - Compose message
- `/messages/<id>` - View message
- `/admin/messages` - Admin message management

### 6. Reviews & Ratings

**Features**:
- 1-5 star rating system
- Text review (optional)
- One review per user per resource
- Users can edit or delete their own reviews
- Average rating calculation and percentage display
- Review pagination (10 per page)
- Top-rated badges (top 3 highest-rated resources)
- Lowest-rated badge (single lowest-rated resource, if at least 2 resources reviewed)
- Admin review moderation (edit, hide, delete)

**Routes**:
- `/resources/<id>/review` - Leave/edit review
- `/resources/<id>/review/delete` - Delete own review
- `/admin/reviews` - Admin review management

### 7. Notifications

**Features**:
- Simulated notification system (database-stored)
- 8 notification types:
  - Booking created
  - Booking approved
  - Booking rejected
  - Booking cancelled
  - Booking modified
  - Recurring series created
  - Waitlist available
  - Owner notified
- Notification center with pagination (20 per page)
- Filter by All/Unread/Read
- Mark as read/unread (single and bulk)
- Delete notifications
- Real-time badge count in navbar
- Styled modals for notification management

**Routes**:
- `/notifications` - Notification center
- `/notifications/<id>/read` - Mark as read
- `/notifications/<id>/unread` - Mark as unread
- `/notifications/mark-all-read` - Mark all as read

### 8. Admin Dashboard

**Features**:
- Full CRUD operations for users, resources, bookings
- User management: create, edit, delete, suspend/unsuspend
- Resource management: create, edit, delete, status management
- Booking management: create, edit, delete, status management
- Message moderation: view, edit, hide, delete flagged messages
- Review moderation: view, edit, hide, delete reviews
- Admin logs: paginated view of all administrative actions
- Analytics dashboard with 8 reports:
  1. Active Resources by Status (Bar chart)
  2. Total Bookings (Last 30 Days) (Line chart)
  3. Category Utilization Summary (Bar chart)
  4. Average Booking Duration per Category (Horizontal bar chart)
  5. Resource Ratings vs. Booking Volume (Scatter plot)
  6. Bookings per User Role (Pie chart)
  7. Booking Status Distribution (Donut chart)
  8. Admin Actions Log Summary (Bar chart)

**Routes**:
- `/admin/dashboard` - Admin dashboard
- `/admin/users` - User management
- `/admin/resources` - Resource management
- `/admin/bookings` - Booking management
- `/admin/messages` - Message moderation
- `/admin/reviews` - Review moderation
- `/admin/reports` - Analytics reports
- `/admin/logs` - Admin action logs

### 9. Resource Concierge (AI Assistant)

**Features**:
- AI-powered chatbot assistant (OpenAI GPT-4o-mini)
- Natural language queries about resources and booking
- Context retrieval from documentation and database
- Role-based access (students see published resources only)
- Booking proposal flow with "Book Now" / "Decline" buttons
- Resource links in responses
- Multi-step, comparative, and temporal query support
- Privacy protection (never reveals other users' data)
- Chatbot UI in lower right corner with full chat history
- Concise, readable responses without technical jargon
- Rate limit handling with user-friendly error messages
- Health check caching to reduce API calls

**Implementation**:
- Retrieval-Augmented Generation (RAG) approach
- Document context from `/docs/context/` markdown files
- Database context via Data Access Layer or Model Context Protocol (MCP)
- **Model Context Protocol (MCP) Integration**:
  - Read-only, secure database access for AI agents
  - Role-based filtering enforced at MCP level
  - Automatic fallback to direct DAL if MCP unavailable
  - Environment-configurable (USE_MCP variable)
  - Structured query interface preventing SQL injection
- Smart document prioritization and filtering
- Context summarization for long contexts
- Improved prompt engineering for concise, actionable responses

**Routes**:
- `/concierge/query` - Process user query (POST)
- `/concierge/health` - Check AI service availability (GET, cached)

---

## Advanced Features (Optional - Implemented)

### 1. Waitlist System
- Join waitlist when resource unavailable or at capacity
- Automatic notifications when resource becomes available
- Waitlist entry management (view details, cancel)
- **Auto-cancellation**: Expired waitlist entries automatically cancelled when requested time passes
- **Waitlist Details Page**: Dedicated page showing full waitlist entry information
- **Date Pre-population**: Start/end dates auto-populated from booking page when joining waitlist
- **Context-aware Navigation**: Cancel redirects to resource page when cancelled from details page

### 2. Calendar Integration
- iCal export for personal bookings
- iCal subscription links for calendar applications
- FullCalendar.js visual calendar interface
- Personal calendar page with multiple view options

### 3. Role-Based Analytics
- Category utilization reports
- Booking statistics by role
- Resource performance metrics
- Department-based analytics (structure in place)

### 4. Image Management
- Multiple images per resource
- Image carousel with navigation arrows and controls
- Display on home page and resource search pages
- Secure file upload with path traversal protection
- Image display order management
- Fallback to placeholder when no images available

### 5. Recurrence Support
- Daily, weekly, monthly recurrence options
- Recurrence end date specification
- Conflict detection per occurrence
- Linked booking series via `parent_booking_id`
- **Series Display**: Recurring bookings displayed as single entry with instance count
- **Series Cancellation**: Cancelling any booking in a series cancels the entire series
- **Safeguards**: Maximum limit (365 instances) and iteration protection to prevent infinite loops

---

## Security Features

### Authentication & Authorization
- Bcrypt password hashing with automatic salting
- Session-based authentication (Flask-Login)
- Role-based access control decorators
- User suspension system

### Input Validation
- Server-side validation with WTForms
- Type validation (string length, numeric ranges, email format)
- Date range validation (end > start)
- Custom validators for business logic

### Security Protections
- CSRF protection (Flask-WTF) on all forms
- XSS protection (Jinja2 automatic escaping)
- SQL injection protection (SQLAlchemy parameterized queries)
- File upload security:
  - File type restrictions (images only)
  - File size limits (16MB)
  - Path traversal protection (`secure_filename()`)
  - Safe storage outside web root

### Privacy
- Minimal PII collection
- Role-based data filtering
- Admin data removal capabilities
- User control over own data (reviews, bookings, messages)
- AI Concierge uses read-only database access (MCP)
- No user data sent to external AI services beyond query processing

### Ethical AI Development
- All AI-generated code reviewed, tested, and validated
- Comprehensive documentation of AI interactions in `.prompt/dev_notes.md`
- Full transparency about AI usage for academic integrity
- AI-authored code marked with attribution comments
- Bias mitigation through grounded responses (RAG approach)
- User safety: AI provides guidance but never executes actions
- Rate limiting and caching to reduce API costs and prevent abuse

---

## User Workflows

### Booking Workflow
1. User searches/browses resources
2. User views resource details (images, description, availability, reviews)
3. User selects booking time via calendar interface
4. System checks for conflicts and capacity
5. If available: Booking created (status based on `requires_approval`)
6. If unavailable: User offered waitlist option
7. Notifications sent to user and resource owner
8. If pending: Admin approves/rejects
9. User receives confirmation notification

### Resource Creation Workflow (Staff/Admin)
1. Staff/Admin navigates to "Create Resource"
2. Fills out resource form (title, description, category, location, capacity, etc.)
3. Uploads multiple images
4. Sets approval requirement and status
5. Resource saved as 'draft' by default
6. Admin can publish resource to make it visible to students

### Review Workflow
1. User views resource details
2. User clicks "Leave Review" (or "Edit Review" if exists)
3. User selects rating (1-5 stars) and optional text
4. Review saved and displayed on resource page
5. Average rating recalculated automatically
6. Top-rated badges updated dynamically

### Message Workflow
1. User views resource or profile
2. User clicks "Message Owner" or navigates to compose
3. **Reply Feature**: When replying, recipient and subject fields auto-populated with "Re: " prefix
4. User writes message and sends
5. Recipient receives notification
6. Recipient views message in inbox
7. If flagged: Admin can moderate message

---

## Current Implementation Status

### ✅ Fully Implemented Core Features
- User Management & Authentication (100%)
- Resource Listings (100%)
- Search & Filter (100%)
- Booking & Scheduling (100%)
- Messaging & Notifications (100% - email-like implementation)
- Reviews & Ratings (100%)
- Admin Panel (100%)
- Documentation structure in place

### ✅ Fully Implemented Advanced Features
- iCal Export (100%)
- Waitlist Features (100%)
- Resource Concierge AI Assistant (100%)
- Multiple Images per Resource (100%)
- Recurrence Support (100%)
- Personal Calendar Page (100%)
- iCal Subscription Links (100%)

### ✅ Recent Enhancements (2025)
- **Staff Admin Access**: Staff members can access limited admin dashboard for resource and booking management
- **MCP Integration**: Model Context Protocol implemented for secure AI database access
- **Waitlist Improvements**: Auto-cancellation, details page, date pre-population
- **Recurring Booking UX**: Series displayed as single entry, series-wide cancellation
- **Image Carousels**: Navigation controls on home and search pages
- **Message Reply**: Auto-populated recipient and subject fields
- **UI Styling**: IU brand guidelines implemented (crimson, gold, mint colors)
- **Banner Image**: Site-wide banner above navbar
- **Login Improvements**: Enhanced error handling and debugging
- **Seed Data**: Updated to include ResourceImage records with proper associations
- **Security Tests**: Comprehensive SQL injection and XSS protection tests
- **Docker Support**: Dockerfile, docker-compose.yml, and deployment documentation

### ⚠️ Partially Implemented
- Reviews not restricted to completed bookings (users can review any resource)
- Department-based analytics (structure exists, reports not implemented)
- Accessibility/WCAG (basic features implemented, no formal audit)

### ❌ Not Implemented
- Google Calendar OAuth Sync (iCal export available as alternative)
- Advanced search with embeddings (simple text matching used)
- Real-time messaging (email-like, not WebSocket-based)
- Threaded messages (individual messages, not grouped)

---

## Key Technical Decisions

### Architecture
- **MVC Pattern**: Clear separation of concerns
- **Data Access Layer**: Encapsulated database operations for maintainability
- **Blueprint Organization**: Modular route structure
- **Application Factory**: Flexible configuration and testing

### Database
- **SQLite for Development**: Easy setup and portability
- **Flask-Migrate**: Version-controlled schema changes
- **ORM Approach**: SQLAlchemy for type safety and relationships

### Security
- **Defense in Depth**: Multiple layers of security (validation, sanitization, escaping)
- **CSRF Protection**: Global protection with minimal exemptions
- **Password Security**: Bcrypt with automatic salting
- **Input Sanitization**: WTForms validation + custom validators

### AI Integration
- **OpenAI GPT-4o-mini**: Cloud-based LLM for Resource Concierge
- **RAG Approach**: Combines document and database context
- **Model Context Protocol (MCP)**: Secure, read-only database access for AI agents
- **Privacy-First**: Role-based filtering, no user data exposure
- **Context-Aware**: Smart document prioritization and filtering
- **Rate Limit Management**: Caching and user-friendly error handling
- **Ethical Practices**: Code review, transparency, bias mitigation, user safety

---

## Development Practices

### AI-First Development
- `.prompt/` folder for AI interaction documentation
- `docs/context/` folder for AI context awareness
- Golden prompts documented for reproducibility
- Development notes track all AI-assisted work

### Version Control
- GitHub for source control
- Branching and PR workflow
- Commit history tracks feature development

### Testing
- **pytest framework** configured with comprehensive test suite
- **Unit Tests**: Business logic, booking conflict detection, status transitions
- **Data Access Layer Tests**: CRUD operations independently tested
- **Integration Tests**: Auth flow, booking workflow, resource management
- **Security Tests**: SQL injection protection, XSS prevention, parameterized queries
- **AI Evaluation Tests**: Code consistency and pattern validation
- **Test Fixtures**: Properly configured to prevent DetachedInstanceError
- **Test Documentation**: Automated test result generation and coverage reports

### Documentation
- Comprehensive database schema documentation
- Requirements compliance report
- Development options and analysis
- Technical documentation in context folder

---

## Deployment Considerations

### Local Development
- SQLite database (no external dependencies)
- Environment variables via `.env` file
- OpenAI API key required for Resource Concierge
- Python 3.10+ required

### Production Deployment
- PostgreSQL recommended for database
- Environment variable configuration
- Static file serving optimization
- Database migration strategy
- **Docker Support**: 
  - Dockerfile for containerized deployment
  - docker-compose.yml for multi-container setup
  - Automatic database migrations on container start
  - Health checks configured
  - Production-ready configuration

---

## Future Enhancement Opportunities

### Short-Term
- Restrict reviews to completed bookings only
- Implement department-based analytics reports
- Formal WCAG accessibility audit
- Enhanced error handling and logging

### Medium-Term
- Google Calendar OAuth integration
- Advanced search with embeddings
- Real-time messaging (WebSocket)
- Threaded message conversations
- Email notification integration (currently simulated)

### Long-Term
- Mobile application
- API for third-party integrations
- Advanced analytics and machine learning insights
- Multi-tenant support for multiple campuses
- Equipment inventory management system

---

## Success Metrics

### Functional Metrics
- ✅ All 8 core requirements fully implemented
- ✅ 5+ advanced optional features implemented
- ✅ 100% compliance with security requirements
- ✅ Comprehensive admin dashboard with analytics

### Technical Metrics
- ✅ MVC architecture with DAL separation
- ✅ 10 database tables with proper relationships
- ✅ Role-based access control throughout
- ✅ AI-powered assistant with context retrieval
- ✅ Responsive UI with Bootstrap 5

### Quality Metrics
- ✅ Server-side validation on all inputs
- ✅ CSRF and XSS protection implemented
- ✅ Password security (Bcrypt hashing)
- ✅ File upload security
- ✅ Privacy controls and data minimization

---

## Recent Updates & Improvements

### UI/UX Enhancements
- **IU Brand Styling**: Implemented Indiana University brand guidelines with crimson, gold, and mint color palette
- **Banner Image**: Site-wide banner above navbar for visual branding
- **Image Carousels**: Enhanced resource display with navigation controls on home and search pages
- **Sidebar Positioning**: Fixed overlap issues with proper z-index and padding adjustments
- **Delete Modals**: Styled Bootstrap modals for booking deletion with CSRF protection

### Feature Improvements
- **Staff Admin Access**: Staff members can now manage resources and bookings through limited admin dashboard
- **Waitlist System**: Auto-cancellation of expired entries, dedicated details page, date pre-population
- **Recurring Bookings**: Improved UX with series display and series-wide cancellation
- **Message Replies**: Auto-populated recipient and subject fields for better user experience
- **AI Concierge**: More concise, readable responses without technical jargon

### Technical Improvements
- **MCP Integration**: Model Context Protocol for secure AI database access
- **Security Testing**: Comprehensive tests for SQL injection and XSS protection
- **Docker Support**: Full containerization with Dockerfile and docker-compose.yml
- **Test Infrastructure**: Improved fixtures, automated documentation, coverage reports
- **Error Handling**: Enhanced login error messages, rate limit handling, booking safeguards

### Documentation
- **README Updates**: Comprehensive AI integration, ethical considerations, and technical overview
- **ERD Diagram**: Full Mermaid ERD with complete attribute definitions
- **PRD**: Product Requirements Document with stakeholders and success metrics
- **Test Documentation**: Automated test result generation and compliance reports

## Conclusion

The Campus Resource Hub is a production-ready, full-featured web application that successfully implements all core requirements and multiple advanced features. The system demonstrates professional software development practices, comprehensive security measures, innovative AI integration with ethical considerations, and continuous improvement through iterative development. Recent enhancements include MCP integration, staff admin access, improved waitlist functionality, enhanced UI/UX, Docker support, and comprehensive testing. The application is well-structured, thoroughly documented, and ready for deployment or further enhancement.

