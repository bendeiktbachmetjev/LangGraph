import pytest
from unittest.mock import patch, Mock
from mentor_ai.cursor.core.graph_processor import GraphProcessor

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_collect_basic_info(mock_llm_client):
    """Test processing collect_basic_info node with complete information"""
    # Mock LLM response
    mock_llm_client.call_llm.return_value = '{"reply": "Nice to meet you, John!", "user_name": "John", "user_age": 25, "next": "classify_category"}'
    
    # Test data
    node_id = "collect_basic_info"
    user_message = "Hi, my name is John and I'm 25."
    current_state = {"session_id": "test123"}
    
    # Process node
    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)
    
    # Verify results
    assert reply == "Nice to meet you, John!"
    assert updated_state["user_name"] == "John"
    assert updated_state["user_age"] == 25
    assert updated_state["session_id"] == "test123"
    assert next_node == "classify_category"
    
    # Verify LLM was called
    mock_llm_client.call_llm.assert_called_once()

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_incomplete_info(mock_llm_client):
    """Test processing collect_basic_info node with incomplete information"""
    # Mock LLM response for incomplete info
    mock_llm_client.call_llm.return_value = '{"reply": "What\'s your age?", "user_name": "John", "user_age": null, "next": "collect_basic_info"}'
    
    # Test data
    node_id = "collect_basic_info"
    user_message = "Hi, my name is John."
    current_state = {"session_id": "test123"}
    
    # Process node
    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)
    
    # Verify results
    assert reply == "What's your age?"
    assert updated_state["user_name"] == "John"
    assert "user_age" not in updated_state  # Should not be added if null
    assert next_node == "collect_basic_info"  # Should stay in same node

def test_process_node_unknown_node():
    """Test processing unknown node"""
    with pytest.raises(ValueError, match="Unknown node"):
        GraphProcessor.process_node("unknown_node", "test message", {"session_id": "test123"}) 

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_classify_category(mock_llm_client):
    """Test processing classify_category node with clear goal type"""
    # Mock LLM response
    mock_llm_client.call_llm.return_value = '{"reply": "Great, let\'s focus on your career!", "goal_type": "career", "next": "improve_intro"}'

    node_id = "classify_category"
    user_message = "I want to improve my career."
    current_state = {"session_id": "test123"}

    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)

    assert reply == "Great, let's focus on your career!"
    assert updated_state["goal_type"] == "career"
    assert updated_state["session_id"] == "test123"
    assert next_node == "improve_intro"
    mock_llm_client.call_llm.assert_called_once() 

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_improve_intro(mock_llm_client):
    """Test processing improve_intro node with automatic transition"""
    # Mock LLM response
    mock_llm_client.call_llm.return_value = '{"reply": "Let\'s talk about your career! In the next steps, I\'ll ask a few questions to help you clarify your career goals and challenges. Ready?", "next": "career_goal"}'

    node_id = "improve_intro"
    user_message = ""
    current_state = {"session_id": "test123"}

    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)

    assert "career" in reply.lower()
    assert updated_state["session_id"] == "test123"
    assert next_node == "career_goal"
    mock_llm_client.call_llm.assert_called_once()

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_improve_obstacles_success(mock_llm_client):
    """Test processing improve_obstacles node with valid obstacles"""
    mock_llm_client.call_llm.return_value = '{"reply": "Thank you for sharing your obstacles. I will now generate a personalized plan for you.", "goals": ["Lack of experience", "Low confidence"], "next": "generate_plan"}'
    node_id = "improve_obstacles"
    user_message = "I lack experience and confidence."
    current_state = {"session_id": "test123"}
    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)
    assert "thank" in reply.lower() and "plan" in reply.lower()
    assert updated_state["goals"] == ["Lack of experience", "Low confidence"]
    assert next_node == "generate_plan"
    mock_llm_client.call_llm.assert_called_once()

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_improve_obstacles_clarify(mock_llm_client):
    """Test processing improve_obstacles node with unclear answer (should clarify)"""
    mock_llm_client.call_llm.return_value = '{"reply": "Could you clarify your main obstacles?", "goals": null, "next": "improve_obstacles"}'
    node_id = "improve_obstacles"
    user_message = "I don't know, maybe something..."
    current_state = {"session_id": "test123"}
    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)
    assert "clarify" in reply.lower() or "obstacle" in reply.lower()
    assert "goals" not in updated_state or updated_state["goals"] is None
    assert next_node == "improve_obstacles"
    mock_llm_client.call_llm.assert_called_once()

@patch('mentor_ai.cursor.core.graph_processor.llm_client')
def test_process_node_generate_plan(mock_llm_client):
    """Test processing generate_plan node with 12 personalized topics"""
    mock_llm_client.call_llm.return_value = '{"reply": "Here is your 12-week plan!","plan": {"week_1_topic": "Wheel of Life","week_2_topic": "Zone of Genius","week_3_topic": "Networking","week_4_topic": "Feedback","week_5_topic": "Time Management","week_6_topic": "Personal Branding","week_7_topic": "Mentorship","week_8_topic": "Emotional Intelligence","week_9_topic": "Goal Setting","week_10_topic": "Resilience","week_11_topic": "Strategic Thinking","week_12_topic": "Review & Celebrate"},"next": "week1_chat"}'
    node_id = "generate_plan"
    user_message = ""
    current_state = {"session_id": "test123", "goal_type": "career", "career_goal": "Become a CTO"}
    reply, updated_state, next_node = GraphProcessor.process_node(node_id, user_message, current_state)
    assert "plan" in reply.lower()
    assert isinstance(updated_state["plan"], dict)
    assert len(updated_state["plan"]) == 12
    assert updated_state["plan"]["week_1_topic"] == "Wheel of Life"
    assert updated_state["plan"]["week_12_topic"] == "Review & Celebrate"
    assert next_node == "week1_chat"
    mock_llm_client.call_llm.assert_called_once()