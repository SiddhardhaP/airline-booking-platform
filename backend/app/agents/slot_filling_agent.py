"""
Slot Filling Agent
Collects booking details via slot filling using LLM
Returns strict JSON: {done, booking_fields, missing}
"""
import os
import json
import re
import logging
import httpx
from typing import Dict, Any
from .base import AgentState

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


async def slot_filling_agent(state: AgentState) -> AgentState:
    """Collect booking details via slot filling using LLM"""
    slots = state["slots"]
    booking_fields = state.get("booking_fields", {})
    user_message = state["user_message"]
    memory_context = state.get("memory_context", [])
    selected_offer = state.get("selected_offer")
    
    # Extract fields from slots first
    if slots.get("full_name"):
        booking_fields["full_name"] = slots["full_name"]
    if slots.get("email"):
        booking_fields["email"] = slots["email"]
    if slots.get("phone"):
        booking_fields["phone"] = slots["phone"]
    
    # Try regex extraction first (faster than LLM)
    # Only use LLM if regex fails or fields are complex
    simple_extraction = False
    if user_message:
        # Quick regex check for simple formats
        if re.search(r'(?:full[_\s]*name|name)\s*:\s*', user_message, re.IGNORECASE) or \
           re.search(r'email\s*:\s*', user_message, re.IGNORECASE) or \
           re.search(r'phone\s*:\s*', user_message, re.IGNORECASE) or \
           ("," in user_message and "@" in user_message):
            # Simple format detected, try regex first
            simple_extraction = True
    
    # Build context for LLM (reduced from 10 to 5 for faster processing)
    context_messages = []
    for memory in memory_context[-5:]:  # Reduced from 10 to 5 messages
        context_messages.append(f"{memory.get('role', 'user').upper()}: {memory.get('text', '')}")
    
    context = "\n".join(context_messages) if context_messages else "No previous conversation."
    
    # Current booking fields status
    current_fields = json.dumps(booking_fields, indent=2)
    
    # Prompt for LLM to extract fields and return strict JSON
    prompt = f"""You are a slot-filling agent for an airline booking system. Extract booking details from the user's message.

Current booking fields collected so far:
{current_fields}

Previous conversation context:
{context}

User's current message: "{user_message}"

Extract the following fields from the user's message:
- full_name: Passenger's full name
- email: Email address
- phone: Phone number (digits only, 10+ digits)

You MUST return ONLY a valid JSON object in this exact format (no markdown, no code blocks, no explanations):
{{
    "done": true/false,
    "booking_fields": {{
        "full_name": "extracted name or null",
        "email": "extracted email or null",
        "phone": "extracted phone or null"
    }},
    "missing": ["list", "of", "missing", "fields"]
}}

Rules:
1. "done" is true ONLY if all three fields (full_name, email, phone) are present and non-null
2. Merge new fields with existing booking_fields (don't overwrite existing fields unless user provides new values)
3. "booking_fields" should contain ALL fields (existing + newly extracted)
4. "missing" should list only the fields that are still missing after extraction
5. Extract from current message, previous context, or both
6. Handle formats like: "Name, email, phone", "full_name: X", "phone: Y", etc.
7. Phone numbers: extract digits only, must be 10+ digits
8. Return ONLY the JSON, nothing else"""

    # If simple extraction possible, try regex first
    if simple_extraction:
        logger.info("Slot Filling Agent: Trying fast regex extraction first")
        regex_result = await _fallback_extraction(state, booking_fields.copy())
        # Check if regex got all fields
        if all(k in regex_result["booking_fields"] and regex_result["booking_fields"][k] 
               for k in ["full_name", "email", "phone"]):
            logger.info("Slot Filling Agent: Regex extraction successful, skipping LLM call")
            return regex_result
    
    try:
        # Call Gemini API with reduced timeout
        async with httpx.AsyncClient(timeout=15.0) as client:  # Reduced from 30.0 to 15.0
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "responseMimeType": "application/json",
                        "maxOutputTokens": 200,  # Limit response size for faster generation
                    }
                },
                timeout=15.0,  # Reduced from 30.0 to 15.0
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                # Fallback to regex extraction
                return await _fallback_extraction(state, booking_fields)
            
            data = response.json()
            # Reduced logging for performance (only log on error)
            
            # Extract JSON from response
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts and "text" in parts[0]:
                    response_text = parts[0]["text"].strip()
                    
                    # Remove markdown code blocks if present
                    response_text = re.sub(r'```json\s*', '', response_text)
                    response_text = re.sub(r'```\s*', '', response_text)
                    response_text = response_text.strip()
                    
                    # Reduced logging for performance
                    # logger.info(f"Slot Filling Agent: Extracted JSON text: {response_text}")
                    
                    # Parse JSON
                    try:
                        result = json.loads(response_text)
                        # Reduced logging for performance
                        # logger.info(f"Slot Filling Agent: Parsed JSON: {json.dumps(result, indent=2)}")
                        
                        # Validate structure
                        if not isinstance(result, dict):
                            raise ValueError("Result is not a dictionary")
                        
                        # Merge booking_fields
                        extracted_fields = result.get("booking_fields", {})
                        for key in ["full_name", "email", "phone"]:
                            if extracted_fields.get(key) and extracted_fields[key] not in [None, "null", ""]:
                                booking_fields[key] = extracted_fields[key]
                        
                        # Clean phone number (digits only)
                        if booking_fields.get("phone"):
                            booking_fields["phone"] = re.sub(r'\D', '', str(booking_fields["phone"]))
                        
                        # Update state with merged booking_fields immediately
                        state["booking_fields"] = booking_fields
                        logger.info(f"Slot Filling Agent: Merged booking_fields into state: {booking_fields}")
                        
                        # Determine done and missing
                        required = ["full_name", "email", "phone"]
                        missing = [field for field in required if field not in booking_fields or not booking_fields[field]]
                        done = len(missing) == 0
                        
                        # If done==true and selected_offer exists, create booking
                        if done and selected_offer:
                            logger.info(f"Slot Filling Agent: All fields collected (done=true), creating booking...")
                            booking_result = await _create_booking(state, booking_fields, selected_offer)
                            if booking_result and booking_result.get("booking_id"):
                                booking_id = booking_result["booking_id"]
                                total_amount = booking_result.get("total_amount", selected_offer.get("price", 0))
                                state["booking_id"] = booking_id
                                state["payment_confirmed"] = True
                                state["response"] = f"✅ Booking confirmed!\n\nBooking ID: {booking_id}\nFlight: {selected_offer.get('airline', '')} {selected_offer.get('flight_no', '')}\nTotal: ₹{total_amount:.2f}\nPassenger: {booking_fields['full_name']}\nEmail: {booking_fields['email']}\nPhone: {booking_fields['phone']}\n\nThank you for booking with us!"
                                return state
                        
                        # Generate response
                        if done:
                            state["response"] = f"Perfect! I have all the details:\n- Name: {booking_fields['full_name']}\n- Email: {booking_fields['email']}\n- Phone: {booking_fields['phone']}\n\nTo confirm payment, please reply 'proceed'."
                        else:
                            missing_text = ", ".join(missing)
                            state["response"] = f"I still need: {missing_text}. Please provide these details."
                        
                        return state
                    except json.JSONDecodeError as e:
                        logger.error(f"Slot Filling Agent: JSON decode error: {str(e)}")
                        logger.error(f"Slot Filling Agent: Response text: {response_text}")
                        return await _fallback_extraction(state, booking_fields)
                else:
                    logger.error("Slot Filling Agent: No text in Gemini response")
                    return await _fallback_extraction(state, booking_fields)
            else:
                logger.error("Slot Filling Agent: No candidates in Gemini response")
                return await _fallback_extraction(state, booking_fields)
                
    except Exception as e:
        logger.error(f"Slot Filling Agent: Exception calling Gemini: {str(e)}", exc_info=True)
        return await _fallback_extraction(state, booking_fields)


