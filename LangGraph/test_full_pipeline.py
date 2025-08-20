#!/usr/bin/env python3
"""
Test the full RAG pipeline from user input to plan generation.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_full_pipeline():
    """Test the complete RAG pipeline."""
    print("🔄 Testing Full RAG Pipeline...")
    
    # Simulate a complete user journey
    print("\n📝 Simulating user journey...")
    
    # Step 1: User starts with career goals
    print("\n1. User: 'I want to improve my career and become a team leader'")
    
    # Step 2: System collects basic info (simulated)
    state = {
        "session_id": "test_session_123",
        "user_name": "John",
        "user_age": 28,
        "goal_type": "career_improve",
        "career_goal": "Become a team leader",
        "skills": ["communication", "project management"],
        "interests": ["leadership", "team building"],
        "goals": ["Improve leadership skills", "Build team management experience"]
    }
    
    print(f"   State: {json.dumps(state, indent=2)}")
    
    # Step 3: Test retrieve_reg node
    print("\n2. Testing retrieve_reg node...")
    
    try:
        from mentor_ai.cursor.core.root_graph import root_graph
        
        if "retrieve_reg" in root_graph:
            retrieve_node = root_graph["retrieve_reg"]
            
            # Test with RAG disabled first
            print("   Testing with RAG disabled (REG_ENABLED=False)...")
            result_disabled = retrieve_node.executor("", state)
            print(f"   Result: {result_disabled}")
            
            # Test with RAG enabled
            print("   Testing with RAG enabled (REG_ENABLED=True)...")
            # Temporarily enable RAG
            import mentor_ai.app.config
            original_setting = mentor_ai.app.config.settings.REG_ENABLED
            mentor_ai.app.config.settings.REG_ENABLED = True
            
            try:
                result_enabled = retrieve_node.executor("", state)
                print(f"   Result: {result_enabled}")
                
                if result_enabled.get("retrieved_chunks"):
                    chunks = result_enabled["retrieved_chunks"]
                    print(f"   ✅ Retrieved {len(chunks)} chunks")
                    
                    for i, chunk in enumerate(chunks[:3], 1):  # Show first 3
                        print(f"   📄 Chunk {i}: {chunk.get('title', 'Unknown')}")
                        print(f"   📝 Content: {chunk.get('content', '')[:100]}...")
                else:
                    print("   ⚠️  No chunks retrieved")
                    
            finally:
                # Restore original setting
                mentor_ai.app.config.settings.REG_ENABLED = original_setting
                
        else:
            print("   ❌ retrieve_reg node not found")
            
    except Exception as e:
        print(f"   ❌ Error testing retrieve_reg: {e}")
    
    # Step 4: Test generate_plan with snippets
    print("\n3. Testing generate_plan with snippets...")
    
    try:
        # Add retrieved chunks to state
        state["retrieved_chunks"] = [
            {
                "title": "Leadership Development Guide",
                "content": "Effective leadership requires developing emotional intelligence, communication skills, and the ability to inspire and motivate team members."
            },
            {
                "title": "Team Management Best Practices",
                "content": "Successful team management involves setting clear goals, providing regular feedback, and creating an environment of trust and collaboration."
            },
            {
                "title": "Career Advancement Strategies", 
                "content": "To advance in your career, focus on building relationships, developing new skills, and demonstrating value to your organization."
            }
        ]
        
        from mentor_ai.cursor.core.prompting import generate_llm_prompt
        from mentor_ai.cursor.core.root_graph import root_graph
        
        generate_node = root_graph["generate_plan"]
        prompt = generate_llm_prompt(generate_node, state, "")
        
        print(f"   ✅ Generated prompt successfully")
        print(f"   📝 Prompt length: {len(prompt)} characters")
        
        # Check for knowledge snippets
        if "KNOWLEDGE SNIPPETS" in prompt:
            print("   ✅ Knowledge snippets found in prompt")
            
            # Extract snippets section
            start_idx = prompt.find("KNOWLEDGE SNIPPETS:")
            if start_idx != -1:
                end_idx = prompt.find("Strictly follow this order", start_idx)
                if end_idx != -1:
                    snippets_section = prompt[start_idx:end_idx]
                    print(f"   📋 Snippets section:\n{snippets_section}")
        else:
            print("   ❌ Knowledge snippets not found in prompt")
            
    except Exception as e:
        print(f"   ❌ Error testing generate_plan: {e}")
    
    # Step 5: Test complete flow
    print("\n4. Testing complete flow...")
    
    try:
        from mentor_ai.cursor.core.graph_processor import GraphProcessor
        
        # Test the flow from improve_obstacles to retrieve_reg to generate_plan
        print("   Testing flow: improve_obstacles → retrieve_reg → generate_plan")
        
        # Simulate improve_obstacles completion
        obstacles_state = {
            "session_id": "test_session_123",
            "goals": ["Improve leadership skills", "Build team management experience"],
            "skills": ["communication", "project management"],
            "career_goal": "Become a team leader"
        }
        
        # Process improve_obstacles node
        reply, updated_state, next_node = GraphProcessor.process_node(
            "improve_obstacles", 
            "I want to improve my leadership and team management skills", 
            obstacles_state
        )
        
        print(f"   improve_obstacles → {next_node}")
        print(f"   Updated state keys: {list(updated_state.keys())}")
        
        if next_node == "retrieve_reg":
            print("   ✅ Correctly transitions to retrieve_reg")
            
            # Process retrieve_reg node
            reply, updated_state, next_node = GraphProcessor.process_node(
                "retrieve_reg",
                "",
                updated_state
            )
            
            print(f"   retrieve_reg → {next_node}")
            
            if next_node == "generate_plan":
                print("   ✅ Correctly transitions to generate_plan")
                print(f"   State has retrieved_chunks: {'retrieved_chunks' in updated_state}")
            else:
                print(f"   ❌ Should transition to generate_plan, but goes to {next_node}")
        else:
            print(f"   ❌ Should transition to retrieve_reg, but goes to {next_node}")
            
    except Exception as e:
        print(f"   ❌ Error testing complete flow: {e}")
    
    print("\n🎉 Full Pipeline Test Complete!")

def test_configuration():
    """Test current configuration."""
    print("\n⚙️  Current Configuration:")
    
    try:
        from mentor_ai.app.config import settings
        
        print(f"REG_ENABLED: {settings.REG_ENABLED}")
        print(f"EMBEDDINGS_PROVIDER: {settings.EMBEDDINGS_PROVIDER}")
        print(f"EMBEDDINGS_MODEL: {settings.EMBEDDINGS_MODEL}")
        print(f"RAG_INDEX_PATH: {settings.RAG_INDEX_PATH}")
        print(f"RETRIEVE_TOP_K: {settings.RETRIEVE_TOP_K}")
        print(f"MAX_CONTEXT_CHARS: {settings.MAX_CONTEXT_CHARS}")
        
        # Check if index exists
        index_path = Path(settings.RAG_INDEX_PATH)
        if index_path.exists():
            print(f"✅ Index exists: {index_path}")
            
            # Check index files
            chunks_file = index_path / "chunks.json"
            if chunks_file.exists():
                with open(chunks_file, 'r') as f:
                    chunks = json.load(f)
                print(f"✅ Index contains {len(chunks)} documents")
            else:
                print("❌ Chunks file missing")
        else:
            print(f"❌ Index missing: {index_path}")
            
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")

if __name__ == "__main__":
    print("🚀 Starting Full Pipeline Test...")
    
    # Test configuration
    test_configuration()
    
    # Test full pipeline
    test_full_pipeline()
    
    print("\n✅ Full pipeline test completed!")
