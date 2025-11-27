# 🏗️ System Documentation

Complete technical documentation covering Architecture, Tech Stack, Agent Workflow, and UI Design.

---

## 📐 Architecture

### System Overview

The Airline Booking Platform is a **multi-tier, microservices-inspired architecture** with a clear separation between frontend, backend, and AI orchestration layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Pages  │  │Components│  │   API    │  │  Router  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend Layer (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Routers  │  │ Services │  │  Models  │  │ Schemas  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │   LangGraph  │    │  External    │
│  + pgvector  │    │   Workflow   │    │    APIs      │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
                            │
                    ┌───────┴────────┐
                    │  AI Agents     │
                    │  (Gemini API)  │
                    └────────────────┘
```

### Architecture Layers

#### 1. **Frontend Layer** (Client-Side)
- **Technology**: React 18 with Vite
- **Purpose**: User interface and interaction
- **Responsibilities**:
  - Render UI components
  - Handle user input
  - Manage client-side state
  - Communicate with backend via REST API
  - Route navigation

#### 2. **Backend Layer** (API Server)
- **Technology**: FastAPI (Python)
- **Purpose**: Business logic and data management
- **Responsibilities**:
  - Handle HTTP requests
  - Process business logic
  - Manage database operations
  - Integrate with external APIs
  - Orchestrate AI workflows

#### 3. **Database Layer** (Data Persistence)
- **Technology**: PostgreSQL 14+ with pgvector extension
- **Purpose**: Store application data and vector embeddings
- **Responsibilities**:
  - Store bookings, offers, and user data
  - Store conversation memories with embeddings
  - Enable semantic search via pgvector
  - Maintain data integrity

#### 4. **AI Orchestration Layer** (LangGraph)
- **Technology**: Custom LangGraph implementation
- **Purpose**: Multi-agent workflow orchestration
- **Responsibilities**:
  - Coordinate agent execution
  - Manage conversation state
  - Route messages to appropriate agents
  - Maintain conversation context

#### 5. **External Services Layer**
- **Amadeus API**: Real-time flight data
- **Gemini API**: LLM for intent classification, slot filling, and embeddings
- **Fallback**: Mock data when APIs unavailable

### Data Flow Architecture

```
User Input
    │
    ▼
Frontend (React)
    │
    │ HTTP POST /api/chat/message
    ▼
Backend Router (chat.py)
    │
    │ process_message()
    ▼
LangGraph Workflow (graph.py)
    │
    ├─► Memory Agent (retrieve context)
    ├─► Intent Agent (classify intent)
    ├─► Router Agent (route to specialist)
    │
    ├─► Flight Search Agent ──► Amadeus API
    ├─► Slot Filling Agent ──► Gemini API
    ├─► Payment Agent ──► Booking API
    └─► Booking Confirmation Agent ──► Database
    │
    │ Response
    ▼
Backend Router
    │
    │ JSON Response
    ▼
Frontend (React)
    │
    ▼
User Interface
```

### Key Architectural Patterns

1. **RESTful API Design**: Standard HTTP methods and status codes
2. **Agent-Based Architecture**: Specialized agents for different tasks
3. **State Management**: Centralized state in LangGraph workflow
4. **Memory Persistence**: Vector embeddings for semantic search
5. **Async/Await**: Non-blocking I/O operations throughout
6. **Error Handling**: Graceful fallbacks at every layer
7. **Non-Blocking Operations**: Background tasks for non-critical operations

---

## 🛠️ Tech Stack

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.x | UI framework |
| **Vite** | Latest | Build tool and dev server |
| **React Router** | 7.x | Client-side routing |
| **Tailwind CSS** | 3.x | Utility-first CSS framework |
| **Axios** | Latest | HTTP client for API calls |
| **React Query** | Latest | Data fetching and caching |

**Key Features**:
- Component-based architecture
- Hooks for state management
- Responsive design with Tailwind
- Fast hot module replacement (HMR)

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Programming language |
| **FastAPI** | Latest | Web framework |
| **SQLAlchemy** | 2.x | ORM for database operations |
| **Alembic** | Latest | Database migration tool |
| **Pydantic** | 2.9+ | Data validation and settings |
| **httpx** | Latest | Async HTTP client |
| **python-dotenv** | Latest | Environment variable management |

**Key Features**:
- Async/await support
- Automatic API documentation (Swagger/OpenAPI)
- Type hints and validation
- High performance

### Database Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 14+ | Relational database |
| **pgvector** | Latest | Vector similarity search extension |
| **Docker** | Latest | Containerization for database |

**Key Features**:
- ACID compliance
- Vector embeddings storage (768 dimensions)
- Semantic search capabilities
- Docker-based deployment

### AI/ML Stack

| Technology | Purpose |
|------------|---------|
| **LangGraph** | Workflow orchestration (custom implementation) |
| **Google Gemini API** | LLM for intent classification and slot filling |
| **Gemini Embedding API** | Generate vector embeddings (embedding-001) |

**Key Features**:
- Multi-agent system
- Intent classification
- Natural language understanding
- Semantic memory retrieval

### External APIs

| Service | Purpose | Fallback |
|---------|---------|----------|
| **Amadeus API** | Real-time flight search | Mock data generator |
| **Gemini API** | LLM operations | Error responses |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Docker Compose** | Database containerization |
| **Git** | Version control |
| **VS Code / Cursor** | IDE |
| **Postman / Thunder Client** | API testing |

### Performance Optimizations

- **Non-blocking memory saves**: Fire-and-forget background tasks
- **Regex-first extraction**: Fast parsing before LLM calls
- **Reduced timeouts**: Optimized timeout values (3s-15s)
- **Limited context windows**: Smaller context for faster processing
- **Parallel operations**: Concurrent API calls
- **Character limits**: 500 chars for embeddings

**Result**: 40-60% faster response times on average.

---

## 🤖 Agent Workflow

### Workflow Overview

The system uses a **multi-agent orchestration pattern** where specialized agents handle specific tasks in a coordinated workflow.

```
┌─────────────────────────────────────────────────────────┐
│              LangGraph Workflow Entry Point             │
│              process_message()                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  1. Memory Manager Agent          │
        │     - Retrieve conversation context│
        │     - Restore booking fields      │
        │     - Restore selected offer      │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  2. Intent Agent                  │
        │     - Classify user intent        │
        │     - Extract slots (origin, dest,│
        │       date, passenger details)    │
        │     - Convert cities to codes     │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │  3. Router Agent                  │
        │     - Route based on intent       │
        └───────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────┐                      ┌───────────────┐
│ Flight Search │                      │ Offer Select  │
│    Agent      │                      │    Agent      │
└───────────────┘                      └───────────────┘
        │                                         │
        ▼                                         ▼
┌───────────────┐                      ┌───────────────┐
│ Slot Filling  │                      │   Payment     │
│    Agent      │                      │    Agent      │
└───────────────┘                      └───────────────┘
        │                                         │
        ▼                                         ▼
┌───────────────┐                      ┌───────────────┐
│   Booking     │                      │   Fallback    │
│ Confirmation  │                      │    Agent      │
│    Agent      │                      └───────────────┘
└───────────────┘
```

### Agent Details

#### 1. **Memory Manager Agent** (`memory_agent.py`)
- **Purpose**: Retrieve relevant conversation context
- **Input**: User message, user email
- **Output**: Memory context (last 10 messages)
- **Technology**: Vector similarity search (pgvector)
- **Optimization**: 3s timeout, limited to 10 messages

**Process**:
1. Generate embedding for user query
2. Search database for similar conversations
3. Return relevant context messages
4. Fallback to text search if embedding fails

#### 2. **Intent Agent** (`intent_agent.py`)
- **Purpose**: Classify user intent and extract slots
- **Input**: User message, memory context
- **Output**: Intent classification + extracted slots
- **Technology**: Gemini 2.5 Flash API
- **Intents**:
  - `flight_search`: User wants to search flights
  - `offer_selection`: User wants to select a flight
  - `slot_filling`: User providing booking details
  - `payment`: User confirming payment
  - `booking_inquiry`: User asking about bookings
  - `general`: General conversation

**Slot Extraction**:
- Origin airport code
- Destination airport code
- Departure date (converted to YYYY-MM-DD)
- Number of adults
- Offer ID
- Passenger details (name, email, phone)

#### 3. **Router Agent** (`router_agent.py`)
- **Purpose**: Route to appropriate specialist agent
- **Input**: Intent classification
- **Output**: Calls appropriate agent
- **Routing Logic**:
  ```python
  if intent == "flight_search":
      → flight_search_agent
  elif intent == "offer_selection":
      → offer_selection_agent
  elif intent == "slot_filling":
      → slot_filling_agent
  elif intent == "payment":
      → payment_agent
  elif intent == "booking_inquiry":
      → booking_confirmation_agent
  else:
      → fallback_agent
  ```

#### 4. **Flight Search Agent** (`flight_search_agent.py`)
- **Purpose**: Search for available flights
- **Input**: Origin, destination, date, passengers
- **Output**: List of flight offers
- **Technology**: Amadeus API (with mock fallback)
- **Process**:
  1. Validate airport codes
  2. Call Amadeus API or use mock data
  3. Format results with prices in INR (₹)
  4. Return formatted list

#### 5. **Offer Selection Agent** (`offer_selection_agent.py`)
- **Purpose**: Handle flight selection
- **Input**: Offer ID or flight number
- **Output**: Confirmation of selected flight
- **Process**:
  1. Parse selection (number or offer ID)
  2. Fetch offer details
  3. Store in state
  4. Request passenger details

#### 6. **Slot Filling Agent** (`slot_filling_agent.py`)
- **Purpose**: Collect passenger booking details
- **Input**: User message with passenger info
- **Output**: Extracted booking fields
- **Technology**: Gemini API + Regex fallback
- **Optimization**: Regex-first extraction (skips LLM for simple formats)
- **Required Fields**:
  - `full_name`: Passenger's full name
  - `email`: Email address
  - `phone`: Phone number (10+ digits)
  - `date_of_birth`: Date of birth (required field, format: YYYY-MM-DD)

**Process**:
1. Try regex extraction first (fast path)
2. If complex, use Gemini API
3. Merge with existing fields
4. Return `{done, booking_fields, missing}`

#### 7. **Payment Agent** (`payment_agent.py`)
- **Purpose**: Process payment confirmation
- **Input**: Payment confirmation keyword ("proceed")
- **Output**: Booking creation
- **Process**:
  1. Validate offer and passenger details
  2. Retrieve offer from memory if needed
  3. Create booking via API
  4. Return booking confirmation

#### 8. **Booking Confirmation Agent** (`booking_confirmation_agent.py`)
- **Purpose**: Provide booking details and history
- **Input**: Booking ID or user email
- **Output**: Formatted booking information
- **Process**:
  1. Fetch booking(s) from database
  2. Format with emojis and structure
  3. Convert USD to INR if needed
  4. Return formatted response

#### 9. **Fallback Agent** (`fallback_agent.py`)
- **Purpose**: Handle general conversation
- **Input**: Unclassified messages
- **Output**: Natural language response
- **Technology**: Gemini API
- **Process**:
  1. Include memory context
  2. Generate friendly response
  3. Maintain professional tone
- **Special Knowledge**:
  - Food service charges: ₹200 (200 Indian Rupees) per booking
  - Date of birth is required for all passengers
  - All prices displayed in Indian Rupees (INR)

### State Management

**AgentState** structure:
```python
{
    "user_message": str,
    "user_email": str,
    "conversation_id": str,
    "intent": Dict[str, Any],
    "slots": Dict[str, Any],
    "flight_search_results": List[Dict],
    "selected_offer": Dict[str, Any],
    "booking_fields": Dict[str, str],
    "payment_confirmed": bool,
    "booking_id": str,
    "memory_context": List[Dict],
    "response": str,
    "metadata": Dict[str, Any]
}
```

### Workflow Execution Flow

```
1. User sends message
   │
   ▼
2. Memory Manager retrieves context (3s timeout)
   │
   ▼
2a. Restore slots from memory (origin, destination, date)
   │
   ▼
3. Intent Agent classifies intent (Gemini API, preserves existing slots)
   │
   ▼
4. Router Agent routes to specialist
   │
   ▼
5. Specialist Agent processes request
   │
   ├─► Flight Search: Amadeus API (20s timeout)
   ├─► Slot Filling: Regex first, then Gemini (15s timeout)
   ├─► Payment: Booking API (8s timeout)
   └─► Booking Inquiry: Database query (8s timeout)
   │
   ▼
6. Response generated
   │
   ▼
7. Memory saved (non-blocking background task)
   │
   ▼
8. Response returned to user
```

### Performance Optimizations in Workflow

1. **Non-blocking memory save**: Doesn't wait for persistence
2. **Regex-first slot filling**: Skips LLM for simple inputs
3. **Reduced timeouts**: Faster failure detection
4. **Limited context**: Smaller memory windows
5. **Parallel operations**: Concurrent API calls where possible
6. **Slot restoration**: Preserves context between messages to avoid re-asking for information

---

## 🎨 UI Design

### Design System

**Color Palette**:
- **Primary**: Blue (#3B82F6) - Actions, links
- **Secondary**: Gray (#6B7280) - Secondary text
- **Success**: Green (#10B981) - Success messages
- **Error**: Red (#EF4444) - Error messages
- **Background**: White (#FFFFFF) - Main background
- **Card Background**: Gray-50 (#F9FAFB) - Card backgrounds

**Typography**:
- **Headings**: Inter, Bold
- **Body**: Inter, Regular
- **Code**: Monospace

**Spacing**: Tailwind's default spacing scale (4px base)

### Page Structure

#### 1. **Chat Page** (`ChatPage.jsx`)
- **Purpose**: AI conversation interface
- **Layout**: Full-width chat interface
- **Components**:
  - Chat message list (scrollable)
  - Textarea input with send button (resizable)
  - Loading indicator
- **Features**:
  - Real-time message display
  - Auto-scroll to latest message
  - Preserves line breaks and formatting
  - Responsive design (mobile-optimized)
  - Resizable textarea with native resize handle
  - Enter to send, Shift+Enter for new line

**UI Elements**:
```
┌─────────────────────────────────────┐
│         Navigation Bar              │
├─────────────────────────────────────┤
│                                     │
│  [User Message]                     │
│  [Bot Response]                     │
│  [User Message]                     │
│  [Bot Response]                     │
│                                     │
│  ────────────────────────────────   │
│  [Type message...]        [Send]    │
└─────────────────────────────────────┘
```

#### 2. **Flight Search Page** (`FlightSearchPage.jsx`)
- **Purpose**: Search for flights
- **Layout**: Centered form with card design
- **Components**:
  - Airport autocomplete inputs (origin/destination)
  - Date picker
  - Passenger count selector
  - Search button
- **Features**:
  - Airport autocomplete with 150+ airports
  - Debounced search (400ms)
  - Keyboard navigation
  - Helper text
  - Loading states

**UI Elements**:
```
┌─────────────────────────────────────┐
│         Navigation Bar              │
├─────────────────────────────────────┤
│                                     │
│    ┌─────────────────────────┐      │
│    │   Search Flights        │      │
│    │                         │      │ 
│    │  Origin: [Autocomplete] │      │
│    │  Dest:   [Autocomplete] │      │
│    │  Date:   [Date Picker]  │      │
│    │  Adults: [Dropdown]     │      │
│    │                         │      │
│    │      [Search Flights]   │      │
│    └─────────────────────────┘      │
│                                     │
└─────────────────────────────────────┘
```

#### 3. **Flight Results Page** (`FlightResultsPage.jsx`)
- **Purpose**: Display search results
- **Layout**: List of flight cards
- **Components**:
  - Flight card component
  - Price display (₹ INR)
  - Select button
  - Back to search link
- **Features**:
  - Responsive grid layout
  - Price highlighting
  - Clear call-to-action

**UI Elements**:
```
┌─────────────────────────────────────┐
│         Navigation Bar              │
├─────────────────────────────────────┤
│  Found 5 flights                    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ AA123  HYD → BOM            │    │
│  │ ₹24,999                     │    │
│  │ [Select Flight]             │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ DL456  HYD → BOM            │    │
│  │ ₹29,049                     │    │
│  │ [Select Flight]             │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

#### 4. **Booking Details Page** (`BookingDetailsPage.jsx`)
- **Purpose**: Collect passenger information
- **Layout**: Form with validation
- **Components**:
  - Text inputs (name, email, phone)
  - Date picker for date of birth (required)
  - Food service checkbox
  - Form validation
  - Submit button
- **Features**:
  - Real-time validation
  - Error messages
  - Clear labels
  - Date of birth is mandatory
  - Food service option (adds ₹200 to total)
  - Responsive grid layout

#### 5. **Payment Page** (`PaymentPage.jsx`)
- **Purpose**: Payment confirmation
- **Layout**: Summary card with payment button
- **Components**:
  - Booking summary
  - Price breakdown (Flight Charges + Food Service if selected)
  - Total price (₹ INR)
  - Confirm payment button
- **Features**:
  - Clear pricing breakdown
  - Food service charge display (₹200 if selected)
  - Confirmation dialog
  - Responsive design

#### 6. **Booking Confirmation Page** (`BookingConfirmationPage.jsx`)
- **Purpose**: Display booking confirmation
- **Layout**: Success message with details
- **Components**:
  - Success icon/message
  - Booking details card
  - Booking ID
  - Route display (origin city → destination city)
  - Food service indicator (if selected)
  - Download ticket button
  - Cancel booking button (for confirmed bookings)
  - Navigation links
- **Features**:
  - Clear success indication
  - Easy navigation
  - Download ticket as HTML file
  - Booking cancellation support
  - Responsive design

#### 7. **Booking History Page** (`BookingHistoryPage.jsx`)
- **Purpose**: Display past bookings
- **Layout**: List of booking cards
- **Components**:
  - Booking card component
  - Route display (origin city → destination city)
  - Status badges
  - Food service indicator (if selected)
  - View details link
  - Cancel button (for confirmed bookings)
- **Features**:
  - Chronological ordering
  - Status indicators
  - Responsive design
  - Origin and destination cities displayed
  - Booking cancellation support

### Component Library

#### **AirportAutocomplete** (`AirportAutocomplete.jsx`)
- **Purpose**: Smart airport code search
- **Features**:
  - Debounced search (400ms)
  - Minimum 2 characters
  - Keyboard navigation (arrow keys, Enter, Escape)
  - Mouse support
  - Loading indicator
  - Helper text
  - Auto-fill with IATA code
- **Data**: 150+ airports worldwide

#### **Navbar** (`Navbar.jsx`)
- **Purpose**: Navigation and branding
- **Features**:
  - Logo/brand name
  - Navigation links (desktop)
  - Mobile hamburger menu
  - Collapsible mobile menu
  - Touch-friendly buttons (min 44x44px)
  - Active route highlighting
  - Responsive design

#### **ErrorMessage** (`ErrorMessage.jsx`)
- **Purpose**: Display error messages
- **Features**:
  - Red color scheme
  - Clear messaging
  - Dismissible (optional)

#### **LoadingSpinner** (`LoadingSpinner.jsx`)
- **Purpose**: Show loading states
- **Features**:
  - Animated spinner
  - Centered display
  - Customizable size

### Responsive Design

**Breakpoints** (Tailwind):
- **sm**: 640px (mobile landscape)
- **md**: 768px (tablet)
- **lg**: 1024px (desktop)
- **xl**: 1280px (large desktop)

**Responsive Patterns**:
- Mobile: Single column, stacked elements, mobile menu
- Tablet: Two columns where appropriate
- Desktop: Multi-column layouts, sidebars

**Mobile Optimizations**:
- Touch-friendly targets (min 44x44px)
- Responsive padding and spacing
- Mobile-first design approach
- Native resize handles for textareas
- Optimized viewport settings
- Prevented iOS text size adjustment
- Improved touch responsiveness

### User Experience Features

1. **Loading States**: Spinners during API calls
2. **Error Handling**: Clear error messages
3. **Form Validation**: Real-time validation feedback
4. **Auto-complete**: Smart airport search
5. **Keyboard Navigation**: Full keyboard support
6. **Responsive**: Works on all screen sizes (mobile, tablet, desktop)
7. **Accessibility**: Semantic HTML, ARIA labels
8. **Food Service**: Optional food service with ₹200 charge
9. **Ticket Download**: Download booking tickets as HTML files
10. **Booking Cancellation**: Cancel confirmed bookings
11. **Context Preservation**: Maintains conversation context between messages
12. **Mobile Menu**: Hamburger menu for mobile navigation

### Design Principles

1. **Simplicity**: Clean, uncluttered interfaces
2. **Consistency**: Uniform design language
3. **Feedback**: Clear user feedback for all actions
4. **Performance**: Fast loading and interactions
5. **Accessibility**: Usable by all users
6. **Mobile-First**: Designed for mobile, enhanced for desktop

---

## 📊 System Metrics

### Performance Targets

- **Response Time**: 2-4s for simple queries, 5-8s for complex
- **Memory Retrieval**: < 3s
- **LLM Calls**: < 15s
- **API Calls**: < 20s with fallback
- **Page Load**: < 2s

### Scalability

- **Concurrent Users**: Designed for 100+ concurrent users
- **Database**: PostgreSQL with connection pooling
- **API Rate Limits**: Handled with retries and fallbacks
- **Caching**: Flight offers cached in database

---

## 🔐 Security Considerations

1. **Environment Variables**: All secrets in `.env` files
2. **Input Validation**: Pydantic schemas for validation
3. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
4. **CORS**: Configured for frontend origin only
5. **Error Handling**: No sensitive data in error messages

---

## 📝 Summary

This system implements a **production-ready, multi-agent AI platform** for airline booking with:

- **Modern Tech Stack**: React, FastAPI, PostgreSQL, LangGraph
- **Intelligent Agents**: Specialized agents for each task
- **Optimized Performance**: 40-60% faster than baseline
- **Beautiful UI**: Clean, responsive, accessible design
- **Robust Architecture**: Scalable, maintainable, extensible

The architecture supports easy extension with new agents, features, and integrations while maintaining high performance and user experience.

