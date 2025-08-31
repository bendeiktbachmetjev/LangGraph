import asyncio
import requests
import json
from app.storage.mongodb import mongodb_manager

async def check_mongodb_state():
    """Check MongoDB state after processing user message"""
    
    # 1. Create session
    resp = requests.post("http://localhost:8000/session")
    session_id = resp.json()["session_id"]
    print(f"Created session: {session_id}")
    
    # 2. Send message
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    resp = requests.post(f"http://localhost:8000/chat/{session_id}", json=chat_payload)
    print(f"Chat response: {resp.json()}")
    
    # 3. Check MongoDB state
    await mongodb_manager.connect()
    state = await mongodb_manager.get_session(session_id)
    print(f"\nMongoDB state:")
    print(json.dumps(state, indent=2, default=str))
    
    await mongodb_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(check_mongodb_state()) 