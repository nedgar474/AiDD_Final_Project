# AI Development Notes

## Project Initialization
1. Created base project structure following MVC pattern
2. Set up SQLAlchemy models with relationships
3. Configured Flask application factory pattern
4. Implemented database migrations and seeding

## Key Design Decisions
- Used Flask-SQLAlchemy for ORM
- Implemented Flask-Login for user authentication
- Used Flask-Migrate for database migrations
- Added Blueprint structure for modular design
- Implemented model relationships with backref
- Added to_dict() methods for API compatibility

## Verification Steps
1. Database models created and verified
2. Sample data insertion tested
3. Relationships between models confirmed
4. Migration scripts generated and tested

## Next Steps
1. Implement authentication views
2. Add resource booking logic
3. Create message system
4. Implement admin dashboard
5. Add test coverage

---

# Pre-Session Bootstrap Prompts

## Initial Project Bootstrap Prompt (from golden_prompts.md)

Based on the project structure and `golden_prompts.md, the initial bootstrap prompt was:

**"AI-First Project Bootstrap — Campus Resource Hub (Full Database Setup)"**

You are an expert full-stack Flask developer setting up the **Campus Resource Hub** project for the AiDD 2025 Capstone.  
Generate a **production-ready, database-integrated Flask scaffold** with migrations and sample seed data.

**Note:** The full original prompt text is not available in the current context, but based on the project structure, it likely included:
- Setting up Flask application with MVC architecture
- Creating SQLAlchemy models for: User, Resource, Booking, Message
- Implementing Flask-Login for authentication
- Setting up Flask-Migrate for database migrations
- Creating blueprint structure for controllers
- Setting up forms with Flask-WTF
- Creating base templates and views
- Implementing database seeding functionality

The project structure shows the following initial models were created:
- **User model**: email, username, password_hash, first_name, last_name, role, is_active, created_at
- **Resource model**: name, description, category, location, image_url, capacity, is_available, is_featured, created_at
- **Booking model**: user_id, resource_id, start_time, end_time, status, notes, created_at
- **Message model**: sender_id, recipient_id, subject, body, read, created_at

**Note:** Earlier conversation history before the current session is not available in the current context. The prompts documented below start from when the user began reporting errors and requesting features.

---

# Complete Conversation History

## Session 1: Initial Error Fixes

### User Prompt 1
"I am receiving the folowing error. Can you examine and fix this for this website?"

**Response:** Fixed `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'` by downgrading Werkzeug to 2.2.2 in requirements.txt to be compatible with Flask==2.2.5.

### User Prompt 2
"Can you create a file that will add test data to the database, including users?"

**Response:** Created `seed_data.py` script to populate the database with test data including users, resources, and bookings.

### User Prompt 3
"When loggin in as the admin i got a "Bad Request The CSRF token is missing." error"

**Response:** Created `LoginForm` using Flask-WTF, updated `auth_controller.py` to use this form, and modified `login.html` to render form fields with `{{ form.hidden_tag() }}` for CSRF protection.

### User Prompt 4
"I just recieved another error - BuildError werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'resource.list'. Did you mean 'resources.view' instead? Traceback (most recent call last) ... jinja2.exceptions.TemplateNotFound: resources/search.html and on check messages I got - TypeError TypeError: The view function for 'message.inbox' did not return a valid response. The function either returned None or ended without a return statement."

**Response:** 
- Fixed endpoint references from `resource.list` to `resources.search` in templates
- Changed `template_folder` in `app.py` from `'views'` to `'views/templates'`
- Implemented proper return statements in `message_controller.py` and `booking_controller.py`
- Created missing template files

### User Prompt 5
"When submitting a booking I got Bad Request The CSRF token is missing."

**Response:** Created `BookingForm` using Flask-WTF, updated `resource_controller.py` to use this form, and modified `resources/book.html` to render `{{ form.hidden_tag() }}` and form fields.

