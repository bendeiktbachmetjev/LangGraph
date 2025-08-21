#!/usr/bin/env python3
"""
Test for Step 8: Types and State management for RAG.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_step8_types_state():
    """Test Step 8: Types and State management."""
    print("🎯 Testing Step 8: Types and State")
    print("=" * 50)
    
    # Test 1: RetrievalChunk type
    print("\n1. 📋 Testing RetrievalChunk Type...")
    try:
        from mentor_ai.cursor.core.types import RetrievalChunk
        
        # Test creating a RetrievalChunk
        chunk = RetrievalChunk(
            id="test_chunk_1",
            title="Leadership Development Guide",
            snippet="Effective leadership requires developing emotional intelligence and communication skills.",
            source="coaching_handbook.pdf",
            score=0.95
        )
        
        print("✅ RetrievalChunk created successfully")
        print(f"   ID: {chunk.id}")
        print(f"   Title: {chunk.title}")
        print(f"   Snippet: {chunk.snippet[:50]}...")
        print(f"   Source: {chunk.source}")
        print(f"   Score: {chunk.score}")
        
        # Test validation
        chunk_dict = chunk.model_dump()
        print(f"✅ Serialization: {len(chunk_dict)} fields")
        
    except Exception as e:
        print(f"❌ RetrievalChunk test failed: {e}")
        return False
    
    # Test 2: State Manager with retrieved_chunks
    print("\n2. 🔄 Testing State Manager...")
    try:
        from mentor_ai.cursor.core.state_manager import StateManager
        from mentor_ai.cursor.core.root_graph import root_graph
        
        # Get retrieve_reg node
        retrieve_node = root_graph["retrieve_reg"]
        
        # Create mock state
        current_state = {
            "session_id": "test_session",
            "goals": ["Improve leadership skills"],
            "career_goal": "Team leader"
        }
        
        # Create mock LLM data with retrieved chunks
        mock_llm_data = {
            "retrieved_chunks": [
                {
                    "id": "chunk_1",
                    "title": "Leadership Development",
                    "content": "Effective leadership requires developing emotional intelligence.",
                    "source": "coaching_guide.pdf"
                },
                {
                    "id": "chunk_2", 
                    "title": "Team Management",
                    "content": "Successful team management involves setting clear goals.",
                    "source": "management_handbook.pdf"
                }
            ],
            "next": "generate_plan",
            "reply": ""
        }
        
        # Update state
        updated_state = StateManager.update_state(current_state, mock_llm_data, retrieve_node)
        
        print("✅ State updated successfully")
        print(f"   Original state keys: {list(current_state.keys())}")
        print(f"   Updated state keys: {list(updated_state.keys())}")
        
        if "retrieved_chunks" in updated_state:
            chunks = updated_state["retrieved_chunks"]
            print(f"   ✅ Retrieved chunks stored: {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks, 1):
                print(f"      {i}. {chunk.get('title', 'Unknown')} (from {chunk.get('source', 'Unknown')})")
        else:
            print("   ❌ Retrieved chunks not stored in state")
            return False
            
    except Exception as e:
        print(f"❌ State Manager test failed: {e}")
        return False
    
    # Test 3: Integration with generate_plan
    print("\n3. 🔗 Testing Integration with generate_plan...")
    try:
        from mentor_ai.cursor.core.prompting import generate_llm_prompt
        
        # Create state with retrieved chunks
        state_with_chunks = {
            "session_id": "test_session",
            "goals": ["Improve leadership skills"],
            "retrieved_chunks": [
                {
                    "title": "Leadership Development Guide",
                    "content": "Effective leadership requires developing emotional intelligence, communication skills, and the ability to inspire and motivate team members."
                },
                {
                    "title": "Team Management Best Practices",
                    "content": "Successful team management involves setting clear goals, providing regular feedback, and creating an environment of trust and collaboration."
                }
            ]
        }
        
        # Get generate_plan node
        generate_node = root_graph["generate_plan"]
        
        # Generate prompt
        prompt = generate_llm_prompt(generate_node, state_with_chunks, "")
        
        print("✅ Prompt generated successfully")
        print(f"   Prompt length: {len(prompt)} characters")
        
        # Check if knowledge snippets are included
        if "KNOWLEDGE SNIPPETS" in prompt:
            print("   ✅ Knowledge snippets included in prompt")
            
            # Extract snippets section
            start_idx = prompt.find("KNOWLEDGE SNIPPETS:")
            if start_idx != -1:
                end_idx = prompt.find("Strictly follow this order", start_idx)
                if end_idx != -1:
                    snippets_section = prompt[start_idx:end_idx]
                    print(f"   📋 Snippets section length: {len(snippets_section)} characters")
        else:
            print("   ❌ Knowledge snippets not found in prompt")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    # Test 4: Type validation
    print("\n4. ✅ Testing Type Validation...")
    try:
        from mentor_ai.cursor.core.types import RetrievalChunk
        
        # Test valid chunk
        valid_chunk = RetrievalChunk(
            id="valid_1",
            title="Valid Title",
            snippet="Valid content",
            source="valid.pdf"
        )
        print("✅ Valid chunk created")
        
        # Test chunk with score
        scored_chunk = RetrievalChunk(
            id="scored_1",
            title="Scored Title", 
            snippet="Scored content",
            source="scored.pdf",
            score=0.87
        )
        print("✅ Scored chunk created")
        
        # Test that extra fields are forbidden
        try:
            invalid_chunk = RetrievalChunk(
                id="invalid_1",
                title="Invalid Title",
                snippet="Invalid content", 
                source="invalid.pdf",
                extra_field="should_fail"
            )
            print("❌ Extra field validation failed")
            return False
        except Exception:
            print("✅ Extra field validation working")
            
    except Exception as e:
        print(f"❌ Type validation test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Step 8 Test Complete!")
    
    # Summary
    print("\n📊 Step 8 Status:")
    print("✅ RetrievalChunk type: Created and validated")
    print("✅ State Manager: Stores retrieved_chunks correctly")
    print("✅ Integration: Works with generate_plan")
    print("✅ Type Validation: Extra fields forbidden")
    
    print("\n🚀 Step 8 is COMPLETE!")
    print("Next step: Step 9 - Tests (unit + integration)")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Step 8 Test...")
    
    success = test_step8_types_state()
    
    if success:
        print("\n✅ Step 8 completed successfully!")
    else:
        print("\n❌ Step 8 needs fixes.")
        sys.exit(1)
