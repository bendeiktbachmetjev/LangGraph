#!/usr/bin/env python3
"""
Quick test to verify memory system is working
"""

import asyncio
import json
from mentor_ai.cursor.core.memory_manager import MemoryManager
from mentor_ai.cursor.core.state_manager import StateManager
from mentor_ai.cursor.core.graph_processor import GraphProcessor

def test_memory_manager():
    """Test MemoryManager functionality"""
    print("🧠 Testing MemoryManager...")
    
    # Test initialization
    prompt_context = MemoryManager.initialize_prompt_context()
    print(f"✅ Initialized prompt_context: {len(prompt_context)} fields")
    
    # Test token estimation
    state = {"prompt_context": prompt_context}
    stats = MemoryManager.get_token_estimate(state)
    print(f"✅ Token estimation: {stats}")
    
    # Test prompt context formatting
    formatted = MemoryManager.format_prompt_context(state)
    print(f"✅ Formatted context length: {len(formatted) if formatted else 0}")
    
    return True

def test_state_manager():
    """Test StateManager memory integration"""
    print("\n🔄 Testing StateManager...")
    
    # Create test state
    current_state = {
        "session_id": "test123",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
    
    # Test memory update
    llm_data = {"reply": "How can I help you?"}
    node = type('Node', (), {'id': 'test_node'})()
    
    updated_state = StateManager.update_state_with_memory(
        current_state, llm_data, node, 
        user_message="Hello", 
        assistant_reply="How can I help you?"
    )
    
    print(f"✅ Updated state has prompt_context: {'prompt_context' in updated_state}")
    print(f"✅ Message count: {updated_state.get('message_count', 'missing')}")
    print(f"✅ Current week: {updated_state.get('current_week', 'missing')}")
    
    return True

def test_graph_processor():
    """Test GraphProcessor memory integration"""
    print("\n⚙️ Testing GraphProcessor...")
    
    # Create test state
    current_state = {
        "session_id": "test123",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
    
    # Test memory-enabled processing
    try:
        reply, updated_state, next_node = GraphProcessor.process_node(
            node_id="collect_basic_info",
            user_message="My name is John",
            current_state=current_state
        )
        
        print(f"✅ Processed with memory: {len(reply) if reply else 0} chars")
        print(f"✅ Has prompt_context: {'prompt_context' in updated_state}")
        print(f"✅ Next node: {next_node}")
        
        return True
    except Exception as e:
        print(f"❌ Error in GraphProcessor: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Memory System Components")
    print("=" * 50)
    
    tests = [
        test_memory_manager,
        test_state_manager,
        test_graph_processor
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All memory system components are working!")
        print("\n💡 Next steps:")
        print("1. Wait for Railway to deploy the new code")
        print("2. Test with a real session in the app")
        print("3. Check memory fields in the session state")
    else:
        print("❌ Some components have issues - check the errors above")

if __name__ == "__main__":
    main()
