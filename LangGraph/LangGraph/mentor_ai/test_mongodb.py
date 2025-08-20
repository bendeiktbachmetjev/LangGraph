#!/usr/bin/env python3
"""
Simple MongoDB connection test
"""
import asyncio
import os
from dotenv import load_dotenv
from app.storage.mongodb import mongodb_manager

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if MongoDB URI is set
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri or "<db_password>" in mongo_uri:
            print("❌ Please set your MongoDB password in .env file")
            print("   Replace <db_password> with your actual password")
            return False
        
        # Try to connect
        await mongodb_manager.connect()
        print("✅ MongoDB connection successful!")
        
        # Test basic operations
        test_session_id = "test_session_123"
        
        # Create session
        success = await mongodb_manager.create_session(test_session_id)
        if success:
            print("✅ Session creation successful!")
        else:
            print("❌ Session creation failed!")
            return False
        
        # Get session
        session = await mongodb_manager.get_session(test_session_id)
        if session:
            print("✅ Session retrieval successful!")
        else:
            print("❌ Session retrieval failed!")
            return False
        
        # Cleanup
        await mongodb_manager.disconnect()
        print("✅ MongoDB test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection()) 