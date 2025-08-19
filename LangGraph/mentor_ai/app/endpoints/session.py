from fastapi import APIRouter, HTTPException, Depends
from uuid import uuid4
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.models import SessionResponse
from fastapi import Path
from fastapi.responses import JSONResponse
import json
from bson import ObjectId
from datetime import datetime
import firebase_admin
from firebase_admin import auth
from fastapi import Request

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

async def get_current_user(request: Request):
    """Extract user ID from Firebase ID token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")
    id_token = auth_header.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token["uid"]  # Return Firebase user ID
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth token")

router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session(user_id: str = Depends(get_current_user)):
    """Create a new onboarding session for the authenticated user"""
    # Check if user already has a session
    existing_session = await mongodb_manager.get_user_session(user_id)
    if existing_session:
        return SessionResponse(
            session_id=existing_session["session_id"], 
            message="User session already exists"
        )
    
    # Create new session for user
    session_id = str(uuid4())
    success = await mongodb_manager.create_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return SessionResponse(session_id=session_id, message="Session created successfully")

@router.get("/goal/{session_id}")
async def get_user_goal(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
):
    """Get the user's main goal for the session (career_goal, self_growth_area, relation_issues, no_goal_reason)"""
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    # Определяем цель в зависимости от ветки
    goal = state.get("career_goal") or state.get("self_growth_goal") or state.get("relation_issues") or state.get("no_goal_reason")
    
    # Ограничиваем цель до 4 слов максимум
    if goal:
        words = goal.split()[:4]  # Берем только первые 4 слова
        goal = " ".join(words)
    
    return JSONResponse({"session_id": session_id, "goal": goal})

@router.get("/topics/{session_id}")
async def get_user_topics(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
):
    """Get the user's 12-week plan topics for the session"""
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    topics = state.get("plan") or state.get("topics")
    return JSONResponse({"session_id": session_id, "topics": topics}) 

@router.get("/state/{session_id}")
async def get_full_state(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
):
    """
    Get the full internal state for a given session.
    This endpoint is intended for debugging and integration purposes.
    Returns the entire state object stored in MongoDB for the session.
    If the session is not found, returns 404.
    """
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    return JSONResponse({"session_id": session_id, "state": to_serializable(state)})

@router.get("/user/session")
async def get_user_session(user_id: str = Depends(get_current_user)):
    """Get the current user's session"""
    session = await mongodb_manager.get_user_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="No session found for user")
    return JSONResponse({"session": to_serializable(session)}) 