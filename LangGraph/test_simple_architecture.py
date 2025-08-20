#!/usr/bin/env python3
"""
Simple test to verify the corrected architecture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mentor_ai', 'cursor', 'core'))

try:
    from root_graph import root_graph
    print("✅ Successfully imported root_graph")
    
    # Check that intermediate nodes are removed
    expected_nodes = [
        "collect_basic_info",
        "classify_category", 
        "improve_intro",
        "improve_skills",
        "improve_obstacles",
        "change_intro",
        "change_skills", 
        "change_obstacles",
        "find_intro",
        "find_skills",
        "find_obstacles",
        "lost_intro",
        "lost_skills",
        "generate_plan",
        "week1_chat"
    ]
    
    actual_nodes = list(root_graph.keys())
    print(f"Expected nodes: {len(expected_nodes)}")
    print(f"Actual nodes: {len(actual_nodes)}")
    
    # Check for removed intermediate nodes
    removed_nodes = ["relationships_to_plan", "self_growth_to_plan", "no_goal_to_plan"]
    for node in removed_nodes:
        if node in actual_nodes:
            print(f"❌ Removed node still present: {node}")
            sys.exit(1)
        else:
            print(f"✅ Removed node not present: {node}")
    
    # Check that all expected nodes are present
    missing_nodes = set(expected_nodes) - set(actual_nodes)
    if missing_nodes:
        print(f"❌ Missing nodes: {missing_nodes}")
        sys.exit(1)
    
    print("✅ All expected nodes are present")
    print("✅ Architecture is correctly simplified")
    
    # Test node transitions
    from root_graph import get_change_obstacles_node, get_find_obstacles_node
    
    # Test change_obstacles transition
    change_obstacles_node = get_change_obstacles_node()
    test_state_with_goals = {"goals": ["goal1", "goal2"]}
    test_state_without_goals = {}
    
    next_node_with_goals = change_obstacles_node.next_node(test_state_with_goals)
    next_node_without_goals = change_obstacles_node.next_node(test_state_without_goals)
    
    if next_node_with_goals == "generate_plan":
        print("✅ change_obstacles correctly transitions to generate_plan when goals are present")
    else:
        print(f"❌ change_obstacles incorrectly transitions to {next_node_with_goals}")
        sys.exit(1)
    
    if next_node_without_goals == "change_obstacles":
        print("✅ change_obstacles correctly stays in place when goals are missing")
    else:
        print(f"❌ change_obstacles incorrectly transitions to {next_node_without_goals}")
        sys.exit(1)
    
    # Test find_obstacles transition
    find_obstacles_node = get_find_obstacles_node()
    
    next_node_with_goals = find_obstacles_node.next_node(test_state_with_goals)
    next_node_without_goals = find_obstacles_node.next_node(test_state_without_goals)
    
    if next_node_with_goals == "generate_plan":
        print("✅ find_obstacles correctly transitions to generate_plan when goals are present")
    else:
        print(f"❌ find_obstacles incorrectly transitions to {next_node_with_goals}")
        sys.exit(1)
    
    if next_node_without_goals == "find_obstacles":
        print("✅ find_obstacles correctly stays in place when goals are missing")
    else:
        print(f"❌ find_obstacles incorrectly transitions to {next_node_without_goals}")
        sys.exit(1)
    
    print("\n🎉 All architecture tests passed!")
    print("✅ Architecture is now consistent: all *_obstacles nodes transition directly to generate_plan")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test error: {e}")
    sys.exit(1)
