"""
Intent Classification Agent
Classifies user intent using strict JSON format
"""
import os
import json
from typing import Dict, Any
import logging
import google.generativeai as genai
from .base import AgentState

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Use gemini-2.5-flash (latest model)
model = genai.GenerativeModel("gemini-2.5-flash")

logger = logging.getLogger(__name__)


async def intent_agent(state: AgentState) -> AgentState:
    """Classify user intent using strict JSON format"""
    user_message = state["user_message"]
    user_email = state["user_email"]
    memory_context = state.get("memory_context", [])
    existing_slots = state.get("slots", {})
    
    # Build context from recent messages
    context_messages = []
    for memory in memory_context[-3:]:  # Last 3 messages for context
        context_messages.append(f"{memory.get('role', 'user').upper()}: {memory.get('text', '')}")
    context = "\n".join(context_messages) if context_messages else "No previous conversation."
    
    # Build existing slots info
    existing_slots_info = ""
    if existing_slots:
        existing_slots_info = f"\n\nIMPORTANT: The following slots have already been collected from previous messages:\n{json.dumps(existing_slots, indent=2)}\n\nYou should preserve these existing slots and only add new information from the current message. Do NOT set existing slots to null unless the user explicitly changes them."
    
    prompt = f"""You are an intent classification agent for an airline booking system.

Classify the user's intent from their message. Return ONLY valid JSON, no other text.

Possible intents:
- "flight_search": User wants to search for flights
- "offer_selection": User wants to select a specific flight offer
- "slot_filling": User is providing booking details
- "payment": User wants to proceed with payment
- "booking_inquiry": User wants to check past bookings, booking history, previous bookings, my bookings, show my bookings, list my bookings, view bookings
- "general": General conversation or questions

IMPORTANT (be concise):
- Convert cities to airport codes (e.g., "Hyderabad"->"HYD", "Mumbai"->"BOM", "Delhi"->"DEL", "Bangalore"->"BLR", "Chennai"->"MAA", "Kolkata"->"CCU", "Vizag"->"VTZ", "Visakhapatnam"->"VTZ", "New York"->"JFK", "London"->"LHR", "Dubai"->"DXB", "Singapore"->"SIN")
- Convert dates to YYYY-MM-DD ("today"/"tomorrow" -> actual dates)
- Extract passenger details: "name: X" or "email: X" or "phone: X" or comma-separated format
- PRESERVE existing slots: If slots already exist from previous messages, keep them unless the user explicitly provides new values

Previous conversation context:
{context}
{existing_slots_info}

Return JSON in this exact format:
{{
    "intent": "intent_name",
    "slots": {{
        "origin": "airport_code or null",
        "destination": "airport_code or null",
        "departure_date": "YYYY-MM-DD or null",
        "adults": number or null,
        "offer_id": "offer_id or null",
        "full_name": "name or null",
        "email": "email or null",
        "phone": "phone or null"
    }},
    "confidence": 0.0-1.0
}}

User message: {user_message}
User email: {user_email}

Return ONLY the JSON:"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        logger.info(f"Intent Agent: Raw response from Gemini: {response_text[:200]}...")
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        logger.info(f"Intent Agent: Extracted JSON: {response_text}")
        intent_data = json.loads(response_text)
        
        state["intent"] = intent_data
        # Merge new slots with existing slots (preserve existing slots, only update with new non-null values)
        new_slots = intent_data.get("slots", {})
        for key, value in new_slots.items():
            # Only update if the new value is not null/None, or if the slot doesn't exist yet
            if value and value != "null" and value is not None:
                state["slots"][key] = value
            elif key not in state["slots"]:
                # If slot doesn't exist and new value is null, set it to None
                state["slots"][key] = None
        
        logger.info(f"Intent Agent: Classified as '{intent_data.get('intent')}' with slots: {intent_data.get('slots')}")
        logger.info(f"Intent Agent: Final merged slots: {state.get('slots', {})}")
        
    except Exception as e:
        logger.error(f"Intent Agent: Error classifying intent: {str(e)}", exc_info=True)
        # Fallback to general intent
        state["intent"] = {"intent": "general", "slots": {}, "confidence": 0.5}
        logger.warning("Intent Agent: Falling back to 'general' intent")
    
    return state

