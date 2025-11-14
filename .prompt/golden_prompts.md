# Campus Resource Hub - Golden Prompts

## Project Bootstrap
[Original prompt text preserved here]

# AI-First Project Bootstrap — Campus Resource Hub (Full Database Setup)

---

## Resource Concierge Implementation Prompts

### Main Implementation Prompt

**Context**: Implement a Resource Concierge AI assistant for the Campus Resource Hub using Ollama with Llama 3.1 8B model. The concierge should answer questions about resources, availability, and help with booking.

**Requirements**:
1. **LLM Setup**: Use Ollama (local) with Llama 3.1 8B model
2. **Document Context**: Index all markdown files in `/docs/context/` folder (recursive)
3. **Database Context**: Query resources using existing DAL with role-based filtering
4. **Query Types**: Support multi-step, comparative, and temporal queries
5. **Role-Based Access**: Students see only published resources; staff/admin see all
6. **Privacy**: Never reveal other users' booking details or personal information
7. **UI**: Popup chatbot in lower right corner with full chat history
8. **Retrieval**: Simple text matching with context summarization if too long
9. **Booking Integration**: Can propose bookings with "Book Now" / "Decline" buttons
10. **Links**: Include links to resources, filter admin links based on role

**Implementation Structure**:
```
/src/ai_features/concierge/
  - context_retriever.py      # Loads and searches docs/context/*.md
  - database_retriever.py     # Queries DAL for resource data
  - query_processor.py        # Processes natural language queries
  - response_generator.py    # Formats LLM responses with links
  - llm_client.py            # Ollama client wrapper
  - booking_proposer.py      # Handles booking suggestion flow
  - role_filter.py           # Filters data based on user roles
  - context_summarizer.py    # Summarizes context if too long
  - concierge_controller.py  # Flask routes for chat API
```

**Key Components**:
- **ContextRetriever**: Recursively scans `/docs/context/` for `.md` files, chunks by sections/paragraphs, simple keyword matching
- **DatabaseRetriever**: Uses ResourceDAO, BookingDAO, ReviewDAO with role-based filtering, extracts keywords from queries
- **QueryProcessor**: Classifies query types (availability, booking, rating, popular, comparative, temporal), routes to appropriate retrievers
- **LLMClient**: Wraps Ollama API, handles errors gracefully, supports context summarization
- **ResponseGenerator**: Formats LLM responses, extracts resource links, adds booking proposals, filters admin links
- **RoleFilter**: Filters resources by status, sanitizes user data, enforces role-based access
- **BookingProposer**: Extracts booking intent, proposes bookings with availability check, formats proposals

**Prompt Template**:
```
You are a helpful assistant for the Campus Resource Hub. Answer questions using ONLY the provided context.

Context from documentation:
{doc_context}

Context from database:
{db_context}

User Question: {user_query}

Instructions:
- Answer using only the provided context
- If information is not available, say so clearly
- Include resource names in your answer
- Format resource links as: [Resource Name](resource_id) where resource_id is the numeric ID
- For booking suggestions, mention that you can help book the resource
- Never make up resource names, locations, or capabilities
- Respect user role: {user_role}
- Be concise but helpful
- If multiple resources match, mention the top 3-5 most relevant

Answer:
```

**UI Implementation**:
- Chatbot popup in lower right corner (position-fixed, z-index: 1050)
- Toggle button (circular, 60x60px) to open/close chatbot
- Chat history with scrollable container
- Input field with send button
- Minimize/close buttons in header
- Display links as buttons below messages
- Display booking proposals with "Book Now" / "Decline" buttons

**Security & Privacy**:
- All queries filtered by user role
- Never include other users' personal data in responses
- Admin dashboard links only shown to admins
- Aggregated statistics only (no individual user data)
- Input sanitization and output validation

---

### Component-Specific Prompts

#### Context Retriever Prompt
**Task**: Create a context retriever that loads all markdown files from `/docs/context/` folder recursively, chunks them by sections/paragraphs, and performs simple keyword matching against user queries. Return top 5 most relevant chunks with source information.

#### Database Retriever Prompt
**Task**: Create a database retriever that uses existing DAL (ResourceDAO, BookingDAO, ReviewDAO) to query resources based on user queries. Extract keywords from natural language queries, filter results by user role (students see only published resources), and return formatted resource information. Support availability queries, popular resources, and top-rated resources.

#### Query Processor Prompt
**Task**: Create a query processor that classifies user queries into types (availability, booking, rating, popular, comparative, temporal, location, category, general) and routes to appropriate retrievers. Handle multi-step queries by breaking them down and combining results.

