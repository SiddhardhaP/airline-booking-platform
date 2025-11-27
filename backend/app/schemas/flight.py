"""
Flight-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin airport code (e.g., JFK)")
    destination: str = Field(..., description="Destination airport code (e.g., LAX)")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    adults: int = Field(1, ge=1, le=9, description="Number of adult passengers")
    children: int = Field(0, ge=0, le=9, description="Number of children")
    infants: int = Field(0, ge=0, le=9, description="Number of infants")


class OfferDetail(BaseModel):
    offer_id: str
    origin: str
    destination: str
    depart_ts: datetime
    arrive_ts: datetime
    airline: str
    flight_no: str
    price: float
    currency: str
    seats: int
    payload: Dict[str, Any]

    model_config = {"from_attributes": True}


class FlightSearchResponse(BaseModel):
    offers: List[OfferDetail]
    count: int

