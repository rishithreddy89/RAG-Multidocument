"""
RAG Pipeline
Orchestrates the complete RAG workflow
"""

from typing import Dict, List
import logging
from pathlib import Path

from .loader import load_document
from .chunker import chunk_documents
from .embedder import embed_texts
from .vectordb import add_documents
from .retriever import retrieve, extract_sources
from .generator import generate_answer

logger = logging.getLogger(__name__)


async def process_document(file_path: str, file_name: str, document_id: str = None) -> Dict:
    """
    Process a document through the RAG pipeline.
    
    Steps:
    1. Load document
    2. Chunk text
    3. Generate embeddings
    4. Store in ChromaDB with document_id
    
    Args:
        file_path: Path to document file
        file_name: Name of the file
        document_id: Unique document identifier for persistence
    
    Returns:
        Dictionary with processing results
    """
    try:
        logger.info(f"Processing document: {file_name} (ID: {document_id})")
        
        # Step 1: Load document
        documents = load_document(file_path, file_name)
        logger.info(f"Loaded {len(documents)} pages/sections")
        
        # Step 2: Chunk documents
        chunks = chunk_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Add document_id to all chunk metadata
        if document_id:
            for chunk in chunks:
                chunk["metadata"]["document_id"] = document_id
        
        # Step 3: Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        logger.info("Generating embeddings...")
        embeddings = embed_texts(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Step 4: Store in ChromaDB
        document_id = add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            document_id=document_id
        )
        
        logger.info(f"✓ Document processed successfully: {document_id}")
        logger.info(f"✓ Inserted {len(chunks)} chunks into ChromaDB")
        logger.info(f"✓ Sample metadata: {metadatas[0] if metadatas else 'None'}")
        
        return {
            "success": True,
            "document_id": document_id,
            "file_name": file_name,
            "chunks_created": len(chunks),
            "message": f"Successfully processed {file_name}"
        }
    
    except Exception as e:
        error_msg = f"Error processing document {file_name}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "file_name": file_name,
            "error": str(e),
            "message": error_msg
        }


async def rag_query(question: str, top_k: int = 5, selected_document_ids: List[str] = None) -> Dict:
    """
    Execute RAG query pipeline with document filtering.
    
    Steps:
    1. Retrieve relevant chunks from selected documents only
    2. Generate answer using LLM
    3. Return answer with sources
    
    Args:
        question: User's question
        top_k: Number of chunks to retrieve
        selected_document_ids: List of document IDs to filter by (required)
    
    Returns:
        Dictionary with answer and sources
    """
    try:
        logger.info(f"RAG query: {question[:100]}...")
        logger.info(f"Filtering by {len(selected_document_ids) if selected_document_ids else 0} document(s)")
        
        # Validate selected documents
        if not selected_document_ids or len(selected_document_ids) == 0:
            logger.warning("No documents selected for query")
            return {
                "success": False,
                "error": "No documents selected. Please select at least one document.",
                "answer": "Please select at least one document to query.",
                "sources": []
            }
        
        # Step 1: Retrieve relevant chunks from selected documents only
        retrieved_chunks = retrieve(
            question, 
            top_k=top_k,
            selected_document_ids=selected_document_ids
        )
        
        # Step 2: Check if any relevant documents found
        if not retrieved_chunks:
            logger.warning("No relevant documents found for query")
            return {
                "success": True,
                "answer": "No relevant information found in uploaded documents.",
                "sources": []
            }
        
        # Step 3: Generate answer
        result = await generate_answer(question, retrieved_chunks)
        result["success"] = True
        
        logger.info("RAG query completed successfully")
        return result
    
    except Exception as e:
        error_msg = f"Error in RAG query: {str(e)}"
        logger.error(error_msg)
        
        # If LLM times out but we have retrieved chunks, return them
        if "timeout" in str(e).lower() and retrieved_chunks:
            logger.warning("LLM timeout - returning context summary")
            context_preview = retrieved_chunks[0]["text"][:500] if retrieved_chunks else ""
            return {
                "success": True,
                "answer": f"[LLM is processing slowly] Here's relevant content from the documents:\n\n{context_preview}...",
                "sources": extract_sources(retrieved_chunks)
            }
        
        return {
            "success": False,
            "error": error_msg,
            "answer": f"Error processing your question: {str(e)}",
            "sources": []
        }


async def batch_process_documents(file_paths: List[str], file_names: List[str]) -> List[Dict]:
    """
    Process multiple documents in batch.
    
    Args:
        file_paths: List of file paths
        file_names: List of file names
    
    Returns:
        List of processing results
    """
    results = []
    
    for file_path, file_name in zip(file_paths, file_names):
        result = await process_document(file_path, file_name)
        results.append(result)
    
    successful = sum(1 for r in results if r.get("success"))
    logger.info(f"Batch processing complete: {successful}/{len(results)} successful")
    
    return results
