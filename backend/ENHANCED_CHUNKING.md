# Enhanced Chunking Pipeline with Metadata Enrichment

## Overview

The chunking pipeline now returns **LangChain Document objects** with enriched metadata including `document_name`, `page_number`, and `section_title` for improved document tracking and retrieval.

## Implementation

### Key Features

✅ **Semantic Paragraph-Based Chunking** - Uses LangChain's `RecursiveCharacterTextSplitter`  
✅ **Section Title Detection** - Automatically detects headers (INTRODUCTION, METHODOLOGY, etc.)  
✅ **Full Metadata Preservation** - Maintains all original metadata from document loader  
✅ **LangChain Document Objects** - Returns proper Document objects ready for embeddings  
✅ **Backward Compatible** - Works with existing dictionary-based document loaders  

## Chunking Configuration

```python
CHUNK_SIZE = 400  # tokens
CHUNK_OVERLAP = 80  # tokens
CHARS_PER_TOKEN = 4  # approximate conversion

# Hierarchical separators (priority order)
SEPARATORS = [
    "\n\n",  # Paragraph breaks (highest priority)
    "\n",    # Line breaks
    ". ",    # Sentence endings
    "! ",    # Exclamations
    "? ",    # Questions
    "; ",    # Semicolons
    ", ",    # Commas
    " ",     # Spaces
    ""       # Character-level (fallback)
]
```

## Enhanced Metadata Fields

Each chunk now includes:

```python
{
    "document_name": "research_paper.pdf",      # Source file name
    "page_number": 1,                           # Page where chunk originated
    "section_title": "INTRODUCTION",            # Detected section header
    "chunk_index": 0,                           # Position within document
    "total_chunks": 5,                          # Total chunks from source
    "chunk_size_tokens": 387,                   # Approximate token count
    "file_name": "research_paper.pdf",          # Original field (preserved)
    "document_id": "uuid-string"                # Added by pipeline
}
```

## Section Title Detection

The `detect_section_title()` function identifies section headers using:

1. **All-caps headers**: `INTRODUCTION`, `METHODOLOGY`, `RESULTS`
2. **Numbered sections**: `1. Introduction`, `1.1 Background`, `2.3.1 Methods`
3. **Title case headers**: Short lines (≤6 words) starting with capital letter
4. **Default**: Returns `"Unknown"` if no pattern matches

### Detection Examples

| Text | Detected Section |
|------|------------------|
| `INTRODUCTION\n\nThis paper...` | `INTRODUCTION` |
| `1. Methodology\n\nWe used...` | `Methodology` |
| `Results and Discussion\n\n...` | `Results and Discussion` |
| `The experiment showed...` | `Unknown` |

## Usage

### Basic Usage

```python
from rag.chunker import chunk_documents

# Documents from loader (dictionary format)
documents = [
    {
        "text": "INTRODUCTION\n\nNLP is...",
        "metadata": {
            "file_name": "paper.pdf",
            "page_number": 1
        }
    }
]

# Chunk documents → Returns List[Document]
chunks = chunk_documents(documents, chunk_size=400, overlap=80)

# Access chunk data
for chunk in chunks:
    print(f"Page {chunk.metadata['page_number']}")
    print(f"Section: {chunk.metadata['section_title']}")
    print(f"Content: {chunk.page_content[:100]}...")
```

### Integration with Pipeline

```python
from rag.pipeline import process_document

# Process document through full pipeline
result = await process_document(
    file_path="/path/to/document.pdf",
    file_name="document.pdf",
    document_id="doc_123"
)

# Pipeline automatically:
# 1. Loads document
# 2. Chunks with enhanced metadata
# 3. Generates embeddings
# 4. Stores in ChromaDB
```

### Extracting Data for Vector Store

```python
# After chunking, extract for embeddings
texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

# Generate embeddings
embeddings = embed_texts(texts)

# Store in vector database
add_documents(texts, embeddings, metadatas)
```

## Output Format

### Before (Dictionary Format)
```python
{
    "text": "chunk content...",
    "metadata": {
        "file_name": "paper.pdf",
        "chunk_index": 0
    }
}
```

### After (LangChain Document)
```python
Document(
    page_content="chunk content...",
    metadata={
        "file_name": "paper.pdf",
        "document_name": "paper.pdf",
        "page_number": 1,
        "section_title": "INTRODUCTION",
        "chunk_index": 0,
        "total_chunks": 5,
        "chunk_size_tokens": 387
    }
)
```

## Testing

Run the enhanced chunking test:

```bash
cd backend
python test_enhanced_chunking.py
```

### Test Output

```
✓ Generated 4 chunks

Chunk 1/4
📋 Metadata:
  • Document Name: research_paper.pdf
  • Page Number: 1
  • Section Title: INTRODUCTION
  • Chunk Index: 0
  • Total Chunks: 2
  • Chunk Size (tokens): 134
```

## Benefits

### 1. **Better Source Attribution**
Chunks now track exact source location (file, page, section)

### 2. **Improved Retrieval Context**
Section titles help users understand context without reading full chunks

### 3. **Multi-Document Support**
Clear document_name tracking enables cross-document reasoning

### 4. **LangChain Compatible**
Returns proper Document objects ready for LangChain workflows

### 5. **Flexible Detection**
Section title detection adapts to various document formatting styles

## Implementation Details

### Function Signature

```python
def chunk_documents(
    documents: List[Dict[str, any]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Chunk documents with semantic splitting and metadata enrichment.
    
    Returns:
        List of LangChain Document objects with enhanced metadata
    """
```

### Processing Flow

```
Input: Dict[text, metadata] from document loader
    ↓
Create LangChain Document
    ↓
Split using RecursiveCharacterTextSplitter
    ↓
For each chunk:
    1. Detect section title from content
    2. Add document_name from metadata
    3. Preserve page_number from metadata
    4. Add chunk_index and total_chunks
    5. Calculate chunk_size_tokens
    ↓
Output: List[Document] with full metadata
```

## Migration Notes

### Breaking Changes

The `chunk_documents()` function now returns `List[Document]` instead of `List[Dict]`.

### Update Required

```python
# OLD
for chunk in chunks:
    text = chunk["text"]
    metadata = chunk["metadata"]

# NEW
for chunk in chunks:
    text = chunk.page_content
    metadata = chunk.metadata
```

### Pipeline Updates

The `pipeline.py` has been updated to handle LangChain Documents:

```python
# Extract data from Document objects
texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]
```

## Future Enhancements

Potential improvements:
1. **Advanced Section Detection**: Use NLP models to detect implicit sections
2. **Table/Figure Tracking**: Metadata for tables and figures within chunks
3. **Cross-Reference Detection**: Track citations and references
4. **Custom Section Patterns**: Allow user-defined section patterns
5. **Multi-Level Sections**: Support hierarchical sections (1.1, 1.1.1, etc.)

## Conclusion

The enhanced chunking pipeline provides rich metadata for improved document tracking, retrieval quality, and source attribution in the RAG system. All metadata is automatically preserved and enriched during the chunking process.