#### LLM Client Prompt
**Task**: Create an LLM client wrapper for Ollama that connects to llama3.1:8b model. Handle errors gracefully, check availability, and support context summarization when context exceeds token limits.

#### Response Generator Prompt
**Task**: Create a response generator that formats LLM responses, extracts resource links from responses, creates clickable links, adds booking proposals when appropriate, and filters admin dashboard links based on user role.

#### Booking Proposer Prompt
**Task**: Create a booking proposer that extracts booking intent from queries (resource name, date, time, duration), checks availability, and formats booking proposals with "Book Now" / "Decline" buttons.

#### Role Filter Prompt
**Task**: Create a role filter that filters resources by status (published only for students), sanitizes user data to remove other users' personal information, and filters admin dashboard links from responses.

#### Context Summarizer Prompt
**Task**: Create a context summarizer that checks if retrieved context exceeds LLM token limits and summarizes if needed, preserving key information while reducing length.

---

### Testing Prompts

#### Test Query Types
1. **Availability Query**: "What study rooms are available next Tuesday afternoon?"
2. **Booking Query**: "I want to book a conference room for tomorrow at 2pm"
3. **Rating Query**: "What are the top-rated resources?"
4. **Popular Query**: "What are the most booked resources?"
5. **Comparative Query**: "Which resource has more capacity, Room A or Room B?"
6. **Temporal Query**: "What resources are typically available on weekends?"
7. **Location Query**: "Show me all resources in Building A"
8. **Category Query**: "What resources have projectors?"

#### Test Role-Based Access
- Student querying for draft/archived resources (should not see them)
- Admin querying for all resources (should see all)
- Verify admin dashboard links only shown to admins

#### Test Privacy
- Query should never reveal other users' booking details
- Query should never reveal other users' personal information
- Only aggregated statistics should be shown

---

### Error Handling Prompts

**LLM Unavailable**: "I apologize, but I'm having trouble processing your request right now. Please try again later."

**No Context Found**: "I don't have information about that in my knowledge base. Could you try rephrasing your question?"

**Ambiguous Query**: "I found multiple resources that might match. Could you be more specific? For example, are you looking for a specific location or category?"

**Booking Conflict**: "I found that resource, but it appears to be unavailable at that time. Would you like me to suggest alternative times or resources?"

---

### UI/UX Prompts

**Chatbot Toggle Button**: Circular button (60x60px) in lower right corner with robot icon, opens chatbot when clicked.

**Chatbot Window**: 400px wide, max 600px height, positioned in lower right corner, scrollable chat history, input field at bottom.

**Message Bubbles**: User messages aligned right (blue), AI messages aligned left (light gray), max width 80%, word wrap enabled.

**Links**: Display as buttons below messages, styled with Bootstrap btn-outline-primary, open in new tab.

**Booking Proposals**: Display in highlighted box with resource details, "Book Now" button (links to booking page), "Decline" button (removes proposal).

**Loading State**: Show spinner with "Thinking..." message while processing query.

---

### Integration Prompts

**Blueprint Registration**: Register concierge_bp in app.py after other blueprints.

**Base Template Integration**: Add chatbot HTML and JavaScript to base.html template, only show for authenticated users.

**CSRF Protection**: Concierge query endpoint should use CSRF protection (Flask-WTF handles this automatically for POST requests).

**Authentication**: All concierge routes require @login_required decorator.

---

### Performance Optimization Prompts

**Context Caching**: Cache loaded documents in memory to avoid re-reading files on every query.

**Query Optimization**: Limit database results to top 10 most relevant, limit document chunks to top 5.

**Context Summarization**: If total context exceeds 2000 characters, summarize before sending to LLM.

**Response Time**: Target < 5 seconds for 90% of queries. Use async processing if needed.

---

### Documentation Prompts

**API Documentation**: Document all concierge endpoints:
- `POST /concierge/query` - Process user query, returns JSON with response, links, booking proposal
- `GET /concierge/health` - Check if LLM service is available

**User Documentation**: Create user guide explaining:
- How to use the concierge
- What types of questions it can answer
- How to book resources through the concierge
- Privacy and security information

---

## End of Resource Concierge Prompts

---

## OpenAI GPT-4o-mini Prompts (Current Implementation)

### Main Response Generation Prompt

**Purpose**: Generate helpful responses to user queries about campus resources and booking process using retrieved context.

**Model**: OpenAI GPT-4o-mini

**Location**: `src/ai_features/concierge/response_generator.py` - `_build_prompt()` method

**Prompt Template (With Context)**:
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

