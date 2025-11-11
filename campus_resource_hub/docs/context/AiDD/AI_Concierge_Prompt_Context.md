# Campus Resource Hub - Resource and Booking Information

## Resources Overview

Resources are items, spaces, or services available for booking in the Campus Resource Hub. Examples include study rooms, computer labs, AV equipment, event spaces, lab instruments, and tutoring time slots.

### Resource Fields

Each resource has the following attributes:

- **id**: Unique identifier (integer)
- **title**: Name of the resource (required, max 100 characters)
- **description**: Detailed description of the resource (text field)
- **category**: Type of resource (required, max 50 characters). Common categories include: Study Rooms, Computer Labs, AV Equipment, Event Spaces, Lab Equipment, Tutoring
- **location**: Physical location or building/room number (max 100 characters)
- **capacity**: Maximum number of people or items that can be booked simultaneously (integer). Resources without capacity limits are treated as unlimited
- **owner_id**: User ID of the resource owner/manager (optional, foreign key to users table)
- **is_available**: Boolean flag indicating if resource is currently available for booking (default: True)
- **requires_approval**: Boolean flag indicating if bookings need admin/staff approval (default: False)
  - If `requires_approval = False`: Bookings are automatically approved (status set to 'active')
  - If `requires_approval = True`: Bookings require approval (status set to 'pending')
- **status**: Resource lifecycle status (default: 'draft')
  - `'draft'`: Resource is not yet published, only visible to staff/admin
  - `'published'`: Resource is live and visible to all users in search/listings
  - `'archived'`: Resource is no longer active but kept for historical records
- **equipment**: Comma-separated list of equipment items available with the resource (optional text field)
- **images**: Multiple images can be uploaded per resource, displayed as a carousel
- **created_at**: Timestamp when resource was created
- **updated_at**: Timestamp when resource was last modified

### Resource Visibility Rules

- **Students**: Can only see and book resources with `status = 'published'`
- **Staff/Admin**: Can see all resources regardless of status (draft, published, archived)
- Only published resources appear in search results and category listings
- Non-published resources return 404 for non-admin users

### Resource Ratings and Reviews

- Resources can have reviews with 1-5 star ratings
- Average rating is calculated from visible reviews only
- Rating is displayed as a percentage (0-100%) next to availability icon
- Top 3 highest-rated resources display "Top Rated" badge
- Single lowest-rated resource (if at least 2 resources have reviews) displays "Lowest Rated" badge
- Reviews are paginated (10 per page) on resource detail pages

---

## Booking Process

### Booking Overview

Bookings allow users to reserve resources for specific time periods. Each booking links a user to a resource with start and end dates/times.

### Booking Fields

Each booking has the following attributes:

- **id**: Unique identifier (integer)
- **user_id**: ID of the user making the booking (required, foreign key to users table)
- **resource_id**: ID of the resource being booked (required, foreign key to resources table)
- **start_date**: Start date and time of the booking (required, datetime)
- **end_date**: End date and time of the booking (required, datetime)
- **status**: Booking status (default: 'pending')
  - `'pending'`: Awaiting approval (for resources that require approval)
  - `'active'`: Confirmed and active booking
  - `'completed'`: Booking has ended
  - `'cancelled'`: Booking was cancelled
- **notes**: Optional notes or special requests (text field)
- **recurrence_type**: Type of recurrence for repeating bookings (optional)
  - `'daily'`: Booking repeats every day
  - `'weekly'`: Booking repeats every week
  - `'monthly'`: Booking repeats every month
  - `None` or `''`: Single booking (no recurrence)
- **recurrence_end_date**: End date for recurrence series (required if recurrence_type is set, must be after start_date)
- **parent_booking_id**: ID of the parent booking in a recurrence series (links all occurrences together)
- **created_at**: Timestamp when booking was created
- **updated_at**: Timestamp when booking was last modified

### Booking Creation Requirements

To create a booking, the following information is required:

1. **Resource**: Must select an existing resource (by resource_id)
2. **Start Date/Time**: Must specify when the booking starts (datetime-local format: YYYY-MM-DDTHH:MM)
3. **End Date/Time**: Must specify when the booking ends (datetime-local format: YYYY-MM-DDTHH:MM)
4. **Validation Rules**:
   - End date must be after start date
   - Cannot book resources that are not available (`is_available = False`)
   - Cannot book resources with `status != 'published'` (unless user is staff/admin)
   - Must pass conflict detection (no overlapping bookings)
   - Must pass capacity checks (if resource has capacity limit)

### Booking Approval Workflow

The booking approval process depends on the resource's `requires_approval` setting:

- **Automatic Approval** (`requires_approval = False`):
  - Booking status is immediately set to `'active'`
  - User receives confirmation notification
  - Resource owner (if set) receives notification

- **Manual Approval** (`requires_approval = True`):
  - Booking status is set to `'pending'`
  - Admin or staff member must approve the booking
  - Upon approval, status changes to `'active'`
  - User receives approval notification
  - If rejected, status changes to `'cancelled'` and user is notified

### Conflict Detection

Before a booking can be created, the system checks for conflicts:

1. **Time Overlap Check**: 
   - Checks if any existing active or pending bookings overlap with the requested time period
   - Overlapping bookings prevent new booking creation
   - Formula: `(new_start < existing_end) AND (new_end > existing_start)`

2. **Capacity Check**:
   - If resource has a `capacity` value (not null/0):
     - Counts all active and pending bookings during the requested time period
     - If count >= capacity, booking is rejected
   - If resource has no capacity limit (capacity is null or 0):
     - Capacity check is skipped (unlimited bookings allowed)

