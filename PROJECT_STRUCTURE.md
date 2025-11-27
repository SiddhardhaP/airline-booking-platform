# Project Structure

## 📂 Complete Directory Tree

```
airline-booking-platform/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── db.py                    # Database configuration
│   │   ├── routers/                 # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── flight.py            # Flight search endpoints
│   │   │   ├── booking.py           # Booking endpoints
│   │   │   ├── memory.py            # Memory/embedding endpoints
│   │   │   └── chat.py              # Chat/LangGraph endpoint
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── cached_offer.py      # Cached flight offers
│   │   │   ├── booking.py           # Booking records
│   │   │   └── convo_memory.py      # Conversation memory with embeddings
│   │   ├── schemas/                 # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── flight.py            # Flight request/response schemas
│   │   │   ├── booking.py           # Booking schemas
│   │   │   └── memory.py            # Memory schemas
│   │   ├── services/                # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── amadeus_service.py   # Amadeus API integration
│   │   │   └── embedding_service.py # Gemini embedding service
│   │   ├── data/                    # Static data files
│   │   │   ├── __init__.py
│   │   │   └── airports.py          # Airport codes and city mappings (150+ airports)
│   │   ├── agents/                  # LangGraph agent modules
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # AgentState type definition
│   │   │   ├── intent_agent.py      # Intent classification
│   │   │   ├── memory_agent.py      # Memory retrieval
│   │   │   ├── flight_search_agent.py
│   │   │   ├── offer_selection_agent.py
│   │   │   ├── slot_filling_agent.py
│   │   │   ├── payment_agent.py
│   │   │   ├── booking_confirmation_agent.py
│   │   │   ├── router_agent.py      # Routes to appropriate agent
│   │   │   └── fallback_agent.py    # General conversation
│   │   └── utils/                   # Utility functions
│   ├── alembic/                      # Database migrations
│   │   ├── env.py                    # Alembic environment config
│   │   ├── script.py.mako            # Migration template
│   │   └── versions/
│   │       └── 001_initial_schema.py # Initial database schema
│   ├── alembic.ini                   # Alembic configuration
│   ├── requirements.txt              # Python dependencies
│   ├── pyproject.toml                # Python project config
│   ├── scripts/                      # Utility scripts
│   │   └── update_currency_to_inr.py # One-time script to update currency
│   ├── env.example                   # Environment variables template
│   └── .env                          # Your actual .env file (create from env.example)
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── pages/                    # React page components
│   │   │   ├── ChatPage.jsx         # AI chat interface
│   │   │   ├── FlightSearchPage.jsx  # Flight search form
│   │   │   ├── FlightResultsPage.jsx # Flight results display
│   │   │   ├── BookingDetailsPage.jsx # Passenger details form
│   │   │   ├── PaymentPage.jsx      # Payment simulation
│   │   │   ├── BookingConfirmationPage.jsx # Booking confirmation
│   │   │   └── BookingHistoryPage.jsx # Past bookings
│   │   ├── components/              # Reusable components
│   │   │   ├── Navbar.jsx           # Navigation bar
│   │   │   ├── AirportAutocomplete.jsx # Airport autocomplete with debouncing
│   │   │   ├── ErrorMessage.jsx     # Error message display
│   │   │   └── LoadingSpinner.jsx   # Loading indicator
│   │   ├── api/                      # API client functions
│   │   │   ├── client.js             # Axios client setup
│   │   │   ├── flight.js             # Flight API calls
│   │   │   ├── booking.js            # Booking API calls
│   │   │   └── chat.js               # Chat API calls
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── App.jsx                   # Main app component
│   │   ├── main.jsx                  # React entry point
│   │   └── index.css                 # Global styles
│   ├── index.html                    # HTML template
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── postcss.config.js             # PostCSS configuration
│   ├── env.example                   # Environment variables template
│   └── .env                          # Your actual .env file (create from env.example)
│
├── langgraph/                        # LangGraph Workflow
│   ├── __init__.py
│   └── graph.py                      # Main workflow orchestrator
│
├── README.md                         # Main documentation
├── RUN_COMMANDS.md                   # Complete command list for setup
├── ENTRY_POINTS.md                   # Entry points and workflow documentation
├── PROJECT_STRUCTURE.md              # This file
├── docker-compose.yml                # Docker configuration for PostgreSQL with pgvector
└── .gitignore                        # Git ignore rules

```

