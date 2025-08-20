from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
from mentor_ai.app.config import settings
import firebase_admin
from firebase_admin import auth

router = APIRouter()

class RAGTestRequest(BaseModel):
    query: str
    top_k: int = 3
    include_sources: bool = True

class RAGSnippetResponse(BaseModel):
    title: str
    content: str
    source: str
    score: float

class RAGTestResponse(BaseModel):
    query: str
    snippets: List[RAGSnippetResponse]
    sources: List[str]
    total_found: int
    search_time_ms: float

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

@router.post("/rag/test", response_model=RAGTestResponse)
async def test_rag_search(
    request: RAGTestRequest,
    user_id: str = Depends(get_current_user)
):
    """Test RAG search functionality with a simple query"""
    import time
    
    if not settings.REG_ENABLED:
        raise HTTPException(
            status_code=400, 
            detail="RAG system is not enabled. Set REG_ENABLED=true in configuration."
        )
    
    start_time = time.time()
    
    try:
        # Initialize retriever
        retriever = RegRetriever()
        
        # Perform search
        results = retriever.search(
            query=request.query,
            top_k=request.top_k
        )
        
        # Convert results to response format
        snippets = []
        sources = set()
        
        for result in results:
            snippet = RAGSnippetResponse(
                title=result.get("title", "Untitled"),
                content=result.get("content", ""),
                source=result.get("source", "Unknown"),
                score=result.get("score", 0.0)
            )
            snippets.append(snippet)
            sources.add(snippet.source)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return RAGTestResponse(
            query=request.query,
            snippets=snippets,
            sources=list(sources),
            total_found=len(snippets),
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"RAG search failed: {str(e)}"
        )

@router.get("/rag/status")
async def rag_status():
    """Get RAG system status"""
    return {
        "enabled": settings.REG_ENABLED,
        "status": "operational" if settings.REG_ENABLED else "disabled"
    }

@router.post("/rag/test/dev", response_model=RAGTestResponse)
async def test_rag_search_dev(request: RAGTestRequest):
    """Test RAG search functionality without authentication (development only)"""
    import time
    
    if not settings.REG_ENABLED:
        raise HTTPException(
            status_code=400, 
            detail="RAG system is not enabled. Set REG_ENABLED=true in configuration."
        )
    
    start_time = time.time()
    
    try:
        # Initialize retriever
        retriever = RegRetriever()
        
        # Perform search
        results = retriever.search(
            query=request.query,
            top_k=request.top_k
        )
        
        # Convert results to response format
        snippets = []
        sources = set()
        
        for result in results:
            snippet = RAGSnippetResponse(
                title=result.get("title", "Untitled"),
                content=result.get("content", ""),
                source=result.get("source", "Unknown"),
                score=result.get("score", 0.0)
            )
            snippets.append(snippet)
            sources.add(snippet.source)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return RAGTestResponse(
            query=request.query,
            snippets=snippets,
            sources=list(sources),
            total_found=len(snippets),
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"RAG search failed: {str(e)}"
        )