3. **Conflict Resolution**:
   - If conflicts are detected, user is offered option to join waitlist
   - Waitlist entries are notified when resource becomes available

### Recurrence Options

Users can create recurring bookings with the following options:

- **Daily**: Booking repeats every day from start_date until recurrence_end_date
- **Weekly**: Booking repeats every week (same day of week) until recurrence_end_date
- **Monthly**: Booking repeats every month (same day of month) until recurrence_end_date

**Recurrence Rules**:
- `recurrence_end_date` must be specified if recurrence_type is set
- `recurrence_end_date` must be after `start_date`
- Each occurrence in the series is created as a separate booking record
- All occurrences are linked via `parent_booking_id` (first booking is parent, others are children)
- Conflict detection runs for each occurrence individually
- If an occurrence has a conflict, it is skipped (not created) but other occurrences still proceed
- Skipped occurrences are noted in the booking creation response

**Example**: 
- Start: Monday, Jan 1, 2024 at 2:00 PM
- End: Monday, Jan 1, 2024 at 4:00 PM
- Recurrence: Weekly
- Repeat Until: Monday, Jan 29, 2024
- Result: Creates 5 bookings (Jan 1, Jan 8, Jan 15, Jan 22, Jan 29)

### Waitlist Feature

If a booking cannot be created due to conflicts or capacity, users can join a waitlist:

- **Waitlist Entry Fields**:
  - `user_id`: User requesting waitlist
  - `resource_id`: Resource being waitlisted
  - `requested_start_date`: Desired start time
  - `requested_end_date`: Desired end time
  - `status`: 'pending', 'notified', or 'cancelled'
  - `notes`: Optional notes

- **Waitlist Behavior**:
  - Users are notified when resource becomes available
  - Notification type: `waitlist_available`
  - Users can view and cancel their waitlist entries
  - Duplicate waitlist entries for same time period are prevented

### Booking Status Lifecycle

1. **Created**: Booking is created with status based on `requires_approval`:
   - If `requires_approval = False`: Status = `'active'`
   - If `requires_approval = True`: Status = `'pending'`

2. **Pending**: Booking awaits admin/staff approval
   - Admin can approve (status → `'active'`)
   - Admin can reject (status → `'cancelled'`)

3. **Active**: Booking is confirmed and active
   - User can cancel (status → `'cancelled'`)
   - Admin can cancel or modify

4. **Completed**: Booking has ended (automatically set when end_date passes)
   - Users can leave reviews after booking is completed

5. **Cancelled**: Booking was cancelled
   - Can be cancelled by user or admin
   - Cancelled bookings free up capacity for other users

### Booking Notifications

The system sends simulated notifications for booking events:

- **Booking Created**: User and resource owner notified when booking is created
- **Booking Approved**: User notified when admin approves pending booking
- **Booking Rejected**: User notified when admin rejects booking
- **Booking Cancelled**: User and resource owner notified when booking is cancelled
- **Booking Modified**: User and resource owner notified when booking details change
- **Recurring Series Created**: User notified when recurring booking series is created
- **Waitlist Available**: User notified when waitlisted resource becomes available

### User Restrictions

- **Suspended Users**: Cannot create bookings or join waitlists
- **Suspended Users**: Cannot send messages
- Suspension is managed by admins and prevents all booking/messaging activity

---

## Common Booking Scenarios

### Scenario 1: Single Booking
- User selects resource, start time, end time
- No recurrence selected
- System checks conflicts and capacity
- If approved, booking created with status 'active' or 'pending' based on resource settings

### Scenario 2: Recurring Weekly Booking
- User selects resource, start time (e.g., Monday 2 PM), end time (e.g., Monday 4 PM)
- Recurrence: Weekly
- Repeat Until: 4 weeks later
- System creates 4 separate bookings (one per week)
- Each booking checked for conflicts individually

### Scenario 3: Capacity-Limited Resource
- Resource has capacity = 5
- 5 active bookings already exist for requested time
- New booking is rejected
- User offered waitlist option
- When one booking ends, waitlist user is notified

### Scenario 4: Approval-Required Resource
- Resource has `requires_approval = True`
- User creates booking
- Booking status = 'pending'
- Admin reviews and approves
- Booking status = 'active'
- User receives approval notification

---

## Resource Search and Discovery

Users can search for resources using:

- **Keyword Search**: Searches in resource title and description (case-insensitive)
- **Category Filter**: Filter by resource category
- **Location Filter**: Filter by location (partial match)
- **Capacity Filter**: Minimum capacity requirement
- **Availability Filter**: Filter by available date/time range (checks conflicts)
- **Sort Options**:
  - Title (A-Z): Alphabetical by title
  - Most Recent: Newest resources first
  - Most Booked: Resources with most bookings first
  - Top Rated: Resources with highest average rating first

Only published resources appear in search results.

---

## Important Notes for AI Assistant

When helping users with resources and bookings:

1. **Always check resource status**: Only suggest published resources to students
2. **Verify availability**: Check if resource is available and not at capacity
3. **Explain approval process**: Inform users if resource requires approval
4. **Mention recurrence**: Explain recurrence options when users ask about repeating bookings
5. **Suggest waitlist**: If resource is unavailable, suggest waitlist option
6. **Check user status**: Suspended users cannot book or message
7. **Provide resource links**: Format as `[Resource Name](resource_id)` where resource_id is numeric
8. **Booking proposals**: When suggesting bookings, include resource name, start time, end time, and recurrence if applicable
9. **Never reveal other users' booking details**: Only show aggregated or user's own booking information
10. **Respect role-based access**: Students see published resources only, staff/admin see all resources

