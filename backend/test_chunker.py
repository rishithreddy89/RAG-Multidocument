"""
Test script for the new semantic chunking strategy
"""

from rag.chunker import chunk_documents, chunk_text
import logging

logging.basicConfig(level=logging.INFO)

# Sample document with clear paragraphs
sample_text = """
Natural Language Processing (NLP) is a subfield of artificial intelligence that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a manner that is valuable.

Machine learning has revolutionized NLP in recent years. Deep learning models, particularly transformer architectures like BERT and GPT, have achieved remarkable performance on various NLP tasks. These models can understand context, semantics, and even generate human-like text.

Retrieval-Augmented Generation (RAG) combines the power of large language models with information retrieval systems. This approach allows models to access external knowledge bases, improving accuracy and reducing hallucinations. RAG systems are particularly useful for question-answering and knowledge-intensive tasks.

The future of NLP looks promising with continuous advancements in model architectures, training techniques, and applications across industries. From healthcare to finance, NLP is transforming how we interact with technology and process information.
"""

def test_semantic_chunking():
    """Test the new semantic chunking strategy"""
    
    print("=" * 80)
    print("Testing Semantic Paragraph-Based Chunking with LangChain")
    print("=" * 80)
    
    # Test 1: Single text chunking
    print("\n[Test 1] Chunking single text:")
    chunks = chunk_text(sample_text, chunk_size=200, overlap=50)
    
    print(f"Generated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk)} chars, ~{len(chunk)//4} tokens):")
        print("-" * 60)
        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    
    # Test 2: Document chunking with metadata
    print("\n" + "=" * 80)
    print("[Test 2] Chunking documents with metadata:")
    
    documents = [
        {
            "text": sample_text,
            "metadata": {
                "file_name": "nlp_guide.txt",
                "page_number": 1,
                "document_id": "doc_001"
            }
        }
    ]
    
    chunked_docs = chunk_documents(documents, chunk_size=300, overlap=80)
    
    print(f"\nGenerated {len(chunked_docs)} document chunks")
    
    for i, doc in enumerate(chunked_docs, 1):
        print(f"\nDocument Chunk {i}:")
        print("-" * 60)
        print(f"Text length: {len(doc['text'])} chars")
        print(f"Metadata: {doc['metadata']}")
        print(f"Preview: {doc['text'][:150]}...")
    
    # Test 3: Verify metadata preservation
    print("\n" + "=" * 80)
    print("[Test 3] Metadata verification:")
    
    for chunk in chunked_docs:
        meta = chunk['metadata']
        assert 'file_name' in meta
        assert 'chunk_index' in meta
        assert 'total_chunks' in meta
        assert 'document_name' in meta
        assert meta['total_chunks'] == len(chunked_docs)
        print(f"✓ Chunk {meta['chunk_index']}: All metadata fields present")
    
    print("\n" + "=" * 80)
    print("All tests passed! ✓")
    print("=" * 80)


if __name__ == "__main__":
    test_semantic_chunking()
