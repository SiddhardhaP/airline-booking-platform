"""
Base types and utilities for agents
"""
from typing import TypedDict, Dict, Any, List, Optional


class AgentState(TypedDict):
    """State shared across all agents"""
    user_message: str
    user_email: str
    conversation_id: str
    intent: Optional[Dict[str, Any]]
    slots: Dict[str, Any]
    flight_search_results: Optional[List[Dict[str, Any]]]
    selected_offer: Optional[Dict[str, Any]]
    booking_fields: Dict[str, Any]
    payment_confirmed: bool
    booking_id: Optional[str]
    memory_context: List[Dict[str, Any]]
    response: str
    metadata: Dict[str, Any]

