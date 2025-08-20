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

@router.get("/rag/debug")
async def rag_debug():
    """Debug endpoint to check index files and paths"""
    import os
    import json
    
    debug_info = {
        "current_working_directory": os.getcwd(),
        "rag_enabled": settings.REG_ENABLED,
        "index_path": settings.RAG_INDEX_PATH,
        "corpus_path": settings.RAG_CORPUS_PATH,
        "directory_contents": {},
        "index_files": {}
    }
    
    # Check current directory contents
    try:
        debug_info["directory_contents"]["current"] = os.listdir(".")
    except Exception as e:
        debug_info["directory_contents"]["current_error"] = str(e)
    
    # Check if RAG directory exists
    try:
        if os.path.exists("RAG"):
            debug_info["directory_contents"]["rag"] = os.listdir("RAG")
            if os.path.exists("RAG/index"):
                debug_info["directory_contents"]["rag_index"] = os.listdir("RAG/index")
        else:
            debug_info["directory_contents"]["rag"] = "RAG directory not found"
    except Exception as e:
        debug_info["directory_contents"]["rag_error"] = str(e)
    
    # Check specific index files
    index_files = ["chunks.json", "embeddings.npy", "metadata.json"]
    for filename in index_files:
        file_path = f"RAG/index/{filename}"
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                debug_info["index_files"][filename] = {
                    "exists": True,
                    "size": file_size,
                    "path": file_path
                }
            else:
                debug_info["index_files"][filename] = {
                    "exists": False,
                    "path": file_path
                }
        except Exception as e:
            debug_info["index_files"][filename] = {
                "exists": False,
                "error": str(e),
                "path": file_path
            }
    
    return debug_info

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

@router.post("/rag/test/agent")
async def test_agent_with_rag():
    """Test full agent flow with RAG integration"""
    try:
        from ...cursor.core.graph_processor import GraphProcessor
        from ...cursor.core.root_graph import root_graph
        
        # Simulate a complete user journey with RAG
        test_state = {
            "session_id": "test_railway_rag_agent",
            "user_name": "John",
            "user_age": 28,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "skills": ["communication", "project management", "teamwork"],
            "goals": ["Improve leadership skills", "Build team management experience", "Develop strategic thinking"]
        }
        
        # Test retrieve_reg node
        if "retrieve_reg" in root_graph:
            try:
                reply, updated_state, next_node = GraphProcessor.process_node(
                    "retrieve_reg",
                    "I want to improve my leadership and team management skills",
                    test_state
                )
                
                retrieved_chunks = updated_state.get("retrieved_chunks", [])
                
                return {
                    "success": True,
                    "next_node": next_node,
                    "retrieved_chunks_count": len(retrieved_chunks),
                    "retrieved_chunks": retrieved_chunks[:3],  # Show first 3 chunks
                    "message": "Agent RAG integration test completed successfully"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Agent RAG test failed: {str(e)}",
                    "message": "Agent RAG integration test failed"
                }
        else:
            return {
                "success": False,
                "error": "retrieve_reg node not found",
                "message": "RAG node not available in agent"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}",
            "message": "Agent RAG test failed"
        }
