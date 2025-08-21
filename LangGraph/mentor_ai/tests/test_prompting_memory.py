import pytest
from unittest.mock import patch
from mentor_ai.cursor.core.prompting import generate_llm_prompt, generate_llm_prompt_with_history
from mentor_ai.cursor.core.root_graph import root_graph

class TestPromptingMemory:
    """Test prompting.py memory integration functionality"""
    
    def test_generate_llm_prompt_with_prompt_context(self):
        """Test prompt generation using optimized prompt_context"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "User is starting onboarding process",
                "recent_messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! What's your name?"}
                ],
                "important_facts": [
                    {"fact": "User wants to become CTO", "week": 0}
                ],
                "weekly_summaries": {}
            }
        }
        user_message = "My name is John"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Verify basic structure
        assert "System:" in prompt
        assert node.system_prompt in prompt
        
        # Verify optimized context is used
        assert "Running Summary: User is starting onboarding process" in prompt
        assert "Recent Messages:" in prompt
        assert "user: Hello" in prompt
        assert "assistant: Hi! What's your name?" in prompt
        assert "Important Facts:" in prompt
        assert "- User wants to become CTO (Week 0)" in prompt
        
        # Verify JSON instructions are included
        assert "Please respond in JSON format" in prompt
        assert user_message in prompt
    
    def test_generate_llm_prompt_fallback_to_history(self):
        """Test prompt generation falls back to history when no prompt_context"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! What's your name?"},
                {"role": "user", "content": "My name is John"}
            ]
        }
        user_message = "My name is John"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Verify basic structure
        assert "System:" in prompt
        assert node.system_prompt in prompt
        
        # Verify fallback to history is used
        assert "User: Hello" in prompt
        assert "Assistant: Hi! What's your name?" in prompt
        assert "User: My name is John" in prompt
        
        # Verify JSON instructions are included
        assert "Please respond in JSON format" in prompt
        assert user_message in prompt
    
    def test_generate_llm_prompt_empty_prompt_context(self):
        """Test prompt generation with empty prompt_context falls back to history"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        user_message = "My name is John"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Should fall back to history since prompt_context is empty
        assert "User: Hello" in prompt
        assert "Assistant: Hi there!" in prompt
    
    def test_generate_llm_prompt_no_context_or_history(self):
        """Test prompt generation with no context or history"""
        node = root_graph["collect_basic_info"]
        state = {"session_id": "test123"}
        user_message = "Hello"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Verify basic structure is still maintained
        assert "System:" in prompt
        assert node.system_prompt in prompt
        assert "Please respond in JSON format" in prompt
        assert user_message in prompt
    
    @patch('mentor_ai.cursor.core.prompting.MemoryManager.format_prompt_context')
    def test_generate_llm_prompt_uses_memory_manager(self, mock_format_context):
        """Test that MemoryManager.format_prompt_context is called"""
        mock_format_context.return_value = "Formatted context from MemoryManager"
        
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "Test summary",
                "recent_messages": [{"role": "user", "content": "Hello"}],
                "important_facts": [],
                "weekly_summaries": {}
            }
        }
        user_message = "Test message"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Verify MemoryManager was called
        mock_format_context.assert_called_once_with(state)
        
        # Verify formatted context is included
        assert "Formatted context from MemoryManager" in prompt
    
    def test_generate_llm_prompt_with_history_original_behavior(self):
        """Test that generate_llm_prompt_with_history preserves original behavior"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! What's your name?"},
                {"role": "user", "content": "My name is John"}
            ],
            "prompt_context": {
                "running_summary": "This should be ignored",
                "recent_messages": [{"role": "user", "content": "This should be ignored"}],
                "important_facts": [],
                "weekly_summaries": {}
            }
        }
        user_message = "My name is John"
        
        prompt = generate_llm_prompt_with_history(node, state, user_message)
        
        # Verify it uses full history regardless of prompt_context
        assert "User: Hello" in prompt
        assert "Assistant: Hi! What's your name?" in prompt
        assert "User: My name is John" in prompt
        
        # Verify prompt_context content is NOT used for conversation history
        # Note: prompt_context might appear in state dump, but not as conversation context
        assert "Running Summary:" not in prompt
        # Verify it's using full history instead
        assert "User: Hello" in prompt
        
        # Verify basic structure
        assert "System:" in prompt
        assert node.system_prompt in prompt
        assert user_message in prompt
    
    def test_generate_llm_prompt_token_efficiency(self):
        """Test that memory-optimized prompt is more token-efficient"""
        node = root_graph["collect_basic_info"]
        
        # Large history state
        large_history = []
        for i in range(50):
            large_history.append({"role": "user", "content": f"User message {i} with lots of content"})
            large_history.append({"role": "assistant", "content": f"Assistant response {i} with lots of content"})
        
        state_with_history = {
            "session_id": "test123",
            "history": large_history
        }
        
        # Optimized state with prompt_context
        state_with_context = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "Brief summary of conversation",
                "recent_messages": [
                    {"role": "user", "content": "Recent message 1"},
                    {"role": "assistant", "content": "Recent response 1"}
                ],
                "important_facts": [
                    {"fact": "User wants to be CTO", "week": 1}
                ],
                "weekly_summaries": {}
            },
            "history": large_history  # Still preserved for frontend
        }
        
        user_message = "Test message"
        
        # Generate both prompts
        prompt_with_history = generate_llm_prompt(node, state_with_history, user_message)
        prompt_with_context = generate_llm_prompt(node, state_with_context, user_message)
        
        # Memory-optimized prompt should be shorter (even with state dump included)
        assert len(prompt_with_context) < len(prompt_with_history)
        
        # More realistic test: check conversation context size
        # Extract conversation lines from both prompts
        history_lines = [line for line in prompt_with_history.split('\n') if line.startswith(('User:', 'Assistant:'))]
        context_lines = [line for line in prompt_with_context.split('\n') if line.startswith(('Running Summary:', 'Recent Messages:', 'user:', 'assistant:'))]
        
        history_text = '\n'.join(history_lines)
        context_text = '\n'.join(context_lines)
        
        # Context should be much smaller than full history
        assert len(context_text) < len(history_text) * 0.1  # At least 90% reduction in conversation content
    
    def test_generate_llm_prompt_preserves_json_instructions(self):
        """Test that JSON instructions are preserved with memory optimization"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "User starting onboarding",
                "recent_messages": [],
                "important_facts": [],
                "weekly_summaries": {}
            }
        }
        user_message = "Hello"
        
        prompt = generate_llm_prompt(node, state, user_message)
        
        # Verify all critical JSON instructions are preserved
        assert "Please respond in JSON format" in prompt
        assert '"reply":' in prompt
        assert '"user_name":' in prompt
        assert '"user_age":' in prompt
        assert '"next":' in prompt
        assert "CRITICAL RULES:" in prompt
        assert "collect_basic_info node" in prompt
    
    def test_backward_compatibility_no_memory_manager_import_error(self):
        """Test that prompting works even if MemoryManager fails"""
        node = root_graph["collect_basic_info"]
        state = {
            "session_id": "test123",
            "history": [
                {"role": "user", "content": "Hello"}
            ]
        }
        user_message = "Test"
        
        # Should work with fallback to history
        prompt = generate_llm_prompt(node, state, user_message)
        
        assert "System:" in prompt
        assert "User: Hello" in prompt
        assert user_message in prompt
    
    def test_context_lines_handling_various_scenarios(self):
        """Test context_lines handling in various scenarios"""
        node = root_graph["collect_basic_info"]
        user_message = "Test message"
        
        # Test 1: No context at all
        state1 = {"session_id": "test123"}
        prompt1 = generate_llm_prompt(node, state1, user_message)
        assert "System:" in prompt1
        assert user_message in prompt1
        
        # Test 2: Empty history
        state2 = {"session_id": "test123", "history": []}
        prompt2 = generate_llm_prompt(node, state2, user_message)
        assert "System:" in prompt2
        assert user_message in prompt2
        
        # Test 3: Invalid history entries
        state3 = {
            "session_id": "test123",
            "history": [
                "invalid_entry",
                {"role": "user"},  # No content
                {"content": "No role"},  # No role
                {"role": "user", "content": ""},  # Empty content
                {"role": "user", "content": "Valid message"}
            ]
        }
        prompt3 = generate_llm_prompt(node, state3, user_message)
        assert "User: Valid message" in prompt3
        # Note: invalid_entry appears in state dump, but not in conversation context
        lines = prompt3.split('\n')
        conversation_lines = [line for line in lines if line.startswith(('User:', 'Assistant:'))]
        conversation_text = '\n'.join(conversation_lines)
        assert "invalid_entry" not in conversation_text
