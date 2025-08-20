#!/usr/bin/env python3
"""
Test script for RAG system functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
from mentor_ai.cursor.modules.retrieval.simple_store import SimpleVectorStore
from mentor_ai.app.config import settings

def test_rag_system():
    """Test the RAG system functionality."""
    print("🧪 Testing RAG System...")
    
    # Test 1: Check if index exists
    print("\n1. Checking index files...")
    index_path = Path(settings.RAG_INDEX_PATH)
    if index_path.exists():
        print(f"✅ Index directory exists: {index_path}")
        
        # Check for required files
        chunks_file = index_path / "chunks.json"
        embeddings_file = index_path / "embeddings.json"
        metadata_file = index_path / "metadata.json"
        
        if chunks_file.exists():
            with open(chunks_file, 'r') as f:
                chunks_data = json.load(f)
            print(f"✅ Chunks file exists with {len(chunks_data)} documents")
        else:
            print("❌ Chunks file missing")
            
        if embeddings_file.exists():
            with open(embeddings_file, 'r') as f:
                embeddings_data = json.load(f)
            print(f"✅ Embeddings file exists with {len(embeddings_data)} vectors")
        else:
            print("❌ Embeddings file missing")
            
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            print(f"✅ Metadata file exists: {metadata}")
        else:
            print("❌ Metadata file missing")
    else:
        print(f"❌ Index directory missing: {index_path}")
        return False
    
    # Test 2: Test vector store loading
    print("\n2. Testing vector store loading...")
    try:
        vector_store = SimpleVectorStore()
        vector_store.load(settings.RAG_INDEX_PATH)
        stats = vector_store.get_stats()
        print(f"✅ Vector store loaded successfully: {stats}")
    except Exception as e:
        print(f"❌ Failed to load vector store: {e}")
        return False
    
    # Test 3: Test retriever initialization
    print("\n3. Testing retriever initialization...")
    try:
        retriever = RegRetriever()
        retriever.initialize(settings.RAG_INDEX_PATH)
        print("✅ Retriever initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize retriever: {e}")
        return False
    
    # Test 4: Test retrieval with sample queries
    print("\n4. Testing retrieval with sample queries...")
    
    test_cases = [
        {
            "name": "Career coaching",
            "state": {
                "goal_type": "career_improve",
                "career_goal": "Become a team leader",
                "skills": ["communication", "project management"],
                "goals": ["Improve leadership skills", "Build team management experience"]
            }
        },
        {
            "name": "Personal growth",
            "state": {
                "goal_type": "self_growth",
                "growth_area": "confidence",
                "passions": ["public speaking", "personal development"],
                "goals": ["Build self-confidence", "Overcome fear of public speaking"]
            }
        },
        {
            "name": "Goal setting",
            "state": {
                "goal_type": "no_goal",
                "lost_skills": "I don't know what I want to achieve",
                "goals": ["Find my purpose", "Set clear life goals"]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        try:
            result = retriever.retrieve(test_case['state'], "I need help with my goals")
            print(f"   ✅ Retrieved {len(result.chunks)} chunks")
            print(f"   📊 Search time: {result.search_time_ms:.2f}ms")
            
            if result.chunks:
                print(f"   📄 Sample chunk: {result.chunks[0].title[:50]}...")
                print(f"   📝 Content preview: {result.chunks[0].content[:100]}...")
            else:
                print("   ⚠️  No chunks retrieved")
                
        except Exception as e:
            print(f"   ❌ Retrieval failed: {e}")
    
    # Test 5: Test snippets generation
    print("\n5. Testing snippets generation...")
    try:
        # Create a sample retrieval result
        from mentor_ai.cursor.modules.retrieval.schemas import RetrievalResult, DocumentChunk
        
        sample_chunks = [
            DocumentChunk(
                id="test_1",
                content="This is a sample coaching technique for improving leadership skills. It involves active listening and clear communication.",
                title="Leadership Coaching",
                source="test.pdf",
                chunk_index=0,
                start_char=0,
                end_char=100
            ),
            DocumentChunk(
                id="test_2", 
                content="Goal setting is crucial for personal development. Start with small, achievable goals and gradually increase complexity.",
                title="Goal Setting Guide",
                source="test.pdf",
                chunk_index=1,
                start_char=0,
                end_char=100
            )
        ]
        
        result = RetrievalResult(
            chunks=sample_chunks,
            query="test query",
            total_results=2,
            search_time_ms=10.0
        )
        
        snippets = result.to_snippets(max_chars=500)
        print(f"✅ Generated {len(snippets)} snippets")
        for i, snippet in enumerate(snippets, 1):
            print(f"   Snippet {i}: {snippet['title']} - {snippet['content'][:50]}...")
            
    except Exception as e:
        print(f"❌ Snippets generation failed: {e}")
    
    print("\n🎉 RAG System Test Complete!")
    return True

def test_configuration():
    """Test RAG configuration."""
    print("\n🔧 Testing RAG Configuration...")
    
    print(f"REG_ENABLED: {settings.REG_ENABLED}")
    print(f"EMBEDDINGS_PROVIDER: {settings.EMBEDDINGS_PROVIDER}")
    print(f"EMBEDDINGS_MODEL: {settings.EMBEDDINGS_MODEL}")
    print(f"RAG_INDEX_PATH: {settings.RAG_INDEX_PATH}")
    print(f"RAG_CORPUS_PATH: {settings.RAG_CORPUS_PATH}")
    print(f"RETRIEVE_TOP_K: {settings.RETRIEVE_TOP_K}")
    print(f"MAX_CHARS_PER_CHUNK: {settings.MAX_CHARS_PER_CHUNK}")
    print(f"MAX_CONTEXT_CHARS: {settings.MAX_CONTEXT_CHARS}")

if __name__ == "__main__":
    print("🚀 Starting RAG System Tests...")
    
    # Test configuration
    test_configuration()
    
    # Test RAG functionality
    success = test_rag_system()
    
    if success:
        print("\n✅ All tests passed! RAG system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
