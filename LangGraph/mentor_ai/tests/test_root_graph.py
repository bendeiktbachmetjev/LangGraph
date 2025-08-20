import pytest
from mentor_ai.cursor.core import root_graph, Node

def test_collect_basic_info_node_structure():
    node = root_graph["collect_basic_info"]
    assert isinstance(node, Node)
    assert node.node_id == "collect_basic_info"
    assert "name" in node.assistant_prompt.lower()
    # Accept either 'age' or 'old' in the prompt
    prompt = node.assistant_prompt.lower()
    assert ("age" in prompt) or ("old" in prompt)
    assert callable(node.next_node)
    assert node.outputs["next"] == "classify_category"
    assert node.outputs["reply"] == str
    assert node.outputs["state.user_name"] == str
    assert node.outputs["state.user_age"] == int 