import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from mentor_ai.app.main import app
from mentor_ai.app.storage.mongodb import mongodb_manager

client = TestClient(app)

class TestChatEndpointsMemory:
    """Test chat endpoints with memory integration"""
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.update_session')
    @patch('mentor_ai.cursor.core.graph_processor.GraphProcessor.process_node')
    def test_chat_with_memory_initialization(self, mock_process_node, mock_update_session, 
                                           mock_get_session, mock_verify_token):
        """Test chat endpoint initializes memory fields for new sessions"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state without memory fields
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [],
            "current_node": "collect_basic_info"
        }
        mock_update_session.return_value = None
        
        # Mock GraphProcessor response
        mock_process_node.return_value = (
            "Hello! What's your name?",
            {
                "session_id": "test123",
                "user_id": "test_user",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello! What's your name?"}
                ],
                "prompt_context": {
                    "running_summary": None,
                    "recent_messages": [{"role": "user", "content": "Hi"}],
                    "important_facts": [],
                    "weekly_summaries": {}
                },
                "message_count": 1,
                "current_week": 1,
                "current_node": "collect_basic_info"
            },
            "collect_basic_info"
        )
        
        # Make request
        response = client.post(
            "/chat/test123",
            json={"message": "Hi"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Hello! What's your name?"
        assert data["session_id"] == "test123"
        
        # Verify memory fields were initialized
        mock_update_session.assert_called_once()
        updated_state = mock_update_session.call_args[0][1]
        assert "prompt_context" in updated_state
        assert "message_count" in updated_state
        assert "current_week" in updated_state
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.update_session')
    @patch('mentor_ai.cursor.core.graph_processor.GraphProcessor.process_node')
    def test_chat_with_existing_memory(self, mock_process_node, mock_update_session, 
                                     mock_get_session, mock_verify_token):
        """Test chat endpoint with existing memory fields"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state with existing memory fields
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [
                {"role": "user", "content": "Previous message"},
                {"role": "assistant", "content": "Previous response"}
            ],
            "prompt_context": {
                "running_summary": "User is in onboarding",
                "recent_messages": [{"role": "user", "content": "Previous message"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 2,
            "current_week": 1,
            "current_node": "collect_basic_info"
        }
        mock_update_session.return_value = None
        
        # Mock GraphProcessor response
        mock_process_node.return_value = (
            "Thanks for the info!",
            {
                "session_id": "test123",
                "user_id": "test_user",
                "history": [
                    {"role": "user", "content": "Previous message"},
                    {"role": "assistant", "content": "Previous response"},
                    {"role": "user", "content": "New message"},
                    {"role": "assistant", "content": "Thanks for the info!"}
                ],
                "prompt_context": {
                    "running_summary": "User is in onboarding",
                    "recent_messages": [
                        {"role": "user", "content": "Previous message"},
                        {"role": "user", "content": "New message"}
                    ],
                    "important_facts": [],
                    "weekly_summaries": {}
                },
                "message_count": 4,
                "current_week": 1,
                "current_node": "collect_basic_info"
            },
            "collect_basic_info"
        )
        
        # Make request
        response = client.post(
            "/chat/test123",
            json={"message": "New message"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Thanks for the info!"
        
        # Verify memory was preserved and updated
        mock_update_session.assert_called_once()
        updated_state = mock_update_session.call_args[0][1]
        assert updated_state["message_count"] == 4
        assert len(updated_state["prompt_context"]["recent_messages"]) == 2
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    def test_get_memory_stats(self, mock_get_session, mock_verify_token):
        """Test getting memory statistics endpoint"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state with memory data
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [{"role": "user", "content": "Hello"}] * 10,
            "prompt_context": {
                "running_summary": "User discussing career goals",
                "recent_messages": [{"role": "user", "content": "Hi"}] * 3,
                "important_facts": [{"fact": "User wants CTO", "week": 1}] * 5,
                "weekly_summaries": {1: {"summary": "Week 1"}}
            },
            "message_count": 25,
            "current_week": 2
        }
        
        # Make request
        response = client.get(
            "/chat/test123/memory-stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test123"
        assert "memory_stats" in data
        
        stats = data["memory_stats"]
        assert stats["message_count"] == 25
        assert stats["current_week"] == 2
        assert stats["running_summary_exists"] is True
        assert stats["recent_messages_count"] == 3
        assert stats["important_facts_count"] == 5
        assert stats["weekly_summaries_count"] == 1
        assert stats["history_count"] == 10
        assert stats["estimated_tokens"] > 0
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.update_session')
    @patch('mentor_ai.cursor.core.graph_processor.GraphProcessor.process_node_with_memory_control')
    def test_memory_control_endpoint_enabled(self, mock_process_node, mock_update_session, 
                                           mock_get_session, mock_verify_token):
        """Test memory control endpoint with memory enabled"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [],
            "current_node": "collect_basic_info"
        }
        mock_update_session.return_value = None
        
        # Mock GraphProcessor response
        mock_process_node.return_value = (
            "Hello with memory!",
            {
                "session_id": "test123",
                "user_id": "test_user",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello with memory!"}
                ],
                "prompt_context": {
                    "running_summary": None,
                    "recent_messages": [{"role": "user", "content": "Hi"}],
                    "important_facts": [],
                    "weekly_summaries": {}
                },
                "message_count": 1,
                "current_week": 1,
                "current_node": "collect_basic_info"
            },
            "collect_basic_info"
        )
        
        # Make request with memory enabled
        response = client.post(
            "/chat/test123/memory-control",
            json={"use_memory": True, "message": "Hi"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Hello with memory!"
        assert data["memory_used"] is True
        assert "memory_stats" in data
        
        # Verify GraphProcessor was called with memory enabled
        mock_process_node.assert_called_once()
        call_args = mock_process_node.call_args
        assert call_args[1]["use_memory"] is True
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.update_session')
    @patch('mentor_ai.cursor.core.graph_processor.GraphProcessor.process_node_with_memory_control')
    def test_memory_control_endpoint_disabled(self, mock_process_node, mock_update_session, 
                                            mock_get_session, mock_verify_token):
        """Test memory control endpoint with memory disabled"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [],
            "current_node": "collect_basic_info"
        }
        mock_update_session.return_value = None
        
        # Mock GraphProcessor response
        mock_process_node.return_value = (
            "Hello without memory!",
            {
                "session_id": "test123",
                "user_id": "test_user",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello without memory!"}
                ],
                "current_node": "collect_basic_info"
            },
            "collect_basic_info"
        )
        
        # Make request with memory disabled
        response = client.post(
            "/chat/test123/memory-control",
            json={"use_memory": False, "message": "Hi"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Hello without memory!"
        assert data["memory_used"] is False
        assert "memory_stats" in data
        
        # Verify GraphProcessor was called with memory disabled
        mock_process_node.assert_called_once()
        call_args = mock_process_node.call_args
        assert call_args[1]["use_memory"] is False
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    def test_memory_stats_session_not_found(self, mock_get_session, mock_verify_token):
        """Test memory stats endpoint with non-existent session"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session not found
        mock_get_session.return_value = None
        
        # Make request
        response = client.get(
            "/chat/nonexistent/memory-stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    def test_memory_stats_access_denied(self, mock_get_session, mock_verify_token):
        """Test memory stats endpoint with access denied"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session belonging to different user
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "different_user",
            "history": []
        }
        
        # Make request
        response = client.get(
            "/chat/test123/memory-stats",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
    
    @patch('mentor_ai.app.endpoints.chat.auth.verify_id_token')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.get_session')
    @patch('mentor_ai.app.storage.mongodb.mongodb_manager.update_session')
    @patch('mentor_ai.cursor.core.graph_processor.GraphProcessor.process_node')
    def test_chat_duplicate_message_prevention(self, mock_process_node, mock_update_session, 
                                             mock_get_session, mock_verify_token):
        """Test that duplicate messages are not added to history"""
        # Mock authentication
        mock_verify_token.return_value = {"uid": "test_user"}
        
        # Mock session state with existing message
        mock_get_session.return_value = {
            "session_id": "test123",
            "user_id": "test_user",
            "history": [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello!"}
            ],
            "current_node": "collect_basic_info"
        }
        mock_update_session.return_value = None
        
        # Mock GraphProcessor response
        mock_process_node.return_value = (
            "Hello again!",
            {
                "session_id": "test123",
                "user_id": "test_user",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello!"}
                ],
                "current_node": "collect_basic_info"
            },
            "collect_basic_info"
        )
        
        # Make request with duplicate message
        response = client.post(
            "/chat/test123",
            json={"message": "Hi"},  # Same message as in history
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify duplicate message was not added
        mock_update_session.assert_called_once()
        updated_state = mock_update_session.call_args[0][1]
        history = updated_state["history"]
        
        # Should have only one "Hi" message
        hi_messages = [msg for msg in history if msg.get("content") == "Hi"]
        assert len(hi_messages) == 1