async def _fallback_extraction(state: AgentState, booking_fields: Dict[str, Any]) -> AgentState:
    """Fallback to regex extraction if LLM fails"""
    logger.info("Slot Filling Agent: Using fallback regex extraction")
    user_message = state["user_message"]
    
    # Simple regex extraction
    if not booking_fields.get("full_name"):
        name_match = re.search(r'(?:full[_\s]*name|name)\s*:\s*([^,\n]+)', user_message, re.IGNORECASE)
        if name_match:
            booking_fields["full_name"] = name_match.group(1).strip()
    
    if not booking_fields.get("email"):
        email_match = re.search(r'email\s*:\s*([^\s,\n]+@[^\s,\n]+)', user_message, re.IGNORECASE)
        if email_match:
            booking_fields["email"] = email_match.group(1).strip()
        elif "@" in user_message:
            email_match = re.search(r'([^\s,\n]+@[^\s,\n]+)', user_message)
            if email_match:
                booking_fields["email"] = email_match.group(1).strip()
    
    if not booking_fields.get("phone"):
        phone_match = re.search(r'phone\s*:\s*([\d\s\-\(\)]+)', user_message, re.IGNORECASE)
        if phone_match:
            phone = re.sub(r'\D', '', phone_match.group(1))
            if len(phone) >= 10:
                booking_fields["phone"] = phone
    
    # Update state
    state["booking_fields"] = booking_fields
    
    # Check what's missing
    required = ["full_name", "email", "phone"]
    missing = [field for field in required if field not in booking_fields or not booking_fields[field]]
    
    if missing:
        missing_text = ", ".join(missing)
        state["response"] = f"I still need: {missing_text}. Please provide these details."
    else:
        state["response"] = f"Perfect! I have all the details:\n- Name: {booking_fields['full_name']}\n- Email: {booking_fields['email']}\n- Phone: {booking_fields['phone']}\n\nTo confirm payment, please reply 'proceed'."
    
    return state


async def _create_booking(state: AgentState, booking_fields: Dict[str, Any], selected_offer: Dict[str, Any]) -> Dict[str, Any]:
    """Create booking in database"""
    user_email = state["user_email"]
    offer_id = selected_offer.get("offer_id")
    
    if not offer_id:
        logger.error("Slot Filling Agent: Cannot create booking, no offer_id")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/booking/simulate_confirm",
                json={
                    "offer_id": offer_id,
                    "user_email": user_email,
                    "passengers": [{
                        "full_name": booking_fields["full_name"],
                        "email": booking_fields["email"],
                        "phone": booking_fields["phone"],
                    }],
                },
                timeout=10.0,
            )
            
            if response.status_code == 200:
                booking_data = response.json()
                logger.info(f"Slot Filling Agent: Booking created successfully: {booking_data['booking_id']}")
                return booking_data  # Return full booking data
            else:
                logger.error(f"Slot Filling Agent: Booking creation failed: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"Slot Filling Agent: Exception creating booking: {str(e)}", exc_info=True)
        return None
