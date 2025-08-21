#!/usr/bin/env python3
"""
Test environment configuration loading.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_env_config():
    """Test that environment variables are loaded correctly."""
    print("🔧 Testing Environment Configuration...")
    print("=" * 50)
    
    # Test 1: Check if .env file exists
    print("\n1. 📁 Checking .env file...")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Show .env content (without API key for security)
        with open(env_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=')[1]
                    if api_key:
                        print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)} characters)")
                    else:
                        print("❌ OPENAI_API_KEY is empty")
                elif line.startswith('REG_ENABLED='):
                    reg_enabled = line.split('=')[1]
                    print(f"✅ REG_ENABLED={reg_enabled}")
    else:
        print("❌ .env file missing")
        return False
    
    # Test 2: Check if python-dotenv is installed
    print("\n2. 📦 Checking python-dotenv...")
    try:
        import dotenv
        print("✅ python-dotenv is installed")
    except ImportError:
        print("❌ python-dotenv is not installed")
        print("   Install with: pip install python-dotenv")
        return False
    
    # Test 3: Test settings loading
    print("\n3. ⚙️  Testing settings loading...")
    try:
        from mentor_ai.app.config import settings
        
        print(f"✅ Settings loaded successfully")
        print(f"   OPENAI_API_KEY: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
        print(f"   REG_ENABLED: {settings.REG_ENABLED}")
        print(f"   EMBEDDINGS_PROVIDER: {settings.EMBEDDINGS_PROVIDER}")
        print(f"   EMBEDDINGS_MODEL: {settings.EMBEDDINGS_MODEL}")
        print(f"   RAG_INDEX_PATH: {settings.RAG_INDEX_PATH}")
        print(f"   RETRIEVE_TOP_K: {settings.RETRIEVE_TOP_K}")
        
        if settings.OPENAI_API_KEY:
            print(f"   ✅ API key is loaded (length: {len(settings.OPENAI_API_KEY)} characters)")
        else:
            print("   ❌ API key is not loaded")
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Test 4: Test OpenAI API connection
    print("\n4. 🔌 Testing OpenAI API connection...")
    try:
        import openai
        
        # Set the API key
        openai.api_key = settings.OPENAI_API_KEY
        
        # Test a simple API call
        print("   Testing embeddings API...")
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input="test"
        )
        
        if response and 'data' in response:
            print("   ✅ OpenAI API connection successful")
            print(f"   📊 Embedding dimension: {len(response['data'][0]['embedding'])}")
        else:
            print("   ❌ OpenAI API response invalid")
            
    except Exception as e:
        print(f"   ❌ OpenAI API test failed: {e}")
        print("   This might be due to:")
        print("   - Invalid API key")
        print("   - Network issues")
        print("   - OpenAI service issues")
    
    print("\n" + "=" * 50)
    print("🎉 Environment Configuration Test Complete!")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Environment Configuration Test...")
    
    success = test_env_config()
    
    if success:
        print("\n✅ Environment configuration is working!")
    else:
        print("\n❌ Environment configuration test failed.")
        sys.exit(1)