### User Prompt 6
"The date picker has dissapeared for the bookings"

**Response:** Modified `BookingForm` in `forms.py` to use `StringField` for `start_date` and `end_date` with `render_kw={"type": "datetime-local"}` to ensure HTML input type is correctly set.

### User Prompt 7
"The Users first name is not showing up on the dashboard page."

**Response:** Updated `src/views/templates/dashboard.html` to use `{{ current_user.first_name if current_user.first_name else current_user.username }}`.

---

## Session 2: Feature Implementation

### User Prompt 8
"I need to add functionality for users to send and receive messages from other users within the app, and a profile page for users to manage their profile settings."

**Response:** 
- Implemented messaging system with inbox, sent, compose, and view routes
- Created user profile management with view, edit, and change password functionality
- Added `ProfileForm` and `PasswordChangeForm`
- Created `profile_controller.py` with all profile routes

### User Prompt 9
"The profile and message pages are not appearing on the page. Can you place the profile button by the sign out button, and add a messaging icon by the sign oout button, and have a "View my Messages" option in the dashboard quick actions area?"

**Response:** 
- Updated navbar in `base.html` to include Profile link and messages icon
- Added "View My Messages" button to dashboard quick actions
- Fixed navbar visibility issues

### User Prompt 10
"I am logged in as the admin and I do not see the profile button or message button by "Logout""

**Response:** Fixed navbar conditional logic to show profile and message buttons for all authenticated users.

### User Prompt 11
"In the ID is being used to display the to and from for the messages. can we switch that to use the username?"

**Response:** Updated message templates to display `message.sender.username` and `message.recipient.username` instead of IDs. Added relationships in Message model.

### User Prompt 12
"Can you add the capability to view sent messages, and add buttons on the messages page to view the inbox and sent messages?"

**Response:** 
- Implemented `sent()` route in `message_controller.py`
- Added navigation buttons for Inbox, Sent, and Compose in all message templates

### User Prompt 13
"Can you enable users to send messages to themselves?"

**Response:** Removed the restriction that prevented users from sending messages to themselves in `message_controller.py`.

### User Prompt 14
"The admin Dashboard is not working, I am getting an error - TypeError TypeError: The view function for 'admin.dashboard' did not return a valid response."

**Response:** Updated `admin_controller.py` to ensure all admin routes return `render_template` calls. Created placeholder templates for all admin pages.

### User Prompt 15
"Can you ad a search bar underneath the Welcome to Campus Reslouce Hub on the main page that will allow users to search for resources?"

**Response:** Added a search bar to `index.html` below the welcome message that allows users to search for resources.

### User Prompt 16
"Can you add the ability for the admin role to add modify and delete users, resources and bookings in the admin dashboard? this should fill in the existing placeholders."

**Response:** 
- Implemented full CRUD operations for users, resources, and bookings in admin dashboard
- Created `AdminUserForm`, `AdminResourceForm`, `AdminBookingForm`
- Added create, edit, and delete routes for all three entities
- Created admin templates for all CRUD operations

### User Prompt 17
"Can you add a non moving sidebar on the left hand side of every page which will have links to the following pages - My Bookings, Resources, calendar (placeholder for now), Messages, and Administrative Dashboard (If admin role)"

**Response:** 
- Implemented fixed left sidebar in `base.html`
- Added links to Home, Dashboard, Resources, Calendar (placeholder), Messages, and Administrative Dashboard (if admin)
- Added CSS styling for the fixed sidebar

### User Prompt 18
"Replace the link to my bookings on the dashboard with a Dashboard link"

**Response:** Replaced "View My Bookings" link in dashboard quick actions with "Dashboard" link.

### User Prompt 19
"revert the previous change and change the My Bookings link in the sidebar to the dashboard"

**Response:** Reverted dashboard change and updated sidebar "My Bookings" link to "Dashboard" pointing to `main.dashboard`.

