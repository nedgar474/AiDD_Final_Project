# Product Requirements Document (PRD)
## Campus Resource Hub

**Version:** 1.0  
**Date:** Fall 2025  
**Project Type:** AiDD 2025 Capstone Project  
**Status:** Production-Ready

---

## 1. Objective

The Campus Resource Hub is a full-stack web application designed to enable university departments, student organizations, and individuals to efficiently list, discover, and reserve campus resources. The system addresses the critical need for centralized resource management by providing a unified platform for booking study rooms, computer labs, AV equipment, lab instruments, event spaces, and other campus facilities.

**Primary Goals:**
- Streamline the resource booking process through an intuitive, calendar-based interface
- Enable efficient resource discovery through advanced search and filtering capabilities
- Support role-based access control to ensure appropriate resource management workflows
- Provide administrative tools for resource oversight, conflict resolution, and analytics
- Enhance user experience through AI-powered assistance and automated notifications

**Problem Statement:**
Currently, campus resource booking is fragmented across multiple systems, spreadsheets, or manual processes, leading to scheduling conflicts, underutilization of resources, and administrative overhead. The Campus Resource Hub consolidates these processes into a single, user-friendly platform that reduces conflicts, increases resource utilization, and provides valuable insights into campus resource usage patterns.

---

## 2. Stakeholders

### Primary Users

**Students**
- **Needs:** Easy discovery and booking of study spaces, equipment, and facilities
- **Pain Points:** Difficulty finding available resources, scheduling conflicts, lack of visibility into resource availability
- **Value:** Quick access to resources, conflict-free bookings, calendar integration

**Staff Members**
- **Needs:** Ability to list and manage department resources, approve bookings for restricted resources
- **Pain Points:** Manual approval processes, lack of visibility into resource usage
- **Value:** Streamlined resource management, booking approval workflows, usage insights

**Administrators**
- **Needs:** Comprehensive oversight of all resources, users, and bookings; analytics and reporting; content moderation
- **Pain Points:** Fragmented data, lack of centralized management, difficulty tracking usage
- **Value:** Centralized dashboard, analytics reports, automated conflict resolution, user management

### Secondary Stakeholders

**University IT Department**
- **Needs:** Secure, maintainable, scalable system architecture
- **Value:** Production-ready application with proper security, testing, and documentation

**Resource Owners (Departments/Organizations)**
- **Needs:** Visibility into resource bookings, ability to set approval requirements
- **Value:** Booking notifications, resource utilization data, approval workflows

**Project Team (Development)**
- **Needs:** Clear requirements, testable features, maintainable codebase
- **Value:** Well-documented system, comprehensive test coverage, modular architecture

---

## 3. Non-Goals

The following features and capabilities are explicitly **out of scope** for this version:

1. **Payment Processing:** No billing, invoicing, or payment integration for resource usage fees.

2. **Multi-tenant Support:** The system is designed for a single university campus, not multiple institutions or organizations.

3. **Resource Maintenance Scheduling:** Equipment maintenance, repair tracking, and service history are not included.

4. **Social Features:** User profiles, social connections, resource sharing between users, and community features are not included.

5. **Access Control Integration:** Integration with campus card systems, door access control, or physical security systems is not included.

---

## 4. Core Features

### 4.1 User Management & Authentication
- **User Registration:** Email and password-based registration with role selection (Student, Staff, Admin)
- **Authentication:** Secure login/logout with bcrypt password hashing
- **Role-Based Access Control:** Three roles (Student, Staff, Admin) with appropriate permissions
- **Profile Management:** Users can view and edit their profile information
- **Account Management:** Admins can suspend/unsuspend users, manage user accounts

### 4.2 Resource Listings
- **Resource CRUD Operations:** Create, read, update, and delete resources with comprehensive metadata
- **Resource Fields:** Title, description, multiple images (carousel), category, location, capacity, equipment lists, owner assignment
- **Resource Lifecycle:** Draft → Published → Archived status workflow
- **Resource Ownership:** Resources can be assigned to specific users or departments
- **Approval Requirements:** Resources can be marked as requiring approval for bookings

### 4.3 Search & Filter
- **Keyword Search:** Full-text search across resource titles and descriptions
- **Category Filtering:** Filter resources by category (Room, Equipment, Space, etc.)
- **Location Filtering:** Search by location with partial matching
- **Availability Filtering:** Filter by date/time availability with conflict detection
- **Capacity Filtering:** Filter by minimum capacity requirements
- **Sort Options:** Sort by title (A-Z), most recent, most booked, or top rated

### 4.4 Booking & Scheduling
- **Calendar-Based Booking:** Visual calendar interface (FullCalendar.js) for intuitive time selection
- **Recurrence Support:** Daily, weekly, and monthly recurring bookings with end date
- **Conflict Detection:** Automatic detection of time overlaps and capacity limits
- **Approval Workflow:** Automatic approval for open resources; staff/admin approval for restricted resources
- **Booking Management:** Users can view, edit, and cancel their bookings
- **Recurring Series Management:** Recurring bookings displayed as single entries with instance counts

### 4.5 Messaging & Notifications
- **User Messaging:** Email-like messaging system between users (inbox/sent folders)
- **Message Moderation:** Admin can flag, hide, and moderate messages
- **Notification System:** Simulated notifications for booking events (created, approved, rejected, cancelled, modified)
- **Notification Center:** Centralized notification management with filtering and pagination
- **Real-time Badge:** Unread notification count displayed in navigation

