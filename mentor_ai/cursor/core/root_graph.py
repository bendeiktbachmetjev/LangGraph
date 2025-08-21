from typing import Callable, Dict, Any, Optional

# Node structure for the graph
class Node:
    def __init__(self, node_id: str, system_prompt: str, outputs: Dict[str, Any], next_node: Optional[Callable] = None, executor: Optional[Callable] = None):
        self.node_id = node_id
        self.system_prompt = system_prompt
        self.outputs = outputs  # Expected outputs from LLM
        self.next_node = next_node  # Function to determine next node
        self.executor = executor  # Optional executor function for non-LLM nodes

# First node: collect_basic_info
def get_collect_basic_info_node():
    return Node(
        node_id="collect_basic_info",
        system_prompt="You are collecting the user's basic personal data through natural conversation.",
        outputs={
            "reply": str,
            "state.user_name": str,  # Extracted by LLM
            "state.user_age": int,   # Extracted by LLM
            "next": "classify_category"
        },
        next_node=lambda state: "classify_category"
    )

def get_classify_category_node():
    return Node(
        node_id="classify_category",
        system_prompt="Analyze the user's work situation and goals to determine the appropriate category.",
        outputs={
            "reply": str,
            "state.goal_type": str,  # 'career_improve' | 'career_change' | 'career_find' | 'no_goal'
            "next": str
        },
        next_node=lambda state: {
            "career_improve": "improve_intro",
            "career_change": "improve_intro", 
            "career_find": "improve_intro",
            "no_goal": "lost_intro"
        }.get(state.get("goal_type"), "classify_category")
    )

def get_improve_intro_node():
    return Node(
        node_id="improve_intro",
        system_prompt="You are introducing the career goal section. Based on the user's goal_type (career_improve, career_change, or career_find), ask the appropriate question about their specific career situation.",
        outputs={
            "reply": str,
            "job_circumstances": dict,
            "next": str
        },
        next_node=lambda state: "improve_skills"
    )

def get_improve_skills_node():
    return Node(
        node_id="improve_skills",
        system_prompt="Understand user's broader strengths and interests: skills they possess, interests they enjoy, and activities they do in free time.",
        outputs={
            "reply": str,
            "skills": list,
            "interests": list,
            "activities": list,
            "exciting_topics": list,
            "next": str
        },
        next_node=lambda state: "improve_obstacles" if (state.get("skills") or state.get("interests")) else "improve_skills"
    )

def get_improve_obstacles_node():
    return Node(
        node_id="improve_obstacles",
        system_prompt="You are helping the user turn their main career obstacles into positive, actionable goals. Capture self-perceived negative qualities neutrally. If unclear or missing, ask one concise clarification.",
        outputs={
            "reply": str,
            "goals": list,
            "negative_qualities": list,
            "next": str
        },
        next_node=lambda state: "retrieve_reg" if state.get("goals") else "improve_obstacles"
    )

def get_change_intro_node():
    return Node(
        node_id="change_intro",
        system_prompt="You are introducing the career change goal section. Motivate the user and explain that you will ask a few questions to help clarify their career change goals.",
        outputs={
            "reply": str,
            "career_change_circumstances": dict,
            "next": str
        },
        next_node=lambda state: "change_skills" if state.get("career_change_circumstances") else "change_intro"
    )

def get_change_skills_node():
    return Node(
        node_id="change_skills",
        system_prompt="You are helping the user clarify their skills and interests for career change. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "skills": list,
            "interests": list,
            "activities": list,
            "exciting_topics": list,
            "next": str
        },
        next_node=lambda state: "change_obstacles" if (state.get("skills") or state.get("interests") or state.get("activities") or state.get("exciting_topics")) else "change_skills"
    )

def get_change_obstacles_node():
    return Node(
        node_id="change_obstacles",
        system_prompt="You are helping the user turn their main relationship issues into positive, actionable goals. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "goals": list,
            "next": str
        },
        next_node=lambda state: "retrieve_reg" if state.get("goals") else "change_obstacles"
    )

def get_find_intro_node():
    return Node(
        node_id="find_intro",
        system_prompt="You are introducing the path-finding section for people without jobs. Motivate the user and explain that you will ask a few questions to help understand their background and find their path.",
        outputs={
            "reply": str,
            "background_circumstances": dict,
            "next": str
        },
        next_node=lambda state: "find_skills" if state.get("background_circumstances") else "find_intro"
    )

