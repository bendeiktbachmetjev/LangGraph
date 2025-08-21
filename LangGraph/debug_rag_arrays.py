#!/usr/bin/env python3
"""
Debug script to check RAG array dimensions and fix the issue.
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mentor_ai.cursor.modules.retrieval.simple_store import SimpleVectorStore
from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever

def debug_rag_arrays():
    """Debug RAG array dimensions and shapes."""
    print("🔍 Debugging RAG Array Dimensions")
    print("=" * 50)
    
    # Test 1: Check SimpleVectorStore directly
    print("\n1. Testing SimpleVectorStore...")
    try:
        store = SimpleVectorStore()
        store.load("RAG/index")
        
        print(f"   Total chunks: {len(store.chunks)}")
        print(f"   Total embeddings: {len(store.embeddings)}")
        
        if store.embeddings:
            print(f"   First embedding length: {len(store.embeddings[0])}")
            print(f"   Embeddings array shape: {np.array(store.embeddings).shape}")
            
            # Check if _embeddings_array is set
            if store._embeddings_array is not None:
                print(f"   _embeddings_array shape: {store._embeddings_array.shape}")
            else:
                print("   _embeddings_array is None")
        
        # Test search with a simple query
        test_embedding = [0.1] * 1536  # Simple test embedding
        print(f"\n   Testing search with embedding length: {len(test_embedding)}")
        
        results = store.search(test_embedding, top_k=3)
        print(f"   Search returned {len(results)} results")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Check RegRetriever
    print("\n2. Testing RegRetriever...")
    try:
        retriever = RegRetriever()
        retriever.initialize("RAG/index")
        
        # Test simple search
        results = retriever.search("coaching", top_k=3)
        print(f"   Search returned {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"   Result {i+1}: {result.get('title', 'Unknown')} (score: {result.get('score', 0.0):.3f})")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check embeddings file directly
    print("\n3. Checking embeddings file...")
    try:
        embeddings_file = Path("RAG/index/embeddings.npy")
        if embeddings_file.exists():
            embeddings = np.load(embeddings_file)
            print(f"   Embeddings file shape: {embeddings.shape}")
            print(f"   Embeddings file dtype: {embeddings.dtype}")
            
            # Check if it's 1D or 2D
            if len(embeddings.shape) == 1:
                print("   ⚠️  Embeddings is 1D - this might be the problem!")
                print("   Expected shape: (num_documents, embedding_dimension)")
                print("   Actual shape: (total_elements,)")
                
                # Try to reshape it
                num_chunks = len(store.chunks) if 'store' in locals() else 372
                embedding_dim = 1536
                expected_size = num_chunks * embedding_dim
                
                if embeddings.size == expected_size:
                    print(f"   ✅ Can reshape to ({num_chunks}, {embedding_dim})")
                    reshaped = embeddings.reshape(num_chunks, embedding_dim)
                    print(f"   Reshaped shape: {reshaped.shape}")
                else:
                    print(f"   ❌ Cannot reshape: size {embeddings.size} != {expected_size}")
            else:
                print("   ✅ Embeddings has correct 2D shape")
        else:
            print("   ❌ Embeddings file not found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag_arrays()
