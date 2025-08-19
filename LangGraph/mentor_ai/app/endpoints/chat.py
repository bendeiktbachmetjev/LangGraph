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
    
    # Ensure history exists
    if "history" not in state or not isinstance(state["history"], list):
        state["history"] = []
    
    # Determine current node (default: collect_basic_info)
    node_id = state.get("current_node", "collect_basic_info")
    user_message = request.message
    reply = None
    updated_state = state
    next_node = node_id
    first_iteration = True

    # Добавляем сообщение пользователя в историю (только для первого шага)
    if user_message:
        updated_state["history"].append({"role": "user", "content": user_message})

    while True:
        try:
            reply, updated_state, next_node = GraphProcessor.process_node(
                node_id=next_node,
                user_message=user_message if first_iteration else "",
                current_state=updated_state
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")
        
        # После получения ответа от LLM добавляем его в историю (только если есть reply)
        if reply:
            updated_state["history"].append({"role": "assistant", "content": reply})

        # Update state in DB after each node
        updated_state["current_node"] = next_node
        await mongodb_manager.update_session(session_id, updated_state)

        # Определяем, нужен ли пользовательский ввод для следующего узла
        if first_iteration:
            first_iteration = False
        else:
            if reply:
                break
        user_message = ""
        node_id = next_node
        if node_id == "exit_to_plan":
            break
    
    return ChatResponse(reply=reply, session_id=session_id) 