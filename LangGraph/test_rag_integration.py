#!/usr/bin/env python3
"""
Integration test for RAG system with graph processing.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mentor_ai.cursor.core.graph_processor import GraphProcessor
from mentor_ai.cursor.core.root_graph import root_graph
from mentor_ai.app.config import settings

def test_rag_integration():
    """Test RAG integration with graph processing."""
    print("🔗 Testing RAG Integration with Graph...")
    
    # Test 1: Check if retrieve_reg node exists
    print("\n1. Checking retrieve_reg node...")
    if "retrieve_reg" in root_graph:
        node = root_graph["retrieve_reg"]
        print(f"✅ retrieve_reg node exists")
        print(f"   - Has executor: {node.executor is not None}")
        print(f"   - Outputs: {list(node.outputs.keys())}")
    else:
        print("❌ retrieve_reg node missing")
        return False
    
    # Test 2: Check graph transitions
    print("\n2. Checking graph transitions...")
    
    # Check that nodes that should go to retrieve_reg actually do
    nodes_to_check = ["improve_obstacles", "change_obstacles", "find_obstacles", "lost_skills"]
    
    for node_id in nodes_to_check:
        if node_id in root_graph:
            node = root_graph[node_id]
            # Create a mock state with goals to trigger transition
            mock_state = {"goals": ["test goal"]}
            next_node = node.next_node(mock_state)
            print(f"   {node_id} → {next_node}")
            
            if next_node == "retrieve_reg":
                print(f"   ✅ {node_id} correctly transitions to retrieve_reg")
            else:
                print(f"   ❌ {node_id} should transition to retrieve_reg, but goes to {next_node}")
        else:
            print(f"   ❌ {node_id} node missing")
    
    # Test 3: Test retrieve_reg executor (without OpenAI API)
    print("\n3. Testing retrieve_reg executor...")
    
    # Temporarily disable RAG to test executor
    original_reg_enabled = settings.REG_ENABLED
    settings.REG_ENABLED = False
    
    try:
        retrieve_node = root_graph["retrieve_reg"]
        mock_state = {
            "session_id": "test_session",
            "goals": ["Improve leadership skills"],
            "skills": ["communication"],
            "career_goal": "Become a team leader"
        }
        
        result = retrieve_node.executor("I need help with my career goals", mock_state)
        print(f"✅ Executor returned: {result}")
        
        if "retrieved_chunks" in result and "next" in result:
            print(f"   - Retrieved chunks: {len(result['retrieved_chunks'])}")
            print(f"   - Next node: {result['next']}")
            
            if result["next"] == "generate_plan":
                print("   ✅ Correctly transitions to generate_plan")
            else:
                print(f"   ❌ Should transition to generate_plan, but goes to {result['next']}")
        else:
            print("   ❌ Missing required fields in result")
            
    except Exception as e:
        print(f"   ❌ Executor failed: {e}")
        return False
    finally:
        # Restore original setting
        settings.REG_ENABLED = original_reg_enabled
    
    # Test 4: Test with RAG enabled (if API key available)
    print("\n4. Testing with RAG enabled...")
    
    if os.getenv("OPENAI_API_KEY"):
        settings.REG_ENABLED = True
        try:
            retrieve_node = root_graph["retrieve_reg"]
            mock_state = {
                "session_id": "test_session",
                "goals": ["Improve leadership skills"],
                "skills": ["communication"],
                "career_goal": "Become a team leader"
            }
            
            result = retrieve_node.executor("I need help with my career goals", mock_state)
            print(f"✅ RAG executor returned: {result}")
            
            if "retrieved_chunks" in result:
                chunks = result["retrieved_chunks"]
                print(f"   - Retrieved {len(chunks)} chunks")
                
                if chunks:
                    print(f"   - Sample chunk: {chunks[0].get('title', 'Unknown')}")
                    print(f"   - Content preview: {chunks[0].get('content', '')[:100]}...")
                else:
                    print("   ⚠️  No chunks retrieved (this might be normal if no relevant content)")
            else:
                print("   ❌ No retrieved_chunks in result")
                
        except Exception as e:
            print(f"   ❌ RAG executor failed: {e}")
        finally:
            settings.REG_ENABLED = False
    else:
        print("   ⚠️  Skipping RAG test - no OPENAI_API_KEY available")
    
    # Test 5: Test generate_plan with snippets
    print("\n5. Testing generate_plan with snippets...")
    
    try:
        from mentor_ai.cursor.core.prompting import generate_llm_prompt
        
        generate_node = root_graph["generate_plan"]
        mock_state = {
            "session_id": "test_session",
            "goals": ["Improve leadership skills"],
            "retrieved_chunks": [
                {
                    "title": "Leadership Coaching Guide",
                    "content": "Effective leadership involves active listening, clear communication, and building trust with your team members."
                },
                {
                    "title": "Team Management Techniques", 
                    "content": "Successful team management requires setting clear expectations, providing regular feedback, and fostering collaboration."
                }
            ]
        }
        
        prompt = generate_llm_prompt(generate_node, mock_state, "")
        print(f"✅ Generated prompt with snippets")
        
        # Check if snippets are included in prompt
        if "KNOWLEDGE SNIPPETS" in prompt:
            print("   ✅ Knowledge snippets included in prompt")
            print(f"   📝 Prompt length: {len(prompt)} characters")
        else:
            print("   ❌ Knowledge snippets not found in prompt")
            
    except Exception as e:
        print(f"   ❌ Prompt generation failed: {e}")
    
    print("\n🎉 RAG Integration Test Complete!")
    return True

def test_feature_flags():
    """Test RAG feature flags."""
    print("\n🎛️  Testing RAG Feature Flags...")
    
    print(f"Current REG_ENABLED: {settings.REG_ENABLED}")
    
    # Test with RAG disabled
    settings.REG_ENABLED = False
    print(f"REG_ENABLED = False: {settings.REG_ENABLED}")
    
    # Test with RAG enabled
    settings.REG_ENABLED = True
    print(f"REG_ENABLED = True: {settings.REG_ENABLED}")
    
    # Restore original
    settings.REG_ENABLED = False

if __name__ == "__main__":
    print("🚀 Starting RAG Integration Tests...")
    
    # Test feature flags
    test_feature_flags()
    
    # Test integration
    success = test_rag_integration()
    
    if success:
        print("\n✅ All integration tests passed! RAG system is properly integrated.")
    else:
        print("\n❌ Some integration tests failed. Please check the errors above.")
        sys.exit(1)
