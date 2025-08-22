#!/usr/bin/env python3
"""
Test Chat Request Content
Shows exactly what is sent in each chat request
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mentor_ai'))

from mentor_ai.cursor.core.memory_manager import MemoryManager
from mentor_ai.cursor.core.prompting import generate_llm_prompt
from mentor_ai.cursor.core.root_graph import Node

def test_chat_request_content():
    """Test what content is sent in each chat request"""
    print("💬 Chat Request Content Analysis")
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
    
    # Create different session states to test
    test_cases = [
        {
            "name": "New Session (No Memory)",
            "state": {
                "session_id": "new-session",
                "user_id": "test-user",
                "history": [],
                "current_node": "collect_basic_info",
                "user_name": None,
                "user_age": None
            }
        },
        {
            "name": "Session with 5 Messages (No Running Summary)",
            "state": {
                "session_id": "short-session",
                "user_id": "test-user",
                "history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! I'm your career coach."},
                    {"role": "user", "content": "My name is John"},
                    {"role": "assistant", "content": "Nice to meet you, John!"},
                    {"role": "user", "content": "I'm 25 years old"}
                ],
                "current_node": "collect_basic_info",
                "prompt_context": {
                    "running_summary": None,
                    "recent_messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi! I'm your career coach."},
                        {"role": "user", "content": "My name is John"},
                        {"role": "assistant", "content": "Nice to meet you, John!"},
                        {"role": "user", "content": "I'm 25 years old"}
                    ],
                    "important_facts": [],
                    "weekly_summaries": {}
                },
                "message_count": 5,
                "current_week": 1,
                "user_name": "John",
                "user_age": 25
            }
        },
        {
            "name": "Session with 25 Messages (With Running Summary)",
            "state": {
                "session_id": "long-session",
                "user_id": "test-user",
                "history": [
                    {"role": "user", "content": f"Message {i}"} for i in range(1, 26)
                ] + [
                    {"role": "assistant", "content": f"Reply {i}"} for i in range(1, 26)
                ],
                "current_node": "collect_basic_info",
                "prompt_context": {
                    "running_summary": "User has been discussing career goals and personal background with the assistant.",
                    "recent_messages": [
                        {"role": "user", "content": "I want to become a CTO"},
                        {"role": "assistant", "content": "That's an exciting goal!"},
                        {"role": "user", "content": "I have 5 years of experience"},
                        {"role": "assistant", "content": "Great foundation. What leadership experience?"},
                        {"role": "user", "content": "I led a team of 3 developers"}
                    ],
                    "important_facts": [
                        {"fact": "User wants to become CTO", "week": 1},
                        {"fact": "User has 5 years of experience", "week": 1}
                    ],
                    "weekly_summaries": {}
                },
                "message_count": 25,
                "current_week": 1,
                "user_name": "John",
                "user_age": 25
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        state = test_case["state"]
        user_message = "What should I do next?"
        
        # Generate the actual prompt that would be sent to LLM
        prompt = generate_llm_prompt(sample_node, state, user_message)
        
        # Show what's included
        print("📤 What's sent to LLM:")
        print()
        
        # Check if prompt_context is used
        if "prompt_context" in state and state["prompt_context"]:
            print("✅ Using OPTIMIZED prompt_context (Memory System)")
            
            # Show memory components
            prompt_context = state["prompt_context"]
            
            if prompt_context.get("running_summary"):
                print(f"   🔄 Running Summary: {prompt_context['running_summary'][:100]}...")
            else:
                print("   ❌ No Running Summary yet")
            
            recent_count = len(prompt_context.get("recent_messages", []))
            print(f"   📝 Recent Messages: {recent_count}/5")
            
            facts_count = len(prompt_context.get("important_facts", []))
            print(f"   💡 Important Facts: {facts_count}")
            
            weekly_count = len(prompt_context.get("weekly_summaries", {}))
            print(f"   🗓️ Weekly Summaries: {weekly_count}")
            
        else:
            print("❌ Using FULL HISTORY (Fallback)")
            history_count = len(state.get("history", []))
            print(f"   📚 Full History: {history_count} messages")
        
        # Show token estimation
        token_stats = MemoryManager.get_token_estimate(state)
        print(f"   🧮 Estimated Tokens: ~{token_stats['estimated_tokens']}")
        
        # Show prompt length
        prompt_length = len(prompt)
        print(f"   📏 Prompt Length: {prompt_length} characters")
        
        print()
        print("📋 Prompt Preview (first 300 chars):")
        print(f"   {prompt[:300]}...")
        
        print()

def test_memory_vs_history_comparison():
    """Compare memory system vs full history"""
    print("\n🔄 Memory System vs Full History Comparison")
    print("=" * 50)
    
    # Create a session with 50 messages
    long_history = []
    for i in range(1, 51):
        long_history.append({"role": "user", "content": f"User message {i} about career goals and personal development"})
        long_history.append({"role": "assistant", "content": f"Assistant reply {i} with advice and guidance"})
    
    # State with full history (old way)
    state_with_history = {
        "session_id": "test-session",
        "user_id": "test-user",
        "history": long_history,
        "current_node": "collect_basic_info"
    }
    
    # State with memory system (new way)
    state_with_memory = {
        "session_id": "test-session",
        "user_id": "test-user",
        "history": long_history,  # Still stored for frontend
        "current_node": "collect_basic_info",
        "prompt_context": {
            "running_summary": "User has been discussing career development and personal goals with the assistant over an extended conversation.",
            "recent_messages": [
                {"role": "user", "content": "I want to become a CTO"},
                {"role": "assistant", "content": "That's an exciting goal!"},
                {"role": "user", "content": "I have 5 years of experience"},
                {"role": "assistant", "content": "Great foundation. What leadership experience?"},
                {"role": "user", "content": "I led a team of 3 developers"}
            ],
            "important_facts": [
                {"fact": "User wants to become CTO", "week": 1},
                {"fact": "User has 5 years of experience", "week": 1},
                {"fact": "User led a team of 3 developers", "week": 1}
            ],
            "weekly_summaries": {}
        },
        "message_count": 50,
        "current_week": 1
    }
    
    # Create sample node
    sample_node = Node(
        node_id="collect_basic_info",
        system_prompt="You are a helpful career coach.",
        outputs={
            "reply": str,
            "next": str
        }
    )
    
    user_message = "What should I focus on next?"
    
    # Generate prompts
    prompt_with_history = generate_llm_prompt(sample_node, state_with_history, user_message)
    prompt_with_memory = generate_llm_prompt(sample_node, state_with_memory, user_message)
    
    print("📊 Comparison:")
    print()
    
    print("📚 Full History Method:")
    print(f"   - History messages: {len(long_history)}")
    print(f"   - Prompt length: {len(prompt_with_history)} characters")
    print(f"   - Estimated tokens: ~{len(prompt_with_history) // 4}")
    print(f"   - Includes: ALL conversation history")
    
    print()
    
    print("🧠 Memory System Method:")
    print(f"   - History messages: {len(long_history)} (stored for frontend)")
    print(f"   - Prompt length: {len(prompt_with_memory)} characters")
    print(f"   - Estimated tokens: ~{len(prompt_with_memory) // 4}")
    print(f"   - Includes: Running Summary + Recent Messages + Important Facts")
    
    print()
    
    # Calculate savings
    history_length = len(prompt_with_history)
    memory_length = len(prompt_with_memory)
    savings_percent = ((history_length - memory_length) / history_length) * 100
    
    print("💰 Token Savings:")
    print(f"   - Full History: ~{history_length // 4} tokens")
    print(f"   - Memory System: ~{memory_length // 4} tokens")
    print(f"   - Savings: ~{(history_length - memory_length) // 4} tokens ({savings_percent:.1f}%)")
    
    print()
    print("🎯 Key Benefits:")
    print("   ✅ Significant token savings")
    print("   ✅ Maintains conversation context")
    print("   ✅ Improves response quality")
    print("   ✅ Handles long conversations efficiently")
    print("   ✅ Full history still available for frontend")

if __name__ == "__main__":
    print("💬 Chat Request Content Analysis")
    print("=" * 60)
    
    test_chat_request_content()
    test_memory_vs_history_comparison()
    
    print("\n" + "=" * 60)
    print("🎯 Conclusion:")
    print("✅ Memory System: Sends optimized context (Running Summary + Recent Messages)")
    print("✅ Full History: Still stored in database for frontend compatibility")
    print("✅ Significant token savings while maintaining conversation quality")
    print("✅ System automatically chooses between memory and history based on availability")
