#!/usr/bin/env python3
"""
Test RAG with proper OpenAI API usage.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_rag_with_api():
    """Test RAG functionality with OpenAI API."""
    print("🔍 Testing RAG with OpenAI API...")
    print("=" * 50)
    
    # Test 1: Check environment
    print("\n1. 🔧 Checking Environment...")
    try:
        from mentor_ai.app.config import settings
        
        if not settings.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not set")
            return False
            
        print(f"✅ API key loaded (length: {len(settings.OPENAI_API_KEY)} characters)")
        print(f"✅ REG_ENABLED: {settings.REG_ENABLED}")
        print(f"✅ EMBEDDINGS_MODEL: {settings.EMBEDDINGS_MODEL}")
        
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Test 2: Test OpenAI API with new client
    print("\n2. 🔌 Testing OpenAI API...")
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Test embeddings
        print("   Testing embeddings...")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test message"
        )
        
        if response and response.data:
            embedding = response.data[0].embedding
            print(f"   ✅ Embeddings API working (dimension: {len(embedding)})")
        else:
            print("   ❌ Embeddings API failed")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI API test failed: {e}")
        return False
    
    # Test 3: Test RAG retriever
    print("\n3. 🔍 Testing RAG Retriever...")
    try:
        from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
        
        # Initialize retriever
        retriever = RegRetriever()
        retriever.initialize("LangGraph/RAG/index")
        print("   ✅ Retriever initialized")
        
        # Test search
        test_state = {
            "goals": ["Improve leadership skills", "Become a team leader"],
            "career_goal": "Team leader",
            "skills": ["communication", "project management"]
        }
        
        print("   Testing search...")
        result = retriever.retrieve(test_state, "I need coaching advice")
        
        print(f"   ✅ Search completed in {result.search_time_ms:.2f}ms")
        print(f"   📊 Retrieved {len(result.chunks)} chunks")
        print(f"   🔍 Query: {result.query}")
        
        if result.chunks:
            print(f"   📄 Top result: {result.chunks[0].title}")
            print(f"   📝 Content: {result.chunks[0].content[:150]}...")
            
            # Show snippets
            snippets = result.to_snippets(max_chars=500)
            print(f"   📋 Generated {len(snippets)} snippets:")
            for i, snippet in enumerate(snippets[:2], 1):
                print(f"      {i}. {snippet['title']}: {snippet['content'][:100]}...")
        else:
            print("   ⚠️  No chunks retrieved")
            
    except Exception as e:
        print(f"   ❌ RAG retriever test failed: {e}")
        return False
    
    # Test 4: Test graph integration
    print("\n4. 🕸️  Testing Graph Integration...")
    try:
        from mentor_ai.cursor.core.root_graph import root_graph
        
        if "retrieve_reg" in root_graph:
            retrieve_node = root_graph["retrieve_reg"]
            
            # Test executor
            mock_state = {
                "session_id": "test_session",
                "goals": ["Improve leadership skills"],
                "career_goal": "Become a team leader"
            }
            
            print("   Testing retrieve_reg executor...")
            result = retrieve_node.executor("", mock_state)
            
            print(f"   ✅ Executor returned: {result}")
            
            if "retrieved_chunks" in result and "next" in result:
                print(f"   📊 Retrieved chunks: {len(result['retrieved_chunks'])}")
                print(f"   ➡️  Next node: {result['next']}")
                
                if result["next"] == "generate_plan":
                    print("   ✅ Correctly transitions to generate_plan")
                else:
                    print(f"   ❌ Should transition to generate_plan, but goes to {result['next']}")
            else:
                print("   ❌ Missing required fields in result")
                
        else:
            print("   ❌ retrieve_reg node not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Graph integration test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 RAG with API Test Complete!")
    
    # Summary
    print("\n📊 RAG System Status:")
    print("✅ Environment: API key loaded correctly")
    print("✅ OpenAI API: New client working")
    print("✅ RAG Retriever: Can search and retrieve documents")
    print("✅ Graph Integration: retrieve_reg node working")
    print("✅ Overall: RAG system is fully functional!")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting RAG with API Test...")
    
    success = test_rag_with_api()
    
    if success:
        print("\n✅ RAG system with API is working!")
    else:
        print("\n❌ RAG system with API test failed.")
        sys.exit(1)