---

## Session 3: Advanced Features

### User Prompt 20
"Please give users the ability to flag messages for admin review, and please create a manage messages page where amins can view flagged messages and edit, hide and delete them. Please give admins the ability to suspend users so they cannot messge people or book resources."

**Response:** 
- Added `is_flagged`, `is_hidden`, and `flag_reason` columns to messages table
- Created message flagging functionality for users
- Created admin message management page with view, edit, hide, unflag, and delete actions
- Added user suspension functionality with `is_suspended` and `suspension_reason` columns
- Updated booking and messaging routes to check for suspension

### User Prompt 21
"I am getting OperationalError - sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: users.is_suspended"

**Response:** Created `fix_database.py` script to manually add missing columns to the SQLite database, including `is_suspended`, `suspension_reason` for users, and other missing columns for messages, bookings, and resources.

### User Prompt 22
"Still getting OperationalError - sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: users.is_suspended"

**Response:** Further investigation and fixes to database path and column additions.

### User Prompt 23
"Still getting OperationalError - sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: bookings.start_date"

**Response:** Added `start_date`, `end_date`, and `updated_at` columns to bookings table via `fix_database.py`.

### User Prompt 24
"Only the dashboard page works, the rest are getting operationalerror"

**Response:** Continued database fixes for all missing columns across all tables.

### User Prompt 25
"Can you seed the Database with the test data?"

**Response:** Updated `seed_data.py` to use raw SQL inserts to populate both new and old columns, ensuring data integrity during seeding.

### User Prompt 26
"The suspend user confirmation box cannot be accessed when it is brought up."

**Response:** Moved suspend and delete modals outside the table in `admin/users.html` for proper z-index, and added CSRF tokens to forms.

### User Prompt 27
"Can you create a modal for delete user?"

**Response:** Created Bootstrap modal for delete user confirmation in `admin/users.html`.

### User Prompt 28
"Can you give faculty role the ability to create resources if they do not already have it, and can you add a check box during resource creation or editing which will place a hold on the resource so that when a user books it the status is shown as pending? And can you change the text input in the manage bookings in the admin dashboard to be a drop down?"

**Response:** 
- Added `faculty_or_admin_required` decorator
- Added `/resources/new` route for faculty/admin resource creation
- Added `requires_approval` checkbox to resource forms
- Updated booking status logic to set `pending` if resource requires approval
- Changed booking status input to dropdown in admin dashboard

### User Prompt 29
"Bookings in the admin dashboard are not changing status when unpdated in the manage bookings screen"

**Response:** 
- Fixed form data binding in `AdminBookingForm` by manually setting choices and data
- Added `db.session.refresh(booking)` after commit
- Added error display in `admin/booking_form.html`

### User Prompt 30
"It works, great job"

**Response:** Acknowledged.

---

## Session 4: Review System

### User Prompt 31
"Please give users the ability to leave reviews on resources, add a Leave Review button (or edit review if the user has left a review) which will allow the user to select a rating of 1-5 and leave a text review. the resource will show the average rating as a percentage next to the availability icon."

**Response:** 
- Created `Review` model with `rating` (1-5) and `review_text`
- Created `ReviewForm` for submitting reviews
- Added review routes in `resource_controller.py`
- Updated resource view to show average rating as percentage
- Added "Leave Review" or "Edit Review" button

### User Prompt 32
"Can you give users the ability to delete their own reviews?"

**Response:** 
- Added delete review route in `resource_controller.py`
- Added "Delete Review" button in review template

### User Prompt 33
"Please add a reviews section to the resources page, under the image which will show a list of 10 reviews, with the rest on additional pages each with 10."

**Response:** 
- Added paginated reviews section to resource view page
- Displays 10 reviews per page
- Filters out hidden reviews

### User Prompt 34
"On the Resources page, please show the reveiw percentage of each resource as it is on their own pages"

