"""
Debug endpoints for testing RAG components.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from rag.embedder import embed_text
from rag.vectordb import get_collection, query_documents
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/collection-stats")
async def get_collection_stats():
    """
    Get ChromaDB collection statistics.
    
    Returns:
        Collection metadata and stats
    """
    try:
        collection = get_collection()
        count = collection.count()
        
        # Get sample items
        sample = collection.get(limit=5)
        
        # Extract unique document_ids
        doc_ids = set()
        for metadata in sample["metadatas"]:
            if "document_id" in metadata:
                doc_ids.add(metadata["document_id"])
        
        return {
            "collection_name": collection.name,
            "total_chunks": count,
            "sample_metadatas": sample["metadatas"][:3],
            "unique_document_ids": list(doc_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retrieval-test")
async def test_retrieval(
    query: str,
    document_ids: Optional[str] = None,
    top_k: int = 5
):
    """
    Test retrieval without calling LLM.
    
    Args:
        query: Query text
        document_ids: Comma-separated document IDs (optional)
        top_k: Number of results
    
    Returns:
        Retrieved chunks with metadata and scores
    """
    try:
        logger.info(f"Debug retrieval test: {query}")
        
        # Parse document_ids
        doc_id_list = None
        if document_ids:
            doc_id_list = [id.strip() for id in document_ids.split(",")]
            logger.info(f"Filtering by document_ids: {doc_id_list}")
        
        # Generate query embedding
        query_embedding = embed_text(query)
        
        # Query ChromaDB
        results = query_documents(
            query_embedding,
            top_k=top_k,
            document_ids=doc_id_list
        )
        
        # Format results
        retrieved = []
        for doc, metadata, distance in zip(
            results["documents"],
            results["metadatas"],
            results["distances"]
        ):
            retrieved.append({
                "text": doc[:200] + "..." if len(doc) > 200 else doc,
                "metadata": metadata,
                "similarity_score": round(1 - distance, 4),
                "distance": round(distance, 4)
            })
        
        return {
            "query": query,
            "document_ids_filter": doc_id_list,
            "results_count": len(retrieved),
            "results": retrieved
        }
    
    except Exception as e:
        logger.error(f"Debug retrieval test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document-chunks/{document_id}")
async def get_document_chunks(document_id: str):
    """
    Get all chunks for a specific document.
    
    Args:
        document_id: Document ID
    
    Returns:
        All chunks with metadata
    """
    try:
        collection = get_collection()
        
        results = collection.get(
            where={"document_id": document_id}
        )
        
        chunks = []
        for doc, metadata in zip(results["documents"], results["metadatas"]):
            chunks.append({
                "text": doc[:200] + "..." if len(doc) > 200 else doc,
                "metadata": metadata
            })
        
        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "chunks": chunks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
