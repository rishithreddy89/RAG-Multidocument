# Chunking Strategy: Semantic Paragraph-Based with LangChain

## Overview

The Multi-Document Reasoning Engine now uses a **semantic paragraph-based chunking strategy** powered by LangChain's `RecursiveCharacterTextSplitter`, replacing the previous character-based sliding window approach.

## Configuration

### Current Settings
- **Chunk Size**: 400 tokens (~1600 characters)
- **Overlap**: 80 tokens (~320 characters)
- **Separator Priority**:
  1. `\n\n` - Paragraph breaks (highest priority)
  2. `\n` - Line breaks
  3. `. ` - Sentence endings
  4. `! ` - Exclamations
  5. `? ` - Questions
  6. `; ` - Semicolons
  7. `, ` - Commas
  8. ` ` - Spaces
  9. `` - Character-level (fallback)

## Comparison: Old vs New

### Previous Strategy (Character-Based)
```
Chunk Size: 700 characters
Overlap: 150 characters
Method: Fixed sliding window with basic sentence detection
Limitations:
- Could break mid-sentence
- No semantic awareness
- Fixed character count regardless of content structure
- Limited boundary detection (only periods and newlines)
```

### New Strategy (Semantic Paragraph-Based)
```
Chunk Size: 400 tokens (~1600 characters)
Overlap: 80 tokens (~320 characters)
Method: Recursive hierarchical splitting with semantic boundaries
Benefits:
- Preserves semantic meaning
- Respects paragraph and section boundaries
- Graceful fallback through separator hierarchy
- Better suited for multi-document reasoning
- Token-based sizing aligns with LLM context windows
```

## Key Improvements

### 1. **Semantic Coherence**
Chunks now preserve logical units of meaning by prioritizing paragraph breaks and sentence boundaries, improving retrieval relevance.

### 2. **Better Cross-Document Reasoning**
Larger, semantically complete chunks provide more context for the LLM to reason across multiple documents.

### 3. **Token-Based Sizing**
Using token counts instead of characters aligns better with LLM context windows and embedding models.

### 4. **Hierarchical Splitting**
The recursive approach tries multiple separators in order, ensuring optimal splits without breaking semantic units.

### 5. **Enhanced Metadata**
Each chunk includes:
- `document_name`: Source document identifier
- `page_number`: Original page (if applicable)
- `chunk_index`: Position within document
- `total_chunks`: Total chunks from source
- `chunk_size_tokens`: Approximate token count
- `document_id`: Unique document identifier

## Usage

### Basic Chunking
```python
from rag.chunker import chunk_text

text = "Your document text here..."
chunks = chunk_text(text, chunk_size=400, overlap=80)
```

### Document Chunking with Metadata
```python
from rag.chunker import chunk_documents

documents = [
    {
        "text": "Document content...",
        "metadata": {
            "file_name": "example.pdf",
            "page_number": 1,
            "document_id": "doc_123"
        }
    }
]

chunks = chunk_documents(documents, chunk_size=400, overlap=80)
```

## Integration

The new chunking strategy is **backward compatible** with the existing RAG pipeline. No changes required to:
- `pipeline.py`
- `embedder.py`
- `retriever.py`
- `vectordb.py`

The chunked output maintains the same dictionary structure:
```python
{
    "text": "chunk content...",
    "metadata": {...}
}
```

## Performance Considerations

### Memory
LangChain adds minimal overhead (~5MB) compared to the benefits of improved chunking quality.

### Speed
The recursive splitting is efficient and processes documents at similar speeds to the previous implementation.

### Quality
Early testing shows improved retrieval relevance and better context preservation for multi-document questions.

## Customization

To adjust chunking parameters, modify the constants in `chunker.py`:

```python
# Configuration - Token-based chunking
CHUNK_SIZE = 400  # tokens (adjust for your use case)
CHUNK_OVERLAP = 80  # tokens (typically 15-25% of chunk size)
CHARS_PER_TOKEN = 4  # approximate characters per token
```

## Testing

Run the test suite to verify chunking behavior:
```bash
python test_chunker.py
```

## Future Enhancements

Potential improvements for consideration:
1. **Token Counting**: Use actual tokenizer (tiktoken) instead of character approximation
2. **Language-Specific Splitters**: Leverage LangChain's language-specific splitters for code or structured documents
3. **Semantic Chunking**: Explore LangChain's experimental SemanticChunker for embedding-based splitting
4. **Adaptive Chunk Sizes**: Dynamically adjust chunk size based on document type or content density

## References

- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [RAG Best Practices](https://www.pinecone.io/learn/chunking-strategies/)
- [Token-Based Chunking](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5)
