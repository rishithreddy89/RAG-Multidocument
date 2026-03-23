"""
Document Loader
Extracts text from PDF and TXT files with intelligent entity extraction.

Enhances metadata by dynamically extracting key entities (persons, organizations, roles)
from document content, enabling accurate attribution in RAG responses.
"""

from pypdf import PdfReader
from typing import List, Dict, Set
import logging
import re

logger = logging.getLogger(__name__)


def extract_entities(text: str) -> Dict:
    """
    Extract key entities from document text using heuristics and NLP-style rules.
    
    Strategy:
    1. Scan first 50 lines (document header/summary section)
    2. Identify prominent nouns and title-case phrases
    3. Classify entities as: persons, organizations, roles
    4. Rank by position (earlier = more likely to be document subject)
    
    Args:
        text: Raw document text
    
    Returns:
        Dictionary with:
        {
            "primary_entity": str,  # Most likely document subject
            "entities": {
                "persons": [...],
                "organizations": [...],
                "roles": [...]
            }
        }
    """
    entities = {
        "persons": set(),
        "organizations": set(),
        "roles": set()
    }
    
    if not text or not text.strip():
        return {
            "primary_entity": "Unknown",
            "entities": {k: [] for k in entities}
        }
    
    lines = text.strip().split('\n')[:50]  # Focus on first 50 lines
    
    # Common role/title keywords
    role_keywords = {
        'engineer', 'developer', 'architect', 'manager', 'lead', 'director',
        'analyst', 'scientist', 'researcher', 'student', 'intern', 'associate',
        'specialist', 'consultant', 'designer', 'officer', 'executive',
        'programmer', 'data scientist', 'ml engineer', 'full stack', 'backend',
        'frontend', 'devops', 'qa', 'qa engineer', 'product manager'
    }
    
    # Common organization indicators
    org_keywords = {
        'company', 'corporation', 'institute', 'university', 'college',
        'organization', 'org', 'organization', 'inc', 'ltd', 'llc',
        'consulting', 'technologies', 'systems', 'solutions'
    }
    
    # Words to skip (common articles, prepositions)
    skip_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'at', 'to', 'for',
        'from', 'by', 'with', 'as', 'is', 'was', 'are', 'were', 'have', 'has',
        'been', 'be', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'shall'
    }
    
    processed_lines = []
    
    for line in lines:
        cleaned = line.strip()
        
        # Skip empty, too short, or obviously metadata lines
        if not cleaned or len(cleaned) < 3:
            continue
        if '@' in cleaned or 'http' in cleaned.lower():
            continue
        if cleaned.lower() in {'resume', 'cv', 'contact', 'email', 'phone', 'address'}:
            continue
        if len(cleaned) > 150:  # Skip very long lines (likely body text)
            continue
        
        processed_lines.append(cleaned)
    
    # Extract person names (2-4 title-cased words)
    for line in processed_lines:
        words = line.split()
        
        # Check if line looks like a person name
        if 2 <= len(words) <= 4:
            # Validate format: mostly letters, title case
            valid_chars = sum(1 for c in line if c.isalpha() or c in " -'")
            if valid_chars / len(line) > 0.75:
                title_case_words = sum(1 for w in words if w[0].isupper() and not w.isupper())
                if title_case_words >= len(words) - 1:  # At least n-1 words title-cased
                    if line not in skip_words:
                        entities["persons"].add(line)
                        break  # Primary entity is likely first name found
        
        # Extract roles (contains role keywords)
        line_lower = line.lower()
        for role in role_keywords:
            if role in line_lower:
                # Extract the full phrase containing the role
                match = re.search(r'([a-zA-Z\s&-]+(?:' + role + r')[a-zA-Z\s&-]*)', line_lower)
                if match:
                    entities["roles"].add(match.group(1).strip().title())
                    break
        
        # Extract organizations (contains org keywords or all-caps phrases)
        for org in org_keywords:
            if org in line_lower:
                entities["organizations"].add(line)
                break
        
        # Check for all-caps phrases (common for organization names)
        all_caps = re.findall(r'\b([A-Z][A-Z0-9\s&-]+)\b', line)
        for phrase in all_caps:
            if len(phrase.split()) <= 3:  # Max 3 words for org names
                entities["organizations"].add(phrase.strip())
    
    # Determine primary entity (person name > organization > role)
    primary_entity = "Unknown"
    if entities["persons"]:
        primary_entity = list(entities["persons"])[0]
    elif entities["organizations"]:
        primary_entity = list(entities["organizations"])[0]
    elif entities["roles"]:
        primary_entity = list(entities["roles"])[0]
    
    # Convert sets to sorted lists
    return {
        "primary_entity": primary_entity,
        "entities": {
            "persons": sorted(list(entities["persons"])),
            "organizations": sorted(list(entities["organizations"])),
            "roles": sorted(list(entities["roles"]))
        }
    }


