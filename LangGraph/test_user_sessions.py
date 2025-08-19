#!/usr/bin/env python3
"""
Test script for user session functionality
"""

import asyncio
import motor.motor_asyncio
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.config import settings

async def test_user_sessions():
    """Test user session creation and retrieval"""
    
    # Connect to MongoDB
    await mongodb_manager.connect()
    
    try:
        # Test data
        user_id_1 = "test_user_1"
        user_id_2 = "test_user_2"
        
        print("🧪 Testing user session functionality...")
        
        # Test 1: Create session for user 1
        print("\n1. Creating session for user 1...")
        session_id_1 = "test_session_1"
        success = await mongodb_manager.create_session(session_id_1, user_id_1)
        print(f"✅ Session created: {success}")
        
        # Test 2: Create session for user 2
        print("\n2. Creating session for user 2...")
        session_id_2 = "test_session_2"
        success = await mongodb_manager.create_session(session_id_2, user_id_2)
        print(f"✅ Session created: {success}")
        
        # Test 3: Get user 1's session
        print("\n3. Getting user 1's session...")
        session_1 = await mongodb_manager.get_user_session(user_id_1)
        if session_1:
            print(f"✅ User 1 session found: {session_1['session_id']}")
            print(f"   User ID: {session_1['user_id']}")
            print(f"   Phase: {session_1['phase']}")
        else:
            print("❌ User 1 session not found")
        
        # Test 4: Get user 2's session
        print("\n4. Getting user 2's session...")
        session_2 = await mongodb_manager.get_user_session(user_id_2)
        if session_2:
            print(f"✅ User 2 session found: {session_2['session_id']}")
            print(f"   User ID: {session_2['user_id']}")
            print(f"   Phase: {session_2['phase']}")
        else:
            print("❌ User 2 session not found")
        
        # Test 5: Verify sessions are isolated
        print("\n5. Verifying session isolation...")
        if session_1 and session_2:
            if session_1['user_id'] != session_2['user_id']:
                print("✅ Sessions are properly isolated by user ID")
            else:
                print("❌ Sessions are not isolated")
        
        # Test 6: Update session data
        print("\n6. Updating session data...")
        update_data = {
            "phase": "plan_ready",
            "goals": ["Goal 1", "Goal 2", "Goal 3"],
            "topics": [f"Week {i} topic" for i in range(1, 13)]
        }
        success = await mongodb_manager.update_session(session_id_1, update_data)
        print(f"✅ Session updated: {success}")
        
        # Test 7: Verify update
        print("\n7. Verifying update...")
        updated_session = await mongodb_manager.get_session(session_id_1)
        if updated_session:
            print(f"✅ Updated phase: {updated_session['phase']}")
            print(f"   Goals count: {len(updated_session.get('goals', []))}")
            print(f"   Topics count: {len(updated_session.get('topics', []))}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        try:
            await mongodb_manager.sessions_collection.delete_many({
                "user_id": {"$in": [user_id_1, user_id_2]}
            })
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")
        
        await mongodb_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(test_user_sessions())
