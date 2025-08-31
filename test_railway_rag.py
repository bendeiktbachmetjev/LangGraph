#!/usr/bin/env python3
"""
Test RAG functionality on Railway with detailed logging.
"""

import requests
import json
import time

def test_railway_rag():
    """Test RAG functionality on Railway."""
    base_url = "https://spotted-mom-production.up.railway.app"
    
    print("🚀 Testing RAG on Railway")
    print("=" * 50)
    
    # Test 1: Check debug endpoint
    print("\n1. Checking Railway debug info...")
    try:
        response = requests.get(f"{base_url}/api/rag/debug")
        if response.status_code == 200:
            debug_info = response.json()
            print(f"   ✅ Debug endpoint working")
            print(f"   RAG enabled: {debug_info.get('rag_enabled')}")
            print(f"   Index path: {debug_info.get('index_path')}")
            print(f"   Index files: {list(debug_info.get('index_files', {}).keys())}")
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Test simple RAG search
    print("\n2. Testing simple RAG search...")
    try:
        payload = {
            "query": "coaching",
            "top_k": 3
        }
        
        response = requests.post(
            f"{base_url}/api/rag/test/dev",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ RAG search working")
            print(f"   Query: {result.get('query')}")
            print(f"   Total found: {result.get('total_found')}")
            print(f"   Search time: {result.get('search_time_ms', 0):.2f}ms")
            
            snippets = result.get('snippets', [])
            for i, snippet in enumerate(snippets[:3], 1):
                title = snippet.get('title', 'Unknown')
                score = snippet.get('score', 0.0)
                print(f"   Result {i}: {title} (score: {score:.3f})")
        else:
            print(f"   ❌ RAG search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test agent flow with RAG
    print("\n3. Testing agent flow with RAG...")
    try:
        # Simulate a complete user journey
        test_state = {
            "session_id": "test_railway_rag",
            "user_name": "Test User",
            "user_age": 30,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "skills": ["communication", "project management"],
            "goals": ["Improve leadership skills", "Build team experience"]
        }
        
        # Test retrieve_reg node directly
        payload = {
            "query": "coaching techniques for goals: Improve leadership skills Build team experience",
            "top_k": 5
        }
        
        response = requests.post(
            f"{base_url}/api/rag/test/dev",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Agent RAG query working")
            print(f"   Found {result.get('total_found')} relevant chunks")
            
            snippets = result.get('snippets', [])
            if snippets:
                print(f"   Top result: {snippets[0].get('title', 'Unknown')} (score: {snippets[0].get('score', 0.0):.3f})")
            else:
                print(f"   ⚠️  No relevant chunks found")
        else:
            print(f"   ❌ Agent RAG query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test different queries
    print("\n4. Testing different queries...")
    test_queries = [
        "leadership development",
        "team management",
        "communication skills",
        "goal setting"
    ]
    
    for query in test_queries:
        try:
            payload = {"query": query, "top_k": 2}
            response = requests.post(
                f"{base_url}/api/rag/test/dev",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                snippets = result.get('snippets', [])
                if snippets:
                    top_score = snippets[0].get('score', 0.0)
                    print(f"   '{query}': {len(snippets)} results, top score: {top_score:.3f}")
                else:
                    print(f"   '{query}': No results")
            else:
                print(f"   '{query}': Failed ({response.status_code})")
        except Exception as e:
            print(f"   '{query}': Error - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Railway RAG test completed!")

if __name__ == "__main__":
    test_railway_rag()