**Response:** Added review percentage and count display to resource cards in search and category pages.

### User Prompt 35
"When I tried to edit a message in the manage messages screen got the following error - Bad Request The CSRF token is missing."

**Response:** Added `{{ csrf_token() }}` hidden input to `admin/message_edit.html` form and other message management forms.

### User Prompt 36
"Please move the home linkto be over the dashboard link in the sidebar"

**Response:** Moved "Home" link above "Dashboard" link in the sidebar.

### User Prompt 37
"Can you add department to the users table to show what department the users are in?"

**Response:** 
- Added `department` column to `users` table
- Updated `User` model
- Added department field to `ProfileForm` and `AdminUserForm`
- Updated profile and admin user templates

---

## Session 5: Admin Logging and Reports

### User Prompt 38
"Can you add the following table to the database to keep logs of admin actions? admin_logs • log_id INTEGER PRIMARY KEY AUTOINCREMENT • admin_id INTEGER REFERENCES users(user_id) • action TEXT • target_table TEXT • details TEXT • timestamp DATETIME"

**Response:** 
- Created `AdminLog` model
- Added `admin_logs` table to database via `fix_database.py`
- Created `log_admin_action` helper function

### User Prompt 39
"Can you add the following reports to the reports page in the admin dashboard? 1️⃣ **Active Resources by Status** - Count of resources grouped by `status`. - Chart type: **Bar chart** - Metric: count of resources per status. 2️⃣ **Total Bookings (Last 30 Days)** - Line chart showing total bookings created per day over the last 30 days. - Aggregate by date. 3️⃣ **Category Utilization Summary** - Total number of bookings grouped by resources - Chart type: **Bar chart** - Metric: count of approved bookings per category. 4️⃣ **Average Booking Duration per Category** - Compute average booking length per resource category. - Chart type: **Horizontal bar chart** 5️⃣ **Resource Ratings vs. Booking Volume** - Correlate average review rating with total booking count per resource. - Chart type: **Scatter plot** - X-axis: average rating, Y-axis: total bookings. 6️⃣ **Bookings per User Role** - Compare booking counts grouped by requester's role. - Chart type: **Pie chart** 7️⃣ **Booking Status Distribution** - Percentage of bookings per status. - Chart type: **Donut or pie chart** 8️⃣ **Admin Actions Log Summary** - Count of admin actions from admin_logs table, grouped by `action` type. - Chart type: **Bar chart**"

**Response:** 
- Implemented 8 reports using Chart.js
- Added data aggregation in `admin_controller.py`
- Created dynamic chart rendering in `admin/reports.html`
- Fixed date formatting issue for SQLite

### User Prompt 40
"Got error - AttributeError AttributeError: 'str' object has no attribute 'strftime'"

**Response:** Fixed date formatting in "Total Bookings (Last 30 Days)" report by using `str(date)` instead of `date.strftime()` for SQLite string output.

### User Prompt 41
"got error when booking - IntegrityError sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: bookings.start_time"

**Response:** 
- Added `start_time` and `end_time` as nullable columns to Booking model for backward compatibility
- Updated booking creation to populate both new (`start_date`, `end_date`) and old (`start_time`, `end_time`) columns
- Renamed property methods to `start_time_display` and `end_time_display`

### User Prompt 42
"Can you remove the numbers on the reports titles and change the color of the admin role in the Bookings per User Role to red, faculty to green and students to blue?"

**Response:** 
- Removed numbers from report titles
- Customized colors for "Bookings per User Role" chart (admin=red, faculty=green, student=blue)

### User Prompt 43
"Can you remove the admin log table from the reports page, and create view admin log button on the admin dashboard which will go to a page displaying a paginated table showing all administrative actions taken (Suspending creating and ddeleting users, changing resource status, hiding editing and deleting messages and editing snd hiding and deleting reviews? Admins should have the ability to edit and delete and hide reviews."

