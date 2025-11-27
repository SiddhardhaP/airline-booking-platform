"""
Conversation Memory Model with pgvector
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from app.db import Base


class ConvoMemory(Base):
    __tablename__ = "convo_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_email = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # user or assistant
    text = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Adjust dimension based on embedding model
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

