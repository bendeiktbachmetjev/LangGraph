from typing import Callable, Dict, Any, Optional

# Node structure for the graph
class Node:
    def __init__(self, node_id: str, system_prompt: str, outputs: Dict[str, Any], next_node: Optional[Callable] = None):
        self.node_id = node_id
        self.system_prompt = system_prompt
        self.outputs = outputs  # Expected outputs from LLM
        self.next_node = next_node  # Function to determine next node

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
            "no_goal": "no_goal_intro"
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
        system_prompt="You are helping the user turn their main career obstacles into positive, actionable goals. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "goals": list,
            "next": str
        },
        next_node=lambda state: "generate_plan" if state.get("goals") else "improve_obstacles"
    )

def get_relationships_intro_node():
    return Node(
        node_id="relationships_intro",
        system_prompt="You are introducing the relationships goal section. Motivate the user and explain that you will ask a few questions to help clarify their relationship goals.",
        outputs={
            "reply": str,
            "next": "relationships_people"
        },
        next_node=lambda state: "relationships_people"
    )

def get_relationships_people_node():
    return Node(
        node_id="relationships_people",
        system_prompt="You are helping the user clarify with whom they want to improve relationships. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "state.relation_people": str,
            "next": str
        },
        next_node=lambda state: "relationships_issues" if state.get("relation_people") else "relationships_people"
    )

def get_relationships_issues_node():
    return Node(
        node_id="relationships_issues",
        system_prompt="You are helping the user turn their main relationship issues into positive, actionable goals. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "goals": list,
            "next": str
        },
        next_node=lambda state: "relationships_to_plan" if state.get("goals") else "relationships_issues"
    )

def get_relationships_to_plan_node():
    return Node(
        node_id="relationships_to_plan",
        system_prompt="You are finishing the relationships information collection. Thank the user and inform them that a personalized plan will be generated next.",
        outputs={
            "reply": str,
            "next": "generate_plan"
        },
        next_node=lambda state: "generate_plan"
    )

def get_self_growth_intro_node():
    return Node(
        node_id="self_growth_intro",
        system_prompt="You are introducing the self-growth goal section. Motivate the user and explain that you will ask a few questions to help clarify their self-improvement goals.",
        outputs={
            "reply": str,
            "next": "self_growth_goal"
        },
        next_node=lambda state: "self_growth_goal"
    )

def get_self_growth_goal_node():
    return Node(
        node_id="self_growth_goal",
        system_prompt="You are helping the user clarify their main self-improvement goal. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "state.goals": str,
            "next": str
        },
        next_node=lambda state: "self_growth_obstacles" if state.get("goals") else "self_growth_goal"
    )

def get_self_growth_obstacles_node():
    return Node(
        node_id="self_growth_obstacles",
        system_prompt="You are helping the user turn their main self-growth obstacles into positive, actionable goals. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "goals": list,
            "next": str
        },
        next_node=lambda state: "self_growth_to_plan" if state.get("goals") else "self_growth_obstacles"
    )

def get_no_goal_intro_node():
    return Node(
        node_id="no_goal_intro",
        system_prompt="You are introducing the no-goal section. Be supportive and explain that it's okay to not have a specific goal right now, and you'll help them explore possibilities.",
        outputs={
            "reply": str,
            "next": "no_goal_reason"
        },
        next_node=lambda state: "no_goal_reason"
    )

def get_no_goal_reason_node():
    return Node(
        node_id="no_goal_reason",
        system_prompt="You are helping the user explore why they don't have a specific goal and what might be meaningful for them. If the answer is unclear or missing, politely ask again.",
        outputs={
            "reply": str,
            "state.no_goal_reason": str,
            "next": str
        },
        next_node=lambda state: "no_goal_to_plan" if state.get("no_goal_reason") else "no_goal_reason"
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

# Graph definition (for now, only the first node)
root_graph = {
    "collect_basic_info": get_collect_basic_info_node(),
    "classify_category": get_classify_category_node(),
    "improve_intro": get_improve_intro_node(),
    "improve_skills": get_improve_skills_node(),
    "improve_obstacles": get_improve_obstacles_node(),
    "relationships_intro": get_relationships_intro_node(),
    "relationships_people": get_relationships_people_node(),
    "relationships_issues": get_relationships_issues_node(),
    "relationships_to_plan": get_relationships_to_plan_node(),
    "self_growth_intro": get_self_growth_intro_node(),
    "self_growth_goal": get_self_growth_goal_node(),
    "self_growth_obstacles": get_self_growth_obstacles_node(),
    "no_goal_intro": get_no_goal_intro_node(),
    "no_goal_reason": get_no_goal_reason_node(),
    "generate_plan": get_generate_plan_node(),
    "week1_chat": get_week1_chat_node(),
    # Other nodes will be added here later
} 