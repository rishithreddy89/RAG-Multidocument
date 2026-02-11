"""
Document Retriever
Retrieves relevant document chunks for a given query
"""

from typing import List, Dict
import logging
from .embedder import embed_text
from .vectordb import query_documents

logger = logging.getLogger(__name__)


def retrieve(query: str, top_k: int = 5, selected_document_ids: List[str] = None) -> List[Dict]:
    """
    Retrieve relevant document chunks for a query.
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        selected_document_ids: List of document IDs to filter by (required)
    
    Returns:
        List of dictionaries with text, metadata, and relevance score
    """
    try:
        # Validate that documents are selected
        if not selected_document_ids or len(selected_document_ids) == 0:
            logger.warning("No documents selected for retrieval")
            return []
        
        # Generate query embedding
        logger.info(f"Generating embedding for query: {query[:100]}...")
        logger.info(f"Filtering by {len(selected_document_ids)} selected document(s)")
        query_embedding = embed_text(query)
        
        # Query ChromaDB with document filtering (limit to 3 chunks for speed)
        results = query_documents(
            query_embedding, 
            top_k=min(top_k, 3),
            document_ids=selected_document_ids
        )
        
        logger.info(f"✓ ChromaDB query completed")
        logger.info(f"  - Documents found: {len(results.get('documents', []))}")
        logger.info(f"  - Distances: {results.get('distances', [])}")
        
        # Handle empty results
        if not results["documents"]:
            logger.warning("❌ No relevant documents found in ChromaDB")
            logger.warning(f"  - Selected document IDs: {selected_document_ids}")
            logger.warning(f"  - Query: {query[:100]}...")
            return []
        
        # Format results
        retrieved_chunks = []
        for doc, metadata, distance in zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        ):
            retrieved_chunks.append({
                "text": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance  # Convert distance to similarity
            })
        
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
        return retrieved_chunks
    
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        return []


def format_retrieved_context(chunks: List[Dict]) -> str:
    """
    Format retrieved chunks into context string for LLM.
    
    Args:
        chunks: Retrieved document chunks
    
    Returns:
        Formatted context string
    """
    if not chunks:
        return ""
    
    context_parts = []
    for idx, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        file_name = metadata.get("file_name", "Unknown")
        page_number = metadata.get("page_number", "N/A")
        text = chunk["text"]
        
        context_parts.append(
            f"[Document: {file_name}, Page: {page_number}]\n{text}\n"
        )
    
    return "\n---\n".join(context_parts)


def extract_sources(chunks: List[Dict]) -> List[Dict]:
    """
    Extract unique source references from retrieved chunks.
    
    Args:
        chunks: Retrieved document chunks
    
    Returns:
        List of unique source dictionaries
    """
    sources = []
    seen = set()
    
    for chunk in chunks:
        metadata = chunk["metadata"]
        file_name = metadata.get("file_name", "Unknown")
        page_number = metadata.get("page_number", "N/A")
        
        # Create unique identifier
        source_key = f"{file_name}_{page_number}"
        
        if source_key not in seen:
            sources.append({
                "file": file_name,
                "page": page_number
            })
            seen.add(source_key)
    
    return sources
