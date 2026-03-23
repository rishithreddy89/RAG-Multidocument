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
        
        # Query ChromaDB with document filtering
        results = query_documents(
            query_embedding, 
            top_k=top_k,
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
        logger.exception(f"Error retrieving documents: {str(e)}")
        return []


def format_retrieved_context(chunks: List[Dict]) -> str:
    """
    Format retrieved chunks with entity-aware attribution.
    
    Ensures that extracted entities (persons, organizations, roles) are prominently
    displayed to prevent misattribution in LLM responses. Uses entity extraction
    results to provide accurate context.
    
    Args:
        chunks: Retrieved document chunks with entity metadata
    
    Returns:
        Formatted context string with entity attribution
    """
    if not chunks:
        return ""
    
    context_parts = []
    current_document = None
    
    for idx, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        file_name = metadata.get("file_name", "Unknown")
        page_number = metadata.get("page_number", "N/A")
        pdf_author = metadata.get("pdf_author")
        pdf_title = metadata.get("pdf_title")
        section_title = metadata.get("section_title", "Unknown Section")
        
        # Extract entity metadata (pipe-separated strings for ChromaDB compatibility)
        primary_entity = metadata.get("primary_entity", "Unknown")
        
        # Parse pipe-separated entity strings back into lists
        entity_persons_str = metadata.get("entity_persons", "")
        entity_organizations_str = metadata.get("entity_organizations", "")
        
        entity_persons = [p.strip() for p in entity_persons_str.split("|") if p.strip()] if entity_persons_str else []
        entity_organizations = [o.strip() for o in entity_organizations_str.split("|") if o.strip()] if entity_organizations_str else []
        
        text = chunk["text"]

        # Add document separator when switching to a new document
        # CRITICAL: Put primary entity first to ensure attribution
        if current_document != file_name:
            current_document = file_name
            separator = f"\n{'='*80}\n"
            separator += f"PRIMARY SUBJECT: {primary_entity}\n"
            if entity_persons:
                separator += f"PEOPLE: {', '.join(entity_persons)}\n"
            if entity_organizations:
                separator += f"ORGANIZATIONS: {', '.join(entity_organizations)}\n"
            separator += f"SOURCE: {file_name}\n"
            if pdf_title:
                separator += f"TITLE: {pdf_title}\n"
            separator += f"{'='*80}\n"
            context_parts.append(separator)

        header_parts = [f"Page: {page_number}", f"Section: {section_title}"]
        context_parts.append(
            f"[{', '.join(header_parts)}]\n{text}\n"
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
