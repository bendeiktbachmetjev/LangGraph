#!/usr/bin/env python3
"""
Local test for RAG functionality.
"""

import os
import sys
from pathlib import Path

# Add the mentor_ai directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "mentor_ai"))

# Set environment variables for RAG
os.environ["REG_ENABLED"] = "true"
os.environ["EMBEDDINGS_PROVIDER"] = "openai"
os.environ["EMBEDDINGS_MODEL"] = "text-embedding-3-small"

try:
    from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
    from mentor_ai.app.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_rag_search():
    """Test RAG search functionality."""
    print("🚀 Testing RAG search locally...")
    
    try:
        # Initialize retriever
        retriever = RegRetriever()
        retriever.initialize(settings.RAG_INDEX_PATH)
        
        # Test search
        query = "leadership"
        results = retriever.search(query, top_k=3)
        
        print(f"✅ Search completed for query: '{query}'")
        print(f"📄 Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.get('title', 'Untitled')}")
            print(f"Score: {result.get('score', 0.0):.4f}")
            print(f"Source: {result.get('source', 'Unknown')}")
            print(f"Content: {result.get('content', '')[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_search()
    sys.exit(0 if success else 1)

