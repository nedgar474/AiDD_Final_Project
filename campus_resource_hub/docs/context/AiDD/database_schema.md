# Campus Resource Hub - Database Schema

## Overview

The Campus Resource Hub uses SQLite for local development (PostgreSQL optional for deployment). The database follows a relational model with 10 main tables supporting user management, resource booking, messaging, reviews, notifications, and administrative functions.

---

## Tables

### 1. users

**Description**: Stores user account information and authentication data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL | User email address (unique) |
| `username` | VARCHAR(80) | UNIQUE, NOT NULL | Username (unique) |
| `password_hash` | VARCHAR(128) | NOT NULL | Bcrypt hashed password |
| `first_name` | VARCHAR(50) | NULL | User's first name |
| `last_name` | VARCHAR(50) | NULL | User's last name |
| `department` | VARCHAR(100) | NULL | User's department |
| `role` | VARCHAR(20) | DEFAULT 'student' | User role: 'student', 'staff', 'admin' |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `is_suspended` | BOOLEAN | DEFAULT FALSE, NOT NULL | Account suspension status |
| `suspension_reason` | TEXT | NULL | Reason for suspension |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Indexes**: 
- `email` (unique)
- `username` (unique)

**Relationships**:
- One-to-Many: `resources` (as owner via `owner_id`)
- One-to-Many: `bookings` (as user)
- One-to-Many: `messages` (as sender and recipient)
- One-to-Many: `reviews` (as reviewer)
- One-to-Many: `notifications` (as recipient)
- One-to-Many: `waitlist` (as user)
- One-to-Many: `admin_logs` (as admin)

---

### 2. resources

