"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import flight, booking, memory, chat
from app.db import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Airline Booking Platform API",
    description="Multi-agent AI-powered flight booking system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flight.router)
app.include_router(booking.router)
app.include_router(memory.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"message": "Airline Booking Platform API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