**Response:** 
- Removed admin log table from reports page
- Created "View Admin Log" button on admin dashboard
- Created paginated admin logs page
- Added admin review management (edit, hide/unhide, delete)
- Created admin review management templates

### User Prompt 44
"I suspended student3 and nothing is displaying in the admin log"

**Response:** 
- Implemented `log_admin_action` helper function
- Integrated logging into all admin CRUD operations (users, resources, bookings, messages, reviews)
- Added logging for suspend/unsuspend actions

### User Prompt 45
"When I unsuspended a user I got Bad Request - The CSRF token is missing."

**Response:** Added CSRF token to the unsuspend form in `admin/users.html`.

---

## Session 6: Image Upload and Carousel

### User Prompt 46
"Can you give admins an faculty the ability to upload images for different resources, and have resource images displayed as a carousel that can change the displayed images by users selecting arrows or automatically after 15 seconds have passed"

**Response:** 
- Created `ResourceImage` model for multiple images per resource
- Added `FileField` for multiple image uploads in `AdminResourceForm`
- Implemented image upload handling in `resource_controller.py` and `admin_controller.py`
- Created Bootstrap 5 carousel with auto-advance every 15 seconds
- Added navigation arrows and dot indicators
- Created `resource_images` table in database
- Added `enctype="multipart/form-data"` to resource forms

### User Prompt 47
"Got this error wen uploading image NameError - NameError: name 'current_app' is not defined"

**Response:** Moved `current_app` import inside the `allowed_file()` and `save_uploaded_images()` functions to ensure it's accessed within the Flask request context.

### User Prompt 48
"Still getting NameError - NameError: name 'current_app' is not defined"

**Response:** Added `from flask import current_app` inside both helper functions in `resource_controller.py` and `admin_controller.py`.

### User Prompt 49
"Geting error NameError - NameError: name 'os' is not defined"

**Response:** Added missing imports to `admin_controller.py`: `import os`, `from werkzeug.utils import secure_filename`, and `from ..models.resource_image import ResourceImage`.

### User Prompt 50
"Can you place every prompt and response so far in the dev_notes.md file, and upload every prompt and response after this into it?"

**Response:** (This is the current response - compiling all prompts and responses into dev_notes.md)

---

## Session 7: Resource Concierge Implementation

### User Prompt 51
"I want to proceed with the local AI Concierge option based on ollama Llama 3.1 8B model. All markdown files in the context folder should be indexed but not outside of it. Sensitive user information should not be shared by the AI. The types of database queries should be supported and other queries should be as long as they are relevant to the campus resource hub website. The AI should be able to handle multistep, comparative and temporal queries. The AI should respect admin roles and restrict access to information based on roles. The AI can answer questions for non-published resources for users with admin or staff roles. It should not revieal other users booking details or other information. the AI should be accessable as a popup located in the lower right hand corner in the form of a chatbot. It should be simple but still show the full chat history. Responses should provide links to relevant resources. retrieval should be simple text matching for now. summarize retrieved context if too long. Concierge should be able to suggest resources based on queries and allow booking based on user responses. the concierge may present the proposed booking Information to the user who will select 'Book Now' or 'Decline' to make the final decision. Concierge responses may link to any relevant page but only show admin dashboard links to admins. For All other requirements use recommended defaults from @development_options.md"

**Response:** Implemented Resource Concierge AI assistant with Ollama integration. Created modular architecture with context retriever, database retriever, query processor, LLM client, response generator, booking proposer, role filter, and context summarizer. Integrated chatbot UI into base template.

### User Prompt 52
"Plan is confirmed, proceed with implementation. When finished please place AI concierge related prompts in the golden_prompts file."

**Response:** Completed implementation and documented prompts in golden_prompts.md.

### User Prompt 53
"Getting error on attempt to install ollama - the termn 'ollama' is not recognized"

**Response:** Clarified that Ollama is a system application, not a Python package. Created OLLAMA_SETUP.md with installation instructions.

