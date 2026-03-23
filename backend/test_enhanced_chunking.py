"""
Test script for enhanced chunking with document_name, page_number, and section_title
"""

from rag.chunker import chunk_documents
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)

# Sample document with clear sections
sample_text_page1 = """
INTRODUCTION

Natural Language Processing (NLP) is a subfield of artificial intelligence that focuses on the interaction between computers and humans through natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a manner that is valuable.

Recent advances in deep learning have transformed the field dramatically. Modern approaches leverage transformer architectures and attention mechanisms to achieve unprecedented performance on language understanding tasks.

METHODOLOGY

Machine learning has revolutionized NLP in recent years. Deep learning models, particularly transformer architectures like BERT and GPT, have achieved remarkable performance on various NLP tasks. These models can understand context, semantics, and even generate human-like text.

Our approach combines retrieval-augmented generation with vector databases for improved accuracy.
"""

sample_text_page2 = """
RESULTS

Retrieval-Augmented Generation (RAG) combines the power of large language models with information retrieval systems. This approach allows models to access external knowledge bases, improving accuracy and reducing hallucinations. RAG systems are particularly useful for question-answering and knowledge-intensive tasks.

Experimental results show a 40% improvement in accuracy compared to baseline methods.

CONCLUSION

The future of NLP looks promising with continuous advancements in model architectures, training techniques, and applications across industries. From healthcare to finance, NLP is transforming how we interact with technology and process information.
"""


def test_enhanced_chunking():
    """Test the enhanced chunking with document_name, page_number, and section_title"""
    
    print("=" * 80)
    print("Testing Enhanced Chunking with Metadata Enrichment")
    print("=" * 80)
    
    # Simulate documents from loader (dictionary format)
    documents = [
        {
            "text": sample_text_page1,
            "metadata": {
                "file_name": "research_paper.pdf",
                "page_number": 1,
                "total_pages": 2
            }
        },
        {
            "text": sample_text_page2,
            "metadata": {
                "file_name": "research_paper.pdf",
                "page_number": 2,
                "total_pages": 2
            }
        }
    ]
    
    # Chunk documents
    print(f"\n📄 Processing {len(documents)} pages from 'research_paper.pdf'...")
    chunks = chunk_documents(documents, chunk_size=150, overlap=30)
    
    print(f"\n✓ Generated {len(chunks)} chunks\n")
    
    # Display all chunks with enhanced metadata
    for i, chunk in enumerate(chunks, 1):
        print(f"{'=' * 80}")
        print(f"Chunk {i}/{len(chunks)}")
        print(f"{'=' * 80}")
        
        # Display metadata
        print(f"\n📋 Metadata:")
        print(f"  • Document Name: {chunk.metadata.get('document_name')}")
        print(f"  • Page Number: {chunk.metadata.get('page_number')}")
        print(f"  • Section Title: {chunk.metadata.get('section_title')}")
        print(f"  • Chunk Index: {chunk.metadata.get('chunk_index')}")
        print(f"  • Total Chunks: {chunk.metadata.get('total_chunks')}")
        print(f"  • Chunk Size (tokens): {chunk.metadata.get('chunk_size_tokens')}")
        
        # Display content preview
        print(f"\n📝 Content ({len(chunk.page_content)} chars):")
        print("-" * 80)
        preview = chunk.page_content[:300]
        print(preview + "..." if len(chunk.page_content) > 300 else preview)
        print()
    
    # Verify all required metadata fields are present
    print("=" * 80)
    print("Metadata Verification")
    print("=" * 80)
    
    required_fields = [
        "document_name",
        "page_number", 
        "section_title",
        "chunk_index",
        "total_chunks",
        "chunk_size_tokens"
    ]
    
    all_passed = True
    for i, chunk in enumerate(chunks, 1):
        missing = [field for field in required_fields if field not in chunk.metadata]
        if missing:
            print(f"❌ Chunk {i}: Missing fields: {missing}")
            all_passed = False
        else:
            print(f"✓ Chunk {i}: All required metadata fields present")
    
    if all_passed:
        print(f"\n{'=' * 80}")
        print("✅ All tests passed! Enhanced metadata enrichment working correctly.")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print("❌ Some tests failed. Check metadata fields.")
        print(f"{'=' * 80}")
    
    # Display summary statistics
    print(f"\n📊 Summary Statistics:")
    print(f"  • Total chunks created: {len(chunks)}")
    print(f"  • Chunks from page 1: {sum(1 for c in chunks if c.metadata['page_number'] == 1)}")
    print(f"  • Chunks from page 2: {sum(1 for c in chunks if c.metadata['page_number'] == 2)}")
    
    sections = {}
    for chunk in chunks:
        section = chunk.metadata['section_title']
        sections[section] = sections.get(section, 0) + 1
    
    print(f"  • Sections detected: {len(sections)}")
    for section, count in sections.items():
        print(f"    - {section}: {count} chunks")
    
    return chunks


if __name__ == "__main__":
    chunks = test_enhanced_chunking()
