from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID

class SessionCreate(BaseModel):
    """Request model for creating a new session"""
    pass

class SessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str
    message: str

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User message")

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    reply: str
    session_id: str

class PlanRequest(BaseModel):
    """Request model for generating plan"""
    pass

class PlanResponse(BaseModel):
    """Response model for plan generation"""
    goals: List[str] = Field(..., min_items=3, max_items=3)
    topics: List[str] = Field(..., min_items=12, max_items=12)
    session_id: str

class StatusResponse(BaseModel):
    """Response model for session status"""
    session_id: str
    phase: Literal["incomplete", "plan_ready"]
    goals: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

class SessionState(BaseModel):
    """Internal session state model"""
    session_id: str
    user_name: Optional[str] = None
    user_age: Optional[int] = None
    goal_type: Optional[Literal["career", "self_growth", "relationships", "no_goal"]] = None
    values: Optional[List[str]] = None
    career_now: Optional[str] = None
    career_goal: Optional[str] = None
    career_obstacles: Optional[List[str]] = None
    relation_people: Optional[str] = None
    relation_issues: Optional[str] = None
    self_growth_area: Optional[str] = None
    self_growth_field: Optional[str] = None
    no_goal_reason: Optional[str] = None
    seed_goals: Optional[List[str]] = None
    phase: Literal["incomplete", "plan_ready"] = "incomplete"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    history: List[dict] = Field(default_factory=list, description="Chat history: list of {'role': 'user'|'assistant', 'content': str}")

class MongoDBDocument(BaseModel):
    """MongoDB document model"""
    session_id: str
    goals: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    phase: Literal["incomplete", "plan_ready"] = "incomplete"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    history: List[dict] = Field(default_factory=list, description="Chat history: list of {'role': 'user'|'assistant', 'content': str}") 