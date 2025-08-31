from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from mentor_ai.cursor.modules.retrieval.retriever import RegRetriever
from mentor_ai.app.config import settings
import firebase_admin
from firebase_admin import auth
import os
import json
import time
import numpy as np
import traceback
import logging

logger = logging.getLogger(__name__)

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

@router.post("/rag/test/simple", response_model=RAGTestResponse)
async def test_rag_search_simple(request: RAGTestRequest):
    """Test RAG search functionality with simple vector search (no OpenAI API required)"""
    
    if not settings.REG_ENABLED:
        raise HTTPException(
            status_code=400, 
            detail="RAG system is not enabled. Set REG_ENABLED=true in configuration."
        )
    
    start_time = time.time()
    
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from cursor.modules.retrieval.simple_store import SimpleVectorStore
        
        # Initialize vector store
        vector_store = SimpleVectorStore()
        
        # Load index
        index_path = settings.RAG_INDEX_PATH
        if not os.path.exists(index_path):
            raise HTTPException(
                status_code=500,
                detail=f"RAG index not found at {index_path}"
            )
        
        vector_store.load(index_path)
        
        # Create a simple random embedding for the query (since we don't have OpenAI API)
        # This is just for testing the vector store functionality
        query_embedding = np.random.rand(1536).tolist()  # 1536 is the embedding dimension
        
        # Search vector store
        chunks = vector_store.search(query_embedding, top_k=request.top_k)
        
        # Convert results to response format
        snippets = []
        sources = set()
        
        for chunk in chunks:
            snippet = RAGSnippetResponse(
                title=getattr(chunk, 'title', 'Untitled'),
                content=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
                source=getattr(chunk, 'source', 'Unknown'),
                score=chunk.metadata.get("similarity_score", 0.0) if hasattr(chunk, 'metadata') and chunk.metadata else 0.0
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
        import traceback
        logger.error(f"RAG search failed: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
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

@router.post("/rag/test/plan")
async def test_plan_generation_with_rag():
    """Test plan generation with RAG knowledge"""
    try:
        from ...cursor.core.graph_processor import GraphProcessor
        from ...cursor.core.root_graph import root_graph
        
        # Test state with retrieved chunks
        test_state = {
            "session_id": "test_plan_rag",
            "user_name": "John",
            "user_age": 28,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "skills": ["communication", "project management", "teamwork"],
            "goals": ["Improve leadership skills", "Build team management experience", "Develop strategic thinking"],
            "retrieved_chunks": [
                {
                    "title": "Creative Management for Creative Teams - Section 86",
                    "content": "Goal setting, Looking, Listening, Empathising, Questioning, Giving feedback, Intuiting, Checking. Most of these appear on any standard list of coaching skills.",
                    "source": "Creative Management for Creative Teams - Mark McGuinness.pdf"
                },
                {
                    "title": "Creative Management for Creative Teams - Section 87", 
                    "content": "Coaching is a goal-focused approach, so the ability to elicit clear, well-defined and emotionally engaging goals from a coachee is one of the most important skills.",
                    "source": "Creative Management for Creative Teams - Mark McGuinness.pdf"
                },
                {
                    "title": "Creative Management for Creative Teams - Section 88",
                    "content": "SMART goals (Specific, Measurable, Attractive, Realistic and Timed). A coach will typically have the habit of thinking and asking questions from a goal-focused mindset.",
                    "source": "Creative Management for Creative Teams - Mark McGuinness.pdf"
                }
            ]
        }
        
        # Test generate_plan node
        if "generate_plan" in root_graph:
            try:
                reply, updated_state, next_node = GraphProcessor.process_node(
                    "generate_plan",
                    "Generate my 12-week plan using the coaching knowledge from the retrieved chunks",
                    test_state
                )
                
                plan = updated_state.get("plan", {})
                reply_text = updated_state.get("reply", "")
                
                # Check if all 12 weeks are present
                week_keys = [f"week_{i}_topic" for i in range(1, 13)]
                missing_weeks = [week for week in week_keys if week not in plan]
                
                return {
                    "success": True,
                    "next_node": next_node,
                    "plan_weeks_count": len(plan),
                    "all_12_weeks_present": len(missing_weeks) == 0,
                    "missing_weeks": missing_weeks,
                    "plan": plan,
                    "reply": reply_text,
                    "retrieved_chunks_used": len(test_state.get("retrieved_chunks", [])),
                    "message": "Plan generation with RAG test completed"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Plan generation failed: {str(e)}",
                    "message": "Plan generation test failed"
                }
        else:
            return {
                "success": False,
                "error": "generate_plan node not found",
                "message": "Plan generation node not available"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Test failed: {str(e)}",
            "message": "Plan generation test failed"
        }

@router.post("/rag/test/chat")
async def test_chat_with_rag():
    """Test full chat flow with RAG integration"""
    try:
        from ...cursor.core.graph_processor import GraphProcessor
        from ...cursor.core.root_graph import root_graph
        
        # Simulate a complete chat flow
        test_message = "Hi, I am John, I am 28 years old and I want to improve my leadership skills to become a team leader. I have skills in communication, project management, and teamwork. My goals are to improve leadership skills, build team management experience, and develop strategic thinking. Please generate my 12-week plan."
        
        # Initialize state
        current_state = {
            "session_id": "test_chat_rag_session",
            "user_name": "John",
            "user_age": 28,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "skills": ["communication", "project management", "teamwork"],
            "goals": ["Improve leadership skills", "Build team management experience", "Develop strategic thinking"]
        }
        
        # Step 1: Process through retrieve_reg node
        print("Processing retrieve_reg node...")
        reply1, state1, next1 = GraphProcessor.process_node(
            "retrieve_reg",
            test_message,
            current_state
        )
        
        retrieved_chunks = state1.get("retrieved_chunks", [])
        print(f"Retrieved {len(retrieved_chunks)} chunks")
        
        # Step 2: Process through generate_plan node
        print("Processing generate_plan node...")
        reply2, state2, next2 = GraphProcessor.process_node(
            "generate_plan",
            test_message,
            state1
        )
        
        plan = state2.get("plan", {})
        reply_text = state2.get("reply", "")
        
        # Check if all 12 weeks are present
        week_keys = [f"week_{i}_topic" for i in range(1, 13)]
        missing_weeks = [week for week in week_keys if week not in plan]
        
        return {
            "success": True,
            "flow": {
                "retrieve_reg": {
                    "next_node": next1,
                    "retrieved_chunks_count": len(retrieved_chunks),
                    "sample_chunks": retrieved_chunks[:2]
                },
                "generate_plan": {
                    "next_node": next2,
                    "plan_weeks_count": len(plan),
                    "all_12_weeks_present": len(missing_weeks) == 0,
                    "missing_weeks": missing_weeks,
                    "reply": reply_text
                }
            },
            "plan": plan,
            "message": "Full chat flow with RAG completed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Chat flow test failed: {str(e)}",
            "message": "Full chat flow test failed"
        }
