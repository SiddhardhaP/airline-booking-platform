"""
Memory-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MemorySave(BaseModel):
    user_email: str
    role: str  # user or assistant
    text: str
    embedding: Optional[List[float]] = None  # Will be generated if not provided


class MemoryRetrieve(BaseModel):
    user_email: str
    query: str
    limit: int = 5


class MemoryItem(BaseModel):
    id: str
    user_email: str
    role: str
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MemoryRetrieveResponse(BaseModel):
    memories: List[MemoryItem]
    count: int