### User Prompt 54
"For other people to download the website and use it, they would have to install ollama as well?"

**Response:** Explained deployment considerations and added Docker analysis to development_options.md.

### User Prompt 55
"How would docker deployment work? don't code anything yet and add analysis to @development_options.md"

**Response:** Added Docker deployment analysis to development_options.md.

### User Prompt 56
"I just got an api key from google AI, How would we go about using it? What changes would need to be made to the site? would this mean dropping ollama for gemini, etc? Place analysis in the @development_options.md - the api key is in the API KEY file in the aidd folder"

**Response:** Added Google Gemini API analysis to development_options.md.

### User Prompt 57
"I just got an API Key from OpenAI, how would that change your analysis? please update @development_options.md key is in the API_KEY file"

**Response:** Updated development_options.md with OpenAI API analysis.

### User Prompt 58
"I want to go with the single provider plan using 4o mini. can you give me an overview of the Changes you intend to make before we proceed? I would also like to know what the impact will be on someone who downloads this site to run it locally for testing will be. Would they need to install anything?"

**Response:** Provided overview of changes: refactor LLMClient to use OpenAI API, update requirements.txt, add environment variable configuration, create .env.example. Local users would need OpenAI API key but no local LLM installation.

### User Prompt 59
"Could they use the api key I have provided?"

**Response:** Explained that API keys are user-specific and should not be shared. Each user needs their own OpenAI API key.

### User Prompt 60
"I will consider this. Please proceed with the 4o mini model change"

**Response:** Refactored LLMClient to use OpenAI GPT-4o-mini, updated requirements.txt, config.py, created .env.example and .gitignore.

### User Prompt 61
"@Python (21-35) getting error no module named open ai"

**Response:** Installed openai package via pip.

### User Prompt 62
"still getting no module named 'openai' error"

**Response:** Verified installation and checked import paths.

### User Prompt 63
"The chatbot is showing up spradically on various pages and dissapeared when I tried to chat with it"

**Response:** Improved JavaScript error handling in base.html for health check and chat submission.

### User Prompt 64
"The chatbot dissapears during chat when enter is pressed - and gave me the error 'Sorry, I'm having trouble connecting. Please try again later.'"

**Response:** Added @csrf.exempt decorator to /concierge/query route, enhanced error handling in frontend and backend.

### User Prompt 65
"Can you update the @REQUIREMENTS_COMPLIANCE_REPORT.md to reflect the changes we made?"

**Response:** Updated compliance report with Resource Concierge section documenting OpenAI GPT-4o-mini implementation, features, and technical details.

### User Prompt 66
"The chatbot is unable to answer questions, can you populate the Ai Concierge prompt context file with Information about the resources and the Booking process?"

**Response:** Created comprehensive AI_Concierge_Prompt_Context.md file with detailed information about resources, booking process, approval workflow, conflict detection, recurrence, waitlist, and common scenarios.

### User Prompt 67
"I just had the following exchange with the chatbot -I would like to book a study room tomorrow from 4-5pm / I'm sorry, but I don't have information about booking study rooms or specific resources available for that purpose. Please check your campus resource hub or relevant platform for booking details. If you need assistance with the booking process, feel free to ask! / I need assistance with the booking process / I'm sorry, but there is no information available regarding the booking process in the provided context. If you have specific resources in mind that you would like to book, please let me know, and I can assist you with that. - it does not seem to have the information it needs"

**Response:** Improved search algorithm with synonym expansion and better scoring. Enhanced prompt instructions to be more directive about using context. Updated context formatting to make it clearer.

### User Prompt 68
"Got this response with a lot of unnecessary info - It seems like you might be looking for information about resources or the booking process. Here's a detailed overview based on the context provided. ### Resources Overview In our system, we have various resources categorized by their features, performance, and pricing. Here are some of the key resources you can consider: 1. **Ollama** - **Cost**: Free - **Setup**: Complex - **Quality**: Good - **Speed**: Slow - **Privacy**: Complete - **Best For**: Development/Testing 2. **Gemini** - **Cost**: ~$0.88/10K - **Setup**: Simple - **Quality**: Very Good - **Speed**: Fast - **Privacy**: Google - **Best For**: Production (Cost) 3. **OpenAI (GPT-4o-mini)** - **Cost**: ~$0.50/10K - **Setup**: Simple - **Quality**: Excellent - **Speed**: Very Fast - **Privacy**: OpenAI - **Best For**: Production (Value) 4. **OpenAI (GPT-4o)** - **Cost**: ~$5-10/10K - **Setup**: Simple - **Quality**: Best-in-Class - **Speed**: Very Fast - **Privacy**: OpenAI - **Best For**: Production (Quality) ### Booking Process To book a resource, follow these steps: 1. **Identify Your Resource**: Determine which resource suits your needs based on cost, quality, and setup complexity. 2. **Access the Booking System**: Log into the Campus Resource Hub. 3. **Create a Booking**: - Navigate to the resource you want to book. - Select the desired time slot and duration for your booking. - Fill out any required information in the booking form. 4. **Approval Workflow**: Your booking may need to go through an approval process depending on the resource and its availability. Ensure you provide all necessary details to expedite this process. 5. **Confirmation**: Once approved, you will receive a confirmation of your booking. If you need assistance with specific resources or further details on the booking process, feel free to ask!"

**Response:** Added smart document prioritization to boost AI_Concierge_Prompt_Context.md for booking queries and filter out LLM provider chunks. Updated prompt to explicitly tell LLM to ignore LLM provider information and focus on campus resources.

### User Prompt 69
"Can you place all the promts in the dev_notes_md file, and the openai prompts in the golden_prompts.md file?"

**Response:** (Current response - adding all prompts to appropriate files)

---

## All Prompts Used in Resource Concierge System

### Main Response Generation Prompt (OpenAI GPT-4o-mini)

**Location**: `src/ai_features/concierge/response_generator.py` - `_build_prompt()` method

**Prompt with Context**:
```
You are a helpful assistant for the Campus Resource Hub - a system for booking campus resources like study rooms, computer labs, AV equipment, event spaces, and other facilities.

The following context contains detailed information about CAMPUS RESOURCES (study rooms, labs, equipment, spaces) and the BOOKING PROCESS for these resources. USE THIS CONTEXT to answer the user's question.

{full_context}

User Question: {query}

IMPORTANT INSTRUCTIONS:
- The context above is about CAMPUS RESOURCES (study rooms, computer labs, equipment, spaces) and how to BOOK them
- This is NOT about LLM providers, AI models, or API keys - ignore any information about Ollama, OpenAI, Gemini, GPT models, or API keys
- You MUST use the context about campus resources and booking to answer the question
- For booking questions: Explain the booking process for campus resources (study rooms, labs, etc.), requirements, approval workflow, and how to create bookings based on the context
- For resource questions: Describe what campus resources are (study rooms, labs, equipment), their fields, categories, and how to find/book them based on the context
- Be specific and reference details from the context (e.g., "According to the booking process, you need to...")
- Include resource names in your answer when available from the database context
- Format resource links as: [Resource Name](resource_id) where resource_id is the numeric ID
- If the user wants to book something, explain the steps they need to take based on the booking process in the context
- Never make up specific resource names, locations, or capabilities that aren't in the context
- Respect user role: {user_role}
- Be helpful, friendly, and actionable
- Focus ONLY on campus resources and booking - ignore any LLM/AI provider information

Answer:
```

**Prompt without Context**:
```
You are a helpful assistant for the Campus Resource Hub. Answer the user's question.

User Question: {query}

Instructions:
- Provide helpful guidance about the Campus Resource Hub system
- If you don't have specific information, provide general guidance
- Be helpful and friendly

Answer:
```