**Variables**:
- `{full_context}`: Formatted context from documentation and database (includes document chunks and database results)
- `{query}`: User's natural language question
- `{user_role}`: Current user's role (student, staff, admin)

**Prompt Template (Without Context)**:
```
You are a helpful assistant for the Campus Resource Hub. Answer the user's question.

User Question: {query}

Instructions:
- Provide helpful guidance about the Campus Resource Hub system
- If you don't have specific information, provide general guidance
- Be helpful and friendly

Answer:
```

**Usage**: This prompt is used when no relevant context is found. Provides fallback guidance.

---

### Context Summarization Prompt

**Purpose**: Summarize long context to fit within token limits while preserving key information.

**Model**: OpenAI GPT-4o-mini

**Location**: `src/ai_features/concierge/llm_client.py` - `summarize_context()` method

**Prompt Template**:
```
Summarize the following context while preserving key information about resources, bookings, and system capabilities. Keep it under {max_length} characters.

Context:
{context}

Summary:
```

**Variables**:
- `{max_length}`: Maximum desired length in characters (default: 1000)
- `{context}`: Long context text that needs to be summarized

**Parameters**:
- `temperature`: 0.3 (lower for more focused summarization)
- `max_tokens`: 200

**Usage**: Called automatically when retrieved context exceeds token limits. Ensures important information is preserved while reducing length.

---

### Prompt Engineering Notes

**Key Design Decisions**:
1. **Explicit Context Instructions**: The prompt explicitly tells the LLM to USE the provided context and not claim it doesn't have information
2. **Domain Clarity**: Clearly states this is about CAMPUS RESOURCES, not LLM providers
3. **Actionable Guidance**: Instructions emphasize being specific and referencing context details
4. **Role Awareness**: Includes user role in prompt for role-based responses
5. **Link Formatting**: Specifies exact format for resource links to enable automatic extraction

**Improvements Made**:
1. Added document prioritization to boost relevant context files
2. Added filtering to exclude LLM provider information for booking queries
3. Enhanced prompt with explicit instructions to ignore LLM/AI provider information
4. Improved context formatting to make relevance clearer
5. Added fallback prompt for when no context is available

**Performance Considerations**:
- Context is limited to top 5 document chunks and top 10 database results
- Context summarization kicks in if total length exceeds 2000 characters
- Prompt is optimized for GPT-4o-mini's token limits and response patterns

---

## End of OpenAI Prompts

---

## IU Brand Styling Implementation Prompts

### Main IU Styling Implementation Prompt

**Purpose**: Implement Indiana University (IU) brand guidelines for the Campus Resource Hub website, ensuring compliance with IU visual identity standards while maintaining all existing functionality.

**Context**: The Campus Resource Hub needs to reflect Indiana University's official brand guidelines, including colors, typography, and design standards as specified in the IU Style Guide.

**Location**: Implementation spans multiple files, primarily `src/static/css/style.css` with minimal template updates.

**IU Brand Guidelines Summary**:

