import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from mentor_ai.cursor.core.memory_manager import MemoryManager

class TestMemoryManager:
    """Test MemoryManager functionality"""
    
    def test_initialize_prompt_context(self):
        """Test prompt_context initialization"""
        context = MemoryManager.initialize_prompt_context()
        
        assert context["running_summary"] is None
        assert context["recent_messages"] == []
        assert context["important_facts"] == []
        assert context["weekly_summaries"] == {}
    
    def test_update_prompt_context_new_session(self):
        """Test updating prompt_context for new session"""
        state = {"session_id": "test123"}
        new_message = {"role": "user", "content": "Hello"}
        
        updated_state = MemoryManager.update_prompt_context(state, new_message)
        
        # Verify prompt_context was initialized
        assert "prompt_context" in updated_state
        assert updated_state["prompt_context"]["recent_messages"] == [new_message]
        assert updated_state["message_count"] == 1
        assert updated_state["prompt_context"]["running_summary"] is None
    
    def test_update_prompt_context_existing_session(self):
        """Test updating prompt_context for existing session"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "Previous summary",
                "recent_messages": [{"role": "user", "content": "Hi"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 5
        }
        new_message = {"role": "assistant", "content": "Hello there!"}
        
        updated_state = MemoryManager.update_prompt_context(state, new_message)
        
        # Verify message was added
        assert len(updated_state["prompt_context"]["recent_messages"]) == 2
        assert updated_state["prompt_context"]["recent_messages"][-1] == new_message
        assert updated_state["message_count"] == 6
        assert updated_state["prompt_context"]["running_summary"] == "Previous summary"
    
    def test_update_prompt_context_limit_recent_messages(self):
        """Test that recent_messages are limited to 5"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [
                    {"role": "user", "content": "Msg1"},
                    {"role": "assistant", "content": "Msg2"},
                    {"role": "user", "content": "Msg3"},
                    {"role": "assistant", "content": "Msg4"},
                    {"role": "user", "content": "Msg5"}
                ],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 5
        }
        new_message = {"role": "assistant", "content": "Msg6"}
        
        updated_state = MemoryManager.update_prompt_context(state, new_message)
        
        # Verify only 5 messages are kept
        assert len(updated_state["prompt_context"]["recent_messages"]) == 5
        assert updated_state["prompt_context"]["recent_messages"][0]["content"] == "Msg2"
        assert updated_state["prompt_context"]["recent_messages"][-1]["content"] == "Msg6"
    
    @patch('mentor_ai.cursor.core.memory_manager.llm_client')
    def test_update_prompt_context_running_summary_update(self, mock_llm_client):
        """Test that running summary is updated every 20 messages"""
        mock_llm_client.call_llm.return_value = "Test summary"
        
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 19,  # Will trigger summary update on next message
            "history": [{"role": "user", "content": "Test message"}]
        }
        new_message = {"role": "user", "content": "Hello"}
        
        updated_state = MemoryManager.update_prompt_context(state, new_message)
        
        # Verify summary was updated
        assert updated_state["prompt_context"]["running_summary"] == "Test summary"
        assert updated_state["message_count"] == 20
        mock_llm_client.call_llm.assert_called_once()
    
    def test_format_prompt_context_empty(self):
        """Test formatting empty prompt_context"""
        state = {"session_id": "test123"}
        
        formatted = MemoryManager.format_prompt_context(state)
        
        assert formatted == ""
    
    def test_format_prompt_context_with_data(self):
        """Test formatting prompt_context with data"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "User is starting onboarding",
                "recent_messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ],
                "important_facts": [
                    {"fact": "User wants to become CTO", "week": 0}
                ],
                "weekly_summaries": {
                    1: {"summary": "Week 1 focused on goal setting"}
                }
            }
        }
        
        formatted = MemoryManager.format_prompt_context(state)
        
        # Verify all sections are included
        assert "Running Summary: User is starting onboarding" in formatted
        assert "Recent Messages:" in formatted
        assert "user: Hello" in formatted
        assert "assistant: Hi there!" in formatted
        assert "Important Facts:" in formatted
        assert "- User wants to become CTO (Week 0)" in formatted
        assert "Weekly Summaries:" in formatted
        assert "Week 1: Week 1 focused on goal setting" in formatted
    
    def test_get_token_estimate_empty(self):
        """Test token estimation for empty prompt_context"""
        state = {"session_id": "test123"}
        
        tokens = MemoryManager.get_token_estimate(state)
        
        assert tokens == 0
    
    def test_get_token_estimate_with_data(self):
        """Test token estimation with data"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "Test summary with some content",
                "recent_messages": [
                    {"role": "user", "content": "Hello world"},
                    {"role": "assistant", "content": "Hi there!"}
                ],
                "important_facts": [
                    {"fact": "User wants CTO", "week": 0}
                ],
                "weekly_summaries": {
                    1: {"summary": "Week 1 summary"}
                }
            }
        }
        
        tokens = MemoryManager.get_token_estimate(state)
        
        # Should return positive number
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_add_important_fact_new_session(self):
        """Test adding important fact to new session"""
        state = {"session_id": "test123"}
        fact = {
            "fact": "User wants to become CTO",
            "week": 0,
            "importance_score": 0.9
        }
        
        updated_state = MemoryManager.add_important_fact(state, fact)
        
        # Verify fact was added
        assert len(updated_state["prompt_context"]["important_facts"]) == 1
        added_fact = updated_state["prompt_context"]["important_facts"][0]
        assert added_fact["fact"] == "User wants to become CTO"
        assert added_fact["week"] == 0
        assert added_fact["importance_score"] == 0.9
        assert "timestamp" in added_fact
    
    def test_add_important_fact_existing_session(self):
        """Test adding important fact to existing session"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [],
                "important_facts": [
                    {"fact": "Existing fact", "week": 0, "importance_score": 0.8}
                ],
                "weekly_summaries": {}
            }
        }
        fact = {
            "fact": "New fact",
            "week": 1,
            "importance_score": 0.9
        }
        
        updated_state = MemoryManager.add_important_fact(state, fact)
        
        # Verify fact was added
        assert len(updated_state["prompt_context"]["important_facts"]) == 2
        assert updated_state["prompt_context"]["important_facts"][-1]["fact"] == "New fact"
    
    def test_add_important_fact_limit_facts(self):
        """Test that important facts are limited to 20"""
        # Create state with 20 existing facts
        existing_facts = [
            {"fact": f"Fact {i}", "week": 0, "importance_score": 0.8}
            for i in range(20)
        ]
        
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [],
                "important_facts": existing_facts,
                "weekly_summaries": {}
            }
        }
        new_fact = {
            "fact": "New fact",
            "week": 1,
            "importance_score": 0.9
        }
        
        updated_state = MemoryManager.add_important_fact(state, new_fact)
        
        # Verify only 20 facts are kept
        assert len(updated_state["prompt_context"]["important_facts"]) == 20
        # Verify oldest fact was removed
        assert updated_state["prompt_context"]["important_facts"][0]["fact"] == "Fact 1"
        # Verify new fact was added
        assert updated_state["prompt_context"]["important_facts"][-1]["fact"] == "New fact"
    
    @patch('mentor_ai.cursor.core.memory_manager.llm_client')
    def test_create_weekly_summary_success(self, mock_llm_client):
        """Test successful weekly summary creation"""
        mock_llm_client.call_llm.return_value = "Week 1 focused on goal setting"
        
        state = {
            "session_id": "test123",
            "history": [{"role": "user", "content": "Hello"}],
            "prompt_context": {
                "important_facts": [
                    {"fact": "User wants CTO", "week": 1}
                ]
            },
            "message_count": 45
        }
        
        summary = MemoryManager.create_weekly_summary("test123", state, 1)
        
        # Verify summary structure
        assert summary["summary"] == "Week 1 focused on goal setting"
        assert len(summary["important_facts"]) == 1
        assert summary["important_facts"][0]["fact"] == "User wants CTO"
        assert summary["message_count"] == 45
        assert "created_at" in summary
        mock_llm_client.call_llm.assert_called_once()
    
    @patch('mentor_ai.cursor.core.memory_manager.llm_client')
    def test_create_weekly_summary_failure(self, mock_llm_client):
        """Test weekly summary creation with LLM failure"""
        mock_llm_client.call_llm.side_effect = Exception("LLM error")
        
        state = {
            "session_id": "test123",
            "history": [],
            "prompt_context": {"important_facts": []},
            "message_count": 10
        }
        
        summary = MemoryManager.create_weekly_summary("test123", state, 1)
        
        # Verify fallback summary
        assert summary["summary"] == "Week 1 conversation summary"
        assert summary["message_count"] == 10
        assert "created_at" in summary
    
    def test_evaluate_important_facts(self):
        """Test important facts evaluation (placeholder)"""
        state = {"session_id": "test123"}
        message = {"role": "user", "content": "I want to become a CTO"}
        
        facts = MemoryManager.evaluate_important_facts(state, message)
        
        # Currently returns empty list (placeholder implementation)
        assert facts == []
    
    def test_format_prompt_context_partial_data(self):
        """Test formatting with partial prompt_context data"""
        state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "Test summary",
                "recent_messages": [],
                "important_facts": [],
                "weekly_summaries": {}
            }
        }
        
        formatted = MemoryManager.format_prompt_context(state)
        
        # Should only include running summary
        assert "Running Summary: Test summary" in formatted
        assert "Recent Messages:" not in formatted
        assert "Important Facts:" not in formatted
        assert "Weekly Summaries:" not in formatted
