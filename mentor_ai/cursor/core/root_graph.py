from typing import Callable, Dict, Any, Optional

# Node structure for the graph
class Node:
    def __init__(self, node_id: str, system_prompt: str, assistant_prompt: str, outputs: Dict[str, Any], next_node: Optional[Callable] = None):
        self.node_id = node_id
        self.system_prompt = system_prompt
        self.assistant_prompt = assistant_prompt
        self.outputs = outputs  # Expected outputs from LLM
        self.next_node = next_node  # Function to determine next node

# First node: collect_basic_info
def get_collect_basic_info_node():
    return Node(
        node_id="collect_basic_info",
        system_prompt="You are collecting the user's basic personal data through natural conversation.",
        assistant_prompt="Let's begin with a quick intro. What's your name and how old are you?",
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
        system_prompt="Ask the user whether they have a goal, and analyze their natural response to determine the category.",
        assistant_prompt="Do you currently have a main personal goal? If yes, what kind of goal is it? Is it about career, self-growth, relationships, or do you feel you have no goal right now?",
        outputs={
            "reply": str,
            "state.goal_type": str,  # 'career' | 'self_growth' | 'relationships' | 'no_goal'
            "next": str
        },
        next_node=lambda state: {
            "career": "career_intro",
            "self_growth": "self_growth_intro",
            "relationships": "relationships_intro",
            "no_goal": "no_goal_intro"
        }.get(state.get("goal_type"), "classify_category")
    )

def get_career_intro_node():
    return Node(
        node_id="career_intro",
        system_prompt="You are introducing the career goal section. Motivate the user and explain that you will ask a few questions to help clarify their career goals.",
        assistant_prompt="Let's talk about your career! In the next steps, I'll ask a few questions to help you clarify your career goals and challenges. Ready?",
        outputs={
            "reply": str,
            "next": "career_goal"
        },
        next_node=lambda state: "career_goal"
    )

def get_career_goal_node():
    return Node(
        node_id="career_goal",
        system_prompt="You are helping the user clarify their main career goal. If the answer is unclear or missing, politely ask again.",
        assistant_prompt="What is your main career goal? For example, a desired position, promotion, new field, or something else.",
        outputs={
            "reply": str,
            "state.goals": str,
            "next": str
        },
        next_node=lambda state: "career_obstacles" if state.get("goals") else "career_goal"
    )

def get_career_obstacles_node():
    return Node(
        node_id="career_obstacles",
        system_prompt="You are helping the user identify the main obstacles or challenges preventing them from achieving their career goal. If the answer is unclear or missing, politely ask again.",
        assistant_prompt="What are the main obstacles or challenges that might prevent you from reaching your career goal? For example, lack of experience, skills, confidence, or something else.",
        outputs={
            "reply": str,
            "state.career_obstacles": str,
            "next": str
        },
        next_node=lambda state: "career_to_plan" if state.get("career_obstacles") else "career_obstacles"
    )

def get_career_to_plan_node():
    return Node(
        node_id="career_to_plan",
        system_prompt="You are finishing the career information collection. Thank the user and inform them that a personalized plan will be generated next.",
        assistant_prompt="Thank you for sharing all the details! Now I'll prepare a personalized career plan for you.",
        outputs={
            "reply": str,
            "next": "generate_plan"
        },
        next_node=lambda state: "generate_plan"
    )

def get_relationships_intro_node():
    return Node(
        node_id="relationships_intro",
        system_prompt="You are introducing the relationships goal section. Motivate the user and explain that you will ask a few questions to help clarify their relationship goals.",
        assistant_prompt="Let's talk about your relationships! In the next steps, I'll ask a few questions to help you clarify your relationship goals and challenges. Ready?",
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
        assistant_prompt="With whom would you like to improve your relationships? For example, family, friends, partner, colleagues, or someone else?",
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
        system_prompt="Help the user formulate a goal to improve their relationships, based on the described issue. The output should be a clear, actionable goal, not just a description of the problem.",
        assistant_prompt="What goal would you like to set to improve this situation? For example: 'Improve communication with my partner', 'Build more trust in my family', etc.",
        outputs={
            "reply": str,
            "state.goals": str,  # This is now a goal to resolve the issue, not the issue itself
            "next": str
        },
        next_node=lambda state: "relationships_to_plan" if state.get("goals") else "relationships_issues"
    )

