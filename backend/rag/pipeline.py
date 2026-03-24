"""
RAG Pipeline
Orchestrates the complete RAG workflow
"""

from typing import Dict, List
import logging
import re

from .loader import load_document
from .chunker import chunk_documents
from .embedder import embed_texts
from .vectordb import add_documents, get_document_metadata, get_document_chunks
from .retriever import retrieve, extract_sources
from .generator import generate_answer

logger = logging.getLogger(__name__)


def _is_page_count_query(question: str) -> bool:
    question = question.lower()
    return (
        "page" in question and
        any(phrase in question for phrase in ["how many", "number of", "total", "pages in", "pages are in"])
    )


def _is_author_query(question: str) -> bool:
    question = question.lower()
    return any(phrase in question for phrase in ["author", "who wrote", "written by", "name of author"])


def _is_title_query(question: str) -> bool:
    question = question.lower()
    return any(phrase in question for phrase in ["title", "name of book", "book name", "document title"])


def _is_summary_query(question: str) -> bool:
    question = question.lower()
    return any(
        phrase in question
        for phrase in [
            "summary",
            "summarize",
            "entire summary",
            "overall summary",
            "summary of the document",
            "summary of this book",
            "what is this document about",
            "what is this book about",
        ]
    )


def _is_word_count_query(question: str) -> bool:
    """Detect queries asking for word count in a document."""
    question = question.lower()
    return (
        "count" in question and
        ("word" in question or "words" in question)
    )


def classify_query(query: str) -> str:
    """
    Classify query into routing type: count, compare, summary, or qa.
    
    Args:
        query: User's question
        
    Returns:
        Route type: "count", "compare", "summary", or "qa"
    """
    q = query.lower()
    
    # Count queries take priority (most specific)
    if ("count" in q or "number of" in q) and ("word" in q or "words" in q):
        return "count"
    
    # Compare queries
    if any(phrase in q for phrase in ["compare", "difference", "differences", "similarities", "similar", "vs", "versus"]):
        return "compare"
    
    # Summary queries
    if any(phrase in q for phrase in ["summary", "summarize", "summarization", "summarise", "overall", "what is this"]):
        return "summary"
    
    # Default to QA
    return "qa"


