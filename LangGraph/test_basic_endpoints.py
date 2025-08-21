#!/usr/bin/env python3
"""
Test script for basic API endpoints without authentication
"""

import requests
import json

# Test configuration
import os
BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def test_basic_endpoints():
    """Test basic API endpoints without authentication"""
    
    print("🧪 Testing basic API endpoints...")
    
    try:
        # Test 1: Check if server is running
        print("\n1. Testing server availability...")
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("❌ Server is not accessible")
            return
        
        # Test 2: Check OpenAPI schema
        print("\n2. Testing OpenAPI schema...")
        response = requests.get(f"{BASE_URL}/openapi.json")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            print(f"✅ OpenAPI schema loaded")
            print(f"   Available endpoints: {len(paths)}")
            
            # List available endpoints
            for path in paths.keys():
                print(f"   - {path}")
        else:
            print("❌ Failed to load OpenAPI schema")
        
        # Test 3: Test session creation without auth (should fail)
        print("\n3. Testing session creation without auth...")
        response = requests.post(f"{BASE_URL}/session")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
        
        # Test 4: Test user session without auth (should fail)
        print("\n4. Testing user session without auth...")
        response = requests.get(f"{BASE_URL}/user/session")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
        
        print("\n🎉 Basic endpoint tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {BASE_URL}")
        print("💡 To test local server: API_URL=http://localhost:8000 python test_basic_endpoints.py")
        print("💡 To test Railway: API_URL=https://spotted-mom-production.up.railway.app python test_basic_endpoints.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_basic_endpoints()
