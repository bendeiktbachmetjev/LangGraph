#!/usr/bin/env python3
"""
Script to check session state in MongoDB and verify memory fields
"""

import asyncio
import json
from mentor_ai.app.storage.mongodb import mongodb_manager

async def check_session_state(session_id: str):
    """Check session state and verify memory fields"""
    print(f"Checking session: {session_id}")
    
    # Get session from MongoDB
    session = await mongodb_manager.get_session(session_id)
    
    if not session:
        print("❌ Session not found!")
        return
    
    print("✅ Session found!")
    print(f"Session ID: {session.get('session_id')}")
    print(f"User ID: {session.get('user_id')}")
    print(f"Current Node: {session.get('current_node')}")
    print(f"Created: {session.get('created_at')}")
    print(f"Updated: {session.get('updated_at')}")
    
    # Check memory fields
    print("\n🔍 Memory Fields Check:")
    
    # Check prompt_context
    prompt_context = session.get('prompt_context')
    if prompt_context:
        print("✅ prompt_context exists")
        print(f"  - Running summary: {bool(prompt_context.get('running_summary'))}")
        print(f"  - Recent messages count: {len(prompt_context.get('recent_messages', []))}")
        print(f"  - Important facts count: {len(prompt_context.get('important_facts', []))}")
        print(f"  - Weekly summaries count: {len(prompt_context.get('weekly_summaries', {}))}")
    else:
        print("❌ prompt_context missing")
    
    # Check message_count
    message_count = session.get('message_count')
    if message_count is not None:
        print(f"✅ message_count: {message_count}")
    else:
        print("❌ message_count missing")
    
    # Check current_week
    current_week = session.get('current_week')
    if current_week is not None:
        print(f"✅ current_week: {current_week}")
    else:
        print("❌ current_week missing")
    
    # Check history
    history = session.get('history', [])
    print(f"✅ History messages: {len(history)}")
    
    # Show sample of recent messages
    if history:
        print("\n📝 Recent Messages:")
        for i, msg in enumerate(history[-3:]):  # Last 3 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:50] + "..." if len(msg.get('content', '')) > 50 else msg.get('content', '')
            print(f"  {i+1}. {role}: {content}")
    
    # Show prompt_context details if exists
    if prompt_context:
        print("\n🧠 Prompt Context Details:")
        
        running_summary = prompt_context.get('running_summary')
        if running_summary:
            print(f"  Running Summary: {running_summary[:100]}...")
        
        recent_messages = prompt_context.get('recent_messages', [])
        if recent_messages:
            print(f"  Recent Messages ({len(recent_messages)}):")
            for i, msg in enumerate(recent_messages):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:50] + "..." if len(msg.get('content', '')) > 50 else msg.get('content', '')
                print(f"    {i+1}. {role}: {content}")
        
        important_facts = prompt_context.get('important_facts', [])
        if important_facts:
            print(f"  Important Facts ({len(important_facts)}):")
            for i, fact in enumerate(important_facts):
                fact_text = fact.get('fact', '')[:50] + "..." if len(fact.get('fact', '')) > 50 else fact.get('fact', '')
                print(f"    {i+1}. {fact_text}")
        
        weekly_summaries = prompt_context.get('weekly_summaries', {})
        if weekly_summaries:
            print(f"  Weekly Summaries ({len(weekly_summaries)}):")
            for week, summary_data in weekly_summaries.items():
                summary_text = summary_data.get('summary', '')[:50] + "..." if len(summary_data.get('summary', '')) > 50 else summary_data.get('summary', '')
                print(f"    Week {week}: {summary_text}")

async def list_all_sessions():
    """List all sessions in the database"""
    print("📋 Listing all sessions...")
    
    try:
        # Get all sessions from MongoDB
        sessions = await mongodb_manager.sessions_collection.find({}).limit(10).to_list(length=10)
        
        if not sessions:
            print("❌ No sessions found in database")
            return
        
        print(f"✅ Found {len(sessions)} sessions:")
        
        for i, session in enumerate(sessions):
            session_id = session.get('session_id', 'Unknown')
            user_id = session.get('user_id', 'Unknown')
            current_node = session.get('current_node', 'Unknown')
            created_at = session.get('created_at', 'Unknown')
            
            # Check if memory fields exist
            has_prompt_context = 'prompt_context' in session
            has_message_count = 'message_count' in session
            has_current_week = 'current_week' in session
            
            memory_status = "✅" if all([has_prompt_context, has_message_count, has_current_week]) else "❌"
            
            print(f"  {i+1}. {memory_status} {session_id}")
            print(f"     User: {user_id}")
            print(f"     Node: {current_node}")
            print(f"     Created: {created_at}")
            print(f"     Memory fields: prompt_context={has_prompt_context}, message_count={has_message_count}, current_week={has_current_week}")
            print()
    
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")

async def main():
    """Main function"""
    print("🔍 Session State Checker")
    print("=" * 50)
    
    # List all sessions first
    await list_all_sessions()
    
    # Ask for specific session to check
    print("\n" + "=" * 50)
    session_id = input("Enter session ID to check (or press Enter to skip): ").strip()
    
    if session_id:
        await check_session_state(session_id)
    else:
        print("Skipping specific session check.")

if __name__ == "__main__":
    asyncio.run(main())
