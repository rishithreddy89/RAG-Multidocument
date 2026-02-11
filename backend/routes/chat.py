"""
Chat endpoint for RAG-powered question answering.
"""

from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from rag.pipeline import rag_query
from services import get_chat_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history")
async def get_chat_history():
    """
    Get chat history.
    
    Returns:
        List of chat messages
    """
    chat_service = get_chat_service()
    messages = chat_service.get_history()
    
    return {
        "messages": messages,
        "count": len(messages)
    }


@router.delete("/history")
async def clear_chat_history():
    """
    Clear chat history.
    
    Returns:
        Success message
    """
    chat_service = get_chat_service()
    chat_service.clear_history()
    
    return {
        "message": "Chat history cleared successfully"
    }


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message using RAG (Retrieval-Augmented Generation).
    
    RAG Pipeline:
        1. Retrieve relevant document chunks from ChromaDB
        2. Construct prompt with retrieved context
        3. Generate LLM response grounded in document context
        4. Return answer with source citations
        5. Save to chat history
    
    Args:
        request: ChatRequest with user message and optional conversation history
    
    Returns:
        ChatResponse with assistant's reply (grounded in uploaded documents)
    
    Raises:
        HTTPException: If RAG query fails
    """
    chat_service = get_chat_service()
    
    logger.info(f"RAG query: {request.message[:100]}...")
    logger.info(f"Selected documents: {request.selected_documents}")
    
    # Validate that at least one document is selected
    if not request.selected_documents or len(request.selected_documents) == 0:
        logger.warning("No documents selected for query")
        raise HTTPException(
            status_code=400, 
            detail="Please select at least one document to query"
        )
    
    # Save user message to history
    chat_service.add_message("user", request.message)
    
    try:
        # Execute RAG pipeline with document filtering (limit to 3 chunks for speed)
        result = await rag_query(
            request.message, 
            top_k=3,
            selected_document_ids=request.selected_documents
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error in RAG pipeline")
            logger.error(f"RAG query failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Extract answer and sources
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])
        
        # Format response with sources
        response_text = answer
        if sources:
            response_text += "\n\n**Sources:**\n"
            for i, source in enumerate(sources[:3], 1):  # Show top 3 sources
                doc_name = source.get("file", source.get("document_name", "Unknown"))
                page = source.get("page", "N/A")
                response_text += f"{i}. {doc_name} (Page {page})\n"
        
        # Save assistant response to history
        chat_service.add_message("assistant", response_text, sources)
        
        logger.info(f"RAG response generated with {len(sources)} sources")
        return ChatResponse(response=response_text)
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error in RAG query: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