def normalize_text(text: str) -> str:
    """
    Normalize text for robust word counting.
    
    - Remove zero-width characters
    - Collapse whitespace
    - Normalize dashes
    
    Args:
        text: Raw text to normalize
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Remove zero-width characters
    text = text.replace("\u200b", " ")
    
    # Normalize dashes and hyphens
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2014", "-")  # em dash
    
    # Collapse multiple whitespace into single space
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def count_words(text: str) -> int:
    """
    Count the number of words in text using regex pattern matching.
    Normalizes text first for robustness.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words found
    """
    if not text:
        return 0
    
    # Normalize text first
    text = normalize_text(text)
    
    # Match word boundaries: sequences of alphanumeric chars and underscores
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def extract_doc_name(query: str, available_docs: List[str]) -> str | None:
    """
    Extract document name from query by matching against available documents.
    
    Matching strategy:
    1. Exact match (case-insensitive)
    2. Substring match (longest first to avoid partial matches)
    3. Fuzzy match on filename without extension
    
    Args:
        query: User's query
        available_docs: List of available document file names
        
    Returns:
        Matched document file name, or None if no match found
    """
    q = query.lower()
    
    if not available_docs:
        return None
    
    # Strategy 1: Try exact matches with common variations
    for doc_name in available_docs:
        doc_lower = doc_name.lower()
        if doc_lower == q or doc_lower in q:
            return doc_name
    
    # Strategy 2: Try substring matching (longest first to avoid partial matches)
    for doc_name in sorted(available_docs, key=len, reverse=True):
        doc_lower = doc_name.lower()
        if doc_lower in q:
            return doc_name
    
    # Strategy 3: Try matching just the filename without extension
    for doc_name in available_docs:
        name_without_ext = doc_name.rsplit('.', 1)[0].lower()
        if name_without_ext in q:
            return doc_name
    
    return None


def get_full_document_text(document_ids: List[str]) -> Dict[str, str]:
    """
    Retrieve the full text of documents by reconstructing from stored chunks.
    
    Args:
        document_ids: List of document IDs to retrieve
        
    Returns:
        Dictionary mapping document_id to full text
    """
    full_texts = {}
    
    for doc_id in document_ids:
        # Get all chunks for this document, ordered by page and chunk index
        chunks = get_document_chunks([doc_id], max_chunks_per_document=999)
        
        # Reconstruct full text by joining chunks in order
        text_parts = [chunk["text"] for chunk in chunks]
        full_text = " ".join(text_parts)
        full_texts[doc_id] = full_text
    
    return full_texts


def run_count_pipeline(query: str, available_docs: List[str]) -> Dict:
    """
    Deterministic word count pipeline - bypasses LLM, retrieval, and embeddings.
    
    NO LLM CALL - Uses deterministic regex-based word counting
    
    Args:
        query: The user's question
        available_docs: List of available document file names
        
    Returns:
        Dictionary with word count and sources
    """
    try:
        # Handle case where no documents are uploaded
        if not available_docs:
            return {
                "success": False,
                "error": "No documents uploaded",
                "answer": "No documents available. Please upload a document first.",
                "sources": []
            }
        
        # Extract document name from query
        doc_name = extract_doc_name(query, available_docs)
        
        # If no document specified in query, auto-select if only one document exists
        if not doc_name:
            if len(available_docs) == 1:
                doc_name = available_docs[0]
                logger.info(f"Auto-selected single document: {doc_name}")
            else:
                doc_list = ", ".join(available_docs)
                return {
                    "success": False,
                    "error": "Document not specified",
                    "answer": f"Please specify which document to count words for.\n\nAvailable documents:\n- {doc_list}",
                    "sources": []
                }
        
        # Get metadata to find document ID
        from .vectordb import get_all_document_metadata
        metadata_list = get_all_document_metadata()
        
        if not metadata_list:
            return {
                "success": False,
                "error": "No documents indexed",
                "answer": "No documents are currently indexed in the system.",
                "sources": []
            }
        
        doc_id = None
        for metadata in metadata_list:
            if metadata["file_name"] == doc_name:
                doc_id = metadata["document_id"]
                break
        
        if not doc_id:
            return {
                "success": False,
                "error": "Document metadata not found",
                "answer": f"Could not find metadata for {doc_name}. Please check the document name.",
                "sources": []
            }
        
        # Get full document text (reconstructed from chunks)
        full_texts = get_full_document_text([doc_id])
        text = full_texts.get(doc_id, "")
        
        if not text:
            return {
                "success": False,
                "error": "Document text empty",
                "answer": f"Could not retrieve text for {doc_name}",
                "sources": []
            }
        
        # Count words
        word_count = count_words(text)
        
        # Format response
        answer = f"{doc_name} contains {word_count:,} words."
        sources = [{"file": doc_name, "page": 1}]
        
        logger.info(f"Word count: {answer}")
        
        return {
            "success": True,
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        error_msg = f"Error counting words: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "answer": "Unable to count words in document.",
            "sources": []
        }


def _try_answer_metadata_query(question: str, selected_document_ids: List[str]) -> Dict | None:
    """
    Answer simple metadata questions directly from stored document metadata.
    """
    if not selected_document_ids:
        return None

    if not (
        _is_page_count_query(question) or
        _is_author_query(question) or
        _is_title_query(question) or
        _is_word_count_query(question)
    ):
        return None
    
    # Word count query - use deterministic pipeline (no LLM)
    if _is_word_count_query(question):
        return run_count_pipeline(question, selected_document_ids)

    summaries = get_document_metadata(selected_document_ids)
    if not summaries:
        return None

    sources = [
        {
            "file": summary["file_name"],
            "page": summary.get("page_number", 1)
        }
        for summary in summaries
    ]

    if _is_page_count_query(question):
        if len(summaries) == 1:
            summary = summaries[0]
            answer = f"{summary['file_name']} has {summary.get('total_pages', 'an unknown number of')} pages."
        else:
            lines = [f"{summary['file_name']}: {summary.get('total_pages', 'Unknown')} pages" for summary in summaries]
            answer = "Selected documents page counts:\n" + "\n".join(lines)

        return {"success": True, "answer": answer, "sources": sources}

    if _is_author_query(question):
        if len(summaries) == 1:
            summary = summaries[0]
            answer = f"The author of {summary['file_name']} is {summary.get('pdf_author', 'Unknown')}."
        else:
            lines = [f"{summary['file_name']}: {summary.get('pdf_author', 'Unknown')}" for summary in summaries]
            answer = "Selected document authors:\n" + "\n".join(lines)

        return {"success": True, "answer": answer, "sources": sources}

    if _is_title_query(question):
        if len(summaries) == 1:
            summary = summaries[0]
            answer = f"The title is {summary.get('pdf_title', summary['file_name'])}."
        else:
            lines = [f"{summary['file_name']}: {summary.get('pdf_title', summary['file_name'])}" for summary in summaries]
            answer = "Selected document titles:\n" + "\n".join(lines)

        return {"success": True, "answer": answer, "sources": sources}

    return None


async def process_document(file_path: str, file_name: str, document_id: str = None) -> Dict:
    """
    Process a document through the RAG pipeline.
    
    Steps:
    1. Load document
    2. Chunk text (returns LangChain Document objects with enriched metadata)
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
        
        # Step 2: Chunk documents (returns LangChain Document objects)
        chunks = chunk_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Add document_id to all chunk metadata
        if document_id:
            for chunk in chunks:
                chunk.metadata["document_id"] = document_id
        
        # Step 3: Extract data for embeddings and storage
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
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

        metadata_answer = _try_answer_metadata_query(question, selected_document_ids)
        if metadata_answer:
            logger.info("Answered query directly from document metadata")
            return metadata_answer

        if _is_summary_query(question):
            logger.info("Summary query detected - using document-wide context")
            retrieved_chunks = get_document_chunks(
                selected_document_ids,
                max_chunks_per_document=30
            )
        else:
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
        if "timeout" in str(e).lower() and 'retrieved_chunks' in locals() and retrieved_chunks:
            logger.warning("LLM timeout - returning safe fallback")
            sources = extract_sources(retrieved_chunks)

            if _is_summary_query(question):
                return {
                    "success": True,
                    "answer": "The model took too long while preparing a full-document summary. Please try a more specific summary request such as chapter-wise summary, summary of the first half, or summary of a specific topic.",
                    "sources": sources
                }

            return {
                "success": True,
                "answer": "The model took too long to generate a grounded answer. Please try a more specific question.",
                "sources": sources
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
