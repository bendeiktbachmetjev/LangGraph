#!/usr/bin/env python3
"""
Simple test script for RAG API endpoints
"""

import requests
import json
import time

# Use Railway URL by default, fallback to localhost for development
import os
BASE_URL = os.getenv("RAG_API_URL", "https://spotted-mom-production.up.railway.app")

def test_rag_status():
    """Test RAG status endpoint"""
    print("🔍 Testing RAG Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/rag/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_search(query, top_k=3):
    """Test RAG search endpoint"""
    print(f"\n🔍 Testing RAG Search: '{query}' (top_k={top_k})")
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "include_sources": True
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/rag/test/dev",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Total found: {data['total_found']}")
            print(f"Sources: {data['sources']}")
            print(f"API search time: {data['search_time_ms']:.2f}ms")
            
            print("\n📄 Snippets:")
            for i, snippet in enumerate(data['snippets'], 1):
                print(f"  {i}. {snippet['title']} (score: {snippet['score']:.2f})")
                print(f"     Source: {snippet['source']}")
                print(f"     Content: {snippet['content'][:100]}...")
                print()
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG API Tests")
    print(f"📍 Using API URL: {BASE_URL}")
    print("💡 To test local server: RAG_API_URL=http://localhost:8000 python test_rag_frontend.py")
    print("💡 To test Railway: RAG_API_URL=https://spotted-mom-production.up.railway.app python test_rag_frontend.py")
    print()
    
    # Test status
    if not test_rag_status():
        print("❌ Status test failed")
        return
    
    # Test various queries
    test_queries = [
        "coaching techniques",
        "goal setting",
        "communication skills",
        "leadership development",
        "time management"
    ]
    
    for query in test_queries:
        test_rag_search(query, top_k=3)
        time.sleep(1)  # Small delay between requests
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
