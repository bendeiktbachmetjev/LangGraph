from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from mentor_ai.app.config import settings
from mentor_ai.app.models import MongoDBDocument, SessionState

logger = logging.getLogger(__name__)

class MongoDBManager:
    """MongoDB connection and operations manager (async, motor)"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.sessions_collection = None
        
    async def connect(self):
        """Connect to MongoDB (async motor)"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DATABASE]
            self.sessions_collection = self.db.sessions
            # Проверка соединения
            await self.db.command('ping')
            logger.info("✅ Successfully connected to MongoDB (motor)")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB (motor)"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB (motor)")



    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID (async motor)"""
        try:
            session = await self.sessions_collection.find_one({"session_id": session_id})
            return session
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update session data (async motor)"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    async def save_plan(self, session_id: str, goals: list, topics: list, summary: str) -> bool:
        """Save generated plan to session (async motor)"""
        try:
            update_data = {
                "goals": goals,
                "topics": topics,
                "summary": summary,
                "phase": "plan_ready",
                "updated_at": datetime.utcnow()
            }
            result = await self.sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            logger.info(f"Saved plan for session: {session_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to save plan for session {session_id}: {e}")
            return False

    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get session by user ID (async motor)"""
        try:
            session = await self.sessions_collection.find_one({"user_id": user_id})
            return session
        except Exception as e:
            logger.error(f"Failed to get session for user {user_id}: {e}")
            return None

    async def create_session(self, session_id: str, user_id: str) -> bool:
        """Create a new session document with user ID (async motor)"""
        try:
            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "phase": "incomplete",
                # Initialize chat history with the assistant's first welcome message
                "history": [
                    {
                        "role": "assistant",
                        "content": "Hi there! 👋 This is your onboarding chat. Feel free to introduce yourself. May I ask your name and your age?"
                    }
                ],
                # Explicitly start from the first node
                "current_node": "collect_basic_info",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await self.sessions_collection.insert_one(session_doc)
            logger.info(f"Created session: {session_id} for user: {user_id}")
            return result.acknowledged
        except Exception as e:
            logger.error(f"Failed to create session {session_id} for user {user_id}: {e}")
            return False

# Global MongoDB manager instance
mongodb_manager = MongoDBManager() 