## 🔑 Key Files Location Reference

### Environment Files
- **Backend .env**: `backend/.env` (create from `backend/env.example`)
- **Frontend .env**: `frontend/.env` (create from `frontend/env.example`)

### Agent Code
- **All Agents**: `backend/app/agents/`
- **Workflow Orchestrator**: `langgraph/graph.py`

### API Endpoints
- **Flight Search**: `backend/app/routers/flight.py`
- **Booking**: `backend/app/routers/booking.py`
- **Memory**: `backend/app/routers/memory.py`
- **Chat**: `backend/app/routers/chat.py`

### Database
- **Models**: `backend/app/models/`
- **Migrations**: `backend/alembic/versions/`

### Frontend Pages
- **All Pages**: `frontend/src/pages/`
- **Components**: `frontend/src/components/`
- **API Clients**: `frontend/src/api/`

## 📝 File Naming Conventions

- **Python files**: `snake_case.py`
- **React components**: `PascalCase.jsx`
- **Configuration files**: `lowercase.config.js` or `lowercase.ini`
- **Environment files**: `.env` (actual) and `env.example` (template)

## 🎯 Entry Points

1. **Backend**: `backend/app/main.py` - Start with `uvicorn app.main:app --reload`
2. **Frontend**: `frontend/src/main.jsx` - Start with `npm run dev`
3. **LangGraph**: `langgraph/graph.py` - Called by chat router

## 🔄 Data Flow

1. **User** → Frontend (React)
2. **Frontend** → Backend API (FastAPI)
3. **Backend** → LangGraph Workflow (if chat)
4. **LangGraph** → Agents → Backend APIs
5. **Backend** → Database (PostgreSQL with pgvector)
6. **Backend** → External APIs (Amadeus, Gemini)
7. **Response** → Frontend → User

## ⚡ Performance Optimizations

The system includes several performance optimizations for faster response times:

- **Memory Retrieval**: Limited to 10 messages (reduced from 30) with 3s timeout
- **Non-blocking Memory Save**: Fire-and-forget background task for conversation persistence
- **Regex-First Slot Filling**: Fast regex extraction before LLM call for simple inputs
- **Reduced LLM Timeouts**: 15s timeout (reduced from 30s) with max output tokens limit
- **Optimized Embeddings**: 8s timeout with 500 character limit for faster processing
- **Parallel Operations**: Memory saves run concurrently
- **Reduced Context Windows**: Smaller context for faster LLM processing

Expected performance: **40-60% faster** on average, with simple queries being **2-3x faster**.

## 💰 Currency Support

- **Default Currency**: INR (Indian Rupees)
- **Price Display**: All prices shown with ₹ symbol
- **API Integration**: Amadeus API requests INR, falls back to USD if not supported
- **Database**: All bookings and offers stored in INR by default
- **Currency Conversion**: Display-only conversion (doesn't modify database records)

## 🍽️ Food Service

- **Food Service Charge**: ₹200 (200 Indian Rupees) per booking
- **Optional**: Users can select food service during booking
- **Display**: Shown in payment breakdown and booking confirmation
- **Database**: Stored in `food_preference` boolean field

## 📋 Booking Requirements

- **Date of Birth**: Required field for all passengers
- **Validation**: Enforced in both frontend and backend
- **Format**: YYYY-MM-DD

## 🎫 Ticket Download

- **Format**: HTML file with formatted ticket
- **Content**: Booking details, route, passengers, food service indicator
- **Location**: Booking confirmation page
- **File Name**: `ticket-{booking_id}.html`

## 📱 Responsive Design

- **Mobile-First**: Designed for mobile, enhanced for desktop
- **Breakpoints**: sm (640px), md (768px), lg (1024px)
- **Mobile Menu**: Hamburger menu for navigation
- **Touch Targets**: Minimum 44x44px for all interactive elements
- **Viewport**: Optimized for all screen sizes

## 🔄 Context Preservation

- **Slot Restoration**: Restores origin, destination, and date from previous messages
- **Memory Integration**: Uses conversation memory to maintain context
- **Prevents Re-asking**: Avoids asking for information already provided

