import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from mentor_ai.cursor.core.state_manager import StateManager
from mentor_ai.cursor.core.root_graph import root_graph, Node

class TestStateManagerMemory:
    """Test StateManager memory integration functionality"""
    
    def test_update_state_with_memory_new_session(self):
        """Test updating state with memory for new session"""
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Hello! What's your name?",
            "user_name": None,
            "user_age": None,
            "next": "collect_basic_info"
        }
        node = root_graph["collect_basic_info"]
        user_message = "Hi there!"
        assistant_reply = "Hello! What's your name?"
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node, user_message, assistant_reply
        )
        
        # Verify memory fields were initialized
        assert "prompt_context" in updated_state
        assert "message_count" in updated_state
        assert "current_week" in updated_state
        
        # Verify messages were added to prompt_context
        recent_messages = updated_state["prompt_context"]["recent_messages"]
        assert len(recent_messages) == 2
        assert recent_messages[0]["content"] == "Hi there!"
        assert recent_messages[1]["content"] == "Hello! What's your name?"
        
        # Verify message count was updated
        assert updated_state["message_count"] == 2
        
        # Verify current week was initialized
        assert updated_state["current_week"] == 1
    
    def test_update_state_with_memory_existing_session(self):
        """Test updating state with memory for existing session"""
        current_state = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": "User started conversation",
                "recent_messages": [
                    {"role": "user", "content": "Previous message"}
                ],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 1,
            "current_week": 1
        }
        llm_data = {
            "reply": "Thanks for the info!",
            "user_name": "John",
            "user_age": 25,
            "next": "classify_category"
        }
        node = root_graph["collect_basic_info"]
        user_message = "My name is John and I'm 25"
        assistant_reply = "Thanks for the info!"
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node, user_message, assistant_reply
        )
        
        # Verify standard state update happened
        assert updated_state["user_name"] == "John"
        assert updated_state["user_age"] == 25
        
        # Verify messages were added to existing context
        recent_messages = updated_state["prompt_context"]["recent_messages"]
        assert len(recent_messages) == 3  # Previous + 2 new
        assert recent_messages[-1]["content"] == "Thanks for the info!"
        
        # Verify message count was incremented
        assert updated_state["message_count"] == 3
    
    def test_handle_week_transition_no_transition(self):
        """Test week transition handling when no transition occurs"""
        state = {
            "session_id": "test123",
            "current_week": 1,
            "prompt_context": {
                "weekly_summaries": {}
            }
        }
        node = root_graph["collect_basic_info"]  # Not a week node
        
        updated_state = StateManager._handle_week_transition(state, node)
        
        # No changes should occur
        assert updated_state["current_week"] == 1
        assert len(updated_state["prompt_context"]["weekly_summaries"]) == 0
    
    @patch('mentor_ai.cursor.core.state_manager.MemoryManager.create_weekly_summary')
    def test_handle_week_transition_with_transition(self, mock_create_summary):
        """Test week transition handling when transition occurs"""
        mock_create_summary.return_value = {
            "summary": "Week 1 focused on basic info collection",
            "important_facts": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 10
        }
        
        state = {
            "session_id": "test123",
            "current_week": 1,
            "prompt_context": {
                "weekly_summaries": {}
            }
        }
        
        # Create a mock week2 node
        week2_node = Node(
            node_id="week2_chat",
            system_prompt="Week 2 chat",
            outputs={"reply": str},
            next_node=lambda state: "week2_chat"
        )
        
        updated_state = StateManager._handle_week_transition(state, week2_node)
        
        # Verify week was updated
        assert updated_state["current_week"] == 2
        
        # Verify weekly summary was created and stored
        assert 1 in updated_state["prompt_context"]["weekly_summaries"]
        summary = updated_state["prompt_context"]["weekly_summaries"][1]
        assert summary["summary"] == "Week 1 focused on basic info collection"
        
        # Verify MemoryManager was called
        mock_create_summary.assert_called_once_with("test123", state, 1)
    
    def test_get_memory_stats_empty_state(self):
        """Test getting memory stats for empty state"""
        state = {"session_id": "test123"}
        
        stats = StateManager.get_memory_stats(state)
        
        assert stats["message_count"] == 0
        assert stats["current_week"] == 1
        assert stats["running_summary_exists"] is False
        assert stats["recent_messages_count"] == 0
        assert stats["important_facts_count"] == 0
        assert stats["weekly_summaries_count"] == 0
        assert stats["history_count"] == 0
        assert stats["estimated_tokens"] == 0
    
    def test_get_memory_stats_with_data(self):
        """Test getting memory stats for state with data"""
        state = {
            "session_id": "test123",
            "message_count": 25,
            "current_week": 3,
            "history": [{"role": "user", "content": "Hello"}] * 10,
            "prompt_context": {
                "running_summary": "User is discussing career goals",
                "recent_messages": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello"}
                ],
                "important_facts": [
                    {"fact": "User wants to be CTO", "week": 1}
                ] * 5,
                "weekly_summaries": {
                    1: {"summary": "Week 1"},
                    2: {"summary": "Week 2"}
                }
            }
        }
        
        stats = StateManager.get_memory_stats(state)
        
        assert stats["message_count"] == 25
        assert stats["current_week"] == 3
        assert stats["running_summary_exists"] is True
        assert stats["recent_messages_count"] == 2
        assert stats["important_facts_count"] == 5
        assert stats["weekly_summaries_count"] == 2
        assert stats["history_count"] == 10
        assert stats["estimated_tokens"] > 0
    
    def test_update_state_with_memory_only_user_message(self):
        """Test updating state with only user message"""
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Thanks!",
            "next": "collect_basic_info"
        }
        node = root_graph["collect_basic_info"]
        user_message = "Hello"
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node, user_message=user_message
        )
        
        # Verify only user message was added
        recent_messages = updated_state["prompt_context"]["recent_messages"]
        assert len(recent_messages) == 1
        assert recent_messages[0]["content"] == "Hello"
        assert recent_messages[0]["role"] == "user"
        
        # Verify message count
        assert updated_state["message_count"] == 1
    
    def test_update_state_with_memory_only_assistant_reply(self):
        """Test updating state with only assistant reply"""
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Thanks!",
            "next": "collect_basic_info"
        }
        node = root_graph["collect_basic_info"]
        assistant_reply = "Thanks!"
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node, assistant_reply=assistant_reply
        )
        
        # Verify only assistant message was added
        recent_messages = updated_state["prompt_context"]["recent_messages"]
        assert len(recent_messages) == 1
        assert recent_messages[0]["content"] == "Thanks!"
        assert recent_messages[0]["role"] == "assistant"
        
        # Verify message count
        assert updated_state["message_count"] == 1
    
    def test_update_state_with_memory_no_messages(self):
        """Test updating state with no messages"""
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Thanks!",
            "next": "collect_basic_info"
        }
        node = root_graph["collect_basic_info"]
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node
        )
        
        # Verify memory fields were initialized but no messages added
        assert "prompt_context" in updated_state
        assert len(updated_state["prompt_context"]["recent_messages"]) == 0
        assert updated_state["message_count"] == 0
    
    @patch('mentor_ai.cursor.core.state_manager.MemoryManager.evaluate_important_facts')
    @patch('mentor_ai.cursor.core.state_manager.MemoryManager.add_important_fact')
    def test_update_state_with_memory_important_facts(self, mock_add_fact, mock_evaluate_facts):
        """Test updating state with important facts evaluation"""
        mock_evaluate_facts.return_value = [
            {"fact": "User wants to be CTO", "week": 1, "importance_score": 0.9}
        ]
        mock_add_fact.side_effect = lambda state, fact: {
            **state,
            "prompt_context": {
                **state["prompt_context"],
                "important_facts": state["prompt_context"]["important_facts"] + [fact]
            }
        }
        
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Great goal!",
            "next": "collect_basic_info"
        }
        node = root_graph["collect_basic_info"]
        user_message = "I want to become a CTO"
        
        updated_state = StateManager.update_state_with_memory(
            current_state, llm_data, node, user_message=user_message
        )
        
        # Verify important facts evaluation was called
        mock_evaluate_facts.assert_called_once()
        mock_add_fact.assert_called_once()
        
        # Verify the fact was added (via mock)
        assert len(updated_state["prompt_context"]["important_facts"]) == 1
    
    def test_backward_compatibility_with_original_update_state(self):
        """Test that original update_state method still works"""
        current_state = {"session_id": "test123"}
        llm_data = {
            "reply": "Hello!",
            "user_name": "John",
            "user_age": 25,
            "next": "classify_category"
        }
        node = root_graph["collect_basic_info"]
        
        # Test original method
        updated_state = StateManager.update_state(current_state, llm_data, node)
        
        # Verify standard functionality still works
        assert updated_state["user_name"] == "John"
        assert updated_state["user_age"] == 25
        assert "updated_at" in updated_state
        
        # Verify memory fields are NOT added by original method
        assert "prompt_context" not in updated_state
        assert "message_count" not in updated_state
