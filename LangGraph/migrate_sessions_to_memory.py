#!/usr/bin/env python3
"""
Script to migrate existing sessions to include memory fields
"""

import asyncio
import json
from datetime import datetime, timezone
from mentor_ai.cursor.core.memory_manager import MemoryManager

async def migrate_session(session_data):
    """Migrate a single session to include memory fields"""
    session_id = session_data.get('session_id')
    print(f"🔄 Migrating session: {session_id}")
    
    # Check if session already has memory fields
    has_prompt_context = 'prompt_context' in session_data
    has_message_count = 'message_count' in session_data
    has_current_week = 'current_week' in session_data
    
    if all([has_prompt_context, has_message_count, has_current_week]):
        print(f"✅ Session {session_id} already has memory fields")
        return session_data
    
    # Initialize memory fields
    updated_session = session_data.copy()
    
    # Add prompt_context if missing
    if not has_prompt_context:
        history = session_data.get('history', [])
        
        # Create initial prompt_context from existing history
        prompt_context = MemoryManager.initialize_prompt_context()
        
        # Add recent messages (up to 5)
        recent_messages = history[-10:] if len(history) > 10 else history
        prompt_context['recent_messages'] = recent_messages
        
        # Create running summary if there are messages
        if len(history) >= 20:
            # Simulate running summary creation
            prompt_context['running_summary'] = f"User has had {len(history)} messages in conversation"
        
        updated_session['prompt_context'] = prompt_context
        print(f"  ✅ Added prompt_context with {len(recent_messages)} recent messages")
    
    # Add message_count if missing
    if not has_message_count:
        history = session_data.get('history', [])
        updated_session['message_count'] = len(history)
        print(f"  ✅ Added message_count: {len(history)}")
    
    # Add current_week if missing
    if not has_current_week:
        updated_session['current_week'] = 1
        print(f"  ✅ Added current_week: 1")
    
    # Add updated timestamp
    updated_session['updated_at'] = datetime.now(timezone.utc)
    
    return updated_session

async def migrate_all_sessions():
    """Migrate all sessions in the database"""
    print("🚀 Starting session migration to memory system...")
    
    try:
        from mentor_ai.app.storage.mongodb import mongodb_manager
        
        # Get all sessions
        sessions = await mongodb_manager.sessions_collection.find({}).to_list(length=None)
        
        if not sessions:
            print("❌ No sessions found in database")
            return
        
        print(f"📊 Found {len(sessions)} sessions to migrate")
        
        migrated_count = 0
        already_migrated_count = 0
        
        for session in sessions:
            session_id = session.get('session_id', 'Unknown')
            
            # Check if already migrated
            has_prompt_context = 'prompt_context' in session
            has_message_count = 'message_count' in session
            has_current_week = 'current_week' in session
            
            if all([has_prompt_context, has_message_count, has_current_week]):
                already_migrated_count += 1
                print(f"⏭️ Session {session_id} already migrated")
                continue
            
            # Migrate session
            try:
                updated_session = await migrate_session(session)
                
                # Update in database
                result = await mongodb_manager.sessions_collection.update_one(
                    {'_id': session['_id']},
                    {'$set': updated_session}
                )
                
                if result.modified_count > 0:
                    migrated_count += 1
                    print(f"✅ Successfully migrated session {session_id}")
                else:
                    print(f"⚠️ No changes made to session {session_id}")
                    
            except Exception as e:
                print(f"❌ Error migrating session {session_id}: {e}")
        
        print(f"\n📈 Migration Summary:")
        print(f"  - Total sessions: {len(sessions)}")
        print(f"  - Already migrated: {already_migrated_count}")
        print(f"  - Successfully migrated: {migrated_count}")
        print(f"  - Failed: {len(sessions) - already_migrated_count - migrated_count}")
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

async def test_migrated_session(session_id):
    """Test a specific migrated session"""
    print(f"\n🧪 Testing migrated session: {session_id}")
    
    try:
        from mentor_ai.app.storage.mongodb import mongodb_manager
        
        session = await mongodb_manager.get_session(session_id)
        
        if not session:
            print(f"❌ Session {session_id} not found")
            return
        
        # Check memory fields
        prompt_context = session.get('prompt_context')
        message_count = session.get('message_count')
        current_week = session.get('current_week')
        
        print(f"✅ Session found:")
        print(f"  - prompt_context: {'✅' if prompt_context else '❌'}")
        print(f"  - message_count: {message_count if message_count is not None else '❌'}")
        print(f"  - current_week: {current_week if current_week is not None else '❌'}")
        
        if prompt_context:
            print(f"  - Recent messages: {len(prompt_context.get('recent_messages', []))}")
            print(f"  - Important facts: {len(prompt_context.get('important_facts', []))}")
            print(f"  - Weekly summaries: {len(prompt_context.get('weekly_summaries', {}))}")
            print(f"  - Running summary: {'✅' if prompt_context.get('running_summary') else '❌'}")
        
        # Test memory stats
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        stats = MemoryManager.get_token_estimate(session)
        print(f"  - Estimated tokens: {stats['estimated_tokens']}")
        
    except Exception as e:
        print(f"❌ Error testing session: {e}")

async def main():
    """Main function"""
    print("🔄 Session Memory Migration Tool")
    print("=" * 50)
    
    # Migrate all sessions
    await migrate_all_sessions()
    
    # Test specific session if provided
    session_id = input("\nEnter session ID to test (or press Enter to skip): ").strip()
    
    if session_id:
        await test_migrated_session(session_id)
    
    print("\n🎉 Migration completed!")

if __name__ == "__main__":
    asyncio.run(main())
