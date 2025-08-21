#!/usr/bin/env python3
"""
Test script for API endpoints with user authentication
"""

import requests
import json
import time

# Test configuration
import os
BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def test_api_endpoints():
    """Test API endpoints with mock authentication"""
    
    print("🧪 Testing API endpoints with user authentication...")
    
    # Mock Firebase ID token (for testing purposes)
    # In real scenario, this would be a valid Firebase ID token
    mock_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vdGVzdC1wcm9qZWN0IiwiYXVkIjoidGVzdC1wcm9qZWN0IiwiYXV0aF90aW1lIjoxNjM0NTY3ODkwLCJ1c2VyX2lkIjoidGVzdF91c2VyXzEiLCJpYXQiOjE2MzQ1Njc4OTAsImV4cCI6MTYzNDU3MTQ5MCwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyJ0ZXN0QGV4YW1wbGUuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.test_signature"
    
    headers = {
        "Authorization": f"Bearer {mock_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Create session
        print("\n1. Testing session creation...")
        response = requests.post(f"{BASE_URL}/session", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session created: {data.get('session_id')}")
            session_id = data.get('session_id')
        else:
            print(f"❌ Failed to create session: {response.text}")
            return
        
        # Test 2: Get user session
        print("\n2. Testing get user session...")
        response = requests.get(f"{BASE_URL}/user/session", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User session retrieved: {data.get('session', {}).get('session_id')}")
        else:
            print(f"❌ Failed to get user session: {response.text}")
        
        # Test 3: Get session state
        print("\n3. Testing get session state...")
        response = requests.get(f"{BASE_URL}/state/{session_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session state retrieved")
            print(f"   Phase: {data.get('state', {}).get('phase')}")
        else:
            print(f"❌ Failed to get session state: {response.text}")
        
        # Test 4: Send chat message
        print("\n4. Testing chat message...")
        chat_data = {"message": "Hello, I'm starting my onboarding!"}
        response = requests.post(f"{BASE_URL}/chat/{session_id}", headers=headers, json=chat_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat message sent")
            print(f"   Reply: {data.get('reply', '')[:100]}...")
        else:
            print(f"❌ Failed to send chat message: {response.text}")
        
        print("\n🎉 API endpoint tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {BASE_URL}")
        print("💡 To test local server: API_URL=http://localhost:8000 python test_api_endpoints.py")
        print("💡 To test Railway: API_URL=https://spotted-mom-production.up.railway.app python test_api_endpoints.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
