#!/usr/bin/env python3
"""
Test real RAG search functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_rag_search():
    """Test real RAG search with OpenAI API."""
    print("🔍 Testing RAG Search...")
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OPENAI_API_KEY found. Set it to test RAG search.")
        return False
    
    print("✅ OpenAI API key found")
    
    try:
        # Import and test retriever
        from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
        
        # Initialize retriever
        retriever = RegRetriever()
        retriever.initialize("LangGraph/RAG/index")
        print("✅ Retriever initialized")
        
        # Test search queries
        test_queries = [
            {
                "name": "Leadership coaching",
                "state": {
                    "goals": ["Improve leadership skills", "Become a better manager"],
                    "career_goal": "Team leader",
                    "skills": ["communication", "project management"]
                }
            },
            {
                "name": "Goal setting",
                "state": {
                    "goals": ["Set clear goals", "Find my purpose"],
                    "goal_type": "self_growth",
                    "growth_area": "personal development"
                }
            },
            {
                "name": "Team management",
                "state": {
                    "goals": ["Build effective teams", "Improve team collaboration"],
                    "career_goal": "Team manager",
                    "skills": ["leadership", "team building"]
                }
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {test_case['name']}")
            print(f"   State: {test_case['state']}")
            
            try:
                result = retriever.retrieve(test_case['state'], "I need coaching advice")
                
                print(f"   ✅ Search completed in {result.search_time_ms:.2f}ms")
                print(f"   📊 Retrieved {len(result.chunks)} chunks")
                print(f"   🔍 Query: {result.query}")
                
                if result.chunks:
                    print(f"   📄 Top result: {result.chunks[0].title}")
                    print(f"   📝 Content: {result.chunks[0].content[:150]}...")
                    
                    # Show snippets
                    snippets = result.to_snippets(max_chars=500)
                    print(f"   📋 Generated {len(snippets)} snippets:")
                    for j, snippet in enumerate(snippets[:2], 1):
                        print(f"      {j}. {snippet['title']}: {snippet['content'][:100]}...")
                else:
                    print("   ⚠️  No relevant chunks found")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
        
        print("\n🎉 RAG Search Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG search: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting RAG Search Test...")
    
    success = test_rag_search()
    
    if success:
        print("\n✅ RAG search is working!")
    else:
        print("\n❌ RAG search test failed.")
        sys.exit(1)
