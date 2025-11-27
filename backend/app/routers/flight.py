"""
Flight search router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
from app.db import get_db
from app.schemas.flight import FlightSearchRequest, FlightSearchResponse, OfferDetail
from app.services.amadeus_service import AmadeusService
from app.models.cached_offer import CachedOffer
from app.utils.logger import get_logger
from app.utils.validators import validate_airport_code, validate_date_format

router = APIRouter(prefix="/api/flight", tags=["flight"])
amadeus_service = AmadeusService()
logger = get_logger(__name__)


def _parse_amadeus_offer(offer: dict) -> dict:
    """Parse Amadeus offer to our format"""
    itinerary = offer.get("itineraries", [{}])[0]
    segments = itinerary.get("segments", [])
    
    if not segments:
        raise ValueError("No segments found in itinerary")
    
    # For multi-segment flights, use first segment's origin and last segment's destination
    first_segment = segments[0]
    last_segment = segments[-1]
    
    origin = first_segment.get("departure", {}).get("iataCode", "").upper()
    destination = last_segment.get("arrival", {}).get("iataCode", "").upper()
    original_offer_id = offer.get("id", "")
    
    # Make offer_id unique by combining with route to avoid conflicts
    # This handles cases where Amadeus returns same IDs for different routes
    unique_offer_id = f"{original_offer_id}_{origin}_{destination}"
    
    price_info = offer.get("price", {})
    
    return {
        "offer_id": unique_offer_id,
        "origin": origin,
        "destination": destination,
        "depart_ts": datetime.fromisoformat(
            first_segment.get("departure", {}).get("at", "").replace("Z", "+00:00")
        ),
        "arrive_ts": datetime.fromisoformat(
            last_segment.get("arrival", {}).get("at", "").replace("Z", "+00:00")
        ),
        "airline": first_segment.get("carrierCode", ""),
        "flight_no": f"{first_segment.get('carrierCode', '')}{first_segment.get('number', '')}",
        "price": float(price_info.get("total", 0)),
        "currency": price_info.get("currency", "INR"),
        "seats": offer.get("numberOfBookableSeats", 1),
        "payload": offer,
    }


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(
    request: FlightSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Search for flights and cache results
    """
    # Validate inputs
    if not validate_airport_code(request.origin):
        raise HTTPException(status_code=400, detail="Invalid origin airport code")
    if not validate_airport_code(request.destination):
        raise HTTPException(status_code=400, detail="Invalid destination airport code")
    if not validate_date_format(request.departure_date):
        raise HTTPException(status_code=400, detail="Invalid departure date format. Use YYYY-MM-DD")
    if request.return_date and not validate_date_format(request.return_date):
        raise HTTPException(status_code=400, detail="Invalid return date format. Use YYYY-MM-DD")
    
    logger.info(f"Searching flights: {request.origin} -> {request.destination} on {request.departure_date}")
    
    try:
        # Search flights via Amadeus
        amadeus_offers = await amadeus_service.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            adults=request.adults,
            children=request.children,
            infants=request.infants,
        )

        # Parse and cache offers
        cached_offers = []
        for offer in amadeus_offers[:15]:  # Limit to 15
            try:
                parsed = _parse_amadeus_offer(offer)
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Failed to parse offer {offer.get('id', 'unknown')}: {str(e)}")
                continue
            
            # Validate that parsed offer matches search parameters
            if parsed.get("origin", "").upper() != request.origin.upper():
                logger.warning(f"Offer {parsed.get('offer_id')} origin mismatch: expected {request.origin}, got {parsed.get('origin')}")
                continue
            if parsed.get("destination", "").upper() != request.destination.upper():
                logger.warning(f"Offer {parsed.get('offer_id')} destination mismatch: expected {request.destination}, got {parsed.get('destination')}")
                continue
            
            # Ensure currency is INR (convert from USD if needed)
            if parsed.get("currency", "INR") == "USD":
                # Convert USD to INR (1 USD ≈ 83 INR)
                parsed["price"] = parsed["price"] * 83
                parsed["currency"] = "INR"
            
            # Check if already cached - verify it matches the current search route
            existing = db.query(CachedOffer).filter(
                CachedOffer.offer_id == parsed["offer_id"],
                CachedOffer.origin == parsed["origin"].upper(),
                CachedOffer.destination == parsed["destination"].upper(),
            ).first()
            
            if existing:
                # Convert to INR for display if needed (don't modify database during read)
                # Only update if we're caching a new offer with USD
                cached_offers.append(existing)
            else:
                # Create new cached offer
                # Note: offer_id is now unique per route, so no need to check for duplicates
                try:
                    cached_offer = CachedOffer(**parsed)
                    db.add(cached_offer)
                    cached_offers.append(cached_offer)
                except IntegrityError as e:
                    # Handle duplicate key error - offer was inserted between check and insert
                    db.rollback()
                    logger.warning(f"Duplicate key error for offer {parsed['offer_id']}, attempting to retrieve existing offer")
                    # Try to get the existing offer for this route
                    existing_offer = db.query(CachedOffer).filter(
                        CachedOffer.offer_id == parsed["offer_id"],
                        CachedOffer.origin == parsed["origin"].upper(),
                        CachedOffer.destination == parsed["destination"].upper(),
                    ).first()
                    if existing_offer:
                        cached_offers.append(existing_offer)
                    else:
                        logger.warning(f"Could not retrieve existing offer {parsed['offer_id']} after duplicate key error")
                    continue
                except Exception as e:
                    # Handle other exceptions
                    db.rollback()
                    logger.error(f"Failed to cache offer {parsed['offer_id']}: {str(e)}")
                    continue

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Failed to commit cached offers due to duplicate key: {str(e)}")
            # Retrieve valid offers that match the search
            valid_cached_offers = []
            for offer in amadeus_offers[:15]:  # Check all 15 offers, not just 5
                parsed_check = _parse_amadeus_offer(offer)
                if (parsed_check.get("origin", "").upper() == request.origin.upper() and
                    parsed_check.get("destination", "").upper() == request.destination.upper()):
                    existing = db.query(CachedOffer).filter(
                        CachedOffer.offer_id == parsed_check["offer_id"],
                        CachedOffer.origin == parsed_check["origin"].upper(),
                        CachedOffer.destination == parsed_check["destination"].upper(),
                    ).first()
                    if existing:
                        valid_cached_offers.append(existing)
            cached_offers = valid_cached_offers
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to commit cached offers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to cache flight offers: {str(e)}")

        # Refresh to get IDs and filter to ensure all offers match the search
        valid_offers = []
        for offer in cached_offers:
            db.refresh(offer)
            # Double-check that the offer matches the search parameters
            if (offer.origin.upper() == request.origin.upper() and 
                offer.destination.upper() == request.destination.upper()):
                valid_offers.append(offer)
            else:
                logger.warning(f"Filtered out offer {offer.offer_id}: route mismatch - expected {request.origin}->{request.destination}, got {offer.origin}->{offer.destination}")

        if not valid_offers:
            logger.warning(f"No valid offers found for route {request.origin} -> {request.destination}")
            return FlightSearchResponse(offers=[], count=0)

        return FlightSearchResponse(
            offers=[OfferDetail.model_validate(offer) for offer in valid_offers],
            count=len(valid_offers),
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Flight search failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")


@router.get("/offer/{offer_id}", response_model=OfferDetail)
async def get_offer_details(offer_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific cached offer
    """
    offer = db.query(CachedOffer).filter(CachedOffer.offer_id == offer_id).first()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Convert USD to INR for display only (don't modify database)
    display_price = offer.price
    display_currency = offer.currency
    if offer.currency == "USD":
        display_price = offer.price * 83  # Convert to INR
        display_currency = "INR"
    
    # Create a copy of the offer with converted values for response
    offer_dict = {
        "offer_id": offer.offer_id,
        "origin": offer.origin,
        "destination": offer.destination,
        "depart_ts": offer.depart_ts,
        "arrive_ts": offer.arrive_ts,
        "airline": offer.airline,
        "flight_no": offer.flight_no,
        "price": display_price,  # Use converted price
        "currency": display_currency,  # Use converted currency
        "seats": offer.seats,
        "payload": offer.payload,
    }
    
    return OfferDetail.model_validate(offer_dict)


@router.get("/airports/search")
async def search_airports_endpoint(query: str = "", limit: int = 10):
    """
    Search airports by IATA code, city name, or airport name
    Returns matching airports for autocomplete
    """
    from app.data.airports import search_airports as search_airports_data
    
    if len(query) < 2:
        return {"airports": []}
    
    results = search_airports_data(query, limit)
    return {"airports": results}

