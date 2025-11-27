"""
Router Agent
Routes to appropriate agent based on intent
"""
import logging
from .base import AgentState
from .flight_search_agent import flight_search_agent
from .offer_selection_agent import offer_selection_agent
from .slot_filling_agent import slot_filling_agent
from .payment_agent import payment_agent
from .booking_confirmation_agent import booking_confirmation_agent
from .fallback_agent import fallback_agent

logger = logging.getLogger(__name__)


async def router_agent(state: AgentState) -> AgentState:
    """Route to appropriate agent based on intent"""
    intent_data = state.get("intent", {})
    intent = intent_data.get("intent", "general")
    
    logger.info(f"Router: Intent = '{intent}', Routing to appropriate agent...")
    
    # Determine next agent
    if intent == "flight_search":
        logger.info("Router: Calling flight_search_agent")
        return await flight_search_agent(state)
    elif intent == "offer_selection":
        logger.info("Router: Calling offer_selection_agent")
        return await offer_selection_agent(state)
    elif intent == "slot_filling":
        logger.info("Router: Calling slot_filling_agent")
        return await slot_filling_agent(state)
    elif intent == "payment":
        logger.info("Router: Calling payment_agent")
        return await payment_agent(state)
    elif intent == "booking_inquiry":
        logger.info("Router: Calling booking_confirmation_agent")
        return await booking_confirmation_agent(state)
    else:
        logger.info(f"Router: Intent '{intent}' not recognized, calling fallback_agent")
        return await fallback_agent(state)

