from pydantic import BaseModel, Field
from typing import Optional, Union, List

class LLMResponse(BaseModel):
    """Base model for LLM responses"""
    reply: str = Field(..., description="Response message to the user")
    next: str = Field(..., description="Next node to transition to")

class CollectBasicInfoResponse(LLMResponse):
    """LLM response for collect_basic_info node"""
    user_name: Optional[Union[str, None]] = Field(
        default=None, 
        description="Extracted user name or null if not provided"
    )
    user_age: Optional[Union[int, str, None]] = Field(
        default=None, 
        description="Extracted user age (number), 'unknown' if refused, or null if not provided"
    )
    
    class Config:
        # Allow "unavailable" as string value for fields
        extra = "forbid" 

class ClassifyCategoryResponse(LLMResponse):
    goal_type: str  # 'improve' | 'change' | 'find' | 'lost'
    
    class Config:
        extra = "forbid"

class RetrievalChunk(BaseModel):
    """Model for retrieved knowledge chunks from RAG system"""
    id: str = Field(..., description="Unique identifier for the chunk")
    title: str = Field(..., description="Title or heading of the chunk")
    snippet: str = Field(..., description="Content snippet for LLM context")
    source: str = Field(..., description="Source document or file name")
    score: Optional[float] = Field(default=None, description="Relevance score from search")
    
    class Config:
        extra = "forbid" 