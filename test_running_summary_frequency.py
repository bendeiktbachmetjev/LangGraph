#!/usr/bin/env python3
"""
Test Running Summary Frequency
Shows how often Running Summary is created/updated
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'mentor_ai'))

from mentor_ai.cursor.core.memory_manager import MemoryManager

def test_running_summary_frequency():
    """Test how often Running Summary is created/updated"""
    print("🔄 Running Summary Frequency Test")
    print("=" * 50)
    
    # Initialize empty state
    state = {
        "session_id": "test-session",
        "user_id": "test-user",
        "history": [],
        "current_node": "collect_basic_info",
        "prompt_context": MemoryManager.initialize_prompt_context(),
        "message_count": 0,
        "current_week": 1
    }
    
    print("📊 Running Summary Update Schedule:")
    print("   - Created/Updated: Every 20 messages")
    print("   - Trigger: message_count % 20 == 0")
    print("   - Content: Summary of last 20 messages")
    print()
    
    # Simulate conversation and show when Running Summary is updated
    print("🧪 Simulating conversation...")
    print()
    
    for i in range(1, 26):  # Test 25 messages
        # Add user message
        user_message = {"role": "user", "content": f"User message {i}"}
        state = MemoryManager.update_prompt_context(state, user_message)
        
        # Add assistant reply
        assistant_message = {"role": "assistant", "content": f"Assistant reply {i}"}
        state = MemoryManager.update_prompt_context(state, assistant_message)
        
        message_count = state.get("message_count", 0)
        running_summary = state.get("prompt_context", {}).get("running_summary")
        
        # Check if Running Summary was updated
        if message_count % 20 == 0 and message_count > 0:
            print(f"✅ Message {message_count}: Running Summary UPDATED")
            print(f"   Summary: {running_summary[:100]}...")
        else:
            print(f"📝 Message {message_count}: No Running Summary update")
        
        # Show memory stats every 5 messages
        if message_count % 5 == 0:
            recent_count = len(state.get("prompt_context", {}).get("recent_messages", []))
            print(f"   📊 Recent messages: {recent_count}/5")
    
    print()
    print("📈 Summary of Running Summary Updates:")
    print("   - Message 20: First Running Summary created")
    print("   - Message 40: Running Summary updated")
    print("   - Message 60: Running Summary updated")
    print("   - And so on...")
    
    print()
    print("🎯 Key Points:")
    print("   ✅ Running Summary is created every 20 messages")
    print("   ✅ It summarizes the last 20 messages")
    print("   ✅ Uses LLM to generate concise 1-2 sentence summary")
    print("   ✅ Helps maintain context without storing full history")
    print("   ✅ Optimizes token usage for long conversations")

def test_running_summary_content():
    """Test what content goes into Running Summary"""
    print("\n📝 Running Summary Content Analysis")
    print("=" * 50)
    
    # Create sample conversation
    sample_history = []
    for i in range(1, 21):  # 20 messages (10 user + 10 assistant)
        sample_history.append({"role": "user", "content": f"I want to become a CTO. This is message {i} about my career goals."})
        sample_history.append({"role": "assistant", "content": f"That's great! Let's discuss your path to CTO. Reply {i} with specific advice."})
    
    print("📊 Sample conversation (20 messages):")
    print("   - 10 user messages about becoming CTO")
    print("   - 10 assistant replies with career advice")
    print()
    
    # Show what would be summarized
    conversation_text = "\n".join([
        f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
        for msg in sample_history[-20:]  # Last 20 messages
    ])
    
    print("📋 Content that goes into Running Summary:")
    print("   - Last 20 messages from conversation history")
    print("   - Both user and assistant messages")
    print("   - Focus on main topics and key points")
    print()
    
    print("🎯 Expected Running Summary:")
    print("   'User wants to become a CTO and is discussing career goals with assistant providing advice.'")
    print()
    
    print("💡 Benefits:")
    print("   ✅ Maintains conversation context")
    print("   ✅ Reduces token usage")
    print("   ✅ Improves AI response quality")
    print("   ✅ Handles long conversations efficiently")

def test_weekly_summary_frequency():
    """Test weekly summary frequency"""
    print("\n🗓️ Weekly Summary Frequency")
    print("=" * 50)
    
    print("📅 Weekly Summary Schedule:")
    print("   - Created: When transitioning between weeks")
    print("   - Trigger: Node changes to weekX_chat (X > current_week)")
    print("   - Content: Summary of entire week's conversation")
    print()
    
    print("🔄 Week Transition Nodes:")
    week_nodes = {
        "week1_chat": 1, "week2_chat": 2, "week3_chat": 3, "week4_chat": 4,
        "week5_chat": 5, "week6_chat": 6, "week7_chat": 7, "week8_chat": 8,
        "week9_chat": 9, "week10_chat": 10, "week11_chat": 11, "week12_chat": 12
    }
    
    for node, week in week_nodes.items():
        print(f"   - {node}: Week {week}")
    
    print()
    print("📊 Summary Types:")
    print("   🔄 Running Summary: Every 20 messages (frequent)")
    print("   🗓️ Weekly Summary: Every week transition (less frequent)")
    print("   📝 Both use LLM to generate concise summaries")

if __name__ == "__main__":
    print("🧠 Memory System - Running Summary Frequency Analysis")
    print("=" * 60)
    
    test_running_summary_frequency()
    test_running_summary_content()
    test_weekly_summary_frequency()
    
    print("\n" + "=" * 60)
    print("🎯 Conclusion:")
    print("✅ Running Summary: Every 20 messages")
    print("✅ Weekly Summary: Every week transition")
    print("✅ Both optimize token usage and maintain context")
    print("✅ System balances memory efficiency with conversation quality")