### Context Summarization Prompt (OpenAI GPT-4o-mini)

**Location**: `src/ai_features/concierge/llm_client.py` - `summarize_context()` method

**Prompt**:
```
Summarize the following context while preserving key information about resources, bookings, and system capabilities. Keep it under {max_length} characters.

Context:
{context}

Summary:
```

---

## Notes for Future Sessions

- Continue adding all new prompts and responses to this file
- Maintain chronological order
- Include both user prompts and AI responses
- Document all code changes and file modifications
- Note any errors encountered and their solutions



# Development Notes - AI Collaboration

This document tracks AI-assisted development activities, prompts, and insights throughout the Campus Resource Hub project.

## AI Tools Used

- **Cursor AI**: Primary IDE with AI assistance
- **GitHub Copilot**: Code completion and suggestions
- **OpenAI GPT-4o-mini**: AI Concierge feature and development assistance

## Model Context Protocol (MCP) Integration

### Implementation Date
December 2024

### Purpose
Implemented MCP (Model Context Protocol) to provide a safer, structured interface for AI agents to query the database. MCP enables read-only, secure database access for the AI Concierge feature.

### Implementation Details

**Files Created:**
- `src/ai_features/mcp_server.py` - MCP server implementation
- `src/ai_features/concierge/mcp_client.py` - MCP client wrapper

**Files Modified:**
- `src/ai_features/concierge/database_retriever.py` - Updated to use MCP when available
- `src/ai_features/concierge/query_processor.py` - Updated to pass app context for MCP
- `src/ai_features/concierge/booking_proposer.py` - Updated to pass app context for MCP
- `src/ai_features/concierge/response_generator.py` - Updated to pass app context for MCP
- `src/ai_features/concierge/concierge_controller.py` - Updated to initialize processors with app context
- `requirements.txt` - Added `mcp>=0.9.0` dependency

### Key Features

1. **Read-Only Database Access**: MCP server provides structured, read-only access to database queries
2. **Role-Based Filtering**: Enforces role-based access control (student, staff, admin)
3. **Fallback Mechanism**: Falls back to direct DAL access if MCP is unavailable
4. **Environment Configuration**: Can be enabled/disabled via `USE_MCP` environment variable

### MCP Methods Available

- `query_resources` - Search resources by query, role, category
- `get_resource_by_id` - Get specific resource details
- `get_resource_availability` - Check resource availability
- `get_resource_reviews` - Get reviews for a resource
- `get_categories` - List all resource categories

### Usage

MCP is automatically enabled by default. To disable:
```bash
export USE_MCP=false
```

The AI Concierge will automatically use MCP when available, falling back to direct DAL access if MCP is unavailable or disabled.

### Benefits

1. **Security**: Structured, read-only access prevents accidental data modification
2. **Separation of Concerns**: Clear separation between AI layer and database access
3. **Standardization**: Uses industry-standard MCP protocol for AI-database interaction
4. **Flexibility**: Can be enabled/disabled without code changes

## Representative Prompts

### MCP Implementation Prompt
```
Implement Model Context Protocol (MCP) integration for the Campus Resource Hub.
The MCP server should provide read-only database access for AI agents, with
role-based filtering and secure query handling. The implementation should
support fallback to direct DAL access if MCP is unavailable.
```

**AI Tool**: Cursor AI  
**Outcome**: Successfully implemented MCP server and client, integrated with existing AI Concierge feature.

## AI-Generated Code Attribution

All AI-generated or AI-suggested code is marked with comments like:
```python
# AI Contribution: [Description of AI assistance]
```

Examples:
- `# AI Contribution: Generated initial scaffold, verified by team.`
- `# AI Contribution: MCP integration implemented with Cursor AI assistance.`

## Golden Prompts

See `.prompt/golden_prompts.md` for especially effective prompts used during development.