def get_find_skills_node():
    return Node(
        node_id="find_skills",
        system_prompt="You are helping the user discover their passions and what truly excites them. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "passions": list,
            "exciting_topics": list,
            "content_consumption": list,
            "next": str
        },
        next_node=lambda state: "find_obstacles" if (state.get("passions") or state.get("exciting_topics") or state.get("content_consumption")) else "find_skills"
    )

def get_find_obstacles_node():
    return Node(
        node_id="find_obstacles",
        system_prompt="You are helping the user turn their main self-growth obstacles into positive, actionable goals. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "goals": list,
            "next": str
        },
        next_node=lambda state: "retrieve_reg" if state.get("goals") else "find_obstacles"
    )

def get_lost_intro_node():
    return Node(
        node_id="lost_intro",
        system_prompt="You are introducing the no-goal section. Be supportive and explain that it's okay to not have a specific goal right now, and you'll help them explore possibilities.",
        outputs={
            "reply": str,
            "next": "lost_skills"
        },
        next_node=lambda state: "lost_skills"
    )

def get_lost_skills_node():
    return Node(
        node_id="lost_skills",
        system_prompt="You are helping the user explore why they don't have a specific goal and what might be meaningful for them. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "state.lost_skills": str,
            "next": str
        },
        next_node=lambda state: "retrieve_reg" if state.get("lost_skills") else "lost_skills"
    )

def get_generate_plan_node():
    return Node(
        node_id="generate_plan",
        system_prompt=(
            "1. Based on the user's state (goals, obstacles, etc.), generate a 12-week personalized plan. Each week should have a unique topic or technique relevant to the user's context.\n"
            "2. Provide a concise summary of the onboarding chat (3-5 sentences) as onboarding_chat_summary.\n"
            "3. In the reply field, briefly reflect on the whole onboarding conversation: mention the main points and gently inform them that they can now close this chat and the 'My Coach' section is available.\n"
            "Be warm, supportive, and clear."
        ),
        outputs={
            "reply": str,
            "plan": dict,  # {"week_1_topic": str, ..., "week_12_topic": str}
            "onboarding_chat_summary": str,
            "next": "week1_chat"
        },
        next_node=lambda state: "week1_chat"
    )

