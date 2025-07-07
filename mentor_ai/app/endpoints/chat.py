from fastapi import APIRouter, HTTPException, Path
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.models import ChatRequest, ChatResponse
from mentor_ai.cursor.core import GraphProcessor

router = APIRouter()

@router.post("/chat/{session_id}", response_model=ChatResponse)
async def chat_with_session(
    session_id: str = Path(..., description="Session ID"),
    request: ChatRequest = ...
):
    """Process user message for a given session_id with automatic node transitions"""
    # Get current state from MongoDB
    state = await mongodb_manager.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Determine current node (default: collect_basic_info)
    node_id = state.get("current_node", "collect_basic_info")
    user_message = request.message
    reply = None
    updated_state = state
    next_node = node_id
    first_iteration = True

    while True:
        try:
            reply, updated_state, next_node = GraphProcessor.process_node(
                node_id=next_node,
                user_message=user_message if first_iteration else "",
                current_state=updated_state
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM processing error: {e}")
        
        # Update state in DB after each node
        updated_state["current_node"] = next_node
        await mongodb_manager.update_session(session_id, updated_state)

        # Определяем, нужен ли пользовательский ввод для следующего узла
        # Если это первый шаг — всегда возвращаем reply
        # Если следующий узел требует пользовательского ввода — выходим из цикла
        # Для простоты: если reply не пустой и не автогенерированный — возвращаем
        # (Можно доработать: добавить флаг в Node, что требуется user input)
        if first_iteration:
            first_iteration = False
        else:
            # Если reply не пустой — значит, LLM ждёт ответа пользователя
            if reply:
                break
        # Если reply пустой — значит, можно переходить дальше автоматически
        # (или если реализован специальный флаг в Node — использовать его)
        # Здесь можно добавить более строгую проверку по типу узла
        user_message = ""  # После первого шага user_message больше не нужен
        node_id = next_node
        # Safety: ограничение на количество автоматических переходов (чтобы не зациклиться)
        if node_id == "exit_to_plan":
            break
    
    return ChatResponse(reply=reply, session_id=session_id) 