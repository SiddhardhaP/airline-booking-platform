"""
Memory Manager Agent
Retrieves relevant conversation memories
"""
import os
import httpx
from typing import List, Dict, Any
from .base import AgentState

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


async def memory_manager_agent(state: AgentState) -> AgentState:
    """Retrieve relevant conversation memories"""
    user_email = state["user_email"]
    user_message = state["user_message"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/memory/retrieve",
                json={
                    "user_email": user_email,
                    "query": user_message,
                    "limit": 10,  # Reduced from 30 for faster retrieval
                },
                timeout=3.0,  # Reduced from 5.0 for faster response
            )
            
            if response.status_code == 200:
                data = response.json()
                state["memory_context"] = [
                    {"role": m["role"], "text": m["text"]}
                    for m in data.get("memories", [])
                ]
    except Exception:
        state["memory_context"] = []
    
    return state

