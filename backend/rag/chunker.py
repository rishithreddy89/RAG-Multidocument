"""
Document Chunker
Splits documents into chunks with overlap for better retrieval
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Configuration
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            last_break = max(last_period, last_newline)
            
            if last_break > chunk_size * 0.5:  # Only break if we're past halfway
                end = start + last_break + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def chunk_documents(documents: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Chunk multiple documents while preserving metadata.
    
    Args:
        documents: List of documents with text and metadata
    
    Returns:
        List of chunks with text and metadata
    """
    chunked_docs = []
    
    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        
        chunks = chunk_text(text)
        
        for chunk_idx, chunk in enumerate(chunks):
            chunked_docs.append({
                "text": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks)
                }
            })
    
    logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
    return chunked_docs
