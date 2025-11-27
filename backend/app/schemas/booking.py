"""
Booking-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class PassengerDetail(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: str  # Required field
    passport_number: Optional[str] = None


class BookingRequest(BaseModel):
    offer_id: str
    passengers: List[PassengerDetail]
    user_email: EmailStr
    food_preference: bool = False


class BookingCreate(BaseModel):
    offer_id: str
    user_email: EmailStr
    passengers: List[Dict[str, Any]]
    total_amount: float
    currency: str = "INR"


class BookingResponse(BaseModel):
    booking_id: str
    user_email: str
    offer_id: str
    passengers: List[Dict[str, Any]]
    total_amount: float
    currency: str
    payment_status: str
    status: str
    food_preference: bool
    origin: Optional[str] = None
    destination: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

