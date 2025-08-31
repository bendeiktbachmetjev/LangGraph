import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from .types import CollectBasicInfoResponse, ClassifyCategoryResponse
from .root_graph import Node
from .memory_manager import MemoryManager
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Manages state updates based on LLM responses"""
    
    @staticmethod
    def parse_llm_response(llm_response: str, node: Node) -> Dict[str, Any]:
        """
        Parse LLM response and return structured data
        """
        try:
            # Parse JSON response
            response_data = json.loads(llm_response)
            
            # Validate response based on node type
            if node.node_id == "collect_basic_info":
                validated_response = CollectBasicInfoResponse(**response_data)
                return validated_response.model_dump()
            elif node.node_id == "classify_category":
                validated_response = ClassifyCategoryResponse(**response_data)
                return validated_response.model_dump()
            else:
                # For other nodes, return raw data for now
                return response_data
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing LLM response: {e}")
    
    @staticmethod
    def update_state(current_state: Dict[str, Any], llm_data: Dict[str, Any], node: Node) -> Dict[str, Any]:
        """
        Update current state with data from LLM response
        """
        updated_state = current_state.copy()
        
        # Update state based on node type
        if node.node_id == "collect_basic_info":
            # Handle user_name
            if llm_data.get("user_name") and llm_data["user_name"] != "unavailable":
                updated_state["user_name"] = llm_data["user_name"]
            elif llm_data.get("user_name") == "unavailable":
                updated_state["user_name"] = "unavailable"
            elif "user_name" in updated_state:
                # Сохраняем уже существующее имя, если новое не пришло
                pass
            # Handle user_age
            if llm_data.get("user_age") is not None and llm_data["user_age"] != "unavailable":
                updated_state["user_age"] = llm_data["user_age"]
            elif llm_data.get("user_age") == "unavailable":
                updated_state["user_age"] = "unavailable"
            elif "user_age" in updated_state:
                # Сохраняем уже существующий возраст, если новый не пришёл
                pass
            # Если user_age is None, не обновляем (оставляем существующее значение или None)
        
        elif node.node_id == "classify_category":
            if llm_data.get("goal_type"):
                # Persist normalized 4-way classification
                updated_state["goal_type"] = llm_data["goal_type"]
        elif node.node_id == "improve_obstacles":
            if llm_data.get("goals") and llm_data["goals"] != "unavailable":
                updated_state["goals"] = llm_data["goals"]
            elif llm_data.get("goals") == "unavailable":
                updated_state["goals"] = []
            # Also store self-perceived negative qualities if provided
            if isinstance(llm_data.get("negative_qualities"), list):
                updated_state["negative_qualities"] = llm_data["negative_qualities"]
        elif node.node_id == "retrieve_reg":
            # Store retrieved chunks for use in generate_plan
            if llm_data.get("retrieved_chunks"):
                updated_state["retrieved_chunks"] = llm_data["retrieved_chunks"]
        elif node.node_id == "generate_plan":
            # Проверяем, что plan — dict и содержит 12 тем
            plan = llm_data.get("plan")
            if isinstance(plan, dict) and len(plan) == 12 and all(plan.get(f"week_{i}_topic") for i in range(1, 13)):
                updated_state["plan"] = plan
            else:
                logger.error(f"Invalid plan structure in generate_plan: {plan}")
            if llm_data.get("onboarding_chat_summary"):
                updated_state["onboarding_chat_summary"] = llm_data["onboarding_chat_summary"]
            updated_state["phase"] = "week1"
            # Clear onboarding history after plan generation, since summary is already saved
            updated_state["history"] = []
        elif node.node_id == "week1_chat":
            # Append new week1 messages to the main history array
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
        elif node.node_id == "week2_chat":
            # Clear history when transitioning to week2 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 2:
                updated_state["history"] = []
            updated_state["current_week"] = 2
        elif node.node_id == "week3_chat":
            # Clear history when transitioning to week3 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 3:
                updated_state["history"] = []
            updated_state["current_week"] = 3
        elif node.node_id == "week4_chat":
            # Clear history when transitioning to week4 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 4:
                updated_state["history"] = []
            updated_state["current_week"] = 4
        elif node.node_id == "week5_chat":
            # Clear history when transitioning to week5 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 5:
                updated_state["history"] = []
            updated_state["current_week"] = 5
        elif node.node_id == "week6_chat":
            # Clear history when transitioning to week6 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 6:
                updated_state["history"] = []
            updated_state["current_week"] = 6
        elif node.node_id == "week7_chat":
            # Clear history when transitioning to week7 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 7:
                updated_state["history"] = []
            updated_state["current_week"] = 7
        elif node.node_id == "week8_chat":
            # Clear history when transitioning to week8 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 8:
                updated_state["history"] = []
            updated_state["current_week"] = 8
        elif node.node_id == "week9_chat":
            # Clear history when transitioning to week9 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 9:
                updated_state["history"] = []
            updated_state["current_week"] = 9
        elif node.node_id == "week10_chat":
            # Clear history when transitioning to week10 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 10:
                updated_state["history"] = []
            updated_state["current_week"] = 10
        elif node.node_id == "week11_chat":
            # Clear history when transitioning to week11 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 11:
                updated_state["history"] = []
            updated_state["current_week"] = 11
        elif node.node_id == "week12_chat":
            # Clear history when transitioning to week12 and append new messages
            if llm_data.get("history"):
                updated_state["history"] = llm_data["history"]
            # Update current week and clear history if transitioning
            current_week = updated_state.get("current_week", 1)
            if current_week != 12:
                updated_state["history"] = []
            updated_state["current_week"] = 12
        elif node.node_id == "change_skills":
            # Save skills/interests/activities if provided
            if isinstance(llm_data.get("skills"), list):
                updated_state["skills"] = llm_data["skills"]
            if isinstance(llm_data.get("interests"), list):
                updated_state["interests"] = llm_data["interests"]
            if isinstance(llm_data.get("activities"), list):
                updated_state["activities"] = llm_data["activities"]
            if isinstance(llm_data.get("exciting_topics"), list):
                updated_state["exciting_topics"] = llm_data["exciting_topics"]
        elif node.node_id == "change_obstacles":
            if llm_data.get("goals") and llm_data["goals"] != "unavailable":
                updated_state["goals"] = llm_data["goals"]
                # Если goals определены, сразу готовимся к генерации плана
                updated_state["next"] = "generate_plan"
            elif llm_data.get("goals") == "unavailable":
                updated_state["goals"] = []

        elif node.node_id == "improve_intro":
            # Persist structured job circumstances if provided
            if isinstance(llm_data.get("job_circumstances"), dict):
                updated_state["job_circumstances"] = llm_data["job_circumstances"]
        elif node.node_id == "change_intro":
            # Persist structured career change circumstances if provided
            if isinstance(llm_data.get("career_change_circumstances"), dict):
                updated_state["career_change_circumstances"] = llm_data["career_change_circumstances"]
        elif node.node_id == "find_intro":
            # Persist structured background circumstances if provided
            if isinstance(llm_data.get("background_circumstances"), dict):
                updated_state["background_circumstances"] = llm_data["background_circumstances"]
        elif node.node_id == "improve_skills":
            # Save skills/interests/activities if provided
            if isinstance(llm_data.get("skills"), list):
                updated_state["skills"] = llm_data["skills"]
            if isinstance(llm_data.get("interests"), list):
                updated_state["interests"] = llm_data["interests"]
            if isinstance(llm_data.get("activities"), list):
                updated_state["activities"] = llm_data["activities"]
            if isinstance(llm_data.get("exciting_topics"), list):
                updated_state["exciting_topics"] = llm_data["exciting_topics"]
        elif node.node_id == "find_skills":
            # Save passions and interests if provided
            if isinstance(llm_data.get("passions"), list):
                updated_state["passions"] = llm_data["passions"]
            if isinstance(llm_data.get("exciting_topics"), list):
                updated_state["exciting_topics"] = llm_data["exciting_topics"]
            if isinstance(llm_data.get("content_consumption"), list):
                updated_state["content_consumption"] = llm_data["content_consumption"]
        elif node.node_id == "find_obstacles":
            if llm_data.get("obstacles") and llm_data["obstacles"] != "unavailable":
                updated_state["obstacles"] = llm_data["obstacles"]
                # Если obstacles определены, сразу готовимся к генерации плана
                updated_state["next"] = "generate_plan"
            elif llm_data.get("obstacles") == "unavailable":
                updated_state["obstacles"] = []
        elif node.node_id == "lost_skills":
            if llm_data.get("lost_skills") and llm_data["lost_skills"] != "unavailable":
                updated_state["lost_skills"] = llm_data["lost_skills"]
                # Если причина определена, сразу готовимся к генерации плана
                updated_state["next"] = "generate_plan"
            elif llm_data.get("lost_skills") == "unavailable":
                updated_state["lost_skills"] = "unavailable"
        
        # Update timestamp
        updated_state["updated_at"] = datetime.now(timezone.utc)
        
        return updated_state
    
    @staticmethod
    def update_state_with_memory(current_state: Dict[str, Any], llm_data: Dict[str, Any], 
                                node: Node, user_message: str = None, assistant_reply: str = None) -> Dict[str, Any]:
        """
        Update current state with data from LLM response and manage memory system
        
        Args:
            current_state: Current session state
            llm_data: Parsed LLM response data
            node: Current node
            user_message: Optional user message to add to memory
            assistant_reply: Optional assistant reply to add to memory
            
        Returns:
            Updated state with memory management
        """
        # First, perform standard state update
        updated_state = StateManager.update_state(current_state, llm_data, node)
        
        # Initialize memory fields if not present
        if "prompt_context" not in updated_state:
            updated_state["prompt_context"] = MemoryManager.initialize_prompt_context()
        if "message_count" not in updated_state:
            updated_state["message_count"] = 0
        if "current_week" not in updated_state:
            updated_state["current_week"] = 1
        
        # Add messages to memory if provided
        if user_message:
            new_message = {"role": "user", "content": user_message}
            updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
            
        if assistant_reply:
            new_message = {"role": "assistant", "content": assistant_reply}
            updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
        
        # Evaluate important facts from user message
        if user_message:
            user_msg_dict = {"role": "user", "content": user_message}
            important_facts = MemoryManager.evaluate_important_facts(updated_state, user_msg_dict)
            for fact in important_facts:
                updated_state = MemoryManager.add_important_fact(updated_state, fact)
        
        # Check for week transition and create weekly summary if needed
        updated_state = StateManager._handle_week_transition(updated_state, node)
        
        logger.info(f"Updated state with memory for session {updated_state.get('session_id', 'unknown')}")
        
        return updated_state
    
    @staticmethod
    def _handle_week_transition(state: Dict[str, Any], node: Node) -> Dict[str, Any]:
        """
        Handle week transitions and create weekly summaries
        
        Args:
            state: Current session state
            node: Current node
            
        Returns:
            Updated state with weekly summary if transition occurred
        """
        # Detect week transitions based on node
        week_nodes = {
            "week1_chat": 1, "week2_chat": 2, "week3_chat": 3, "week4_chat": 4,
            "week5_chat": 5, "week6_chat": 6, "week7_chat": 7, "week8_chat": 8,
            "week9_chat": 9, "week10_chat": 10, "week11_chat": 11, "week12_chat": 12
        }
        
        if node.node_id in week_nodes:
            new_week = week_nodes[node.node_id]
            current_week = state.get("current_week", 1)
            
            # If transitioning to a new week, create summary of previous week
            if new_week > current_week:
                session_id = state.get("session_id", "unknown")
                
                # Create summary for the completed week
                weekly_summary = MemoryManager.create_weekly_summary(
                    session_id, state, current_week
                )
                
                # Store weekly summary in prompt_context
                if "prompt_context" not in state:
                    state["prompt_context"] = MemoryManager.initialize_prompt_context()
                
                state["prompt_context"]["weekly_summaries"][str(current_week)] = weekly_summary
                state["current_week"] = new_week
                
                logger.info(f"Created weekly summary for week {current_week}, session {session_id}")
        
        return state
    
    @staticmethod
    def get_memory_stats(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get memory system statistics for debugging and monitoring
        
        Args:
            state: Current session state
            
        Returns:
            Dictionary with memory statistics
        """
        prompt_context = state.get("prompt_context", {})
        
        stats = {
            "message_count": state.get("message_count", 0),
            "current_week": state.get("current_week", 1),
            "running_summary_exists": prompt_context.get("running_summary") is not None,
            "recent_messages_count": len(prompt_context.get("recent_messages", [])),
            "important_facts_count": len(prompt_context.get("important_facts", [])),
            "weekly_summaries_count": len(prompt_context.get("weekly_summaries", {})),
            "history_count": len(state.get("history", [])),
            "estimated_tokens": MemoryManager.get_token_estimate(state)
        }
        
        return stats
    
    @staticmethod
    def get_next_node(llm_data: Dict[str, Any], current_node: Node, updated_state: Dict[str, Any]) -> str:
        """
        Determine next node based on LLM response and state
        """
        def is_name_provided(val):
            return val not in (None, "", "unavailable", "unknown")
        def is_age_provided(val):
            return val not in (None, "", "unavailable")
        if current_node.node_id == "collect_basic_info":
            name = updated_state.get("user_name")
            age = updated_state.get("user_age")
            # Если нет имени — остаёмся в collect_basic_info
            if not is_name_provided(name):
                return "collect_basic_info"
            # Если есть имя, но нет возраста — остаёмся в collect_basic_info
            if age is None or age == "":
                return "collect_basic_info"
            # Если есть имя и возраст (или возраст == 'unknown'), идём дальше
        return llm_data.get("next", current_node.node_id) 