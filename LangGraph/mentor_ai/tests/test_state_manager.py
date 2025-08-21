import pytest
from mentor_ai.cursor.core.state_manager import StateManager
from mentor_ai.cursor.core.root_graph import root_graph

def test_parse_llm_response_valid():
    """Test parsing valid LLM response"""
    node = root_graph["collect_basic_info"]
    llm_response = '{"reply": "Nice to meet you, John!", "user_name": "John", "user_age": 25, "next": "classify_category"}'
    
    result = StateManager.parse_llm_response(llm_response, node)
    assert result["reply"] == "Nice to meet you, John!"
    assert result["user_name"] == "John"
    assert result["user_age"] == 25
    assert result["next"] == "classify_category"

def test_parse_llm_response_invalid_json():
    """Test parsing invalid JSON response"""
    node = root_graph["collect_basic_info"]
    llm_response = '{"reply": "Hello", "user_name": "John"'  # Invalid JSON
    
    with pytest.raises(ValueError, match="Invalid JSON response"):
        StateManager.parse_llm_response(llm_response, node)

def test_update_state_complete_info():
    """Test state update with complete information"""
    node = root_graph["collect_basic_info"]
    current_state = {"session_id": "test123"}
    llm_data = {
        "reply": "Nice to meet you, John!",
        "user_name": "John",
        "user_age": 25,
        "next": "classify_category"
    }
    
    updated_state = StateManager.update_state(current_state, llm_data, node)
    assert updated_state["user_name"] == "John"
    assert updated_state["user_age"] == 25
    assert "updated_at" in updated_state
    assert updated_state["session_id"] == "test123"

def test_update_state_unavailable():
    """Test state update when user refuses to provide information"""
    node = root_graph["collect_basic_info"]
    current_state = {"session_id": "test123"}
    llm_data = {
        "reply": "No problem, we can proceed.",
        "user_name": "unavailable",
        "user_age": None,
        "next": "classify_category"
    }
    
    updated_state = StateManager.update_state(current_state, llm_data, node)
    assert updated_state["user_name"] == "unavailable"
    assert "user_age" not in updated_state

def test_get_next_node():
    """Test determining next node"""
    node = root_graph["collect_basic_info"]
    llm_data = {"next": "classify_category"}
    updated_state = {"user_name": "John", "user_age": 25}
    
    next_node = StateManager.get_next_node(llm_data, node, updated_state)
    assert next_node == "classify_category" 