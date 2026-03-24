"""
Document Chunker
Semantic paragraph-based chunking using LangChain for improved RAG retrieval
"""

from typing import List, Dict
import logging
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_core.documents import Document
except Exception:
    try:
        from langchain.schema import Document
    except Exception:
        # Last-resort: define a minimal Document dataclass fallback
        from dataclasses import dataclass

        @dataclass
        class Document:
            page_content: str
            metadata: dict

logger = logging.getLogger(__name__)

# Configuration - Token-based chunking for better semantic coherence
CHUNK_SIZE = 400  # tokens
CHUNK_OVERLAP = 80  # tokens

# Approximate characters per token (rough estimate for English text)
CHARS_PER_TOKEN = 4

# Calculate character-based equivalents for the splitter
CHUNK_SIZE_CHARS = CHUNK_SIZE * CHARS_PER_TOKEN  # ~1600 characters
CHUNK_OVERLAP_CHARS = CHUNK_OVERLAP * CHARS_PER_TOKEN  # ~320 characters


def _to_int(value, default: int = 0) -> int:
    """Best-effort conversion to int."""
    try:
        return int(value)
    except Exception:
        return default


def create_text_splitter(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> RecursiveCharacterTextSplitter:
    """
    Create a LangChain RecursiveCharacterTextSplitter configured for semantic chunking.
    
    The splitter prioritizes splitting by:
    1. Double newlines (paragraphs) - \n\n
    2. Single newlines - \n
    3. Sentence endings - . ! ?
    4. Spaces
    
    Args:
        chunk_size: Target chunk size in tokens (default: 400)
        chunk_overlap: Overlap between chunks in tokens (default: 80)
    
    Returns:
        Configured RecursiveCharacterTextSplitter
    """
    # Convert tokens to approximate character counts
    chunk_size_chars = chunk_size * CHARS_PER_TOKEN
    chunk_overlap_chars = chunk_overlap * CHARS_PER_TOKEN
    
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        length_function=len,
        separators=[
            "\n\n",  # Paragraph breaks (highest priority)
            "\n",    # Line breaks
            ". ",    # Sentence endings with space
            "! ",    # Exclamation with space
            "? ",    # Question with space
            "; ",    # Semicolon
            ", ",    # Comma
            " ",     # Spaces (lowest priority)
            ""       # Fallback to character splitting
        ],
        keep_separator=True,  # Preserve separators for context
        is_separator_regex=False
    )


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into semantic chunks using LangChain's RecursiveCharacterTextSplitter.
    
    This function prioritizes semantic boundaries (paragraphs, sentences) over
    fixed character counts for better retrieval and reasoning.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens (default: 400)
        overlap: Overlap between chunks in tokens (default: 80)
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    splitter = create_text_splitter(chunk_size, overlap)
    chunks = splitter.split_text(text)
    
    # Clean up chunks (strip whitespace)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks


def detect_section_title(text: str) -> str:
    """
    Detect section title from the beginning of a text chunk.
    
    Looks for common patterns like:
    - All caps lines (INTRODUCTION)
    - Numbered sections (1. Introduction, 1.1 Background)
    - Title case headings followed by newline
    
    Args:
        text: Text chunk to analyze
    
    Returns:
        Detected section title or "Unknown"
    """
    lines = text.strip().split('\n')
    
    if not lines:
        return "Unknown"
    
    first_line = lines[0].strip()
    
    # Check if first line is all caps (common for section headers)
    if first_line.isupper() and len(first_line.split()) <= 5 and len(first_line) > 0:
        return first_line
    
    # Check for numbered sections (e.g., "1. Introduction", "1.1 Methods")
    import re
    numbered_pattern = r'^(\d+\.)+\s*([A-Z][a-zA-Z\s]+)$'
    match = re.match(numbered_pattern, first_line)
    if match:
        return match.group(2).strip()
    
    # Check for title case headings (first line is short and title-cased)
    if (len(first_line.split()) <= 6 and 
        first_line[0].isupper() and 
        len(first_line) < 100 and
        not first_line.endswith(('.', '!', '?'))):
        return first_line
    
    return "Unknown"


