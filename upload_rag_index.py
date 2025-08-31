#!/usr/bin/env python3
"""
Script to upload RAG index to Railway server.
"""

import os
import requests
import json
from pathlib import Path

def upload_index_files():
    """Upload RAG index files to Railway server."""
    print("🚀 Uploading RAG index to Railway...")
    
    # Railway API endpoint (you'll need to create this endpoint)
    base_url = "https://spotted-mom-production.up.railway.app"
    
    # Files to upload
    index_files = [
        "RAG/index/chunks.json",
        "RAG/index/embeddings.npy", 
        "RAG/index/metadata.json"
    ]
    
    for file_path in index_files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"📤 Uploading {file_path}...")
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                response = requests.post(f"{base_url}/api/rag/upload", files=files)
                
                if response.status_code == 200:
                    print(f"✅ Successfully uploaded {file_path}")
                else:
                    print(f"❌ Failed to upload {file_path}: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path}: {e}")
    
    print("✅ Index upload completed!")

def test_rag_after_upload():
    """Test RAG functionality after upload."""
    print("\n🧪 Testing RAG after upload...")
    
    base_url = "https://spotted-mom-production.up.railway.app"
    
    try:
        # Test RAG search
        response = requests.post(
            f"{base_url}/api/rag/test/dev",
            headers={"Content-Type": "application/json"},
            json={"query": "leadership", "top_k": 2}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ RAG test successful!")
            print(f"📄 Found {result.get('total_found', 0)} results")
            print(f"⏱️ Search time: {result.get('search_time_ms', 0):.2f}ms")
            
            snippets = result.get('snippets', [])
            for i, snippet in enumerate(snippets[:2], 1):
                print(f"\n--- Result {i} ---")
                print(f"Title: {snippet.get('title', 'Untitled')}")
                print(f"Score: {snippet.get('score', 0.0):.4f}")
                print(f"Content: {snippet.get('content', '')[:200]}...")
        else:
            print(f"❌ RAG test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing RAG: {e}")

if __name__ == "__main__":
    # Note: This requires a /api/rag/upload endpoint on the server
    # For now, we'll just test the current state
    print("⚠️ Note: Upload functionality requires server-side endpoint")
    print("Testing current RAG state...")
    
    test_rag_after_upload()

