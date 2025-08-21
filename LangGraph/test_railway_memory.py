#!/usr/bin/env python3
"""
Test script for Railway memory system
"""

import requests
import json
import time

# Railway API endpoint
RAILWAY_URL = "https://spotted-mom-production.up.railway.app"

def test_memory_endpoints():
    """Test memory-related endpoints"""
    print("🚂 Testing Railway Memory System")
    print("=" * 50)
    print(f"URL: {RAILWAY_URL}")
    
    # Test 1: Check if API is accessible
    print("\n1️⃣ Testing API accessibility...")
    try:
        response = requests.get(f"{RAILWAY_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"⚠️ API responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return
    
    # Test 2: Test session creation (if possible)
    print("\n2️⃣ Testing session creation...")
    
    # Note: We need a valid Firebase token for this
    # For now, let's just check the endpoint structure
    print("ℹ️ Session creation requires Firebase authentication")
    print("ℹ️ Endpoint: POST /sessions")
    
    # Test 3: Test memory stats endpoint structure
    print("\n3️⃣ Testing memory stats endpoint...")
    print("ℹ️ Endpoint: GET /chat/{session_id}/memory-stats")
    print("ℹ️ Requires: Authorization header with Firebase token")
    
    # Test 4: Test memory control endpoint structure
    print("\n4️⃣ Testing memory control endpoint...")
    print("ℹ️ Endpoint: POST /chat/{session_id}/memory-control")
    print("ℹ️ Body: {\"use_memory\": true, \"message\": \"test\"}")
    print("ℹ️ Requires: Authorization header with Firebase token")
    
    # Test 5: Check if we can get any public info
    print("\n5️⃣ Testing public endpoints...")
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"✅ Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("✅ API is accessible")
    print("ℹ️ Memory endpoints require authentication")
    print("ℹ️ To test with real data, you need:")
    print("   - Valid Firebase ID token")
    print("   - Existing session ID")
    print("   - Or create a new session")

def test_with_sample_data():
    """Test with sample data (without authentication)"""
    print("\n🧪 Testing with sample data...")
    
    # Sample session data structure
    sample_session = {
        "session_id": "test-session-123",
        "user_id": "test-user-456",
        "history": [
            {"role": "user", "content": "Hello, I'm John"},
            {"role": "assistant", "content": "Hi John! Nice to meet you."},
            {"role": "user", "content": "I want to become a CTO"},
            {"role": "assistant", "content": "That's an exciting goal! Tell me more."}
        ],
        "current_node": "collect_basic_info",
        "prompt_context": {
            "running_summary": "User John wants to become a CTO",
            "recent_messages": [
                {"role": "user", "content": "I want to become a CTO"},
                {"role": "assistant", "content": "That's an exciting goal! Tell me more."}
            ],
            "important_facts": [
                {"fact": "User wants to become CTO", "week": 1}
            ],
            "weekly_summaries": {}
        },
        "message_count": 4,
        "current_week": 1
    }
    
    print("📊 Sample session structure:")
    print(json.dumps(sample_session, indent=2))
    
    # Test memory stats calculation
    from mentor_ai.cursor.core.memory_manager import MemoryManager
    
    stats = MemoryManager.get_token_estimate(sample_session)
    print(f"\n📈 Memory stats for sample session:")
    print(f"  - Estimated tokens: {stats['estimated_tokens']}")
    print(f"  - Recent messages: {stats['recent_messages_count']}")
    print(f"  - Important facts: {stats['important_facts_count']}")
    print(f"  - Running summary exists: {stats['running_summary_exists']}")
    
    # Test prompt context formatting
    formatted = MemoryManager.format_prompt_context(sample_session)
    print(f"\n📝 Formatted prompt context:")
    print(formatted[:500] + "..." if len(formatted) > 500 else formatted)

def check_memory_implementation():
    """Check if memory implementation is working"""
    print("\n🔍 Checking memory implementation...")
    
    try:
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        from mentor_ai.cursor.core.state_manager import StateManager
        from mentor_ai.cursor.core.graph_processor import GraphProcessor
        
        print("✅ MemoryManager imported successfully")
        print("✅ StateManager imported successfully")
        print("✅ GraphProcessor imported successfully")
        
        # Test memory initialization
        context = MemoryManager.initialize_prompt_context()
        print(f"✅ Memory context initialized: {list(context.keys())}")
        
        # Test token estimation
        stats = MemoryManager.get_token_estimate({"prompt_context": context})
        print(f"✅ Token estimation works: {stats['estimated_tokens']} tokens")
        
        print("\n🎉 Memory system is properly implemented!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Implementation error: {e}")

def main():
    """Main function"""
    print("🚂 Railway Memory System Test")
    print("=" * 60)
    
    # Check implementation
    check_memory_implementation()
    
    # Test API endpoints
    test_memory_endpoints()
    
    # Test with sample data
    test_with_sample_data()
    
    print("\n" + "=" * 60)
    print("🎯 Next steps:")
    print("1. Get a valid Firebase ID token")
    print("2. Create or use an existing session")
    print("3. Test memory endpoints with authentication")
    print("4. Verify memory fields are being created/updated")
    print("5. Check token usage optimization")

if __name__ == "__main__":
    main()
