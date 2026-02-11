"""
Quick test script to verify RAG dependencies and pipeline.
"""

def test_imports():
    """Test that all RAG dependencies can be imported."""
    try:
        import chromadb
        print("✓ chromadb imported")
        
        import sentence_transformers
        print("✓ sentence_transformers imported")
        
        import pypdf
        print("✓ pypdf imported")
        
        print("\n✓ All RAG dependencies are installed and working!")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_rag_modules():
    """Test that all RAG modules can be imported."""
    try:
        from rag import loader, chunker, embedder, vectordb, retriever, generator, pipeline
        print("✓ All RAG modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ RAG module import failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing RAG Setup...")
    print("=" * 50)
    
    if test_imports():
        print("\n" + "=" * 50)
        test_rag_modules()
        print("=" * 50)
        print("\n✓ RAG system is ready!")
    else:
        print("\n✗ Please install dependencies: pip3 install --user chromadb sentence-transformers pypdf --break-system-packages")
