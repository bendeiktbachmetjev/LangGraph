import pytest
from mentor_ai.cursor.core.types import CollectBasicInfoResponse

def test_collect_basic_info_response_valid():
    """Test valid response with complete information"""
    response = CollectBasicInfoResponse(
        reply="Nice to meet you, John!",
        user_name="John",
        user_age=25,
        next="classify_category"
    )
    assert response.reply == "Nice to meet you, John!"
    assert response.user_name == "John"
    assert response.user_age == 25
    assert response.next == "classify_category"

def test_collect_basic_info_response_incomplete():
    """Test response with incomplete information"""
    response = CollectBasicInfoResponse(
        reply="What's your age?",
        user_name="John",
        user_age=None,
        next="collect_basic_info"
    )
    assert response.user_name == "John"
    assert response.user_age is None
    assert response.next == "collect_basic_info"

def test_collect_basic_info_response_unavailable():
    """Test response when user refuses to provide information"""
    response = CollectBasicInfoResponse(
        reply="No problem, we can proceed.",
        user_name="unavailable",
        user_age=None,
        next="classify_category"
    )
    assert response.user_name == "unavailable"
    assert response.user_age is None 