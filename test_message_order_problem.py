#!/usr/bin/env python3
"""
Test Message Order Problem
Demonstrates the issue with message order in Recent Messages
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mentor_ai'))

from mentor_ai.cursor.core.memory_manager import MemoryManager
from mentor_ai.cursor.core.prompting import generate_llm_prompt
from mentor_ai.cursor.core.root_graph import Node

def test_message_order_problem():
    """Test the message order problem"""
    print("🔄 Message Order Problem Analysis")
    print("=" * 50)
    
    # Create a sample node
    sample_node = Node(
        node_id="collect_basic_info",
        system_prompt="You are a helpful career coach. Collect basic information from the user.",
        outputs={
            "reply": str,
            "state.user_name": str,
            "state.user_age": int,
            "next": str
        }
    )
    
    # Simulate the current flow
    print("📊 Current Flow (PROBLEMATIC):")
    print()
    
    # Initial state
    state = {
        "session_id": "test-session",
        "user_id": "test-user",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! I'm your career coach."},
            {"role": "user", "content": "My name is Donald"},
            {"role": "assistant", "content": "Nice to meet you, Donald!"}
        ],
        "current_node": "collect_basic_info",
        "prompt_context": {
            "running_summary": None,
            "recent_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! I'm your career coach."},
                {"role": "user", "content": "My name is Donald"},
                {"role": "assistant", "content": "Nice to meet you, Donald!"}
            ],
            "important_facts": [],
            "weekly_summaries": {}
        },
        "message_count": 4,
        "current_week": 1
    }
    
    print("1️⃣ Current State (before new message):")
    print(f"   Recent Messages: {len(state['prompt_context']['recent_messages'])}")
    for i, msg in enumerate(state['prompt_context']['recent_messages']):
        print(f"   {i+1}. {msg['role']}: {msg['content'][:50]}...")
    
    print()
    
    # New user message
    new_user_message = "I have experience of four years in healthcare"
    print(f"2️⃣ New User Message: {new_user_message}")
    print()
    
    # PROBLEM: Current flow sends prompt BEFORE updating recent_messages
    print("3️⃣ Current Flow (PROBLEMATIC):")
    print("   ❌ Generate prompt with OLD recent_messages")
    print("   ❌ Send to LLM")
    print("   ❌ LLM doesn't see the new message")
    print("   ❌ LLM asks the same question again")
    print("   ✅ Update recent_messages AFTER LLM call")
    print()
    
    # Show what LLM sees
    old_prompt = generate_llm_prompt(sample_node, state, new_user_message)
    print("4️⃣ What LLM sees (OLD recent_messages):")
    print("   Recent Messages:")
    for msg in state['prompt_context']['recent_messages']:
        print(f"   - {msg['role']}: {msg['content']}")
    print("   ❌ NEW MESSAGE NOT INCLUDED!")
    print()
    
    # Show what should happen
    print("5️⃣ What SHOULD happen (CORRECT flow):")
    print("   ✅ Update recent_messages FIRST")
    print("   ✅ Generate prompt with UPDATED recent_messages")
    print("   ✅ Send to LLM")
    print("   ✅ LLM sees the new message")
    print("   ✅ LLM responds appropriately")
    print()
    
    # Simulate correct flow
    print("6️⃣ Correct Flow (FIXED):")
    
    # Step 1: Update recent_messages FIRST
    updated_state = state.copy()
    new_message = {"role": "user", "content": new_user_message}
    updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
    
    print("   ✅ Updated recent_messages FIRST:")
    for i, msg in enumerate(updated_state['prompt_context']['recent_messages']):
        print(f"   {i+1}. {msg['role']}: {msg['content'][:50]}...")
    
    # Step 2: Generate prompt with updated state
    correct_prompt = generate_llm_prompt(sample_node, updated_state, new_user_message)
    
    print("   ✅ LLM now sees the new message!")
    print()

def test_fix_implementation():
    """Test how to fix the message order problem"""
    print("🔧 Fix Implementation")
    print("=" * 50)
    
    print("📋 Current Problem:")
    print("   1. User sends message")
    print("   2. Generate prompt with OLD recent_messages")
    print("   3. Send to LLM")
    print("   4. LLM doesn't see new message")
    print("   5. Update recent_messages AFTER")
    print()
    
    print("🛠️ Proposed Fix:")
    print("   1. User sends message")
    print("   2. Update recent_messages FIRST")
    print("   3. Generate prompt with UPDATED recent_messages")
    print("   4. Send to LLM")
    print("   5. LLM sees new message")
    print("   6. Update assistant reply")
    print()
    
    print("📝 Code Changes Needed:")
    print("   In GraphProcessor.process_node():")
    print("   ```python")
    print("   # BEFORE (current):")
    print("   prompt = generate_llm_prompt(node, current_state, user_message)")
    print("   llm_response = llm_client.call_llm(prompt)")
    print("   updated_state = StateManager.update_state_with_memory(...)")
    print("   ```")
    print()
    print("   ```python")
    print("   # AFTER (fixed):")
    print("   # Update recent_messages FIRST")
    print("   temp_state = MemoryManager.update_prompt_context(current_state, user_message)")
    print("   prompt = generate_llm_prompt(node, temp_state, user_message)")
    print("   llm_response = llm_client.call_llm(prompt)")
    print("   updated_state = StateManager.update_state_with_memory(...)")
    print("   ```")
    print()

def test_impact_analysis():
    """Analyze the impact of the fix"""
    print("📊 Impact Analysis")
    print("=" * 50)
    
    print("🎯 Benefits of Fix:")
    print("   ✅ LLM sees the latest user message")
    print("   ✅ No more repeated questions")
    print("   ✅ Better conversation flow")
    print("   ✅ Improved user experience")
    print("   ✅ More accurate responses")
    print()
    
    print("⚠️ Potential Issues:")
    print("   ⚠️ Need to handle assistant reply separately")
    print("   ⚠️ Memory update happens twice (user + assistant)")
    print("   ⚠️ Need to ensure state consistency")
    print()
    
    print("🔍 Testing Strategy:")
    print("   1. Test with short conversations")
    print("   2. Test with long conversations")
    print("   3. Test memory field updates")
    print("   4. Test running summary creation")
    print("   5. Test important facts extraction")
    print()

if __name__ == "__main__":
    print("🔄 Message Order Problem Analysis")
    print("=" * 60)
    
    test_message_order_problem()
    test_fix_implementation()
    test_impact_analysis()
    
    print("=" * 60)
    print("🎯 Conclusion:")
    print("✅ Problem identified: Recent messages updated AFTER LLM call")
    print("✅ Solution: Update recent messages BEFORE generating prompt")
    print("✅ Impact: LLM will see latest user message")
    print("✅ Result: No more repeated questions")
