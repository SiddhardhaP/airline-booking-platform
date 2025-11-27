"""
Booking router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.db import get_db
from app.schemas.booking import BookingRequest, BookingResponse, BookingCreate
from app.models.booking import Booking
from app.models.cached_offer import CachedOffer
from app.utils.logger import get_logger
from app.utils.validators import validate_email, validate_phone
from app.data.airports import get_city_by_code

router = APIRouter(prefix="/api/booking", tags=["booking"])
logger = get_logger(__name__)


@router.post("/simulate_confirm", response_model=BookingResponse)
async def simulate_booking(
    request: BookingRequest,
    db: Session = Depends(get_db),
):
    """
    Simulate booking confirmation (no real payment)
    """
    # Validate inputs
    if not validate_email(request.user_email):
        raise HTTPException(status_code=400, detail="Invalid user email format")
    
    for passenger in request.passengers:
        if not validate_email(passenger.email):
            raise HTTPException(status_code=400, detail=f"Invalid email for passenger: {passenger.full_name}")
        if not validate_phone(passenger.phone):
            raise HTTPException(status_code=400, detail=f"Invalid phone for passenger: {passenger.full_name}")
        if not passenger.date_of_birth:
            raise HTTPException(status_code=400, detail=f"Date of birth is required for passenger: {passenger.full_name}")
    
    # Verify offer exists and has available seats
    offer = db.query(CachedOffer).filter(CachedOffer.offer_id == request.offer_id).first()
    
    if not offer:
        logger.warning(f"Offer not found: {request.offer_id}")
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Check if offer has enough seats available
    if offer.seats < len(request.passengers):
        logger.warning(f"Insufficient seats: requested {len(request.passengers)}, available {offer.seats}")
        raise HTTPException(
            status_code=400, 
            detail=f"Not enough seats available. Requested: {len(request.passengers)}, Available: {offer.seats}"
        )
    
    logger.info(f"Creating booking for user: {request.user_email}, offer: {request.offer_id}")
    
    try:
        # Calculate total amount
        total_amount = offer.price * len(request.passengers)
        
        # Add 200 INR if food preference is selected
        if request.food_preference:
            food_charge = 200.0
            if offer.currency == "USD":
                # Convert 200 INR to USD (200 / 83 ≈ 2.41 USD)
                food_charge = 200.0 / 83.0
            total_amount += food_charge
            logger.info(f"Food service selected: Added {food_charge} {offer.currency} to total amount")
        
        # Create booking
        booking = Booking(
            booking_id=str(uuid.uuid4()),
            user_email=request.user_email,
            offer_id=request.offer_id,
            passengers=[p.model_dump() for p in request.passengers],
            total_amount=total_amount,
            currency=offer.currency,
            payment_status="paid",
            status="confirmed",
            food_preference=request.food_preference,
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking created successfully: {booking.booking_id}")
        
        # Get city names for origin and destination
        origin_city = get_city_by_code(offer.origin)
        destination_city = get_city_by_code(offer.destination)
        
        # Create response dict with booking data including origin and destination
        booking_dict = {
            "booking_id": booking.booking_id,
            "user_email": booking.user_email,
            "offer_id": booking.offer_id,
            "passengers": booking.passengers,
            "total_amount": booking.total_amount,
            "currency": booking.currency,
            "payment_status": booking.payment_status,
            "status": booking.status,
            "food_preference": booking.food_preference,
            "origin": offer.origin,
            "destination": offer.destination,
            "origin_city": origin_city,
            "destination_city": destination_city,
            "created_at": booking.created_at,
        }
        
        return BookingResponse.model_validate(booking_dict)
    except Exception as e:
        db.rollback()
        logger.error(f"Booking creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Booking creation failed: {str(e)}")


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """
    Get booking details by booking ID
    """
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Fetch offer details to get origin and destination
    offer = db.query(CachedOffer).filter(CachedOffer.offer_id == booking.offer_id).first()
    
    # Convert currency for display only (don't modify database)
    display_amount = booking.total_amount
    display_currency = booking.currency
    if booking.currency == "USD":
        display_amount = booking.total_amount * 83  # Convert to INR (1 USD ≈ 83 INR)
        display_currency = "INR"
    
    # Get city names for origin and destination
    origin_city = get_city_by_code(offer.origin) if offer else None
    destination_city = get_city_by_code(offer.destination) if offer else None
    
    # Create response dict with booking data
    booking_dict = {
        "booking_id": booking.booking_id,
        "user_email": booking.user_email,
        "offer_id": booking.offer_id,
        "passengers": booking.passengers,
        "total_amount": display_amount,  # Use converted amount for display
        "currency": display_currency,  # Use converted currency for display
        "payment_status": booking.payment_status,
        "status": booking.status,
        "food_preference": booking.food_preference,
        "origin": offer.origin if offer else None,
        "destination": offer.destination if offer else None,
        "origin_city": origin_city,
        "destination_city": destination_city,
        "created_at": booking.created_at,
    }
    
    return BookingResponse.model_validate(booking_dict)


@router.get("/user/{user_email}", response_model=list[BookingResponse])
async def get_user_bookings(user_email: str, db: Session = Depends(get_db)):
    """
    Get all bookings for a user
    Converts USD to INR for backward compatibility
    """
    bookings = db.query(Booking).filter(Booking.user_email == user_email).all()
    
    # Convert USD to INR for display only (don't modify database)
    result = []
    for booking in bookings:
        # Convert currency for display only, don't modify database
        display_amount = booking.total_amount
        display_currency = booking.currency
        if booking.currency == "USD":
            display_amount = booking.total_amount * 83  # Convert to INR (1 USD ≈ 83 INR)
            display_currency = "INR"
        
        # Fetch offer details to get origin and destination
        offer = db.query(CachedOffer).filter(CachedOffer.offer_id == booking.offer_id).first()
        
        # Get city names for origin and destination
        origin_city = get_city_by_code(offer.origin) if offer else None
        destination_city = get_city_by_code(offer.destination) if offer else None
        
        booking_dict = {
            "booking_id": booking.booking_id,
            "user_email": booking.user_email,
            "offer_id": booking.offer_id,
            "passengers": booking.passengers,
            "total_amount": display_amount,  # Use converted amount for display
            "currency": display_currency,  # Use converted currency for display
            "payment_status": booking.payment_status,
            "status": booking.status,
            "food_preference": booking.food_preference,
            "origin": offer.origin if offer else None,
            "destination": offer.destination if offer else None,
            "origin_city": origin_city,
            "destination_city": destination_city,
            "created_at": booking.created_at,
        }
        
        result.append(BookingResponse.model_validate(booking_dict))
    
    return result


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(booking_id: str, db: Session = Depends(get_db)):
    """
    Cancel a booking by booking ID
    """
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    try:
        # Update booking status to cancelled
        booking.status = "cancelled"
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking cancelled successfully: {booking.booking_id}")
        
        # Fetch offer details to get origin and destination
        offer = db.query(CachedOffer).filter(CachedOffer.offer_id == booking.offer_id).first()
        
        # Convert currency for display only (don't modify database)
        display_amount = booking.total_amount
        display_currency = booking.currency
        if booking.currency == "USD":
            display_amount = booking.total_amount * 83  # Convert to INR (1 USD ≈ 83 INR)
            display_currency = "INR"
        
        # Get city names for origin and destination
        origin_city = get_city_by_code(offer.origin) if offer else None
        destination_city = get_city_by_code(offer.destination) if offer else None
        
        # Create response dict with booking data
        booking_dict = {
            "booking_id": booking.booking_id,
            "user_email": booking.user_email,
            "offer_id": booking.offer_id,
            "passengers": booking.passengers,
            "total_amount": display_amount,  # Use converted amount for display
            "currency": display_currency,  # Use converted currency for display
            "payment_status": booking.payment_status,
            "status": booking.status,
            "food_preference": booking.food_preference,
            "origin": offer.origin if offer else None,
            "destination": offer.destination if offer else None,
            "origin_city": origin_city,
            "destination_city": destination_city,
            "created_at": booking.created_at,
        }
        
        return BookingResponse.model_validate(booking_dict)
    except Exception as e:
        db.rollback()
        logger.error(f"Booking cancellation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Booking cancellation failed: {str(e)}")

