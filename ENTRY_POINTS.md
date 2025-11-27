# Project Entry Points

This document explains all the entry points (start points) of the project.

## 🎯 Main Entry Points

### 1. **Backend Entry Point** (Python/FastAPI)
**File**: `backend/app/main.py`

This is the **main entry point** for the backend server.

```python
# backend/app/main.py
from fastapi import FastAPI
from app.routers import flight, booking, memory, chat

app = FastAPI(...)  # FastAPI application instance

# All routers are registered here
app.include_router(flight.router)
app.include_router(booking.router)
app.include_router(memory.router)
app.include_router(chat.router)
```

**How to Start:**
```bash
cd airline-booking-platform/backend
uvicorn app.main:app --reload --port 8000
```

**What it does:**
- Creates the FastAPI application
- Registers all API routers (flight, booking, memory, chat)
- Sets up CORS middleware
- Creates database tables on startup
- Serves the API at `http://localhost:8000`

---

### 2. **Frontend Entry Point** (React)
**File**: `frontend/src/main.jsx`

This is the **main entry point** for the React frontend.

```javascript
// frontend/src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**How to Start:**
```bash
cd airline-booking-platform/frontend
npm run dev
```

**What it does:**
- Renders the React app into the DOM
- Loads the `App.jsx` component
- Starts the Vite development server at `http://localhost:5173`

---

### 3. **LangGraph Workflow Entry Point**
**File**: `langgraph/graph.py`

This is the **entry point** for the AI agent workflow.

```python
# langgraph/graph.py
async def process_message(
    message: str,
    user_email: str,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Main entry point for processing chat messages"""
    # Workflow execution...
```

**How it's called:**
- Called by `backend/app/routers/chat.py` when a chat message is received
- Not started directly - it's invoked by the backend API

**What it does:**
- Processes chat messages through the multi-agent workflow
- Orchestrates: Memory → Intent → Router → Agent
- Returns AI-generated responses

---

## 📊 Application Flow

### Startup Sequence

```
1. Backend (main.py)
   ├── Creates FastAPI app
   ├── Connects to database
   ├── Registers routers
   └── Starts server on port 8000

2. Frontend (main.jsx)
   ├── Renders React app
   ├── Loads App.jsx
   └── Starts Vite dev server on port 5173

3. User Interaction
   ├── Frontend sends request → Backend API
   ├── Backend routes to appropriate handler
   ├── If chat: Backend calls LangGraph (graph.py)
   └── Response sent back to Frontend
```

---

## 🔍 Key Files Breakdown

### Backend Structure

```
backend/app/main.py          ← START HERE (Backend entry point)
├── app/db.py                ← Database connection
├── app/routers/             ← API endpoints
│   ├── flight.py           ← Flight search endpoints
│   ├── booking.py          ← Booking endpoints
│   ├── memory.py           ← Memory/embedding endpoints
│   └── chat.py             ← Chat endpoint (calls LangGraph)
├── app/services/            ← Business logic
│   ├── amadeus_service.py  ← Flight API integration
│   └── embedding_service.py ← Embedding generation
└── app/agents/              ← AI agents (used by LangGraph)
    ├── intent_agent.py
    ├── flight_search_agent.py
    └── ... (other agents)
```

### Frontend Structure

```
frontend/src/main.jsx        ← START HERE (Frontend entry point)
├── App.jsx                  ← Main app component
│   ├── Router setup
│   └── Page components
├── pages/                   ← Page components
│   ├── ChatPage.jsx
│   ├── FlightSearchPage.jsx
│   └── ... (other pages)
└── hooks/                   ← Custom React hooks
    ├── useChat.js
    └── ... (other hooks)
```

### LangGraph Structure

```
langgraph/graph.py           ← START HERE (Workflow orchestrator)
└── Calls agents from:
    backend/app/agents/
    ├── intent_agent.py
    ├── memory_agent.py
    ├── router_agent.py
    └── ... (other agents)
```

---

## 🚀 Quick Start Commands

### Start Backend
```bash
cd airline-booking-platform/backend
uvicorn app.main:app --reload
```
**Entry Point**: `backend/app/main.py`
**URL**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

### Start Frontend
```bash
cd airline-booking-platform/frontend
npm run dev
```
**Entry Point**: `frontend/src/main.jsx`
**URL**: http://localhost:5173

### LangGraph (Automatic)
- No direct start needed
- Automatically invoked when chat endpoint is called
- Entry Point: `langgraph/graph.py`

---

## 📝 Important Notes

1. **Backend must start first** - Frontend depends on backend API
2. **Database must be set up** - Run migrations before starting backend
3. **Environment variables** - Both backend and frontend need `.env` files
4. **LangGraph is integrated** - No separate process needed, called by backend

---

## 🔗 Entry Point Summary

| Component | Entry Point File | Command to Start |
|-----------|-----------------|------------------|
| **Backend API** | `backend/app/main.py` | `uvicorn app.main:app --reload` |
| **Frontend** | `frontend/src/main.jsx` | `npm run dev` |
| **LangGraph** | `langgraph/graph.py` | Called automatically by backend |

---

## 🎯 Where to Begin

1. **For Backend Development**: Start with `backend/app/main.py`
2. **For Frontend Development**: Start with `frontend/src/main.jsx`
3. **For AI Agent Development**: Start with `langgraph/graph.py` and `backend/app/agents/`

---

**Remember**: The main entry points are:
- **Backend**: `backend/app/main.py` 
- **Frontend**: `frontend/src/main.jsx`
- **LangGraph**: `langgraph/graph.py` (called by backend)

