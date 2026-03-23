# Entity Extraction in RAG Pipeline

## Overview
The enhanced RAG system now performs intelligent entity extraction from document content to prevent misattribution errors. Instead of relying on weak metadata (filenames, missing PDF metadata), the system dynamically extracts key entities from text.

## Architecture

### 1. **Loader (rag/loader.py)**
- **Function**: `extract_entities(text: str) → Dict`
- **Extracts**:
  - Person names (e.g., "Gopidi Rishith Reddy")
  - Organizations (e.g., "Google", "IIT Delhi")
  - Roles/Titles (e.g., "Software Engineer", "Student")
- **Returns**: 
  ```python
  {
    "primary_entity": "Gopidi Rishith Reddy",
    "entities": {
      "persons": ["Gopidi Rishith Reddy", ...],
      "organizations": ["Google", ...],
      "roles": ["Software Engineer", ...]
    }
  }
  ```

### 2. **Extraction Strategy**
1. Scans first 50 lines (document header)
2. Uses heuristics:
   - Title-case phrases (2-4 words) → person names
   - Keywords like "engineer", "manager", "student" → roles
   - Organization indicators (company, university, corporation) → orgs
3. Filters noise:
   - Skips emails, URLs, phone numbers
   - Ignores common resume keywords
4. Ranks by position (earlier = more likely primary subject)

### 3. **Data Flow Through Pipeline**

```
PDF/TXT File
    ↓
[loader.py] extract_entities() 
    ↓
Metadata enriched with:
  - primary_entity
  - entities (persons, organizations, roles)
  - entity_persons, entity_organizations, entity_roles
    ↓
[chunker.py] chunk_documents() - Preserves all entity metadata
    ↓
[embedder.py] embed_texts() - Entity info in chunk text
    ↓
[vectordb.py] add_documents() - Stores metadata
    ↓
[retriever.py] query_documents() - Retrieves with entity context
    ↓
[retriever.py] format_retrieved_context() - Displays entities prominently
    ↓
[generator.py] LLM receives clear attribution context
```

### 4. **Key Metadata Fields**

Each chunk now includes:
```python
metadata = {
    "file_name": "resume_job.pdf",
    "page_number": 1,
    "total_pages": 5,
    "primary_entity": "Gopidi Rishith Reddy",  # PRIMARY SUBJECT
    "entities": {
        "persons": ["Gopidi Rishith Reddy"],
        "organizations": ["Google", "IIT"],
        "roles": ["Software Engineer"]
    },
    "entity_persons": ["Gopidi Rishith Reddy"],
    "entity_organizations": ["Google", "IIT"],
    "entity_roles": ["Software Engineer"]
}
```

### 5. **Context Formatting (Retriever)**

Retrieved context now displays:
```
================================================================================
PRIMARY SUBJECT: Gopidi Rishith Reddy
PEOPLE: Gopidi Rishith Reddy
ORGANIZATIONS: Google, IIT
SOURCE: resume_job.pdf
TITLE: Resume
================================================================================

[Page: 1, Section: Experience]
Chunk text with relevant information...
```

## Usage Example

### Query
**Q**: "Who won the Map and App Hackathon?"

### Before (Incorrect)
> "resume_job.pdf won the Map and App Hackathon"

### After (Correct)
> "Gopidi Rishith Reddy won the Map and App Hackathon" 
> (Primary Subject: Gopidi Rishith Reddy, Document: resume_job.pdf)

## Implementation Details

### Heuristic Rules

1. **Person Name Detection**
   - 2-4 words in title case
   - ≥75% alphabetic characters (allows hyphens, apostrophes)
   - First occurrence in document header

2. **Organization Detection**
   - Contains keywords: company, institute, university, corporation, etc.
   - OR: All-caps phrases (≤3 words)
   - Early document position

3. **Role Detection**
   - Contains keywords: engineer, developer, manager, student, etc.
   - Extracted as full phrase (e.g., "Software Engineer", not just "Engineer")

### Fallback Strategy

```python
if primary_entity == "Unknown":
    # Use PDF metadata if available
    primary_entity = pdf_author
    
if primary_entity == "Unknown":
    # Use filename as last resort
    primary_entity = file_name
```

## Testing

1. **Clear Old Data**
   ```bash
   rm -rf backend/data/chromadb/*
   ```

2. **Upload Resumes**
   - Upload 3 resume PDFs through the UI

3. **Test Queries**
   - "Who won the Map and App Hackathon?" → Should show person name
   - "Who studies at IIT?" → Should show organization and person
   - "What are the technical skills?" → Should maintain proper attribution

## Benefits

✅ **Accurate Attribution**: No more filename confusion  
✅ **Entity-Aware Retrieval**: Filters relevant documents by entity  
✅ **Robust Pipeline**: Works with or without PDF metadata  
✅ **Embedding Context**: Entity info in embeddings improves semantic search  
✅ **Non-Domain-Specific**: Works with any document type, not just resumes  

## Future Enhancements

- NER (Named Entity Recognition) using spaCy or transformers
- Entity linking to external knowledge bases
- Multi-language support
- Industry-specific entity patterns
