"""
Pydantic schemas for retrieval module.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentChunk(BaseModel):
    """Represents a chunk of document text with metadata."""
    
    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="Text content of the chunk")
    title: str = Field(..., description="Title of the source document")
    source: str = Field(..., description="Source file path")
    chunk_index: int = Field(..., description="Index of this chunk within the document")
    start_char: int = Field(..., description="Starting character position in original document")
    end_char: int = Field(..., description="Ending character position in original document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RetrievalResult(BaseModel):
    """Result of a retrieval operation."""
    
    chunks: List[DocumentChunk] = Field(..., description="Retrieved document chunks")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional search metadata")
    
    def to_snippets(self, max_chars: int = 3000) -> List[Dict[str, str]]:
        """Convert chunks to simplified snippets for LLM context."""
        snippets = []
        total_chars = 0
        
        for chunk in self.chunks:
            # Create snippet with title and content
            snippet = {
                "title": chunk.title,
                "content": chunk.content[:500],  # Limit individual snippet length
                "source": chunk.source
            }
            
            snippet_chars = len(snippet["title"]) + len(snippet["content"])
            if total_chars + snippet_chars > max_chars:
                break
                
            snippets.append(snippet)
            total_chars += snippet_chars
            
        return snippets
