"""
Document Loader
Extracts text from PDF and TXT files
"""

from pypdf import PdfReader
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def load_pdf(file_path: str, file_name: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF file page by page.
    
    Args:
        file_path: Path to PDF file
        file_name: Name of the file
    
    Returns:
        List of dictionaries with text and metadata for each page
    """
    try:
        reader = PdfReader(file_path)
        documents = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            
            if text.strip():  # Only add non-empty pages
                documents.append({
                    "text": text,
                    "metadata": {
                        "file_name": file_name,
                        "page_number": page_num,
                        "total_pages": len(reader.pages)
                    }
                })
        
        logger.info(f"Extracted {len(documents)} pages from {file_name}")
        return documents
    
    except Exception as e:
        logger.error(f"Error loading PDF {file_name}: {str(e)}")
        raise Exception(f"Failed to load PDF: {str(e)}")


def load_txt(file_path: str, file_name: str) -> List[Dict[str, any]]:
    """
    Load text from TXT file.
    
    Args:
        file_path: Path to TXT file
        file_name: Name of the file
    
    Returns:
        List with single dictionary containing text and metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        documents = [{
            "text": text,
            "metadata": {
                "file_name": file_name,
                "page_number": 1,
                "total_pages": 1
            }
        }]
        
        logger.info(f"Loaded text file {file_name}")
        return documents
    
    except Exception as e:
        logger.error(f"Error loading TXT {file_name}: {str(e)}")
        raise Exception(f"Failed to load TXT: {str(e)}")


def load_document(file_path: str, file_name: str) -> List[Dict[str, any]]:
    """
    Load document based on file extension.
    
    Args:
        file_path: Path to file
        file_name: Name of the file
    
    Returns:
        List of documents with text and metadata
    """
    if file_name.lower().endswith('.pdf'):
        return load_pdf(file_path, file_name)
    elif file_name.lower().endswith('.txt'):
        return load_txt(file_path, file_name)
    else:
        raise ValueError(f"Unsupported file type: {file_name}")
