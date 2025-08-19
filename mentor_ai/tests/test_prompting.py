import pytest
from mentor_ai.cursor.core.root_graph import root_graph
from mentor_ai.cursor.core.prompting import generate_llm_prompt

def test_generate_llm_prompt_collect_basic_info():
    node = root_graph["collect_basic_info"]
    state = {"session_id": "test123"}  # История пуста
    user_message = "Hi, my name is John and I'm 25."
    prompt = generate_llm_prompt(node, state, user_message)
    
    # Check basic structure
    assert "System:" in prompt
    assert node.system_prompt in prompt
    # История пуста — не проверяем наличие 'User:'
    # assert "User:" in prompt
    # assert user_message in prompt
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

def test_generate_llm_prompt_with_history():
    node = root_graph["collect_basic_info"]
    state = {
        "session_id": "test123",
        "history": [
            {"role": "user", "content": "Hi, my name is John."},
            {"role": "assistant", "content": "Hello John! How old are you?"},
            {"role": "user", "content": "I'm 25."}
        ]
    }
    user_message = "I want to improve my career."
    # История уже содержит все сообщения, user_message не добавляется напрямую
    prompt = generate_llm_prompt(node, state, user_message)

    # Проверяем, что история корректно сериализована
    assert "System:" in prompt
    assert node.system_prompt in prompt
    assert "User: Hi, my name is John." in prompt
    assert "Assistant: Hello John! How old are you?" in prompt
    assert "User: I'm 25." in prompt
    # Проверяем, что json instructions присутствуют
    assert "Please respond in JSON format" in prompt
    assert '"reply":' in prompt
    assert '"user_name":' in prompt
    assert '"user_age":' in prompt
    assert '"next":' in prompt
    assert "unavailable" in prompt
    assert "null" in prompt 