def get_relationships_to_plan_node():
    return Node(
        node_id="relationships_to_plan",
        system_prompt="You are finishing the relationships information collection. Thank the user and inform them that a personalized plan will be generated next.",
        assistant_prompt="Thank you for sharing all the details! Now I'll prepare a personalized relationships plan for you.",
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
        assistant_prompt="Let's talk about your personal growth! In the next steps, I'll ask a few questions to help you clarify your self-improvement goals and challenges. Ready?",
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
        assistant_prompt="What is your main self-improvement goal? For example, building confidence, developing new skills, improving habits, or something else?",
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
        system_prompt="You are helping the user identify the main obstacles or challenges preventing them from achieving their self-improvement goal. If the answer is unclear or missing, politely ask again.",
        assistant_prompt="What are the main obstacles or challenges that might prevent you from reaching your self-improvement goal? For example, lack of time, motivation, support, or something else?",
        outputs={
            "reply": str,
            "state.self_growth_obstacles": str,
            "next": str
        },
        next_node=lambda state: "self_growth_to_plan" if state.get("self_growth_obstacles") else "self_growth_obstacles"
    )

def get_self_growth_to_plan_node():
    return Node(
        node_id="self_growth_to_plan",
        system_prompt="You are finishing the self-growth information collection. Thank the user and inform them that a personalized plan will be generated next.",
        assistant_prompt="Thank you for sharing all the details! Now I'll prepare a personalized self-improvement plan for you.",
        outputs={
            "reply": str,
            "next": "generate_plan"
        },
        next_node=lambda state: "generate_plan"
    )

def get_no_goal_intro_node():
    return Node(
        node_id="no_goal_intro",
        system_prompt="You are introducing the no-goal section. Be supportive and explain that it's okay to not have a specific goal right now, and you'll help them explore possibilities.",
        assistant_prompt="It's completely okay to not have a specific goal right now! Many people go through periods where they're not sure what they want to focus on. Let's explore together what might be meaningful for you.",
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
        assistant_prompt="What do you think is the main reason you don't have a specific goal right now? For example, feeling overwhelmed, not knowing where to start, or something else?",
        outputs={
            "reply": str,
            "state.no_goal_reason": str,
            "next": str
        },
        next_node=lambda state: "no_goal_to_plan" if state.get("no_goal_reason") else "no_goal_reason"
    )

def get_no_goal_to_plan_node():
    return Node(
        node_id="no_goal_to_plan",
        system_prompt="You are finishing the no-goal information collection. Thank the user and inform them that a personalized exploration plan will be generated next.",
        assistant_prompt="Thank you for sharing! Now I'll prepare a personalized plan to help you explore different possibilities and find what might be meaningful for you.",
        outputs={
            "reply": str,
            "next": "generate_plan"
        },
        next_node=lambda state: "generate_plan"
    )

def get_generate_plan_node():
    return Node(
        node_id="generate_plan",
        system_prompt="You are an expert coach. Based on the user's state (goals, obstacles, etc.), generate a 12-week personalized plan. Each week should have a unique topic or technique relevant to the user's context.",
        assistant_prompt="Based on your answers, I will now generate a 12-week personalized plan. Each week will focus on a specific topic or technique to help you reach your goal.",
        outputs={
            "reply": str,
            "plan": dict,  # {"week_1_topic": str, ..., "week_12_topic": str}
            "next": "plan_ready"
        },
        next_node=lambda state: "plan_ready"
    )

def get_plan_ready_node():
    return Node(
        node_id="plan_ready",
        system_prompt="You are finishing the session. Congratulate the user, summarize that the plan is ready, wish them success, and clearly instruct the user to close this chat and go to the My Coach section.",
        assistant_prompt="Your personalized 12-week plan is ready! Wishing you success on your journey. Please close this chat and go to the My Coach section to continue working with your plan. If you need support or want to review your plan, you can always return to My Coach.",
        outputs={
            "reply": str
        },
        next_node=None
    )

# Graph definition (for now, only the first node)
root_graph = {
    "collect_basic_info": get_collect_basic_info_node(),
    "classify_category": get_classify_category_node(),
    "career_intro": get_career_intro_node(),
    "career_goal": get_career_goal_node(),
    "career_obstacles": get_career_obstacles_node(),
    "career_to_plan": get_career_to_plan_node(),
    "relationships_intro": get_relationships_intro_node(),
    "relationships_people": get_relationships_people_node(),
    "relationships_issues": get_relationships_issues_node(),
    "relationships_to_plan": get_relationships_to_plan_node(),
    "self_growth_intro": get_self_growth_intro_node(),
    "self_growth_goal": get_self_growth_goal_node(),
    "self_growth_obstacles": get_self_growth_obstacles_node(),
    "self_growth_to_plan": get_self_growth_to_plan_node(),
    "no_goal_intro": get_no_goal_intro_node(),
    "no_goal_reason": get_no_goal_reason_node(),
    "no_goal_to_plan": get_no_goal_to_plan_node(),
    "generate_plan": get_generate_plan_node(),
    "plan_ready": get_plan_ready_node(),
    # Other nodes will be added here later
} 