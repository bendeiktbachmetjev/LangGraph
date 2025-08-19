import pytest
from unittest.mock import Mock, patch
from mentor_ai.cursor.core.llm_client import LLMClient

def test_validate_json_response_valid():
    """Test JSON validation with valid JSON"""
    client = LLMClient()
    valid_json = '{"reply": "Hello", "user_name": "John", "next": "test"}'
    assert client.validate_json_response(valid_json) is True

def test_validate_json_response_invalid():
    """Test JSON validation with invalid JSON"""
    client = LLMClient()
    invalid_json = '{"reply": "Hello", "user_name": "John"'  # Missing closing brace
    assert client.validate_json_response(invalid_json) is False

@patch('mentor_ai.cursor.core.llm_client.OpenAI')
def test_llm_client_initialization(mock_openai):
    """Test LLM client initialization"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        client = LLMClient()
        assert client.model == "gpt-4"
        mock_openai.assert_called_once_with(api_key='test_key')

@patch('mentor_ai.cursor.core.llm_client.OpenAI')
def test_call_llm_success(mock_openai):
    """Test successful LLM call"""
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"reply": "Hello", "user_name": "John", "next": "test"}'
    
    mock_client_instance = Mock()
    mock_client_instance.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client_instance
    
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        client = LLMClient()
        result = client.call_llm("Test prompt")
        
        assert result == '{"reply": "Hello", "user_name": "John", "next": "test"}'
        mock_client_instance.chat.completions.create.assert_called_once() 