**Description**: Stores information about bookable campus resources (study rooms, labs, equipment, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique resource identifier |
| `title` | VARCHAR(100) | NOT NULL | Resource name/title |
| `description` | TEXT | NULL | Detailed resource description |
| `category` | VARCHAR(50) | NOT NULL | Resource category (e.g., Study Rooms, Computer Labs, AV Equipment) |
| `location` | VARCHAR(100) | NULL | Physical location/building/room |
| `image_url` | VARCHAR(255) | NULL | Legacy single image URL (deprecated, use resource_images) |
| `capacity` | INTEGER | NULL | Maximum capacity (NULL = unlimited) |
| `owner_id` | INTEGER | FOREIGN KEY → users.id, NULL | Resource owner/manager user ID |
| `is_available` | BOOLEAN | DEFAULT TRUE | Current availability status |
| `is_featured` | BOOLEAN | DEFAULT FALSE | Featured resource flag |
| `requires_approval` | BOOLEAN | DEFAULT FALSE, NOT NULL | Whether bookings need approval |
| `status` | VARCHAR(20) | DEFAULT 'draft', NOT NULL | Resource status: 'draft', 'published', 'archived' |
| `equipment` | TEXT | NULL | Comma-separated list of equipment items |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Resource creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Last update timestamp |

**Indexes**:
- `owner_id` (foreign key)
- `category`
- `status`

**Relationships**:
- Many-to-One: `users` (as owner via `owner_id`)
- One-to-Many: `bookings` (as resource)
- One-to-Many: `reviews` (as resource)
- One-to-Many: `resource_images` (as resource)
- One-to-Many: `waitlist` (as resource)
- One-to-Many: `notifications` (as related_resource)

**Methods**:
- `average_rating()`: Calculates average rating from visible reviews
- `rating_percentage()`: Returns rating as percentage (0-100%)
- `review_count()`: Returns count of visible reviews

---

### 3. bookings

**Description**: Stores booking/reservation records for resources.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique booking identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who made the booking |
| `resource_id` | INTEGER | FOREIGN KEY → resources.id, NOT NULL | Resource being booked |
| `start_date` | DATETIME | NOT NULL | Booking start date and time |
| `end_date` | DATETIME | NOT NULL | Booking end date and time |
| `start_time` | DATETIME | NULL | Legacy start time (backward compatibility) |
| `end_time` | DATETIME | NULL | Legacy end time (backward compatibility) |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Booking status: 'pending', 'active', 'completed', 'cancelled' |
| `notes` | TEXT | NULL | Booking notes/special requests |
| `recurrence_type` | VARCHAR(20) | NULL | Recurrence type: 'daily', 'weekly', 'monthly', or NULL |
| `recurrence_end_date` | DATETIME | NULL | End date for recurrence series |
| `parent_booking_id` | INTEGER | FOREIGN KEY → bookings.id, NULL | Parent booking ID for recurring series |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Booking creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Last update timestamp |

**Indexes**:
- `user_id` (foreign key)
- `resource_id` (foreign key)
- `parent_booking_id` (foreign key, self-referential)
- `start_date`, `end_date` (for conflict detection queries)
- `status`

**Relationships**:
- Many-to-One: `users` (as user via `user_id`)
- Many-to-One: `resources` (as resource via `resource_id`)
- One-to-Many: `bookings` (as parent via `parent_booking_id` - self-referential for recurrence)
- Many-to-One: `bookings` (as child via `parent_booking_id`)
- One-to-Many: `notifications` (as related_booking)

**Properties**:
- `start_time_display`: Formatted start time string (HH:MM AM/PM)
- `end_time_display`: Formatted end time string (HH:MM AM/PM)
- `status_color`: Bootstrap color class based on status

---

### 4. messages

**Description**: Stores user-to-user messages within the system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique message identifier |
| `sender_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who sent the message |
| `recipient_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who receives the message |
| `subject` | VARCHAR(200) | NOT NULL | Message subject line |
| `body` | TEXT | NOT NULL | Message body/content |
| `is_read` | BOOLEAN | DEFAULT FALSE, NOT NULL | Read status |
| `is_flagged` | BOOLEAN | DEFAULT FALSE, NOT NULL | Flagged for admin review |
| `is_hidden` | BOOLEAN | DEFAULT FALSE, NOT NULL | Hidden from public view |
| `flag_reason` | TEXT | NULL | Reason for flagging |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Message creation timestamp |

**Indexes**:
- `sender_id` (foreign key)
- `recipient_id` (foreign key)
- `is_read`
- `is_flagged`
- `created_at`

**Relationships**:
- Many-to-One: `users` (as sender via `sender_id`)
- Many-to-One: `users` (as recipient via `recipient_id`)

---

### 5. reviews

**Description**: Stores user reviews and ratings for resources.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique review identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who wrote the review |
| `resource_id` | INTEGER | FOREIGN KEY → resources.id, NOT NULL | Resource being reviewed |
| `rating` | INTEGER | NOT NULL | Rating value (1-5 stars) |
| `review_text` | TEXT | NULL | Review text content |
| `is_hidden` | BOOLEAN | DEFAULT FALSE, NOT NULL | Hidden from public display |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Review creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, ON UPDATE, NOT NULL | Last update timestamp |

**Indexes**:
- `user_id` (foreign key)
- `resource_id` (foreign key)
- `is_hidden`
- `rating`

**Relationships**:
- Many-to-One: `users` (as reviewer via `user_id`)
- Many-to-One: `resources` (as resource via `resource_id`)

**Constraints**:
- One review per user per resource (enforced at application level)

---

### 6. notifications

**Description**: Stores system notifications for users (simulated notification system).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique notification identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User receiving the notification |
| `type` | VARCHAR(50) | NOT NULL | Notification type: 'booking_created', 'booking_approved', 'booking_rejected', 'booking_cancelled', 'booking_modified', 'recurring_series', 'waitlist_available', 'owner_notified' |
| `title` | VARCHAR(200) | NOT NULL | Notification title |
| `message` | TEXT | NOT NULL | Notification message content |
| `related_booking_id` | INTEGER | FOREIGN KEY → bookings.id, NULL | Related booking (if applicable) |
| `related_resource_id` | INTEGER | FOREIGN KEY → resources.id, NULL | Related resource (if applicable) |
| `is_read` | BOOLEAN | DEFAULT FALSE, NOT NULL | Read status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Notification creation timestamp |

**Indexes**:
- `user_id` (foreign key)
- `related_booking_id` (foreign key)
- `related_resource_id` (foreign key)
- `is_read`
- `type`
- `created_at`

**Relationships**:
- Many-to-One: `users` (as recipient via `user_id`)
- Many-to-One: `bookings` (as related_booking via `related_booking_id`)
- Many-to-One: `resources` (as related_resource via `related_resource_id`)

**Properties**:
- `notification_icon`: Font Awesome icon class based on type
- `notification_color`: Bootstrap color class based on type

**Methods**:
- `mark_as_read()`: Marks notification as read and commits to database

---

### 7. waitlist

**Description**: Stores waitlist entries for unavailable or fully booked resources.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique waitlist entry identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User on waitlist |
| `resource_id` | INTEGER | FOREIGN KEY → resources.id, NOT NULL | Resource being waitlisted |
| `requested_start_date` | DATETIME | NOT NULL | Desired start date/time |
| `requested_end_date` | DATETIME | NOT NULL | Desired end date/time |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Waitlist status: 'pending', 'notified', 'cancelled' |
| `notes` | TEXT | NULL | Waitlist notes |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Waitlist entry creation timestamp |
| `notified_at` | DATETIME | NULL | Timestamp when user was notified of availability |

**Indexes**:
- `user_id` (foreign key)
- `resource_id` (foreign key)
- `status`
- `requested_start_date`, `requested_end_date` (for conflict checking)

**Relationships**:
- Many-to-One: `users` (as user via `user_id`)
- Many-to-One: `resources` (as resource via `resource_id`)

---

### 8. admin_logs

**Description**: Stores audit log of all administrative actions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `log_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique log entry identifier |
| `admin_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | Admin user who performed the action |
| `action` | TEXT | NOT NULL | Description of the action performed |
| `target_table` | TEXT | NULL | Database table affected (if applicable) |
| `details` | TEXT | NULL | Additional details about the action |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Action timestamp |

**Indexes**:
- `admin_id` (foreign key)
- `timestamp`
- `target_table`

**Relationships**:
- Many-to-One: `users` (as admin via `admin_id`)

**Logged Actions**:
- User creation, editing, deletion, suspension
- Resource creation, editing, deletion, status changes
- Booking creation, editing, deletion, status changes
- Message editing, hiding, deletion
- Review editing, hiding, deletion

---

### 9. resource_images

**Description**: Stores multiple images per resource (replaces legacy single `image_url` field).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique image identifier |
| `resource_id` | INTEGER | FOREIGN KEY → resources.id, NOT NULL | Resource this image belongs to |
| `image_path` | VARCHAR(255) | NOT NULL | File path to the image |
| `display_order` | INTEGER | DEFAULT 0, NOT NULL | Display order for carousel (lower = first) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Image upload timestamp |

**Indexes**:
- `resource_id` (foreign key)
- `display_order`

**Relationships**:
- Many-to-One: `resources` (as resource via `resource_id`)

**Cascade Behavior**:
- Images are deleted when resource is deleted (cascade delete)

---

### 10. calendar_subscriptions

**Description**: Stores iCal subscription tokens for calendar integration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique subscription identifier |
| `user_id` | INTEGER | FOREIGN KEY → users.id, NOT NULL | User who owns the subscription |
| `token` | VARCHAR(64) | UNIQUE, NOT NULL, INDEXED | Unique subscription token (for URL) |
| `is_active` | BOOLEAN | DEFAULT TRUE, NOT NULL | Subscription active status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, NOT NULL | Subscription creation timestamp |
| `last_accessed_at` | DATETIME | NULL | Timestamp of last calendar access |
| `access_count` | INTEGER | DEFAULT 0, NOT NULL | Number of times subscription was accessed |
| `expires_at` | DATETIME | NULL | Optional expiration date for subscription |
| `status_filter` | VARCHAR(20) | NULL | Booking status filter (active, pending, etc.) |
| `start_date` | DATETIME | NULL | Optional start date filter for bookings |
| `end_date` | DATETIME | NULL | Optional end date filter for bookings |

**Indexes**:
- `user_id` (foreign key)
- `token` (unique, indexed)

**Relationships**:
- Many-to-One: `users` (as user via `user_id`)

**Methods**:
- `generate_token()`: Static method to generate secure random token
- `create_for_user()`: Static method to create subscription and deactivate existing ones
- `record_access()`: Records subscription access and increments counter
- `is_valid()`: Checks if subscription is still valid (active and not expired)

---

## Entity Relationship Diagram (Text Representation)

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ email       │◄──────────────────┐
│ username    │                    │
│ password_   │                    │
│   hash      │                    │
│ first_name  │                    │
│ last_name   │                    │
│ department  │                    │
│ role        │                    │
│ is_active   │                    │
│ is_suspended│                    │
│ created_at  │                    │
└─────────────┘                    │
       │                            │
       │                            │
       ├────────────────────────────┼────────────────────────────┐
       │                            │                            │
       │                            │                            │
┌──────▼──────────┐        ┌───────▼──────────┐        ┌───────▼──────────┐
│   resources     │        │    bookings     │        │    messages     │
│─────────────────│        │─────────────────│        │─────────────────│
│ id (PK)         │        │ id (PK)          │        │ id (PK)          │
│ title           │        │ user_id (FK)     │        │ sender_id (FK)   │
│ description     │        │ resource_id (FK)  │        │ recipient_id(FK) │
│ category        │        │ start_date       │        │ subject          │
│ location        │        │ end_date         │        │ body             │
│ capacity        │        │ status           │        │ is_read          │
│ owner_id (FK)   │        │ recurrence_type  │        │ is_flagged       │
│ status          │        │ parent_booking_id │        │ created_at       │
│ requires_       │        │ created_at       │        └──────────────────┘
│   approval      │        └──────────────────┘
│ equipment       │                 │
│ created_at      │                 │
└─────────────────┘                 │
       │                            │
       │                            │
       ├────────────────────────────┼────────────────────────────┐
       │                            │                            │
       │                            │                            │
┌──────▼──────────┐        ┌───────▼──────────┐        ┌───────▼──────────┐
│    reviews      │        │  notifications   │        │    waitlist     │
│─────────────────│        │─────────────────│        │─────────────────│
│ id (PK)         │        │ id (PK)          │        │ id (PK)          │
│ user_id (FK)    │        │ user_id (FK)     │        │ user_id (FK)     │
│ resource_id(FK) │        │ type             │        │ resource_id (FK) │
│ rating          │        │ title            │        │ requested_start_ │
│ review_text     │        │ message          │        │   date           │
│ is_hidden       │        │ related_booking_ │        │ requested_end_   │
│ created_at      │        │   id (FK)        │        │   date           │
└─────────────────┘        │ related_resource │        │ status           │
                           │   _id (FK)       │        │ created_at       │
                           │ is_read          │        └──────────────────┘
                           │ created_at       │
                           └──────────────────┘
                                    │
                                    │
                           ┌────────▼──────────┐
                           │  resource_images  │
                           │──────────────────│
                           │ id (PK)          │
                           │ resource_id (FK) │
                           │ image_path       │
                           │ display_order    │
                           │ created_at       │
                           └──────────────────┘

┌─────────────┐        ┌─────────────────────┐
│    users    │        │   admin_logs        │
│─────────────│        │─────────────────────│
│ id (PK)     │        │ log_id (PK)         │
│ ...         │        │ admin_id (FK)       │
└─────────────┘        │ action              │
       │               │ target_table        │
       │               │ details             │
       └───────────────► timestamp           │
                       └─────────────────────┘

┌─────────────┐        ┌─────────────────────┐
│    users    │        │ calendar_           │
│─────────────│        │   subscriptions     │
│─────────────│        │─────────────────────│
│ id (PK)     │        │ id (PK)             │
│ ...         │        │ user_id (FK)        │
└─────────────┘        │ token (UNIQUE)      │
       │               │ is_active           │
       └───────────────► created_at          │
                       │ revoked_at          │
                       └─────────────────────┘
```

---

## Relationships Summary

### One-to-Many Relationships

1. **User → Resources** (as owner)
   - One user can own many resources
   - Foreign key: `resources.owner_id` → `users.id`

2. **User → Bookings**
   - One user can have many bookings
   - Foreign key: `bookings.user_id` → `users.id`

3. **User → Messages** (as sender and recipient)
   - One user can send many messages
   - One user can receive many messages
   - Foreign keys: `messages.sender_id` → `users.id`, `messages.recipient_id` → `users.id`

4. **User → Reviews**
   - One user can write many reviews
   - Foreign key: `reviews.user_id` → `users.id`

5. **User → Notifications**
   - One user can receive many notifications
   - Foreign key: `notifications.user_id` → `users.id`

6. **User → Waitlist**
   - One user can have many waitlist entries
   - Foreign key: `waitlist.user_id` → `users.id`

7. **User → Admin Logs**
   - One admin can perform many logged actions
   - Foreign key: `admin_logs.admin_id` → `users.id`

8. **User → Calendar Subscriptions**
   - One user can have many calendar subscriptions
   - Foreign key: `calendar_subscriptions.user_id` → `users.id`

9. **Resource → Bookings**
   - One resource can have many bookings
   - Foreign key: `bookings.resource_id` → `resources.id`

10. **Resource → Reviews**
    - One resource can have many reviews
    - Foreign key: `reviews.resource_id` → `resources.id`

11. **Resource → Resource Images**
    - One resource can have many images
    - Foreign key: `resource_images.resource_id` → `resources.id`
    - Cascade delete: images deleted when resource deleted

12. **Resource → Waitlist**
    - One resource can have many waitlist entries
    - Foreign key: `waitlist.resource_id` → `resources.id`

13. **Resource → Notifications**
    - One resource can be related to many notifications
    - Foreign key: `notifications.related_resource_id` → `resources.id`

14. **Booking → Notifications**
    - One booking can generate many notifications
    - Foreign key: `notifications.related_booking_id` → `bookings.id`

### Self-Referential Relationships

1. **Booking → Booking** (for recurrence)
   - One booking can be the parent of many child bookings (recurring series)
   - Foreign key: `bookings.parent_booking_id` → `bookings.id`
   - Self-referential relationship

---

## Key Constraints and Business Rules

### User Constraints
- Email must be unique
- Username must be unique
- Role must be one of: 'student', 'staff', 'admin'
- Suspended users cannot book resources or send messages

### Resource Constraints
- Status must be one of: 'draft', 'published', 'archived'
- Only 'published' resources are visible to students
- Staff/admin can see all resources regardless of status
- Capacity NULL means unlimited capacity

### Booking Constraints
- Status must be one of: 'pending', 'active', 'completed', 'cancelled'
- `end_date` must be after `start_date` (enforced at application level)
- Recurrence type must be one of: 'daily', 'weekly', 'monthly', or NULL
- If `recurrence_type` is set, `recurrence_end_date` must be after `start_date`
- `parent_booking_id` links bookings in a recurring series

### Review Constraints
- Rating must be between 1 and 5 (enforced at application level)
- One review per user per resource (enforced at application level)

### Waitlist Constraints
- Status must be one of: 'pending', 'notified', 'cancelled'
- `requested_end_date` must be after `requested_start_date` (enforced at application level)

### Notification Constraints
- Type must be one of: 'booking_created', 'booking_approved', 'booking_rejected', 'booking_cancelled', 'booking_modified', 'recurring_series', 'waitlist_available', 'owner_notified'

---

## Indexes

### Primary Indexes
- All tables have `id` (or `log_id` for admin_logs) as PRIMARY KEY

### Foreign Key Indexes
- `resources.owner_id`
- `bookings.user_id`
- `bookings.resource_id`
- `bookings.parent_booking_id`
- `messages.sender_id`
- `messages.recipient_id`
- `reviews.user_id`
- `reviews.resource_id`
- `notifications.user_id`
- `notifications.related_booking_id`
- `notifications.related_resource_id`
- `waitlist.user_id`
- `waitlist.resource_id`
- `admin_logs.admin_id`
- `resource_images.resource_id`
- `calendar_subscriptions.user_id`

### Unique Indexes
- `users.email` (unique)
- `users.username` (unique)
- `calendar_subscriptions.token` (unique)

### Performance Indexes
- `bookings.start_date`, `bookings.end_date` (for conflict detection)
- `bookings.status`
- `resources.status`
- `resources.category`
- `messages.is_read`, `messages.is_flagged`
- `messages.created_at`
- `notifications.is_read`
- `notifications.type`
- `notifications.created_at`
- `reviews.is_hidden`
- `reviews.rating`
- `waitlist.status`
- `admin_logs.timestamp`
- `admin_logs.target_table`

---

## Cascade Behaviors

### Delete Cascades
- **Resource → Resource Images**: When a resource is deleted, all associated images are deleted (cascade delete)
- **Resource → Reviews**: When a resource is deleted, all associated reviews are deleted (cascade delete)

### No Cascades (Manual Handling)
- **User → Resources**: Resources are not automatically deleted when user is deleted (owner_id set to NULL or resource deleted separately)
- **User → Bookings**: Bookings are not automatically deleted when user is deleted (handled at application level)
- **User → Messages**: Messages are not automatically deleted when user is deleted (preserved for audit)
- **User → Reviews**: Reviews are not automatically deleted when user is deleted (preserved for historical data)

---

## Data Types and Defaults

### Common Patterns
- **Timestamps**: `DATETIME` with `DEFAULT CURRENT_TIMESTAMP`
- **Booleans**: `BOOLEAN` with `DEFAULT FALSE` or `DEFAULT TRUE`
- **Status Fields**: `VARCHAR(20)` or `VARCHAR(50)` with application-level validation
- **Text Fields**: `TEXT` for longer content, `VARCHAR` for shorter fields
- **Foreign Keys**: `INTEGER` with `FOREIGN KEY` constraint

### Default Values
- User role: 'student'
- Resource status: 'draft'
- Booking status: 'pending'
- Waitlist status: 'pending'
- Boolean flags: Mostly `FALSE` by default, except `is_active` (TRUE) and `is_available` (TRUE)

---

## Notes

1. **Legacy Fields**: The `bookings` table includes `start_time` and `end_time` fields for backward compatibility. New code should use `start_date` and `end_date`.

2. **Image Storage**: The `resources.image_url` field is deprecated. Use `resource_images` table for multiple images per resource.

3. **Recurrence**: Recurring bookings are stored as separate booking records linked via `parent_booking_id`. The first booking in a series is the parent.

4. **Status Workflows**:
   - Resources: draft → published → archived
   - Bookings: pending → active → completed (or cancelled at any point)

5. **Privacy**: Suspended users cannot book resources or send messages, but their existing data is preserved.

6. **Audit Trail**: All admin actions are logged in `admin_logs` for accountability and compliance.

