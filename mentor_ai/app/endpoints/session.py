from fastapi import APIRouter, HTTPException
from uuid import uuid4
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.models import SessionResponse
from fastapi import Path
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new onboarding session and return session_id"""
    session_id = str(uuid4())
    success = await mongodb_manager.create_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return SessionResponse(session_id=session_id, message="Session created successfully")

@router.get("/goal/{session_id}")
async def get_user_goal(session_id: str = Path(..., description="Session ID")):
    """Get the user's main goal for the session (career_goal, self_growth_area, relation_issues, no_goal_reason)"""
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    # Определяем цель в зависимости от ветки
    goal = state.get("career_goal") or state.get("self_growth_goal") or state.get("relation_issues") or state.get("no_goal_reason")
    
    # Ограничиваем цель до 4 слов максимум
    if goal:
        words = goal.split()[:4]  # Берем только первые 4 слова
        goal = " ".join(words)
    
    return JSONResponse({"session_id": session_id, "goal": goal})

@router.get("/topics/{session_id}")
async def get_user_topics(session_id: str = Path(..., description="Session ID")):
    """Get the user's 12-week plan topics for the session"""
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    topics = state.get("plan") or state.get("topics")
    return JSONResponse({"session_id": session_id, "topics": topics}) 

@router.get("/state/{session_id}")
async def get_full_state(session_id: str = Path(..., description="Session ID")):
    """
    Get the full internal state for a given session.
    This endpoint is intended for debugging and integration purposes.
    Returns the entire state object stored in MongoDB for the session.
    If the session is not found, returns 404.
    """
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse({"session_id": session_id, "state": state}) 