def chunk_documents(
    documents: List[Dict[str, any]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Chunk multiple documents using semantic paragraph-based chunking.
    
    This function uses LangChain's RecursiveCharacterTextSplitter to create
    semantically coherent chunks that preserve meaning and improve retrieval
    quality for multi-document reasoning.
    
    Each chunk includes enriched metadata:
    - document_name: Source file name
    - page_number: Page where chunk originated
    - section_title: Detected section heading (or "Unknown")
    - chunk_index: Position within document
    - total_chunks: Total chunks from source
    - chunk_size_tokens: Approximate token count
    
    Args:
        documents: List of documents with text and metadata (dict format)
        chunk_size: Target chunk size in tokens (default: 400)
        overlap: Overlap between chunks in tokens (default: 80)
    
    Returns:
        List of LangChain Document objects with enriched metadata
    """
    splitter = create_text_splitter(chunk_size, overlap)
    all_chunked_docs = []
    
    for doc in documents:
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})
        
        if not text or not text.strip():
            logger.warning(f"Skipping empty document: {metadata.get('file_name', 'unknown')}")
            continue
        
        # Split text directly so we can compute per-chunk char offsets
        chunk_texts = splitter.split_text(text)
        chunk_texts = [c.strip() for c in chunk_texts if c and c.strip()]
        total_chunks = len(chunk_texts)
        cursor = 0
        
        # Enrich each chunk with enhanced metadata
        for chunk_idx, chunk_text in enumerate(chunk_texts):
            # Compute chunk char offsets in source page text
            search_start = max(0, cursor - CHUNK_OVERLAP_CHARS)
            char_start = text.find(chunk_text, search_start)
            if char_start == -1:
                char_start = text.find(chunk_text)
            if char_start == -1:
                char_start = cursor
            char_end = min(len(text), char_start + len(chunk_text))
            cursor = max(cursor, char_end)

            # Detect section title from chunk content
            section_title = detect_section_title(chunk_text)
            
            # Get entity data from source metadata
            entity_persons = metadata.get("entity_persons", [])
            entity_organizations = metadata.get("entity_organizations", [])
            entity_roles = metadata.get("entity_roles", [])
            
            # Convert lists to pipe-separated strings for ChromaDB compatibility
            # (ChromaDB doesn't accept lists in metadata, only primitives)
            persons_str = "|".join(entity_persons) if entity_persons else ""
            orgs_str = "|".join(entity_organizations) if entity_organizations else ""
            roles_str = "|".join(entity_roles) if entity_roles else ""
            
            # Enrich metadata - use only flat, primitive types for ChromaDB compatibility
            chunk_metadata = dict(metadata)
            page_number = _to_int(metadata.get("page_number", metadata.get("page", 1)), 1)
            document_name = metadata.get("file_name", metadata.get("document_name", "unknown"))

            chunk_metadata.update({
                "doc_name": document_name,
                "document_name": document_name,
                "page": str(page_number),
                "page_number": str(page_number),
                "section_title": section_title,
                "chunk_index": str(chunk_idx),
                "total_chunks": str(total_chunks),
                "chunk_size_tokens": str(len(chunk_text) // CHARS_PER_TOKEN),
                "char_start": str(char_start),
                "char_end": str(char_end),
                "bbox": metadata.get("bbox", ""),
                # Entity extraction data (flattened for ChromaDB)
                "primary_entity": metadata.get("primary_entity", "Unknown"),
                "entity_persons": persons_str,
                "entity_organizations": orgs_str,
                "entity_roles": roles_str
            })

            chunk = Document(
                page_content=chunk_text,
                metadata=chunk_metadata
            )
            
            all_chunked_docs.append(chunk)
    
    logger.info(f"Created {len(all_chunked_docs)} semantic chunks from {len(documents)} documents")
    logger.info(f"Chunking strategy: {chunk_size} tokens/chunk with {overlap} token overlap")
    
    # Log sample metadata for verification
    if all_chunked_docs:
        sample_meta = all_chunked_docs[0].metadata
        logger.info(f"Sample chunk metadata: {sample_meta}")
    
    return all_chunked_docs
