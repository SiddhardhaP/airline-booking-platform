"""
Booking Model
"""
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from app.db import Base


def utc_now():
    """Get current UTC time as timezone-naive datetime for SQLAlchemy compatibility"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_email = Column(String, nullable=False, index=True)
    offer_id = Column(String, ForeignKey("cached_offers.offer_id"), nullable=False)
    passengers = Column(JSON, nullable=False)  # List of passenger details
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    payment_status = Column(String, default="pending")  # pending, paid, failed
    status = Column(String, default="confirmed")  # confirmed, cancelled
    food_preference = Column(Boolean, default=False)  # Whether user wants food
    created_at = Column(DateTime, default=utc_now)

