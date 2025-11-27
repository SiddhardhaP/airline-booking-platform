"""
Payment Agent
Handles payment confirmation
"""
import os
import httpx
import re
import logging
from .base import AgentState

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
logger = logging.getLogger(__name__)


async def payment_agent(state: AgentState) -> AgentState:
    """Handle payment confirmation"""
    user_message = state["user_message"].lower().strip()
    
    if "proceed" not in user_message and "confirm" not in user_message and "yes" not in user_message:
        state["response"] = "Please reply 'proceed' to confirm payment and complete your booking."
        return state
    
    # Proceed with booking
    selected_offer = state.get("selected_offer")
    booking_fields = state["booking_fields"]
    user_email = state["user_email"]
    memory_context = state.get("memory_context", [])
    
    # If no offer in current state, try to extract from memory context
    if not selected_offer:
        logger.info("Payment Agent: No offer in state, searching memory context...")
        offer_id = None
        flight_search_results = None
        
        # First check if offer_id was restored from memory in metadata
        restored_offer_id = state.get("metadata", {}).get("restored_offer_id")
        if restored_offer_id:
            offer_id = restored_offer_id
            logger.info(f"Payment Agent: Using restored offer_id from metadata: {offer_id}")
        
        # First, look for flight search results in memory
        for memory in reversed(memory_context):  # Check most recent first
            if memory.get("role") == "assistant":
                text = memory.get("text", "")
                # Look for flight list pattern
                if "I found" in text and "flights" in text.lower():
                    # Try to extract offer IDs from the flight list
                    offer_ids = re.findall(r'OFFER_[A-Z0-9]+', text, re.IGNORECASE)
                    if offer_ids:
                        # Store the first one as potential default, but we'll look for selection
                        flight_search_results = offer_ids
                        logger.info(f"Payment Agent: Found flight search results with {len(offer_ids)} offers")
        
        # Look for offer_id in memory context (previous assistant messages)
        logger.info(f"Payment Agent: Searching {len(memory_context)} memory messages for offer_id")
        for idx, memory in enumerate(reversed(memory_context)):  # Check most recent first
            if memory.get("role") == "assistant":
                text = memory.get("text", "")
                logger.info(f"Payment Agent: Checking assistant message #{idx}: {text[:150]}...")
                # Look for "Offer ID: OFFER_XXXXX" pattern (more flexible)
                offer_match = re.search(r'Offer\s+ID\s*:\s*([A-Z0-9_]+)', text, re.IGNORECASE)
                if offer_match:
                    offer_id = offer_match.group(1)
                    logger.info(f"Payment Agent: Found offer_id in memory (Offer ID pattern): {offer_id}")
                    break
                # Also check for "selected flight" or "I've selected" messages
                if "selected flight" in text.lower() or "i've selected" in text.lower() or "i selected" in text.lower():
                    offer_match = re.search(r'OFFER_[A-Z0-9]+', text, re.IGNORECASE)
                    if offer_match:
                        offer_id = offer_match.group(0)
                        logger.info(f"Payment Agent: Found offer_id in selection message: {offer_id}")
                        break
                # Also check for any OFFER_ pattern in assistant messages (last resort)
                if not offer_id:
                    offer_match = re.search(r'OFFER_[A-Z0-9]+', text, re.IGNORECASE)
                    if offer_match:
                        offer_id = offer_match.group(0)
                        logger.info(f"Payment Agent: Found offer_id in assistant message (any pattern): {offer_id}")
                        break
        
        if not offer_id:
            logger.warning("Payment Agent: Could not find offer_id in any memory messages")
        
        # If still no offer_id, check if user mentioned a number in their message
        if not offer_id and flight_search_results:
            num_match = re.search(r'\b([1-5])\b', user_message)
            if num_match:
                flight_num = int(num_match.group(1))
                if 1 <= flight_num <= len(flight_search_results):
                    offer_id = flight_search_results[flight_num - 1]
                    logger.info(f"Payment Agent: User selected flight #{flight_num}, offer_id: {offer_id}")
        
        # If found, retrieve the offer
        if offer_id:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{BACKEND_URL}/api/flight/offer/{offer_id}",
                        timeout=10.0,
                    )
                    if response.status_code == 200:
                        selected_offer = response.json()
                        logger.info(f"Payment Agent: Retrieved offer from API: {selected_offer.get('offer_id')}")
                    else:
                        logger.warning(f"Payment Agent: Could not retrieve offer {offer_id}: {response.status_code}")
            except Exception as e:
                logger.error(f"Payment Agent: Error retrieving offer: {str(e)}")
    
    if not selected_offer:
        state["response"] = "No offer selected. Please select a flight first. You can select by number (1-5) or provide the offer ID."
        return state
    
    # If booking fields are empty, try to extract from memory context and current message
    if not all(k in booking_fields for k in ["full_name", "email", "phone"]):
        logger.info("Payment Agent: Missing booking fields, searching memory context and current message...")
        
        # First, check the current user message for field: value format
        current_message = state.get("user_message", "")
        if current_message:
            # Extract from current message (handles "full_name:", "phone:", etc., including spaces before colon)
            if not booking_fields.get("full_name"):
                # Handle "full_name:", "full name:", "name:", "full_name :" formats
                name_match = re.search(r'(?:full[_\s]*name|name)\s*:\s*([^,\n]+)', current_message, re.IGNORECASE)
                if name_match:
                    booking_fields["full_name"] = name_match.group(1).strip()
                    logger.info(f"Payment Agent: Extracted full_name from current message: {booking_fields['full_name']}")
            
            if not booking_fields.get("email"):
                email_match = re.search(r'email\s*:\s*([^\s,\n]+@[^\s,\n]+)', current_message, re.IGNORECASE)
                if email_match:
                    booking_fields["email"] = email_match.group(1).strip()
                    logger.info(f"Payment Agent: Extracted email from current message: {booking_fields['email']}")
                elif "@" in current_message:
                    email_match = re.search(r'([^\s,\n]+@[^\s,\n]+)', current_message)
                    if email_match:
                        booking_fields["email"] = email_match.group(1).strip()
                        logger.info(f"Payment Agent: Extracted email from current message: {booking_fields['email']}")
            
            if not booking_fields.get("phone"):
                phone_match = re.search(r'phone\s*:\s*([\d\s\-\(\)]+)', current_message, re.IGNORECASE)
                if phone_match:
                    phone = re.sub(r'\D', '', phone_match.group(1))
                    if len(phone) >= 10:
                        booking_fields["phone"] = phone
                        logger.info(f"Payment Agent: Extracted phone from current message: {booking_fields['phone']}")
                # Also try to find standalone phone number
                elif re.search(r'\d{10,15}', current_message):
                    phone_match = re.search(r'(\d{10,15})', current_message)
                    if phone_match:
                        booking_fields["phone"] = phone_match.group(1)
                        logger.info(f"Payment Agent: Extracted phone from current message: {booking_fields['phone']}")
        
        # Look for passenger details in memory (check most recent first)
        for memory in reversed(memory_context):
            text = memory.get("text", "")
            role = memory.get("role", "")
            
            # Check assistant messages for "Perfect! I have all the details" format
            if role == "assistant":
                # Look for the confirmation message with all details
                if "Perfect! I have all the details" in text or ("Name:" in text and "Email:" in text and "Phone:" in text):
                    # Extract details using regex
                    if not booking_fields.get("full_name"):
                        name_match = re.search(r'Name:\s*([^\n,]+)', text, re.IGNORECASE)
                        if name_match:
                            booking_fields["full_name"] = name_match.group(1).strip()
                            logger.info(f"Payment Agent: Found full_name in assistant memory: {booking_fields['full_name']}")
                    
                    if not booking_fields.get("email"):
                        email_match = re.search(r'Email:\s*([^\n,]+)', text, re.IGNORECASE)
                        if email_match:
                            booking_fields["email"] = email_match.group(1).strip()
                            logger.info(f"Payment Agent: Found email in assistant memory: {booking_fields['email']}")
                    
                    if not booking_fields.get("phone"):
                        phone_match = re.search(r'Phone:\s*([^\n,]+)', text, re.IGNORECASE)
                        if phone_match:
                            booking_fields["phone"] = re.sub(r'\D', '', phone_match.group(1))
                            logger.info(f"Payment Agent: Found phone in assistant memory: {booking_fields['phone']}")
            
            # Check user messages for raw input like "PUTTA SIDDHARDHA 003siddhu@gmail.com 7569221375"
            if role == "user":
                # Try to parse space-separated format: "Name email phone"
                if not all(k in booking_fields for k in ["full_name", "email", "phone"]):
                    parts = text.split()
                    if len(parts) >= 3:
                        # Try to identify email (contains @) and phone (digits)
                        email_part = None
                        phone_part = None
                        name_parts = []
                        
                        for part in parts:
                            if "@" in part:
                                email_part = part
                            elif re.match(r'^\d+$', re.sub(r'\D', '', part)) and len(re.sub(r'\D', '', part)) >= 10:
                                phone_part = re.sub(r'\D', '', part)
                            else:
                                name_parts.append(part)
                        
                        if not booking_fields.get("full_name") and name_parts:
                            booking_fields["full_name"] = " ".join(name_parts)
                            logger.info(f"Payment Agent: Extracted full_name from user memory: {booking_fields['full_name']}")
                        
                        if not booking_fields.get("email") and email_part:
                            booking_fields["email"] = email_part
                            logger.info(f"Payment Agent: Extracted email from user memory: {booking_fields['email']}")
                        
                        if not booking_fields.get("phone") and phone_part:
                            booking_fields["phone"] = phone_part
                            logger.info(f"Payment Agent: Extracted phone from user memory: {booking_fields['phone']}")
                
                # Also try "field: value" format (including "full_name :" with space)
                if not booking_fields.get("full_name"):
                    name_match = re.search(r'(?:full[_\s]*name|name)\s*:\s*([^,\n]+)', text, re.IGNORECASE)
                    if name_match:
                        booking_fields["full_name"] = name_match.group(1).strip()
                        logger.info(f"Payment Agent: Extracted full_name from user memory (field:value): {booking_fields['full_name']}")
                
                if not booking_fields.get("email"):
                    email_match = re.search(r'email\s*:\s*([^\s,\n]+@[^\s,\n]+)', text, re.IGNORECASE)
                    if email_match:
                        booking_fields["email"] = email_match.group(1).strip()
                        logger.info(f"Payment Agent: Extracted email from user memory (field:value): {booking_fields['email']}")
                    elif "@" in text:
                        email_match = re.search(r'([^\s,\n]+@[^\s,\n]+)', text)
                        if email_match:
                            booking_fields["email"] = email_match.group(1).strip()
                            logger.info(f"Payment Agent: Extracted email from user memory: {booking_fields['email']}")
                
                if not booking_fields.get("phone"):
                    phone_match = re.search(r'phone\s*:\s*([\d\s\-\(\)]+)', text, re.IGNORECASE)
                    if phone_match:
                        phone = re.sub(r'\D', '', phone_match.group(1))
                        if len(phone) >= 10:
                            booking_fields["phone"] = phone
                            logger.info(f"Payment Agent: Extracted phone from user memory (field:value): {booking_fields['phone']}")
        
        # Also check slots from current message
        slots = state.get("slots", {})
        if slots.get("full_name") and not booking_fields.get("full_name"):
            booking_fields["full_name"] = slots["full_name"]
            logger.info(f"Payment Agent: Found full_name in slots: {booking_fields['full_name']}")
        if slots.get("email") and not booking_fields.get("email"):
            booking_fields["email"] = slots["email"]
            logger.info(f"Payment Agent: Found email in slots: {booking_fields['email']}")
        if slots.get("phone") and not booking_fields.get("phone"):
            booking_fields["phone"] = slots["phone"]
            logger.info(f"Payment Agent: Found phone in slots: {booking_fields['phone']}")
        
        logger.info(f"Payment Agent: Final booking fields after extraction: {booking_fields}")
    
    # Update state with booking fields
    state["booking_fields"] = booking_fields
    
    if not all(k in booking_fields for k in ["full_name", "email", "phone"]):
        missing = [k for k in ["full_name", "email", "phone"] if k not in booking_fields or not booking_fields[k]]
        state["response"] = f"Missing passenger details: {', '.join(missing)}. Please provide these details."
        return state
    
    try:
        logger.info(f"Payment Agent: Creating booking for offer {selected_offer.get('offer_id')} with passenger {booking_fields.get('full_name')}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/booking/simulate_confirm",
                json={
                    "offer_id": selected_offer["offer_id"],
                    "user_email": user_email,
                    "passengers": [{
                        "full_name": booking_fields["full_name"],
                        "email": booking_fields["email"],
                        "phone": booking_fields["phone"],
                    }],
                },
                timeout=10.0,
            )
            
            logger.info(f"Payment Agent: Booking API response status: {response.status_code}")
            
            if response.status_code == 200:
                booking_data = response.json()
                state["booking_id"] = booking_data["booking_id"]
                state["payment_confirmed"] = True
                state["response"] = f"✅ Booking confirmed!\n\nBooking ID: {booking_data['booking_id']}\nFlight: {selected_offer['airline']} {selected_offer['flight_no']}\nTotal: ₹{booking_data['total_amount']:.2f}\nStatus: {booking_data['status']}\n\nThank you for booking with us!"
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                    logger.error(f"Payment Agent: Booking failed - {error_detail}")
                except:
                    pass
                state["response"] = f"Booking failed. {error_detail if error_detail else 'Please try again.'}"
    
    except Exception as e:
        logger.error(f"Payment Agent: Exception during booking: {str(e)}", exc_info=True)
        state["response"] = f"Payment processing failed: {str(e)}"
    
    return state