def load_pdf(file_path: str, file_name: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF file page by page with intelligent entity extraction.
    
    Process:
    1. Extract text from all pages
    2. Perform entity extraction on full text (persons, organizations, roles)
    3. Inject primary entity into page 1 for embedding context
    4. Store complete entity metadata for retrieval attribution
    
    Args:
        file_path: Path to PDF file
        file_name: Name of the file
    
    Returns:
        List of dictionaries with text and enriched metadata
    """
    try:
        reader = PdfReader(file_path)
        documents = []
        pdf_metadata = reader.metadata or {}
        pdf_author = pdf_metadata.get('/Author') or pdf_metadata.get('/author') or "Unknown"
        pdf_title = pdf_metadata.get('/Title') or pdf_metadata.get('/title') or file_name
        
        # Extract full text for entity extraction
        full_text = ""
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n"
        
        # Perform intelligent entity extraction
        entity_data = extract_entities(full_text)
        primary_entity = entity_data["primary_entity"]
        if primary_entity == "Unknown" and pdf_author != "Unknown":
            primary_entity = pdf_author  # Fallback to PDF metadata if available
        
        logger.info(f"📄 {file_name} | Primary Entity: {primary_entity} | Organizations: {entity_data['entities']['organizations']}")
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if page_num == 1:
                # Inject primary entity into page 1 text for embedding context
                # This ensures the embedding captures the entity association
                entity_header = f"SUBJECT: {primary_entity}\n"
                
                metadata_lines = [entity_header]
                if pdf_title and pdf_title != file_name:
                    metadata_lines.append(f"DOCUMENT: {pdf_title}")
                if pdf_author and pdf_author != "Unknown":
                    metadata_lines.append(f"SOURCE: {pdf_author}")

                text = "\n".join(metadata_lines) + "\n\n" + text
            
            if text.strip():  # Only add non-empty pages
                documents.append({
                    "text": text,
                    "metadata": {
                        "file_name": file_name,
                        "page_number": page_num,
                        "total_pages": len(reader.pages),
                        "pdf_author": pdf_author,
                        "pdf_title": pdf_title,
                        # Entity extraction results
                        "primary_entity": primary_entity,
                        "entities": entity_data["entities"],  # {persons, organizations, roles}
                        "entity_persons": entity_data["entities"]["persons"],
                        "entity_organizations": entity_data["entities"]["organizations"],
                        "entity_roles": entity_data["entities"]["roles"]
                    }
                })
        
        logger.info(f"✓ Extracted {len(documents)} pages from {file_name}")
        return documents
    
    except Exception as e:
        logger.error(f"Error loading PDF {file_name}: {str(e)}")
        raise Exception(f"Failed to load PDF: {str(e)}")


def load_txt(file_path: str, file_name: str) -> List[Dict[str, any]]:
    """
    Load text from TXT file with entity extraction.
    
    Args:
        file_path: Path to TXT file
        file_name: Name of the file
    
    Returns:
        List with single dictionary containing text and enriched metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract entities from content
        entity_data = extract_entities(text)
        primary_entity = entity_data["primary_entity"]
        
        # Inject primary entity into text for embedding
        entity_header = f"SUBJECT: {primary_entity}\n"
        enriched_text = entity_header + "\n" + text
        
        logger.info(f"📄 {file_name} | Primary Entity: {primary_entity}")
        
        documents = [{
            "text": enriched_text,
            "metadata": {
                "file_name": file_name,
                "page_number": 1,
                "total_pages": 1,
                # Entity extraction results
                "primary_entity": primary_entity,
                "entities": entity_data["entities"],
                "entity_persons": entity_data["entities"]["persons"],
                "entity_organizations": entity_data["entities"]["organizations"],
                "entity_roles": entity_data["entities"]["roles"]
            }
        }]
        
        logger.info(f"✓ Loaded text file {file_name}")
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
