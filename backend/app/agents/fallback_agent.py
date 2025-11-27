"""
Fallback Agent
Handles general conversation and fallback cases
"""
import os
import google.generativeai as genai
from .base import AgentState

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Use gemini-2.5-flash (latest model)
model = genai.GenerativeModel("gemini-2.5-flash")


async def fallback_agent(state: AgentState) -> AgentState:
    """Handle general conversation and fallback cases"""
    user_message = state["user_message"]
    memory_context = state.get("memory_context", [])
    
    # Build context
    context = ""
    if memory_context:
        context = "Previous conversation:\n" + "\n".join([
            f"{m['role']}: {m['text']}" for m in memory_context[-3:]
        ]) + "\n\n"
    
    prompt = f"""You are a helpful airline customer support assistant. Be friendly, professional, and concise.

IMPORTANT INFORMATION ABOUT OUR SERVICES:
- Food Service Charge: If you select the food service option during booking, an additional charge of ₹200 (200 Indian Rupees) will be added to your total amount per booking. This is a fixed charge regardless of the number of passengers.
- Date of Birth: Date of birth is required for all passengers during booking.
- Currency: All prices are displayed in Indian Rupees (INR).

When users ask about food charges, food service cost, meal charges, or food pricing, you should clearly state: "Food service costs ₹200 (200 Indian Rupees) per booking. This charge will be added to your total amount if you select the food service option during booking."

{context}User: {user_message}

Assistant:"""

    try:
        response = model.generate_content(prompt)
        state["response"] = response.text.strip()
    except Exception:
        state["response"] = "I'm here to help you with flight bookings. You can search for flights, select offers, provide booking details, and complete payments. How can I assist you today?"
    
    return state

