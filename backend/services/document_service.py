"""
Document Service
Handles document persistence, metadata management, and lifecycle
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging
import shutil

logger = logging.getLogger(__name__)

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
METADATA_FILE = DATA_DIR / "metadata.json"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


class DocumentService:
    """Manages document storage and metadata."""
    
    def __init__(self):
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from JSON file."""
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {"documents": []}
        return {"documents": []}
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        try:
            with open(METADATA_FILE, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise
    
    def add_document(
        self, 
        file_path: str, 
        file_name: str,
        file_size: int
    ) -> Dict:
        """
        Add a document to persistent storage.
        
        Args:
            file_path: Current path of uploaded file
            file_name: Original filename
            file_size: File size in bytes
        
        Returns:
            Document metadata dict
        """
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Determine file extension and create persistent path
        file_ext = Path(file_name).suffix
        persistent_filename = f"{document_id}{file_ext}"
        persistent_path = UPLOADS_DIR / persistent_filename
        
        # Copy file to persistent storage
        shutil.copy2(file_path, persistent_path)
        logger.info(f"Copied {file_name} to {persistent_path}")
        
        # Create metadata entry
        doc_metadata = {
            "document_id": document_id,
            "file_name": file_name,
            "file_path": str(persistent_path),
            "file_size": file_size,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Add to metadata
        self.metadata["documents"].append(doc_metadata)
        self._save_metadata()
        
        logger.info(f"Document added: {file_name} (ID: {document_id})")
        return doc_metadata
    
    def get_all_documents(self) -> List[Dict]:
        """Get all stored documents."""
        return self.metadata["documents"]
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get a specific document by ID."""
        for doc in self.metadata["documents"]:
            if doc["document_id"] == document_id:
                return doc
        return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from storage.
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        # Find document in metadata
        doc = self.get_document(document_id)
        if not doc:
            logger.warning(f"Document not found: {document_id}")
            return False
        
        # Delete physical file
        file_path = Path(doc["file_path"])
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
        
        # Remove from metadata
        self.metadata["documents"] = [
            d for d in self.metadata["documents"] 
            if d["document_id"] != document_id
        ]
        self._save_metadata()
        
        logger.info(f"Document deleted: {document_id}")
        return True
    
    def document_exists(self, document_id: str) -> bool:
        """Check if document exists."""
        return self.get_document(document_id) is not None


# Singleton instance
_document_service = None

def get_document_service() -> DocumentService:
    """Get or create document service singleton."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
