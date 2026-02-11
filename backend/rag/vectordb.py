"""
Vector Database using ChromaDB
Handles document storage and similarity search
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Global ChromaDB client (initialized once)
_chroma_client = None
_collection = None

# Configuration
PERSIST_DIRECTORY = Path(__file__).parent.parent / "data" / "chromadb"
COLLECTION_NAME = "documents"


def get_chroma_client() -> chromadb.Client:
    """
    Get or initialize ChromaDB client (singleton pattern).
    
    Returns:
        ChromaDB client instance
    """
    global _chroma_client
    
    if _chroma_client is None:
        # Create persist directory if it doesn't exist
        PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at {PERSIST_DIRECTORY}")
        _chroma_client = chromadb.PersistentClient(
            path=str(PERSIST_DIRECTORY),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.info("ChromaDB client initialized")
    
    return _chroma_client


def get_collection():
    """
    Get or create the documents collection.
    
    Returns:
        ChromaDB collection instance
    """
    global _collection
    
    if _collection is None:
        client = get_chroma_client()
        
        try:
            _collection = client.get_collection(name=COLLECTION_NAME)
            logger.info(f"Loaded existing collection: {COLLECTION_NAME}")
        except Exception:
            _collection = client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Multi-document reasoning engine documents"}
            )
            logger.info(f"Created new collection: {COLLECTION_NAME}")
    
    return _collection


def add_documents(
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
    document_id: Optional[str] = None
) -> str:
    """
    Add documents to ChromaDB collection.
    
    Args:
        texts: List of document texts
        embeddings: List of embedding vectors
        metadatas: List of metadata dictionaries
        document_id: Optional document ID (generated if not provided)
    
    Returns:
        Document ID
    """
    collection = get_collection()
    
    if document_id is None:
        document_id = str(uuid.uuid4())
    
    # Generate unique IDs for each chunk
    ids = [f"{document_id}_{i}" for i in range(len(texts))]
    
    # Add document_id to metadata
    for metadata in metadatas:
        metadata["document_id"] = document_id
    
    # Add to ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    
    logger.info(f"Added {len(texts)} chunks to ChromaDB with document_id: {document_id}")
    return document_id


def query_documents(
    query_embedding: List[float],
    top_k: int = 5,
    document_ids: Optional[List[str]] = None
) -> Dict:
    """
    Query ChromaDB for similar documents.
    
    Args:
        query_embedding: Query embedding vector
        top_k: Number of results to return
        document_ids: Optional list of document IDs to filter by
    
    Returns:
        Dictionary with documents, metadatas, and distances
    """
    collection = get_collection()
    
    # Build query parameters
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }
    
    # Add document_id filter if provided
    if document_ids:
        query_params["where"] = {
            "document_id": {"$in": document_ids}
        }
        logger.info(f"✓ Filtering query by document_ids: {document_ids}")
    else:
        logger.warning("⚠️  No document_ids filter - querying entire collection")
    
    # Log collection state before query
    collection_count = collection.count()
    logger.info(f"✓ Collection has {collection_count} total chunks")
    
    results = collection.query(**query_params)
    
    # Extract results
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []
    
    logger.info(f"✓ Retrieved {len(documents)} chunks from ChromaDB")
    if len(documents) > 0:
        logger.info(f"  - Sample result metadata: {metadatas[0] if metadatas else 'None'}")
        logger.info(f"  - Similarity scores: {[round(1-d, 3) for d in distances[:3]]}")
    
    return {
        "documents": documents,
        "metadatas": metadatas,
        "distances": distances
    }


def delete_by_document_id(document_id: str):
    """
    Delete all chunks for a specific document.
    
    Args:
        document_id: Document ID to delete
    """
    collection = get_collection()
    
    # Query to find all IDs with this document_id
    results = collection.get(
        where={"document_id": document_id}
    )
    
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted document {document_id} with {len(results['ids'])} chunks")
    else:
        logger.warning(f"No chunks found for document_id: {document_id}")


def get_collection_stats() -> Dict:
    """
    Get statistics about the collection.
    
    Returns:
        Dictionary with collection statistics
    """
    collection = get_collection()
    count = collection.count()
    
    return {
        "collection_name": COLLECTION_NAME,
        "total_documents": count,
        "persist_directory": str(PERSIST_DIRECTORY)
    }


def reset_collection():
    """
    Delete all documents from the collection.
    WARNING: This will delete all data!
    """
    global _collection
    
    client = get_chroma_client()
    
    try:
        client.delete_collection(name=COLLECTION_NAME)
        logger.info(f"Deleted collection: {COLLECTION_NAME}")
    except Exception as e:
        logger.warning(f"Could not delete collection: {str(e)}")
    
    # Recreate collection
    _collection = None
    get_collection()
    logger.info("Collection reset complete")