def get_retrieve_reg_node():
    """Node for retrieving relevant coaching knowledge from RAG system."""
    def retrieve_reg_executor(user_message: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Executor function for retrieve_reg node."""
        from ...app.config import settings
        
        # Check if RAG is enabled
        if not settings.REG_ENABLED:
            return {
                "retrieved_chunks": [],
                "next": "generate_plan",
                "reply": ""
            }
        
        try:
            # Import here to avoid circular imports
            from ..modules.retrieval.retriever import RegRetriever
            
            # Initialize retriever
            retriever = RegRetriever()
            retriever.initialize(settings.RAG_INDEX_PATH)
            
            # Retrieve relevant documents
            result = retriever.retrieve(current_state, user_message)
            
            # Convert to snippets for LLM context
            snippets = result.to_snippets(max_chars=settings.MAX_CONTEXT_CHARS)
            
            return {
                "retrieved_chunks": snippets,
                "next": "generate_plan",
                "reply": ""
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in retrieve_reg executor: {e}")
            return {
                "retrieved_chunks": [],
                "next": "generate_plan", 
                "reply": ""
            }
    
    return Node(
        node_id="retrieve_reg",
        system_prompt="Retrieve relevant coaching knowledge from the knowledge base.",
        outputs={
            "retrieved_chunks": list,
            "next": "generate_plan"
        },
        next_node=lambda state: "generate_plan",
        executor=retrieve_reg_executor
    )

def get_week1_chat_node():
    return Node(
        node_id="week1_chat",
        system_prompt="You are the user's mentor for Week 1. Use the onboarding_chat_summary and the topic for week 1 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week1_history.",
        outputs={
            "reply": str,
            "week1_history": list,
            "next": "week1_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week1_chat"
    )

def get_week2_chat_node():
    return Node(
        node_id="week2_chat",
        system_prompt="You are the user's mentor for Week 2. Use the onboarding_chat_summary and the topic for week 2 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week2_history.",
        outputs={
            "reply": str,
            "week2_history": list,
            "next": "week2_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week2_chat"
    )

def get_week3_chat_node():
    return Node(
        node_id="week3_chat",
        system_prompt="You are the user's mentor for Week 3. Use the onboarding_chat_summary and the topic for week 3 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week3_history.",
        outputs={
            "reply": str,
            "week3_history": list,
            "next": "week3_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week3_chat"
    )

def get_week4_chat_node():
    return Node(
        node_id="week4_chat",
        system_prompt="You are the user's mentor for Week 4. Use the onboarding_chat_summary and the topic for week 4 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week4_history.",
        outputs={
            "reply": str,
            "week4_history": list,
            "next": "week4_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week4_chat"
    )

def get_week5_chat_node():
    return Node(
        node_id="week5_chat",
        system_prompt="You are the user's mentor for Week 5. Use the onboarding_chat_summary and the topic for week 5 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week5_history.",
        outputs={
            "reply": str,
            "week5_history": list,
            "next": "week5_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week5_chat"
    )

def get_week6_chat_node():
    return Node(
        node_id="week6_chat",
        system_prompt="You are the user's mentor for Week 6. Use the onboarding_chat_summary and the topic for week 6 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week6_history.",
        outputs={
            "reply": str,
            "week6_history": list,
            "next": "week6_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week6_chat"
    )

def get_week7_chat_node():
    return Node(
        node_id="week7_chat",
        system_prompt="You are the user's mentor for Week 7. Use the onboarding_chat_summary and the topic for week 7 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week7_history.",
        outputs={
            "reply": str,
            "week7_history": list,
            "next": "week7_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week7_chat"
    )

def get_week8_chat_node():
    return Node(
        node_id="week8_chat",
        system_prompt="You are the user's mentor for Week 8. Use the onboarding_chat_summary and the topic for week 8 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week8_history.",
        outputs={
            "reply": str,
            "week8_history": list,
            "next": "week8_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week8_chat"
    )

def get_week9_chat_node():
    return Node(
        node_id="week9_chat",
        system_prompt="You are the user's mentor for Week 9. Use the onboarding_chat_summary and the topic for week 9 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week9_history.",
        outputs={
            "reply": str,
            "week9_history": list,
            "next": "week9_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week9_chat"
    )

def get_week10_chat_node():
    return Node(
        node_id="week10_chat",
        system_prompt="You are the user's mentor for Week 10. Use the onboarding_chat_summary and the topic for week 10 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week10_history.",
        outputs={
            "reply": str,
            "week10_history": list,
            "next": "week10_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week10_chat"
    )

def get_week11_chat_node():
    return Node(
        node_id="week11_chat",
        system_prompt="You are the user's mentor for Week 11. Use the onboarding_chat_summary and the topic for week 11 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week11_history.",
        outputs={
            "reply": str,
            "week11_history": list,
            "next": "week11_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week11_chat"
    )

def get_week12_chat_node():
    return Node(
        node_id="week12_chat",
        system_prompt="You are the user's mentor for Week 12. Use the onboarding_chat_summary and the topic for week 12 from the plan to start a focused conversation. Encourage the user to discuss and reflect on this week's topic. Save all messages in week12_history.",
        outputs={
            "reply": str,
            "week12_history": list,
            "next": "week12_chat"  # Stay in this node for ongoing chat
        },
        next_node=lambda state: "week12_chat"
    )

# Graph definition (for now, only the first node)
root_graph = {
    "collect_basic_info": get_collect_basic_info_node(),
    "classify_category": get_classify_category_node(),
    "improve_intro": get_improve_intro_node(),
    "improve_skills": get_improve_skills_node(),
    "improve_obstacles": get_improve_obstacles_node(),
    "change_intro": get_change_intro_node(),
    "change_skills": get_change_skills_node(),
    "change_obstacles": get_change_obstacles_node(),
    "find_intro": get_find_intro_node(),
    "find_skills": get_find_skills_node(),
    "find_obstacles": get_find_obstacles_node(),
    "lost_intro": get_lost_intro_node(),
    "lost_skills": get_lost_skills_node(),
    "retrieve_reg": get_retrieve_reg_node(),
    "generate_plan": get_generate_plan_node(),
    "week1_chat": get_week1_chat_node(),
    "week2_chat": get_week2_chat_node(),
    "week3_chat": get_week3_chat_node(),
    "week4_chat": get_week4_chat_node(),
    "week5_chat": get_week5_chat_node(),
    "week6_chat": get_week6_chat_node(),
    "week7_chat": get_week7_chat_node(),
    "week8_chat": get_week8_chat_node(),
    "week9_chat": get_week9_chat_node(),
    "week10_chat": get_week10_chat_node(),
    "week11_chat": get_week11_chat_node(),
    "week12_chat": get_week12_chat_node(),
    # Other nodes will be added here later
} 