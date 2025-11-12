# Demo Steps - Campus Resource Hub

This document provides step-by-step instructions for common actions in the Campus Resource Hub system.

---

## 1. As a Student: Book a Resource

1. **Log in** to the Campus Resource Hub with your student account credentials
2. **Navigate to Resources**:
   - Click on "Resources" in the sidebar, OR
   - Click on "Home" and browse available resources
3. **Search or Browse** for the resource you want to book:
   - Use the search bar to find specific resources by name, category, or location
   - Or browse by category using the category filters
4. **View Resource Details**:
   - Click on the resource card or title to open the resource details page
5. **Check Availability**:
   - Review the resource information (location, capacity, equipment, etc.)
   - Check the calendar view to see existing bookings
6. **Click "Book Now"** button on the resource details page
7. **Select Date and Time**:
   - Use the calendar widget to select your booking time:
     - **First click**: Sets the start time
     - **Second click**: Sets the end time
     - **Third click**: Clears the selection
   - The selected time range will be displayed below the calendar
8. **Fill in Booking Details**:
   - Add any special requirements or notes in the "Notes" field (optional)
   - Select recurrence type if needed (None, Daily, Weekly, Monthly)
   - If recurrence is selected, choose the recurrence end date
9. **Review Resource Details**:
   - Verify the location and capacity information shown
10. **Submit Booking Request**:
    - Click the "Submit Booking Request" button
    - Wait for confirmation message
11. **Confirmation**:
    - You will see a success message
    - You will receive a notification about your booking
    - The booking status will be "pending" if approval is required, or "active" if auto-approved

---

## 2. As a Staff Member: Create a Resource

**Note**: Staff members can create and manage resources and bookings, but cannot create users. User creation requires admin access. If you need to create a user, please contact an administrator.

1. **Log in** to the Campus Resource Hub with your staff account credentials
2. **Navigate to Administrative Dashboard**:
   - Click on "Admin" in the top navigation bar, OR
   - Click on "Administrative Dashboard" in the sidebar
3. **Access Resource Management**:
   - On the Admin Dashboard, click the "Manage Resources" button in the Resources card
4. **Create New Resource**:
   - Click the "Create New Resource" button (usually at the top of the resources list)
5. **Fill in Resource Information**:
   - **Title**: Enter the resource name (e.g., "Computer Lab 1")
   - **Description**: Provide a detailed description of the resource
   - **Category**: Select from dropdown (Lab, Study Room, Equipment, Event Space, etc.)
   - **Location**: Enter the physical location (e.g., "Building A, Room 101")
   - **Capacity**: Enter the maximum number of people (optional)
   - **Equipment**: Enter comma-separated list of equipment (optional)
   - **Status**: Select from Draft, Published, or Archived
   - **Availability**: Check "Is Available" if the resource is currently available
   - **Featured**: Check if this should be a featured resource
   - **Requires Approval**: Check if bookings need admin/staff approval
   - **Owner**: Select the resource owner from the dropdown (optional)
6. **Upload Images** (optional):
   - Click "Choose Files" under "Upload Images"
   - Select one or more image files (jpg, jpeg, png, gif, webp)
   - Multiple images will be displayed as a carousel
7. **Save Resource**:
   - Click the "Create Resource" or "Save" button
8. **Confirmation**:
   - You will see a success message
   - The resource will be added to the system
   - If status is "Published", it will be visible to all users
   - If status is "Draft", only admins and staff can see it

---

## 3. As an Admin: Change the Status of a Booking

1. **Log in** to the Campus Resource Hub with your admin account credentials
2. **Navigate to Administrative Dashboard**:
   - Click on "Admin" in the top navigation bar, OR
   - Click on "Administrative Dashboard" in the sidebar
3. **Access Booking Management**:
   - On the Admin Dashboard, click the "Manage Bookings" button in the Bookings card
4. **Find the Booking**:
   - Browse the list of bookings, or
   - Use search/filter options if available
5. **Edit the Booking**:
   - Click the "Edit" button next to the booking you want to modify
6. **Change Status**:
   - In the booking form, find the "Status" dropdown field
   - Select the new status from the dropdown:
     - **Pending**: Booking is awaiting approval
     - **Active**: Booking is confirmed and active
     - **Cancelled**: Booking has been cancelled
     - **Completed**: Booking has been completed
7. **Update Other Details** (if needed):
   - Modify start date/time if needed
   - Modify end date/time if needed
   - Update notes if needed
   - Modify recurrence settings if applicable
8. **Save Changes**:
   - Click the "Update Booking" or "Save" button
9. **Confirmation**:
   - You will see a success message indicating the status change
   - The user will receive a notification about the status change
   - The booking will be updated in the system

---

## 4. As an Admin: Suspend a User

1. **Log in** to the Campus Resource Hub with your admin account credentials
2. **Navigate to Administrative Dashboard**:
   - Click on "Admin" in the top navigation bar, OR
   - Click on "Administrative Dashboard" in the sidebar
3. **Access User Management**:
   - On the Admin Dashboard, click the "Manage Users" button in the Users card
4. **Find the User**:
   - Browse the list of users, or
   - Use search/filter options if available
5. **Suspend the User**:
   - Find the user you want to suspend in the list
   - Click the "Suspend" button next to the user
6. **Provide Suspension Reason** (if prompted):
   - Enter a reason for the suspension in the provided field
   - This helps document why the user was suspended
7. **Confirm Suspension**:
   - Review the suspension details
   - Click "Confirm" or "Suspend User" to proceed
8. **Confirmation**:
   - You will see a success message
   - The user's account will be suspended
   - Suspended users cannot:
     - Log in to the system
     - Make new bookings
     - Send messages
   - The suspension will be logged in the Admin Logs
9. **To Unsuspend a User** (if needed):
   - Find the suspended user in the list
   - Click the "Unsuspend" button
   - Confirm the action
   - The user will regain access to the system

---

## 5. As a Student: Cancel a Booking

1. **Log in** to the Campus Resource Hub with your student account credentials
2. **Navigate to Your Bookings**:
   - Click on "Dashboard" in the sidebar or top navigation
   - Find your booking in the "My Bookings" section, OR
   - Click on "Calendar" in the sidebar and find your booking
3. **View Booking Details**:
   - Click on the booking to open the booking details page
4. **Cancel the Booking**:
   - On the booking details page, find the "Cancel Booking" button
   - Click the "Cancel Booking" button (red button with X icon)
5. **Confirm Cancellation**:
   - A modal dialog will appear asking you to confirm
   - Review the booking information displayed:
     - Resource name
     - Date and time
     - Duration
   - If it's a recurring booking, you'll see a warning that all instances will be cancelled
   - Click "Yes, Cancel Booking" to confirm, OR
   - Click "Keep Booking" to cancel the action
6. **Confirmation**:
   - You will see a success message confirming the cancellation
   - The booking status will change to "cancelled"
   - You will receive a notification about the cancellation
   - If it was a recurring booking, all future instances will also be cancelled
7. **Note**: 
   - You can only cancel bookings that belong to you
   - You cannot cancel bookings that are already completed
   - You cannot cancel bookings that are already cancelled

---

## Additional Notes

- **Staff Members**: Can manage resources and bookings, but cannot manage users, messages, reviews, or access reports
- **Admins**: Have full access to all administrative features
- **Students**: Can book resources, view their bookings, send messages, and manage their profile
- All actions are logged in the Admin Logs (viewable by admins only)
- Notifications are sent for important actions (booking approvals, cancellations, etc.)

