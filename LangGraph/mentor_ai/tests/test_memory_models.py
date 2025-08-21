import pytest
from datetime import datetime
from mentor_ai.app.models import SessionState, MongoDBDocument

class TestMemoryModels:
    """Test memory system models and backward compatibility"""
    
    def test_session_state_backward_compatibility(self):
        """Test that SessionState works with old data structure"""
        # Test with minimal data (old format)
        old_data = {
            "session_id": "test123",
            "user_name": "John",
            "user_age": 25,
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        session_state = SessionState(**old_data)
        
        # Verify old fields work
        assert session_state.session_id == "test123"
        assert session_state.user_name == "John"
        assert session_state.user_age == 25
        assert len(session_state.history) == 2
        assert session_state.history[0]["role"] == "user"
        assert session_state.history[1]["role"] == "assistant"
        
        # Verify new fields have defaults
        assert session_state.prompt_context == {}
        assert session_state.message_count == 0
        assert session_state.current_week == 1
    
    def test_session_state_with_memory_fields(self):
        """Test SessionState with new memory fields"""
        memory_data = {
            "session_id": "test456",
            "user_name": "Alice",
            "history": [{"role": "user", "content": "Hello"}],
            "prompt_context": {
                "running_summary": "User is starting onboarding",
                "recent_messages": [{"role": "user", "content": "Hello"}],
                "important_facts": [
                    {"fact": "User wants to become CTO", "week": 0, "importance_score": 0.9}
                ],
                "weekly_summaries": {
                    1: {"summary": "Week 1 focused on goal setting", "facts": []}
                }
            },
            "message_count": 5,
            "current_week": 2
        }
        
        session_state = SessionState(**memory_data)
        
        # Verify all fields work
        assert session_state.session_id == "test456"
        assert session_state.user_name == "Alice"
        assert len(session_state.history) == 1
        
        # Verify memory fields
        assert session_state.prompt_context["running_summary"] == "User is starting onboarding"
        assert len(session_state.prompt_context["recent_messages"]) == 1
        assert len(session_state.prompt_context["important_facts"]) == 1
        assert session_state.prompt_context["important_facts"][0]["fact"] == "User wants to become CTO"
        assert len(session_state.prompt_context["weekly_summaries"]) == 1
        assert session_state.message_count == 5
        assert session_state.current_week == 2
    
    def test_mongodb_document_backward_compatibility(self):
        """Test that MongoDBDocument works with old data structure"""
        # Test with minimal data (old format)
        old_data = {
            "session_id": "test789",
            "goals": ["Goal 1", "Goal 2", "Goal 3"],
            "topics": ["Topic 1"] * 12,
            "history": [{"role": "user", "content": "Hello"}]
        }
        
        mongo_doc = MongoDBDocument(**old_data)
        
        # Verify old fields work
        assert mongo_doc.session_id == "test789"
        assert len(mongo_doc.goals) == 3
        assert len(mongo_doc.topics) == 12
        assert len(mongo_doc.history) == 1
        
        # Verify new fields have defaults
        assert mongo_doc.prompt_context == {}
        assert mongo_doc.message_count == 0
        assert mongo_doc.current_week == 1
    
    def test_mongodb_document_with_memory_fields(self):
        """Test MongoDBDocument with new memory fields"""
        memory_data = {
            "session_id": "test999",
            "goals": ["Goal 1", "Goal 2", "Goal 3"],
            "topics": ["Topic 1"] * 12,
            "history": [{"role": "user", "content": "Hello"}],
            "prompt_context": {
                "running_summary": "User completed onboarding",
                "recent_messages": [{"role": "user", "content": "Hello"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 10,
            "current_week": 1
        }
        
        mongo_doc = MongoDBDocument(**memory_data)
        
        # Verify all fields work
        assert mongo_doc.session_id == "test999"
        assert len(mongo_doc.goals) == 3
        assert len(mongo_doc.topics) == 12
        assert len(mongo_doc.history) == 1
        
        # Verify memory fields
        assert mongo_doc.prompt_context["running_summary"] == "User completed onboarding"
        assert len(mongo_doc.prompt_context["recent_messages"]) == 1
        assert mongo_doc.message_count == 10
        assert mongo_doc.current_week == 1
    
    def test_session_state_default_values(self):
        """Test that SessionState has correct default values"""
        minimal_data = {"session_id": "test_default"}
        session_state = SessionState(**minimal_data)
        
        # Verify defaults
        assert session_state.session_id == "test_default"
        assert session_state.user_name is None
        assert session_state.user_age is None
        assert session_state.history == []
        assert session_state.prompt_context == {}
        assert session_state.message_count == 0
        assert session_state.current_week == 1
        assert session_state.phase == "incomplete"
    
    def test_mongodb_document_default_values(self):
        """Test that MongoDBDocument has correct default values"""
        minimal_data = {"session_id": "test_default"}
        mongo_doc = MongoDBDocument(**minimal_data)
        
        # Verify defaults
        assert mongo_doc.session_id == "test_default"
        assert mongo_doc.goals == []
        assert mongo_doc.topics == []
        assert mongo_doc.summary is None
        assert mongo_doc.history == []
        assert mongo_doc.prompt_context == {}
        assert mongo_doc.message_count == 0
        assert mongo_doc.current_week == 1
        assert mongo_doc.phase == "incomplete"
    
    def test_prompt_context_structure_validation(self):
        """Test that prompt_context accepts valid structure"""
        valid_prompt_context = {
            "running_summary": "Test summary",
            "recent_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            "important_facts": [
                {
                    "fact": "User wants to become CTO",
                    "context": "Career goal",
                    "week": 0,
                    "importance_score": 0.9,
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            ],
            "weekly_summaries": {
                1: {
                    "summary": "Week 1 summary",
                    "important_facts": ["Fact 1"],
                    "created_at": "2024-01-15T10:30:00Z",
                    "message_count": 45
                }
            }
        }
        
        data = {
            "session_id": "test_structure",
            "prompt_context": valid_prompt_context
        }
        
        session_state = SessionState(**data)
        
        # Verify structure is preserved
        assert session_state.prompt_context["running_summary"] == "Test summary"
        assert len(session_state.prompt_context["recent_messages"]) == 2
        assert len(session_state.prompt_context["important_facts"]) == 1
        assert len(session_state.prompt_context["weekly_summaries"]) == 1
        assert session_state.prompt_context["important_facts"][0]["fact"] == "User wants to become CTO"
        assert session_state.prompt_context["weekly_summaries"][1]["summary"] == "Week 1 summary"
    
    def test_model_serialization(self):
        """Test that models can be serialized and deserialized"""
        original_data = {
            "session_id": "test_serialization",
            "user_name": "Test User",
            "history": [{"role": "user", "content": "Hello"}],
            "prompt_context": {
                "running_summary": "Test summary",
                "recent_messages": [{"role": "user", "content": "Hello"}],
                "important_facts": [],
                "weekly_summaries": {}
            },
            "message_count": 5,
            "current_week": 2
        }
        
        # Create model
        session_state = SessionState(**original_data)
        
        # Serialize to dict
        serialized = session_state.model_dump()
        
        # Deserialize back to model
        deserialized = SessionState(**serialized)
        
        # Verify data is preserved
        assert deserialized.session_id == original_data["session_id"]
        assert deserialized.user_name == original_data["user_name"]
        assert len(deserialized.history) == len(original_data["history"])
        assert deserialized.prompt_context["running_summary"] == original_data["prompt_context"]["running_summary"]
        assert deserialized.message_count == original_data["message_count"]
        assert deserialized.current_week == original_data["current_week"]
