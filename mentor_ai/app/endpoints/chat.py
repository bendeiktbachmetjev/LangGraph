from fastapi import APIRouter, HTTPException, Path, Depends, Request
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.models import ChatRequest, ChatResponse
from mentor_ai.cursor.core import GraphProcessor
import firebase_admin
from firebase_admin import auth

router = APIRouter()

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

@router.post("/chat/{session_id}", response_model=ChatResponse)
async def chat_with_session(
    session_id: str = Path(..., description="Session ID"),
    request: ChatRequest = ..., 
    user_id: str = Depends(get_current_user)
):
    """Process user message for a given session_id with automatic node transitions"""
    # Get current state from MongoDB
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    # Ensure history exists for frontend compatibility
    if "history" not in state or not isinstance(state["history"], list):
        state["history"] = []
    
    # Initialize memory fields if not present (for new sessions)
    if "prompt_context" not in state:
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        state["prompt_context"] = MemoryManager.initialize_prompt_context()
    if "message_count" not in state:
        state["message_count"] = 0
    if "current_week" not in state:
        state["current_week"] = 1
    
    # Determine current node (default: collect_basic_info)
    node_id = state.get("current_node", "collect_basic_info")
    user_message = request.message
    reply = None
    updated_state = state.copy()
    next_node = node_id

    # FIRST: Update state with user message BEFORE processing
    # This ensures the agent sees the latest user message
    if user_message:
        # Add user message to history first
        if not any(msg.get("content") == user_message for msg in updated_state.get("history", [])):
            updated_state["history"].append({"role": "user", "content": user_message})
        
        # Update memory system with user message
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        new_message = {"role": "user", "content": user_message}
        updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
        
        # Evaluate important facts from user message
        important_facts = MemoryManager.evaluate_important_facts(updated_state, new_message)
        for fact in important_facts:
            updated_state = MemoryManager.add_important_fact(updated_state, fact)

    # SECOND: Now process the node with updated state
    try:
        reply, updated_state, next_node = GraphProcessor.process_node(
            node_id=next_node,
            user_message=user_message,
            current_state=updated_state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")

    # THIRD: Add assistant reply to history
    if reply and not any(msg.get("content") == reply for msg in updated_state.get("history", [])):
        updated_state["history"].append({"role": "assistant", "content": reply})

    updated_state["current_node"] = next_node
    await mongodb_manager.update_session(session_id, updated_state)

    return ChatResponse(reply=reply, session_id=session_id)

@router.post("/chat/{session_id}/test", response_model=ChatResponse)
async def test_chat_without_auth(
    session_id: str = Path(..., description="Session ID"),
    request: ChatRequest = ...
):
    """Temporary endpoint for testing without authentication"""
    # Get current state from MongoDB
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Ensure history exists for frontend compatibility
    if "history" not in state or not isinstance(state["history"], list):
        state["history"] = []
    
    # Initialize memory fields if not present (for new sessions)
    if "prompt_context" not in state:
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        state["prompt_context"] = MemoryManager.initialize_prompt_context()
    if "message_count" not in state:
        state["message_count"] = 0
    if "current_week" not in state:
        state["current_week"] = 1
    
    # Determine current node (default: collect_basic_info)
    node_id = state.get("current_node", "collect_basic_info")
    user_message = request.message
    reply = None
    updated_state = state.copy()
    next_node = node_id

    # FIRST: Update state with user message BEFORE processing
    if user_message:
        # Add user message to history first
        if not any(msg.get("content") == user_message for msg in updated_state.get("history", [])):
            updated_state["history"].append({"role": "user", "content": user_message})
        
        # Update memory system with user message
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        new_message = {"role": "user", "content": user_message}
        updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
        
        # Evaluate important facts from user message
        important_facts = MemoryManager.evaluate_important_facts(updated_state, new_message)
        for fact in important_facts:
            updated_state = MemoryManager.add_important_fact(updated_state, fact)

    # SECOND: Now process the node with updated state
    try:
        reply, updated_state, next_node = GraphProcessor.process_node(
            node_id=next_node,
            user_message=user_message,
            current_state=updated_state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")

    # THIRD: Add assistant reply to history
    if reply and not any(msg.get("content") == reply for msg in updated_state.get("history", [])):
        updated_state["history"].append({"role": "assistant", "content": reply})

    updated_state["current_node"] = next_node
    await mongodb_manager.update_session(session_id, updated_state)

    return ChatResponse(reply=reply, session_id=session_id)

@router.get("/chat/{session_id}/memory-stats")
async def get_memory_stats(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(get_current_user)
):
    """Get memory statistics for a session"""
    # Get current state from MongoDB
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    # Get memory statistics
    from mentor_ai.cursor.core.graph_processor import GraphProcessor
    memory_stats = GraphProcessor.get_memory_stats(state)
    
    return {
        "session_id": session_id,
        "memory_stats": memory_stats
    }

@router.post("/chat/{session_id}/memory-control")
async def control_memory_usage(
    session_id: str = Path(..., description="Session ID"),
    request: dict = ...,  # {"use_memory": bool, "message": str}
    user_id: str = Depends(get_current_user)
):
    """Process message with optional memory control"""
    # Get current state from MongoDB
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session belongs to user
    if state.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this session")
    
    # Ensure history exists for frontend compatibility
    if "history" not in state or not isinstance(state["history"], list):
        state["history"] = []
    
    # Initialize memory fields if not present
    if "prompt_context" not in state:
        from mentor_ai.cursor.core.memory_manager import MemoryManager
        state["prompt_context"] = MemoryManager.initialize_prompt_context()
    if "message_count" not in state:
        state["message_count"] = 0
    if "current_week" not in state:
        state["current_week"] = 1
    
    # Extract parameters
    use_memory = request.get("use_memory", True)
    user_message = request.get("message", "")
    
    # Determine current node
    node_id = state.get("current_node", "collect_basic_info")
    reply = None
    updated_state = state
    next_node = node_id

    # Process with memory control
    try:
        reply, updated_state, next_node = GraphProcessor.process_node_with_memory_control(
            node_id=next_node,
            user_message=user_message,
            current_state=updated_state,
            use_memory=use_memory
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")

    # Ensure history is updated for frontend compatibility
    if user_message and not any(msg.get("content") == user_message for msg in updated_state.get("history", [])):
        updated_state["history"].append({"role": "user", "content": user_message})
    if reply and not any(msg.get("content") == reply for msg in updated_state.get("history", [])):
        updated_state["history"].append({"role": "assistant", "content": reply})

    updated_state["current_node"] = next_node
    await mongodb_manager.update_session(session_id, updated_state)

    return {
        "reply": reply,
        "session_id": session_id,
        "memory_used": use_memory,
        "memory_stats": GraphProcessor.get_memory_stats(updated_state)
    }