"""
Document upload endpoint for storing and processing files with RAG.
"""

from fastapi import APIRouter, UploadFile, HTTPException, File
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
from schemas.chat import UploadResponse
from config import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS
from rag.pipeline import process_document
from rag.vectordb import delete_by_document_id
from services import get_document_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["documents"])


@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents.
    
    Returns:
        List of document metadata
    """
    document_service = get_document_service()
    documents = document_service.get_all_documents()
    
    return {
        "documents": documents,
        "count": len(documents)
    }


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document completely.
    
    This will:
    1. Remove the physical file
    2. Delete metadata entry
    3. Remove all embeddings from ChromaDB
    
    Args:
        document_id: Document ID to delete
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If document not found or deletion fails
    """
    document_service = get_document_service()
    
    # Check if document exists
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    
    try:
        # Delete from ChromaDB
        logger.info(f"Deleting embeddings for document: {document_id}")
        delete_by_document_id(document_id)
        
        # Delete from storage
        success = document_service.delete_document(document_id)
        
        if success:
            return {
                "message": f"Document deleted successfully: {doc['file_name']}",
                "document_id": document_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")
    
    except Exception as e:
        error_msg = f"Error deleting document: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process documents for RAG.
    
    Phase 2: Full RAG implementation with persistence
        1. Save files to persistent storage
        2. Extract text (PDF/TXT)
        3. Chunk documents
        4. Generate embeddings
        5. Store in ChromaDB with document_id
        6. Save metadata
    
    Args:
        files: List of files to upload (PDF or TXT)
    
    Returns:
        UploadResponse with uploaded file names and processing status
    
    Raises:
        HTTPException: If file format is unsupported or processing fails
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    document_service = get_document_service()
    uploaded_files = []
    processing_results = []
    
    for file in files:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. "
                       f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        
        # Save file temporarily first
        temp_path = DOCUMENTS_DIR / file.filename
        
        try:
            # Save uploaded file temporarily
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Get file size
            file_size = temp_path.stat().st_size
            
            # Add to persistent storage and get document_id
            doc_metadata = document_service.add_document(
                file_path=str(temp_path),
                file_name=file.filename,
                file_size=file_size
            )
            
            document_id = doc_metadata["document_id"]
            persistent_path = doc_metadata["file_path"]
            
            logger.info(f"✓ Document stored: {file.filename} (ID: {document_id})")
            uploaded_files.append(file.filename)
            
            # Process document through RAG pipeline with document_id
            logger.info(f"▶ Processing {file.filename} through RAG pipeline...")
            
            try:
                result = await process_document(
                    persistent_path, 
                    file.filename,
                    document_id=document_id
                )
                processing_results.append(result)
                
                if result.get("success"):
                    logger.info(f"✓ Successfully processed: {file.filename}")
                    logger.info(f"  - Chunks created: {result.get('chunks_created', 0)}")
                else:
                    logger.error(f"✗ Failed to process: {file.filename} - {result.get('error')}")
                    # Roll back metadata entry if RAG processing failed
                    logger.warning(f"Rolling back metadata for failed document: {document_id}")
                    document_service.delete_document(document_id)
                    raise Exception(result.get('error', 'RAG processing failed'))
                    
            except Exception as rag_error:
                # If RAG fails, delete the document from storage
                logger.error(f"✗ RAG processing failed for {file.filename}: {str(rag_error)}")
                document_service.delete_document(document_id)
                raise
            
            # Clean up temporary file if different from persistent
            if temp_path != Path(persistent_path):
                temp_path.unlink(missing_ok=True)
        
        except Exception as e:
            error_msg = f"Failed to upload/process {file.filename}: {str(e)}"
            logger.error(error_msg)
            # Clean up on error
            temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=error_msg)
    
    # Build response message
    successful_count = sum(1 for r in processing_results if r.get("success"))
    total_chunks = sum(r.get("chunks_created", 0) for r in processing_results if r.get("success"))
    
    message = (
        f"Successfully uploaded and processed {successful_count}/{len(uploaded_files)} file(s). "
        f"Created {total_chunks} searchable chunks. Documents are now ready for RAG queries."
    )
    
    return UploadResponse(
        message=message,
        files=uploaded_files
    )


@router.get("/documents/{document_id}/file")
async def get_document_file(document_id: str):
    """
    Serve the actual PDF/document file for viewing.
    
    Args:
        document_id: Document ID to retrieve
    
    Returns:
        FileResponse with the document
    """
    document_service = get_document_service()
    document = document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(document["file_path"])
    
    if not file_path.exists():
        logger.error(f"Document file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Document file not found on disk")
    
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=document["file_name"]
    )
