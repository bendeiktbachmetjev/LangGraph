import pytest
from unittest.mock import Mock, patch
from mentor_ai.cursor.core.graph_processor import GraphProcessor
from mentor_ai.cursor.core.root_graph import root_graph

class TestGraphProcessorMemory:
    """Test GraphProcessor memory integration functionality"""
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_process_node_with_memory_enabled(self, mock_state_manager, mock_llm_client):
        """Test processing node with memory enabled"""
        # Mock LLM response
        mock_llm_client.call_llm.return_value = '{"reply": "Hello! What is your name?", "user_name": null, "user_age": null, "next": "collect_basic_info"}'
        
        # Mock state manager methods
        mock_state_manager.parse_llm_response.return_value = {
            "reply": "Hello! What is your name?",
            "user_name": None,
            "user_age": None,
            "next": "collect_basic_info"
        }
        mock_state_manager.update_state_with_memory.return_value = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [{"role": "user", "content": "Hi"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 1
        }
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        mock_state_manager.get_memory_stats.return_value = {
            "message_count": 1,
            "current_week": 1,
            "running_summary_exists": False,
            "recent_messages_count": 1,
            "important_facts_count": 0,
            "weekly_summaries_count": 0,
            "history_count": 0,
            "estimated_tokens": 50
        }
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Process node
        reply, updated_state, next_node = GraphProcessor.process_node(
            node_id, user_message, current_state
        )
        
        # Verify results
        assert reply == "Hello! What is your name?"
        assert next_node == "collect_basic_info"
        assert "prompt_context" in updated_state
        assert updated_state["message_count"] == 1
        
        # Verify memory management was used
        mock_state_manager.update_state_with_memory.assert_called_once()
        mock_state_manager.get_memory_stats.assert_called_once()
        
        # Verify LLM was called
        mock_llm_client.call_llm.assert_called_once()
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_process_node_with_memory_control_enabled(self, mock_state_manager, mock_llm_client):
        """Test processing node with memory control enabled"""
        # Mock LLM response
        mock_llm_client.call_llm.return_value = '{"reply": "Hello! What is your name?", "user_name": null, "user_age": null, "next": "collect_basic_info"}'
        
        # Mock state manager methods
        mock_state_manager.parse_llm_response.return_value = {
            "reply": "Hello! What is your name?",
            "user_name": None,
            "user_age": None,
            "next": "collect_basic_info"
        }
        mock_state_manager.update_state_with_memory.return_value = {
            "session_id": "test123",
            "prompt_context": {
                "running_summary": None,
                "recent_messages": [{"role": "user", "content": "Hi"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 1
        }
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        mock_state_manager.get_memory_stats.return_value = {
            "message_count": 1,
            "current_week": 1,
            "running_summary_exists": False,
            "recent_messages_count": 1,
            "important_facts_count": 0,
            "weekly_summaries_count": 0,
            "history_count": 0,
            "estimated_tokens": 50
        }
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Process node with memory enabled
        reply, updated_state, next_node = GraphProcessor.process_node_with_memory_control(
            node_id, user_message, current_state, use_memory=True
        )
        
        # Verify results
        assert reply == "Hello! What is your name?"
        assert next_node == "collect_basic_info"
        assert "prompt_context" in updated_state
        
        # Verify memory management was used
        mock_state_manager.update_state_with_memory.assert_called_once()
        mock_state_manager.get_memory_stats.assert_called_once()
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_process_node_with_memory_control_disabled(self, mock_state_manager, mock_llm_client):
        """Test processing node with memory control disabled"""
        # Mock LLM response
        mock_llm_client.call_llm.return_value = '{"reply": "Hello! What is your name?", "user_name": null, "user_age": null, "next": "collect_basic_info"}'
        
        # Mock state manager methods
        mock_state_manager.parse_llm_response.return_value = {
            "reply": "Hello! What is your name?",
            "user_name": None,
            "user_age": None,
            "next": "collect_basic_info"
        }
        mock_state_manager.update_state.return_value = {
            "session_id": "test123",
            "history": [{"role": "user", "content": "Hi"}]
        }
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Process node with memory disabled
        reply, updated_state, next_node = GraphProcessor.process_node_with_memory_control(
            node_id, user_message, current_state, use_memory=False
        )
        
        # Verify results
        assert reply == "Hello! What is your name?"
        assert next_node == "collect_basic_info"
        
        # Verify old state management was used (no memory)
        mock_state_manager.update_state.assert_called_once()
        mock_state_manager.update_state_with_memory.assert_not_called()
        mock_state_manager.get_memory_stats.assert_not_called()
    
    @patch('mentor_ai.cursor.core.graph_processor.generate_llm_prompt')
    @patch('mentor_ai.cursor.core.prompting.generate_llm_prompt_with_history')
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_prompt_generation_with_memory_control(self, mock_state_manager, mock_llm_client, 
                                                  mock_generate_history, mock_generate_memory):
        """Test that correct prompt generation method is used based on memory setting"""
        # Mock responses
        mock_llm_client.call_llm.return_value = '{"reply": "Hello!", "next": "collect_basic_info"}'
        mock_state_manager.parse_llm_response.return_value = {"reply": "Hello!", "next": "collect_basic_info"}
        mock_state_manager.update_state_with_memory.return_value = {"session_id": "test123"}
        mock_state_manager.update_state.return_value = {"session_id": "test123"}
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        mock_state_manager.get_memory_stats.return_value = {"message_count": 1}
        
        # Mock prompt generation
        mock_generate_memory.return_value = "Memory optimized prompt"
        mock_generate_history.return_value = "History based prompt"
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Test with memory enabled
        GraphProcessor.process_node_with_memory_control(
            node_id, user_message, current_state, use_memory=True
        )
        mock_generate_memory.assert_called_once()
        mock_generate_history.assert_not_called()
        
        # Reset mocks
        mock_generate_memory.reset_mock()
        mock_generate_history.reset_mock()
        
        # Test with memory disabled
        GraphProcessor.process_node_with_memory_control(
            node_id, user_message, current_state, use_memory=False
        )
        mock_generate_history.assert_called_once()
        mock_generate_memory.assert_not_called()
    
    def test_get_memory_stats(self):
        """Test getting memory statistics"""
        current_state = {
            "session_id": "test123",
            "message_count": 25,
            "current_week": 3,
            "prompt_context": {
                "running_summary": "User discussing career goals",
                "recent_messages": [{"role": "user", "content": "Hi"}] * 3,
                "important_facts": [{"fact": "User wants CTO", "week": 1}] * 5,
                "weekly_summaries": {1: {"summary": "Week 1"}, 2: {"summary": "Week 2"}}
            },
            "history": [{"role": "user", "content": "Hello"}] * 10
        }
        
        stats = GraphProcessor.get_memory_stats(current_state)
        
        assert stats["message_count"] == 25
        assert stats["current_week"] == 3
        assert stats["running_summary_exists"] is True
        assert stats["recent_messages_count"] == 3
        assert stats["important_facts_count"] == 5
        assert stats["weekly_summaries_count"] == 2
        assert stats["history_count"] == 10
        assert stats["estimated_tokens"] > 0
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_backward_compatibility_original_process_node(self, mock_state_manager, mock_llm_client):
        """Test that original process_node method still works for backward compatibility"""
        # Mock LLM response
        mock_llm_client.call_llm.return_value = '{"reply": "Hello!", "next": "collect_basic_info"}'
        
        # Mock state manager methods
        mock_state_manager.parse_llm_response.return_value = {"reply": "Hello!", "next": "collect_basic_info"}
        mock_state_manager.update_state_with_memory.return_value = {"session_id": "test123"}
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        mock_state_manager.get_memory_stats.return_value = {"message_count": 1}
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Process node using original method
        reply, updated_state, next_node = GraphProcessor.process_node(
            node_id, user_message, current_state
        )
        
        # Verify results
        assert reply == "Hello!"
        assert next_node == "collect_basic_info"
        
        # Verify memory management was used (new default behavior)
        mock_state_manager.update_state_with_memory.assert_called_once()
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_error_handling_with_memory(self, mock_state_manager, mock_llm_client):
        """Test error handling when memory management fails"""
        # Mock LLM response
        mock_llm_client.call_llm.return_value = '{"reply": "Hello!", "next": "collect_basic_info"}'
        
        # Mock state manager methods
        mock_state_manager.parse_llm_response.return_value = {"reply": "Hello!", "next": "collect_basic_info"}
        mock_state_manager.update_state_with_memory.side_effect = Exception("Memory error")
        mock_state_manager.get_next_node.return_value = "collect_basic_info"
        
        # Test data
        node_id = "collect_basic_info"
        user_message = "Hi"
        current_state = {"session_id": "test123"}
        
        # Should raise exception
        with pytest.raises(Exception, match="Memory error"):
            GraphProcessor.process_node(node_id, user_message, current_state)
    
    @patch('mentor_ai.cursor.core.graph_processor.llm_client')
    @patch('mentor_ai.cursor.core.graph_processor.StateManager')
    def test_non_llm_node_with_memory(self, mock_state_manager, mock_llm_client):
        """Test processing non-LLM node with memory management"""
        # Create a mock node with executor
        mock_node = Mock()
        mock_node.executor = Mock(return_value={"reply": "Executed!", "next": "next_node"})
        mock_node.node_id = "test_node"
        
        # Mock root_graph
        with patch('mentor_ai.cursor.core.graph_processor.root_graph', {"test_node": mock_node}):
            # Mock state manager methods
            mock_state_manager.update_state_with_memory.return_value = {
                "session_id": "test123",
                "prompt_context": {"recent_messages": []},
                "message_count": 1
            }
            mock_state_manager.get_next_node.return_value = "next_node"
            mock_state_manager.get_memory_stats.return_value = {"message_count": 1}
            
            # Test data
            node_id = "test_node"
            user_message = "Hi"
            current_state = {"session_id": "test123"}
            
            # Process node
            reply, updated_state, next_node = GraphProcessor.process_node(
                node_id, user_message, current_state
            )
            
            # Verify results
            assert reply == "Executed!"
            assert next_node == "next_node"
            
            # Verify executor was called
            mock_node.executor.assert_called_once_with(user_message, current_state)
            
            # Verify memory management was still used
            mock_state_manager.update_state_with_memory.assert_called_once()