**Colors:**
- **Primary**: IU Crimson (#990000) - MUST be dominant in all communication pieces
- **Primary/Alternate**: IU Cream (#EDEBEB) or white for backgrounds
- **Secondary Options**: 
  - Gold (#F1BE48) - Supporting accent color
  - Mint/Dark Mint (#008264) - Part of broader secondary palette
  - Midnight/Dark Midnight (#006298) - Secondary "cool" accent tone
- **Usage Rule**: Choose ONE secondary color and its tints/shades; avoid multiple secondaries simultaneously
- **Neutral Grays**: Light grays, neutrals, and white for backgrounds and whitespace
- **First Section Requirement**: First section of every page MUST be white with text for accessibility

**Typography:**
- **Headings (h1-h6)**: 
  - Preferred: 'Georgia Pro' (if licensed)
  - Fallback: Georgia (system font, wide availability)
  - Final fallback: Any serif font
- **Body Text**: 
  - Franklin Gothic or 'Franklin Gothic Medium'
  - Fallback: Arial
  - Final fallback: Generic sans-serif
- **Note**: When embedding custom fonts via @font-face, ensure licensing compliance

**Implementation Requirements**:

1. **CSS Variables Setup**:
   ```css
   :root {
       /* IU Primary Colors */
       --iu-crimson: #990000;
       --iu-crimson-hover: #b30000;
       --iu-cream: #EDEBEB;
       --iu-white: #ffffff;
       
       /* IU Secondary Colors (Gold selected as primary secondary) */
       --iu-gold: #F1BE48;
       --iu-mint: #008264;
       --iu-midnight: #006298;
       
       /* Neutral Grays */
       --iu-gray-light: #f5f5f5;
       --iu-gray-medium: #cccccc;
       --iu-gray-dark: #666666;
       --iu-text-primary: #333333;
       --iu-text-secondary: #666666;
       
       /* Bootstrap Overrides - IU Crimson as Primary */
       --bs-primary: var(--iu-crimson);
       --bs-primary-rgb: 153, 0, 0;
   }
   ```

2. **Typography Implementation**:
   ```css
   /* Headings - Serif (Georgia Pro/Georgia) */
   h1, h2, h3, h4, h5, h6 {
       font-family: 'Georgia Pro', Georgia, serif;
       font-weight: 600;
       line-height: 1.2;
   }
   
   /* Body Text - Sans-serif (Franklin Gothic/Arial) */
   body {
       font-family: Franklin Gothic, 'Franklin Gothic Medium', Arial, sans-serif;
   }
   ```

3. **Component Overrides**:
   - Buttons: Primary buttons use IU Crimson (#990000)
   - Cards: White or IU Cream backgrounds
   - Navbar: IU Crimson background
   - Sidebar: Active link color changed from Bootstrap blue to IU Crimson
   - Forms: IU-compliant styling
   - Badges: Use IU color palette
   - Modals: IU-compliant styling

4. **Accessibility Requirements**:
   - First section of every page MUST be white background with text
   - Ensure proper contrast ratios (WCAG compliant)
   - Focus states clearly visible
   - Keyboard navigation support

**Key Principles**:
- **Crimson Dominance**: IU Crimson must be the most prominent color
- **Consistency**: Use design system approach with consistent spacing, colors, typography
- **Progressive Enhancement**: Start with foundation, add enhancements incrementally
- **No Functionality Changes**: Maintain all existing functionality while updating styling
- **Performance**: Minimize custom CSS size, use CSS variables for maintainability

**Files to Modify**:
- **Primary**: `src/static/css/style.css` (~80-85% of changes)
- **Templates**: Minimal updates to ~8-12 template files (~10-15% of changes)
- **JavaScript**: Chart.js color definitions in `admin/reports.html` (~5% of changes)

**Implementation Steps**:
1. Add IU CSS variables to `style.css`
2. Implement IU typography (headings and body text)
3. Override Bootstrap primary color to IU Crimson
4. Update component styles (buttons, cards, navbar, sidebar, forms, badges, modals)
5. Ensure first section white background requirement
6. Update Chart.js colors in admin reports
7. Test accessibility and contrast
8. Verify all functionality still works

**Testing Requirements**:
- Verify IU Crimson is dominant color throughout site
- Check typography renders correctly (Georgia for headings, Franklin Gothic/Arial for body)
- Ensure first section of all pages is white with text
- Test accessibility (contrast, focus states, keyboard navigation)
- Verify all existing functionality works
- Test responsive design with IU styling

**Resources**:
- IU Style Guide: `docs/context/AiDD/IU_Style_Guide.md`
- IU Web Framework Documentation: https://plus.college.indiana.edu/guidelines/style-guide/index.html
- IU Styling Scope Analysis: `docs/context/AiDD/IU_Styling_Scope_Analysis.md`

---

### IU Styling Component-Specific Prompts

#### CSS Variables Prompt
**Task**: Create CSS custom properties (variables) for IU brand colors, including primary (IU Crimson), secondary colors (Gold, Mint, Midnight), neutral grays, and Bootstrap overrides. Ensure IU Crimson is set as the Bootstrap primary color.

#### Typography Prompt
**Task**: Implement IU typography standards: Georgia Pro/Georgia for headings (h1-h6) and Franklin Gothic/Arial for body text. Ensure proper font fallbacks and maintain readability.

#### Component Styling Prompt
**Task**: Update all Bootstrap components (buttons, cards, navbar, sidebar, forms, badges, modals) to use IU color palette. Ensure IU Crimson is the dominant color, and components maintain accessibility standards.

#### Accessibility Prompt
**Task**: Ensure all styling changes maintain WCAG compliance, including proper contrast ratios, visible focus states, and white background for first section of every page as required by IU guidelines.

#### Chart.js Color Update Prompt
**Task**: Update Chart.js color definitions in admin reports to use IU color palette (IU Crimson, Gold, Mint, Midnight) instead of default Bootstrap colors.

---

## End of IU Brand Styling Prompts

---

You are an expert full-stack Flask developer setting up the **Campus Resource Hub** project for the AiDD 2025 Capstone.  
Generate a **production-ready, database-integrated Flask scaffold** with migrations and sample seed data.

[... full prompt contents ...]