"""
Cached Offer Model
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta, timezone
import uuid
from app.db import Base


def utc_now():
    """Get current UTC time as timezone-naive datetime for SQLAlchemy compatibility"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CachedOffer(Base):
    __tablename__ = "cached_offers"

    offer_id = Column(String, primary_key=True, index=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    depart_ts = Column(DateTime, nullable=False)
    arrive_ts = Column(DateTime, nullable=False)
    airline = Column(String, nullable=False)
    flight_no = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    seats = Column(Integer, default=1)
    payload = Column(JSON, nullable=False)  # Full API response
    cached_at = Column(DateTime, default=utc_now)
    expire_at = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expire_at:
            self.expire_at = utc_now() + timedelta(hours=24)

