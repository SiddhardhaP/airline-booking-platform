"""
Chat router for LangGraph integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
import os
from app.utils.logger import get_logger

# Add langgraph directory to path
langgraph_path = os.path.join(os.path.dirname(__file__), "../../../langgraph")
if langgraph_path not in sys.path:
    sys.path.insert(0, langgraph_path)

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_email: str = Field(..., description="User email address")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuity")


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatMessage):
    """
    Process chat message through LangGraph workflow
    """
    try:
        from graph import process_message
        
        logger.info(f"Processing chat message for user: {request.user_email}")
        
        result = await process_message(
            message=request.message,
            user_email=request.user_email,
            conversation_id=request.conversation_id,
        )
        
        logger.info(f"Chat message processed successfully. Conversation ID: {result.get('conversation_id')}")
        
        return ChatResponse(
            response=result.get("response", ""),
            conversation_id=result.get("conversation_id", ""),
            metadata=result.get("metadata"),
        )
    
    except ImportError as e:
        logger.error(f"Failed to import LangGraph module: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="LangGraph module not found. Please check the installation."
        )
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )

