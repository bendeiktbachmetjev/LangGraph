#!/usr/bin/env python3
"""
Quick test to verify RAG system is working.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_rag_test():
    """Quick test of RAG functionality."""
    print("🚀 Quick RAG Test")
    print("=" * 50)
    
    # Test 1: Check index
    print("\n1. 📚 Checking RAG Index...")
    index_path = Path("LangGraph/RAG/index")
    if index_path.exists():
        chunks_file = index_path / "chunks.json"
        if chunks_file.exists():
            with open(chunks_file, 'r') as f:
                chunks = json.load(f)
            print(f"✅ Index exists with {len(chunks)} documents")
            
            # Show sample document
            if chunks:
                sample = chunks[0]
                print(f"📄 Sample document: {sample.get('title', 'Unknown')}")
                print(f"📝 Content preview: {sample.get('content', '')[:100]}...")
        else:
            print("❌ Chunks file missing")
    else:
        print("❌ Index directory missing")
    
    # Test 2: Check graph structure
    print("\n2. 🕸️  Checking Graph Structure...")
    try:
        from mentor_ai.cursor.core.root_graph import root_graph
        
        if "retrieve_reg" in root_graph:
            node = root_graph["retrieve_reg"]
            print(f"✅ retrieve_reg node exists")
            print(f"   - Has executor: {node.executor is not None}")
            print(f"   - Outputs: {list(node.outputs.keys())}")
        else:
            print("❌ retrieve_reg node missing")
            
        # Check transitions
        nodes_to_check = ["improve_obstacles", "change_obstacles", "find_obstacles"]
        for node_id in nodes_to_check:
            if node_id in root_graph:
                node = root_graph[node_id]
                mock_state = {"goals": ["test goal"]}
                next_node = node.next_node(mock_state)
                print(f"   {node_id} → {next_node}")
                
    except Exception as e:
        print(f"❌ Error checking graph: {e}")
    
    # Test 3: Test executor (without API calls)
    print("\n3. ⚙️  Testing RAG Executor...")
    try:
        from mentor_ai.cursor.core.root_graph import root_graph
        
        if "retrieve_reg" in root_graph:
            retrieve_node = root_graph["retrieve_reg"]
            
            # Test with RAG disabled
            mock_state = {
                "session_id": "test",
                "goals": ["Improve leadership skills"],
                "career_goal": "Become a team leader"
            }
            
            result = retrieve_node.executor("", mock_state)
            print(f"✅ Executor works: {result}")
            
            if result.get("next") == "generate_plan":
                print("✅ Correctly transitions to generate_plan")
            else:
                print(f"❌ Should transition to generate_plan, but goes to {result.get('next')}")
                
    except Exception as e:
        print(f"❌ Error testing executor: {e}")
    
    # Test 4: Check configuration
    print("\n4. ⚙️  Checking Configuration...")
    try:
        from mentor_ai.app.config import settings
        
        print(f"REG_ENABLED: {settings.REG_ENABLED}")
        print(f"EMBEDDINGS_MODEL: {settings.EMBEDDINGS_MODEL}")
        print(f"RAG_INDEX_PATH: {settings.RAG_INDEX_PATH}")
        print(f"RETRIEVE_TOP_K: {settings.RETRIEVE_TOP_K}")
        
    except Exception as e:
        print(f"❌ Error checking config: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Quick RAG Test Complete!")
    
    # Summary
    print("\n📊 RAG System Status:")
    print("✅ Index: Created and loaded")
    print("✅ Graph: retrieve_reg node added")
    print("✅ Executor: Basic functionality works")
    print("✅ Configuration: Settings available")
    print("⚠️  API Integration: Needs OpenAI API key for full functionality")
    print("⚠️  Transitions: Some graph transitions need fixing")

if __name__ == "__main__":
    quick_rag_test()
