"""
LangGraph workflow orchestrator
Main entry point for processing chat messages
"""
import os
import uuid
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from dotenv import load_dotenv
import sys
import logging
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend"))

from app.agents import (
    AgentState,
    intent_agent,
    memory_manager_agent,
    router_agent,
)

load_dotenv()

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Setup logging
logger = logging.getLogger(__name__)


def restore_booking_fields_from_memory(memory_context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Restore booking_fields from memory context.
    Looks for "Perfect! I have all the details" message or extracts from user messages.
    """
    booking_fields = {}
    
    # Check most recent messages first
    for memory in reversed(memory_context):
        text = memory.get("text", "")
        role = memory.get("role", "")
        
        # Check assistant messages for "Perfect! I have all the details" format
        if role == "assistant":
            if "Perfect! I have all the details" in text or ("Name:" in text and "Email:" in text and "Phone:" in text):
                # Extract details using regex
                if not booking_fields.get("full_name"):
                    name_match = re.search(r'Name:\s*([^\n,]+)', text, re.IGNORECASE)
                    if name_match:
                        booking_fields["full_name"] = name_match.group(1).strip()
                
                if not booking_fields.get("email"):
                    email_match = re.search(r'Email:\s*([^\n,]+)', text, re.IGNORECASE)
                    if email_match:
                        booking_fields["email"] = email_match.group(1).strip()
                
                if not booking_fields.get("phone"):
                    phone_match = re.search(r'Phone:\s*([^\n,]+)', text, re.IGNORECASE)
                    if phone_match:
                        booking_fields["phone"] = re.sub(r'\D', '', phone_match.group(1))
        
        # Check user messages for field: value format or raw input
        if role == "user":
            # Try "field: value" format (including "full_name :" with space before colon)
            if not booking_fields.get("full_name"):
                name_match = re.search(r'(?:full[_\s]*name|name)\s*:\s*([^,\n]+)', text, re.IGNORECASE)
                if name_match:
                    booking_fields["full_name"] = name_match.group(1).strip()
            
            if not booking_fields.get("email"):
                email_match = re.search(r'email\s*:\s*([^\s,\n]+@[^\s,\n]+)', text, re.IGNORECASE)
                if email_match:
                    booking_fields["email"] = email_match.group(1).strip()
                elif "@" in text:
                    email_match = re.search(r'([^\s,\n]+@[^\s,\n]+)', text)
                    if email_match:
                        booking_fields["email"] = email_match.group(1).strip()
            
            if not booking_fields.get("phone"):
                phone_match = re.search(r'phone\s*:\s*([\d\s\-\(\)]+)', text, re.IGNORECASE)
                if phone_match:
                    phone = re.sub(r'\D', '', phone_match.group(1))
                    if len(phone) >= 10:
                        booking_fields["phone"] = phone
                # Also try standalone phone number
                elif re.search(r'\d{10,15}', text):
                    phone_match = re.search(r'(\d{10,15})', text)
                    if phone_match:
                        booking_fields["phone"] = phone_match.group(1)
            
            # Try space-separated format: "Name email phone"
            if not all(k in booking_fields for k in ["full_name", "email", "phone"]):
                parts = text.split()
                if len(parts) >= 3:
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
                    if not booking_fields.get("email") and email_part:
                        booking_fields["email"] = email_part
                    if not booking_fields.get("phone") and phone_part:
                        booking_fields["phone"] = phone_part
    
    if booking_fields:
        logger.info(f"Restored booking_fields from memory: {booking_fields}")
    
    return booking_fields


def restore_selected_offer_from_memory(memory_context: List[Dict[str, Any]]) -> Optional[str]:
    """
    Restore selected_offer_id from memory context.
    Looks for "Offer ID: OFFER_XXXXX" or "selected flight" messages.
    """
    # Check most recent messages first
    for memory in reversed(memory_context):
        if memory.get("role") == "assistant":
            text = memory.get("text", "")
            # Look for "Offer ID: OFFER_XXXXX" pattern
            offer_match = re.search(r'Offer\s+ID\s*:\s*([A-Z0-9_]+)', text, re.IGNORECASE)
            if offer_match:
                offer_id = offer_match.group(1)
                logger.info(f"Restored offer_id from memory: {offer_id}")
                return offer_id
            # Also check for "selected flight" messages
            if "selected flight" in text.lower() or "i've selected" in text.lower():
                offer_match = re.search(r'OFFER_[A-Z0-9]+', text, re.IGNORECASE)
                if offer_match:
                    offer_id = offer_match.group(0)
                    logger.info(f"Restored offer_id from selection message: {offer_id}")
                    return offer_id
    
    return None


def restore_slots_from_memory(memory_context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Restore flight search slots (origin, destination, departure_date, adults) from memory context.
    Looks for previously mentioned origin, destination, and dates in the conversation.
    """
    slots = {}
    
    # First, check assistant responses for "I understood" patterns (most reliable)
    for memory in reversed(memory_context):
        if memory.get("role") == "assistant":
            text = memory.get("text", "")
            # Look for "I understood: Origin: HYD, Destination: VTZ" pattern
            if "I understood" in text:
                origin_match = re.search(r'Origin\s*:\s*([A-Z]{3})', text, re.IGNORECASE)
                if origin_match:
                    slots["origin"] = origin_match.group(1).upper()
                
                dest_match = re.search(r'Destination\s*:\s*([A-Z]{3})', text, re.IGNORECASE)
                if dest_match:
                    slots["destination"] = dest_match.group(1).upper()
                
                date_match = re.search(r'Date\s*:\s*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
                if date_match:
                    slots["departure_date"] = date_match.group(1)
                
                adults_match = re.search(r'Adults?\s*:\s*(\d+)', text, re.IGNORECASE)
                if adults_match:
                    try:
                        slots["adults"] = int(adults_match.group(1))
                    except:
                        pass
    
    # If we found slots from assistant responses, return early (most reliable)
    if slots:
        logger.info(f"Restored slots from assistant 'I understood' messages: {slots}")
        return slots
    
    # Fallback: Check user messages for origin/destination patterns
    city_to_code = {
        "hyderabad": "HYD", "mumbai": "BOM", "delhi": "DEL", "bangalore": "BLR",
        "chennai": "MAA", "kolkata": "CCU", "vizag": "VTZ", "visakhapatnam": "VTZ",
        "pune": "PNQ", "goa": "GOI", "ahmedabad": "AMD", "jaipur": "JAI"
    }
    
    for memory in reversed(memory_context):
        text = memory.get("text", "").lower()
        role = memory.get("role", "")
        
        # Look for origin patterns in user messages
        if not slots.get("origin") and role == "user":
            # Check for airport codes
            origin_match = re.search(r'\b(origin|from)\s*:?\s*([A-Z]{3})\b', text, re.IGNORECASE)
            if origin_match:
                slots["origin"] = origin_match.group(2).upper()
            else:
                # Check for city names
                for city, code in city_to_code.items():
                    if city in text:
                        # Check if it's mentioned as origin (look for "from" or "origin" nearby)
                        words = text.split()
                        city_idx = -1
                        for i, word in enumerate(words):
                            if city in word:
                                city_idx = i
                                break
                        if city_idx >= 0:
                            # Check nearby words for "from" or "origin"
                            start = max(0, city_idx - 3)
                            end = min(len(words), city_idx + 3)
                            nearby = " ".join(words[start:end])
                            if "from" in nearby or "origin" in nearby:
                                slots["origin"] = code
                                break
        
        # Look for destination patterns in user messages
        if not slots.get("destination") and role == "user":
            dest_match = re.search(r'\b(destination|to)\s*:?\s*([A-Z]{3})\b', text, re.IGNORECASE)
            if dest_match:
                slots["destination"] = dest_match.group(2).upper()
            else:
                # Check for city names
                for city, code in city_to_code.items():
                    if city in text:
                        # Check if it's mentioned as destination (look for "to" or "destination" nearby)
                        words = text.split()
                        city_idx = -1
                        for i, word in enumerate(words):
                            if city in word:
                                city_idx = i
                                break
                        if city_idx >= 0:
                            # Check nearby words for "to" or "destination"
                            start = max(0, city_idx - 3)
                            end = min(len(words), city_idx + 3)
                            nearby = " ".join(words[start:end])
                            if "to" in nearby or "destination" in nearby or "vizag" in text:
                                slots["destination"] = code
                                break
        
        # Look for date patterns
        if not slots.get("departure_date"):
            # Check for YYYY-MM-DD format
            date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
            if date_match:
                slots["departure_date"] = date_match.group(1)
        
        # Look for adults count
        if not slots.get("adults"):
            adults_match = re.search(r'\b(adults?|passengers?)\s*:?\s*(\d+)\b', text, re.IGNORECASE)
            if adults_match:
                try:
                    slots["adults"] = int(adults_match.group(2))
                except:
                    pass
    
    logger.info(f"Restored slots from memory: {slots}")
    return slots


async def process_message(
    message: str,
    user_email: str,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for processing chat messages through LangGraph workflow
    
    Workflow:
    1. Retrieve memory context
    2. Classify intent
    3. Route to appropriate agent
    4. Save conversation to memory
    """
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Initialize state
    state: AgentState = {
        "user_message": message,
        "user_email": user_email,
        "conversation_id": conversation_id,
        "intent": None,
        "slots": {},
        "flight_search_results": None,
        "selected_offer": None,
        "booking_fields": {},
        "payment_confirmed": False,
        "booking_id": None,
        "memory_context": [],
        "response": "",
        "metadata": {},
    }
    
    # Execute workflow
    # 1. Retrieve memory
    logger.info(f"Step 1: Retrieving memory for user: {user_email}")
    state = await memory_manager_agent(state)
    
    # Restore state from memory context
    memory_context = state.get("memory_context", [])
    logger.info(f"Memory context retrieved: {len(memory_context)} messages")
    
    # Restore slots from memory BEFORE intent classification
    restored_slots = restore_slots_from_memory(memory_context)
    if restored_slots:
        # Merge restored slots into state (don't overwrite, just add missing ones)
        for key, value in restored_slots.items():
            if value and value != "null":  # Only add non-null values
                state["slots"][key] = value
        logger.info(f"Restored slots from memory: {restored_slots}")
    else:
        logger.info("No slots found in memory context")
    
    # Restore booking_fields
    restored_fields = restore_booking_fields_from_memory(memory_context)
    if restored_fields:
        state["booking_fields"] = restored_fields
        logger.info(f"Restored booking_fields from memory: {restored_fields}")
    else:
        logger.info("No booking_fields found in memory context")
    
    # Restore selected_offer_id (we'll fetch the full offer in the payment agent)
    restored_offer_id = restore_selected_offer_from_memory(memory_context)
    if restored_offer_id:
        # Store the offer_id in metadata so payment agent can use it
        state["metadata"]["restored_offer_id"] = restored_offer_id
        logger.info(f"Restored offer_id from memory: {restored_offer_id}")
    
    # 2. Classify intent
    logger.info(f"Step 2: Classifying intent for message: {message[:50]}...")
    logger.info(f"Slots before intent agent: {state.get('slots', {})}")
    state = await intent_agent(state)
    intent_classified = state.get("intent", {})
    logger.info(f"Intent classified: {intent_classified}")
    logger.info(f"Slots after intent agent: {state.get('slots', {})}")
    
    # 3. Route to appropriate agent
    logger.info(f"Step 3: Routing to agent based on intent: {intent_classified.get('intent', 'unknown')}")
    state = await router_agent(state)
    logger.info(f"Step 4: Agent response generated: {state.get('response', '')[:100]}...")
    
    # 4. Save conversation to memory (non-blocking - fire and forget)
    # Use asyncio.create_task to run in background without blocking response
    async def save_memory_background():
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                # Save both messages in parallel
                await asyncio.gather(
                    client.post(
                        f"{BACKEND_URL}/api/memory/save",
                        json={
                            "user_email": user_email,
                            "role": "user",
                            "text": message,
                        },
                        timeout=2.0,
                    ),
                    client.post(
                        f"{BACKEND_URL}/api/memory/save",
                        json={
                            "user_email": user_email,
                            "role": "assistant",
                            "text": state["response"],
                        },
                        timeout=2.0,
                    ),
                    return_exceptions=True,  # Don't fail if one fails
                )
        except Exception:
            pass  # Memory save is non-critical
    
    # Start background task but don't wait for it
    asyncio.create_task(save_memory_background())
    
    return {
        "response": state["response"],
        "conversation_id": conversation_id,
        "metadata": {
            "intent": state.get("intent"),
            "booking_id": state.get("booking_id"),
        },
    }
