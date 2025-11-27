"""
Offer Selection Agent
Handles flight offer selection
"""
import os
import httpx
from .base import AgentState

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


async def offer_selection_agent(state: AgentState) -> AgentState:
    """Handle offer selection"""
    slots = state["slots"]
    offer_id = slots.get("offer_id")
    
    if not offer_id and state.get("flight_search_results"):
        # Try to extract offer ID from message
        user_message = state["user_message"].lower()
        for offer in state["flight_search_results"]:
            if offer["offer_id"].lower() in user_message or str(offer["offer_id"]) in user_message:
                offer_id = offer["offer_id"]
                break
        
        # Check if user selected by number
        try:
            num = int(state["user_message"].strip())
            if 1 <= num <= len(state["flight_search_results"]):
                offer_id = state["flight_search_results"][num - 1]["offer_id"]
        except ValueError:
            pass
    
    if not offer_id:
        state["response"] = "Please provide the offer ID or select a flight number from the search results."
        return state
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/flight/offer/{offer_id}",
                timeout=10.0,
            )
            
            if response.status_code == 200:
                offer_data = response.json()
                state["selected_offer"] = offer_data
                # Include offer_id in response so it can be retrieved from memory later
                state["response"] = f"Great! I've selected flight {offer_data['airline']} {offer_data['flight_no']} for ₹{offer_data['price']:.2f}.\n\nOffer ID: {offer_data['offer_id']}\n\nNow I need some passenger details:\n- Full name\n- Email\n- Phone number\n\nPlease provide these details."
            else:
                state["response"] = "Offer not found. Please select a valid offer."
    
    except Exception as e:
        state["response"] = f"Could not retrieve offer details: {str(e)}"
    
    return state

