import pytest
from mentor_ai.cursor.core.root_graph import root_graph
from mentor_ai.cursor.core.prompting import generate_llm_prompt

def test_generate_llm_prompt_collect_basic_info():
    node = root_graph["collect_basic_info"]
    state = {"session_id": "test123"}
    user_message = "Hi, my name is John and I'm 25."
    prompt = generate_llm_prompt(node, state, user_message)
    
    # Check basic structure
    assert "System:" in prompt
    assert node.system_prompt in prompt
    assert "Assistant:" in prompt
    assert node.assistant_prompt in prompt
    assert "User:" in prompt
    assert user_message in prompt
    assert "Current state:" in prompt
    assert "test123" in prompt
    
    # Check JSON instructions
    assert "Please respond in JSON format" in prompt
    assert '"reply":' in prompt
    assert '"user_name":' in prompt
    assert '"user_age":' in prompt
    assert '"next":' in prompt
    assert "unavailable" in prompt
    assert "null" in prompt 