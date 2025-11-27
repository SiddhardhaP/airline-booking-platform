"""
Embedding service for conversation memory
"""
import os
import asyncio
from typing import List
import httpx
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"

    async def generate_embedding(self, text: str, retries: int = 3) -> List[float]:
        """
        Generate embedding for text using Gemini API
        Returns 768-dimensional vector
        Handles timeouts and rate limits with retries
        """
        if not self.api_key:
            # Return zero vector if no API key (for development)
            logger.warning("No GEMINI_API_KEY found, returning zero vector")
            return [0.0] * 768

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:  # Reduced from 15.0 to 8.0
                    response = await client.post(
                        f"{self.base_url}?key={self.api_key}",
                        json={"model": "models/embedding-001", "content": {"parts": [{"text": text[:500]}]}},  # Limit text to 500 chars for faster processing
                        timeout=8.0,  # Reduced from 15.0 to 8.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        return data.get("embedding", {}).get("values", [0.0] * 768)
                    elif response.status_code == 429:
                        # Rate limited - wait and retry
                        wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                        logger.warning(f"Rate limited (429), waiting {wait_time}s before retry {attempt + 1}/{retries}")
                        if attempt < retries - 1:
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.error("Rate limit exceeded after retries, returning zero vector")
                            return [0.0] * 768
                    else:
                        logger.warning(f"Embedding API returned status {response.status_code}, returning zero vector")
                        return [0.0] * 768
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException) as e:
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"Embedding API timeout (attempt {attempt + 1}/{retries}), waiting {wait_time}s: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error("Embedding API timeout after retries, returning zero vector")
                    return [0.0] * 768
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}, returning zero vector")
                return [0.0] * 768
        
        # Fallback to zero vector
        return [0.0] * 768

