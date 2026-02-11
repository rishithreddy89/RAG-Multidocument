"""
Embedding Generator
Uses sentence-transformers to generate embeddings
Model is loaded once at startup for performance
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

# Global model instance (loaded once)
_embedding_model = None
MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model() -> SentenceTransformer:
    """
    Get or initialize the embedding model (singleton pattern).
    
    Returns:
        SentenceTransformer model instance
    """
    global _embedding_model
    
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        _embedding_model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded successfully")
    
    return _embedding_model


def embed_text(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector as list of floats
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch processing).
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings.tolist()


def get_embedding_dimension() -> int:
    """
    Get the dimension of embeddings from the model.
    
    Returns:
        Embedding dimension
    """
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()
