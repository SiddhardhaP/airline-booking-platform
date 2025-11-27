"""
Memory router for conversation embeddings
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db
from app.schemas.memory import MemorySave, MemoryRetrieve, MemoryRetrieveResponse, MemoryItem
from app.models.convo_memory import ConvoMemory
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory", tags=["memory"])
embedding_service = EmbeddingService()


@router.post("/save")
async def save_memory(
    memory: MemorySave,
    db: Session = Depends(get_db),
):
    """
    Save conversation memory with embedding
    """
    # Generate embedding if not provided
    embedding = memory.embedding
    if not embedding:
        embedding = await embedding_service.generate_embedding(memory.text)
    
    # Create memory record
    convo_memory = ConvoMemory(
        user_email=memory.user_email,
        role=memory.role,
        text=memory.text,
        embedding=embedding,
    )
    
    db.add(convo_memory)
    db.commit()
    db.refresh(convo_memory)
    
    return {"id": str(convo_memory.id), "status": "saved"}


@router.post("/retrieve", response_model=MemoryRetrieveResponse)
async def retrieve_memory(
    request: MemoryRetrieve,
    db: Session = Depends(get_db),
):
    """
    Retrieve relevant conversation memories using vector similarity
    Falls back to simple text search if embedding generation fails
    """
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.generate_embedding(request.query)
        
        # Check if we got a valid embedding (not all zeros)
        if all(x == 0.0 for x in query_embedding):
            # Fallback to simple text search if embedding failed
            logger.warning("Embedding generation failed, falling back to text search")
            query = text("""
                SELECT id, user_email, role, text, created_at, 0.5 as similarity
                FROM convo_memory
                WHERE user_email = :user_email
                    AND (text ILIKE :search_pattern OR text ILIKE :search_pattern2)
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            search_pattern = f"%{request.query}%"
            results = db.execute(
                query,
                {
                    "user_email": request.user_email,
                    "search_pattern": search_pattern,
                    "search_pattern2": f"%{request.query[:20]}%",  # Partial match
                    "limit": request.limit,
                }
            ).fetchall()
        else:
            # Vector similarity search using pgvector
            # Format embedding as PostgreSQL array string
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            query = text("""
                SELECT id, user_email, role, text, created_at,
                       1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM convo_memory
                WHERE user_email = :user_email
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)
            
            results = db.execute(
                query,
                {
                    "user_email": request.user_email,
                    "query_embedding": embedding_str,
                    "limit": request.limit,
                }
            ).fetchall()
        
        # Process results
        memories = []
        for row in results:
            memories.append(
                MemoryItem(
                    id=str(row[0]),
                    user_email=row[1],
                    role=row[2],
                    text=row[3],
                    created_at=row[4],
                )
            )
        
        return MemoryRetrieveResponse(memories=memories, count=len(memories))
        
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}, falling back to simple text search")
        # Fallback to simple text search on any error
        try:
            memories = (
                db.query(ConvoMemory)
                .filter(ConvoMemory.user_email == request.user_email)
                .order_by(ConvoMemory.created_at.desc())
                .limit(request.limit)
                .all()
            )
            
            return MemoryRetrieveResponse(
                memories=[MemoryItem.model_validate(m) for m in memories],
                count=len(memories),
            )
        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {str(fallback_error)}")
            return {"memories": []}