### 4.6 Reviews & Ratings
- **Rating System:** 1-5 star ratings for resources
- **Text Reviews:** Optional text reviews with resource feedback
- **Aggregate Calculations:** Average rating and review count displayed on resources
- **Top-Rated Badges:** Visual indicators for highest and lowest rated resources
- **Review Moderation:** Admins can edit, hide, or delete reviews

### 4.7 Admin Dashboard
- **User Management:** Full CRUD operations for users (create, edit, suspend, delete)
- **Resource Management:** Complete resource administration with image uploads
- **Booking Management:** View, edit, approve, reject, and delete bookings
- **Content Moderation:** Moderate reviews and flagged messages
- **Analytics Dashboard:** 8 comprehensive reports with Chart.js visualizations:
  - Active Resources by Status
  - Total Bookings (Last 30 Days)
  - Category Utilization Summary
  - Average Booking Duration per Category
  - Resource Ratings vs. Booking Volume
  - Bookings per User Role
  - Booking Status Distribution
  - Admin Actions Log Summary
- **Admin Logs:** Audit trail of all administrative actions

### 4.8 Advanced Features (Optional)
- **AI Resource Concierge:** OpenAI GPT-4o-mini powered chatbot for natural language resource queries
- **Waitlist System:** Join waitlists for unavailable resources with automatic notifications
- **Calendar Integration:** iCal export and subscription links for external calendar applications
- **Personal Calendar:** Full calendar view of user bookings with multiple view options (day, week, month, list)

---

## 5. Success Metrics

### 5.1 Functional Metrics

**Booking Efficiency**
- **Target:** 95% of booking attempts complete successfully without conflicts
- **Measurement:** Ratio of successful bookings to total booking attempts
- **Current Status:** Conflict detection prevents overlapping bookings; capacity checking ensures availability

**Resource Utilization**
- **Target:** Increase resource utilization by 20% compared to manual processes
- **Measurement:** Percentage of time resources are booked vs. available
- **Tracking:** Admin analytics dashboard provides utilization reports by category and resource

**User Adoption**
- **Target:** 80% of active campus users register within first semester
- **Measurement:** Number of registered users vs. total campus population
- **Tracking:** Admin dashboard user statistics

### 5.2 User Experience Metrics

**Search Effectiveness**
- **Target:** Users find desired resources within 3 search attempts
- **Measurement:** Average number of searches before successful booking
- **Tracking:** Search query logs and booking conversion rates

**Booking Completion Time**
- **Target:** Average booking time under 2 minutes from search to confirmation
- **Measurement:** Time from resource search to booking confirmation
- **Tracking:** User session analytics and booking flow completion rates

**AI Concierge Usage**
- **Target:** 30% of users interact with AI Concierge for resource discovery
- **Measurement:** Percentage of users who use AI Concierge feature
- **Tracking:** Concierge query logs and user engagement metrics

### 5.3 Technical Metrics

**System Reliability**
- **Target:** 99.5% uptime during business hours
- **Measurement:** System availability percentage
- **Tracking:** Server monitoring and error logs

**Security Compliance**
- **Target:** Zero security incidents (SQL injection, XSS, CSRF attacks)
- **Measurement:** Number of security vulnerabilities detected
- **Tracking:** Security audit results, penetration testing

**Test Coverage**
- **Target:** 80% code coverage with unit, integration, and end-to-end tests
- **Measurement:** Percentage of code covered by automated tests
- **Tracking:** pytest coverage reports

**Performance**
- **Target:** Page load times under 2 seconds for 95% of requests
- **Measurement:** Average response time for key pages
- **Tracking:** Application performance monitoring

### 5.4 Business Metrics

**Administrative Efficiency**
- **Target:** Reduce administrative time for resource management by 40%
- **Measurement:** Time spent on resource management tasks
- **Tracking:** Admin action logs and workflow completion times

**Conflict Resolution**
- **Target:** Reduce booking conflicts by 90% compared to manual scheduling
- **Measurement:** Number of booking conflicts detected and prevented
- **Tracking:** Conflict detection logs and booking statistics

**User Satisfaction**
- **Target:** Average resource rating of 4.0+ stars
- **Measurement:** Average rating across all resources
- **Tracking:** Review and rating data from user feedback

---

## 6. Technical Constraints

- **Technology Stack:** Python 3.10+, Flask, SQLAlchemy, Bootstrap 5, SQLite (PostgreSQL optional)
- **Architecture:** Model-View-Controller (MVC) with Data Access Layer (DAL)
- **Security:** CSRF protection, XSS prevention, SQL injection protection, password hashing (bcrypt)
- **Testing:** pytest framework with unit, integration, and end-to-end tests
- **Documentation:** Comprehensive README, API documentation, ERD diagram, migration guides

---

## 7. Future Considerations

While not included in the current scope, the following features may be considered for future iterations:

- Real-time messaging with WebSocket support
- Mobile native applications (iOS/Android)
- Additional AI features (embedding-based search, predictive analytics)
- Payment processing integration
- External calendar OAuth sync (Google Calendar, Outlook)
- Multi-tenant support for multiple campuses
- Resource maintenance scheduling
- Advanced custom reporting and data export
- Social features and user communities
- Access control system integration

---

**Document Owner:** Team 15
**Last Updated:** Fall 2025  
**Next Review:** End of Capstone Project

