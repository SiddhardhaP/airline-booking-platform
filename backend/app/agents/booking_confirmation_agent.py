"""
Booking Confirmation Agent
Provides booking confirmation details and booking history
"""
import os
import httpx
import logging
from datetime import datetime
from .base import AgentState

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
logger = logging.getLogger(__name__)


async def booking_confirmation_agent(state: AgentState) -> AgentState:
    """Provide booking confirmation details or booking history"""
    booking_id = state.get("booking_id")
    user_email = state.get("user_email")
    
    # If specific booking_id is provided, get that booking
    if booking_id:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_URL}/api/booking/{booking_id}",
                    timeout=8.0,  # Reduced from 10.0 to 8.0
                )
                
                if response.status_code == 200:
                    booking_data = response.json()
                    currency_symbol = "₹" if booking_data.get("currency") == "INR" else "$"
                    state["response"] = (
                        f"📋 Booking Details:\n\n"
                        f"Booking ID: {booking_data['booking_id']}\n"
                        f"Status: {booking_data['status']}\n"
                        f"Total: {currency_symbol}{booking_data['total_amount']:.2f} {booking_data.get('currency', 'INR')}\n"
                        f"Payment Status: {booking_data.get('payment_status', 'pending')}\n"
                        f"Created: {booking_data['created_at']}"
                    )
                else:
                    state["response"] = "Could not retrieve booking details."
        except Exception as e:
            logger.error(f"Error retrieving booking: {str(e)}")
            state["response"] = "Could not retrieve booking details."
    # Otherwise, get all bookings for the user
    elif user_email:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BACKEND_URL}/api/booking/user/{user_email}",
                    timeout=8.0,  # Reduced from 10.0 to 8.0
                )
                
                if response.status_code == 200:
                    bookings = response.json()
                    
                    if not bookings or len(bookings) == 0:
                        state["response"] = "You don't have any bookings yet. Would you like to search for flights?"
                    else:
                        # Format bookings with clean spacing and structure
                        booking_count = len(bookings)
                        booking_list = []
                        
                        for i, booking in enumerate(bookings, 1):
                            # Convert USD to INR if needed (for backward compatibility)
                            booking_currency = booking.get("currency", "INR")
                            booking_amount = booking.get("total_amount", 0)
                            
                            if booking_currency == "USD":
                                booking_amount = booking_amount * 83  # Convert to INR
                                booking_currency = "INR"
                                logger.info(f"Converted USD booking {booking['booking_id']} to INR")
                            
                            currency_symbol = "₹" if booking_currency == "INR" else "$"
                            
                            # Parse created_at if it's a string
                            created_at = booking.get("created_at")
                            if isinstance(created_at, str):
                                try:
                                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                    created_at = created_at.strftime("%B %d, %Y")
                                except:
                                    created_at = created_at[:10]  # Just take date part
                            
                            # Get passenger names
                            passengers = booking.get("passengers", [])
                            passenger_names = []
                            for passenger in passengers:
                                if isinstance(passenger, dict):
                                    passenger_names.append(passenger.get("full_name", "Unknown"))
                                else:
                                    passenger_names.append(str(passenger))
                            
                            # Format each booking with clean structure
                            booking_text = f"""📘 Booking {i}

• Booking ID: {booking['booking_id']}
• Date: {created_at}
• Passenger: {', '.join(passenger_names)}
• Total: {currency_symbol}{booking_amount:.2f} {booking_currency}
• Status: {booking.get('status', 'confirmed')}"""
                            
                            booking_list.append(booking_text)
                        
                        # Combine all bookings with double line breaks between them
                        bookings_text = "\n\n".join(booking_list)
                        
                        # Construct final response with header and footer
                        state["response"] = f"""📒 Your Booking History ({booking_count} booking{'s' if booking_count != 1 else ''})

{bookings_text}

Would you like details about a specific booking?"""
                else:
                    logger.error(f"Error retrieving bookings: {response.status_code}")
                    state["response"] = "Could not retrieve your booking history. Please try again."
        except Exception as e:
            logger.error(f"Error retrieving user bookings: {str(e)}", exc_info=True)
            state["response"] = "Could not retrieve your booking history. Please try again."
    else:
        state["response"] = "I need your email address to retrieve your bookings. Please provide your email."
    
    return state

