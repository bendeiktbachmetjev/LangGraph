from typing import Dict, Any
from .root_graph import Node

def generate_llm_prompt(node: Node, state: Dict[str, Any], user_message: str) -> str:
    """
    Generate a prompt for LLM based on the current node, state, and user message.
    Now uses full chat history for context.
    """
    # System prompt (for LLM context)
    system = f"System: {node.system_prompt}"
    
    # Собираем историю сообщений
    history_lines = []
    history = state.get("history", [])
    for msg in history:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content")
        if not content:
            continue
        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            history_lines.append(f"Assistant: {content}")
    
    # Optionally, include state for LLM context (except sensitive fields)
    state_str = f"Current state: {state}" if state else ""
    
    # JSON instructions (как раньше)
    if node.node_id == "collect_basic_info":
        json_instructions = f"""
IMPORTANT: You are in the collect_basic_info node. Your ONLY task is to extract user_name and user_age.

Current state:
user_name: {state.get('user_name', None)}
user_age: {state.get('user_age', None)}

Please respond in JSON format with EXACTLY this structure:
{{
  "reply": "Your response to the user",
  "user_name": "extracted name or null if not provided",
  "user_age": "extracted age (number) or 'unknown' if refused, or null if not provided",
  "next": "next node to go to"
}}

CRITICAL RULES:
1. ONLY extract user_name and user_age - nothing else
2. If user_name is missing in state and user_age is missing in state, your reply MUST politely ask for BOTH name and age, and set next to "collect_basic_info"
3. If user_name is missing in state, but user_age is present, your reply MUST politely ask ONLY for name, and set next to "collect_basic_info"
4. If user_age is missing in state, but user_name is present, your reply MUST politely ask ONLY for age, and set next to "collect_basic_info"
5. If both are provided (или unavailable/unknown), your reply MUST include a greeting AND IMMEDIATELY ask: 'Do you currently have a main personal goal? If yes, what kind of goal is it? Is it about career, self-growth, relationships, or do you feel you have no goal right now?' and set next to "classify_category"
6. DO NOT ask about occupation, work, location, or anything else
7. ONLY ask for name and age (или цель, если оба поля уже есть)
8. If user refuses to provide name, set user_name to "unavailable" and stay on this node.
9. If user refuses to provide age, set user_age to "unknown" (string, not null) and proceed to next node.
"""
    elif node.node_id == "classify_category":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "goal_type": "career | self_growth | relationships | no_goal",
  "next": "career_intro | self_growth_intro | relationships_intro | no_goal_intro"
}
CRITICAL RULES:
1. Analyze the user's answer and set goal_type accordingly.
2. If unclear, politely clarify and set next to "classify_category".
3. Only use the allowed values for goal_type and next.
"""
    elif node.node_id == "career_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "career_goal"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just motivate and explain that you will ask about career goals next.
2. Set next to "career_goal".
"""
    elif node.node_id == "career_goal":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "career_goal": "extracted career goal as a string or null if not provided",
  "next": "career_goal | career_obstacles"
}
CRITICAL RULES:
1. ONLY extract the user's main career goal.
2. If career_goal is missing or unclear, politely ask again and set next to "career_goal".
3. If career_goal is provided, acknowledge and set next to "career_obstacles".
4. Do NOT ask about obstacles, skills, or anything else at this step.
"""
    elif node.node_id == "career_obstacles":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "goals": ["Goal 1", "Goal 2", ...],
  "next": "career_obstacles | career_to_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main career obstacles and turn them into 2–3 positive, actionable goals (not just a description of the problem).
2. If goals is missing or unclear, politely ask again and set next to "career_obstacles".
3. If goals is provided, acknowledge and set next to "career_to_plan".
4. Do NOT ask about obstacles, skills, or anything else at this step.
"""
    elif node.node_id == "career_to_plan":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just thank the user and inform them that a personalized plan will be generated next.
2. Set next to "generate_plan".
"""
    elif node.node_id == "generate_plan":
        json_instructions = f"""
IMPORTANT: You are in the generate_plan node. Your task is to create a 12-week personalized plan for the user based on their state (goal, obstacles, etc.).

Current state context:
- Goal type: {state.get('goal_type', 'unknown')}
- Career goal: {state.get('career_goal', 'not specified')}
- Career obstacles: {state.get('career_obstacles', 'not specified')}
- Relationship people: {state.get('relation_people', 'not specified')}
- Relationship issues: {state.get('relation_issues', 'not specified')}
- Self-growth goal: {state.get('self_growth_goal', 'not specified')}
- Self-growth obstacles: {state.get('self_growth_obstacles', 'not specified')}
- No goal reason: {state.get('no_goal_reason', 'not specified')}

Please respond in JSON format with EXACTLY this structure:
{{
  "reply": "Your response to the user (short intro, e.g. 'Here is your 12-week plan!')",
  "plan": {{
    "week_1_topic": "Build confidence through daily practice",
    "week_2_topic": "Overcome fear of judgment gradually",
    "week_3_topic": "Develop self-awareness and reflection skills",
    "week_4_topic": "Build resilience against challenges",
    "week_5_topic": "Maintain positive mindset daily",
    "week_6_topic": "Set clear personal growth goals",
    "week_7_topic": "Practice self-encouragement techniques",
    "week_8_topic": "Develop strong self-discipline habits",
    "week_9_topic": "Learn assertive communication skills",
    "week_10_topic": "Accept and appreciate yourself fully",
    "week_11_topic": "Build healthy self-esteem foundation",
    "week_12_topic": "Reflect on progress and plan future"
  }},
  "next": "plan_ready"
}}

CRITICAL RULES:
1. Use the user's state (goal, obstacles, etc.) to personalize the topics based on their goal_type.
2. For career goals: focus on professional development, networking, skill-building, etc.
3. For relationship goals: focus on communication, trust-building, conflict resolution, etc.
4. For self-growth goals: focus on personal development, confidence, habits, mindset, etc.
5. For no-goal: focus on exploration, self-discovery, finding purpose, etc.
6. Each week must have a unique, relevant topic or technique.
7. Topics must be actionable and practical for the user's context.
8. Each topic should be EXACTLY 7 words maximum - keep it concise and clear. Count words carefully!
9. Goals should be summarized in 4 words maximum for display purposes.
10. Do NOT ask any questions. Only generate the plan.
11. Set next to "plan_ready".
"""
    elif node.node_id == "plan_ready":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  \"reply\": \"Your response to the user (congratulations, summary, etc.)\"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just congratulate the user and confirm the plan is ready.
"""
    elif node.node_id == "relationships_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  \"reply\": \"Your response to the user\",
  \"next\": \"relationships_people\"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just motivate and explain that you will ask about relationships next.
2. Set next to \"relationships_people\".
"""
    elif node.node_id == "relationships_people":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  \"reply\": \"Your response to the user\",
  \"relation_people\": \"extracted people as a string or null if not provided\",
  \"next\": \"relationships_people | relationships_issues\"
}
CRITICAL RULES:
1. ONLY extract with whom the user wants to improve relationships.
2. If relation_people is missing or unclear, politely ask again and set next to \"relationships_people\".
3. If relation_people is provided, acknowledge and set next to \"relationships_issues\".
4. Do NOT ask about issues, goals, or anything else at this step.
"""
    elif node.node_id == "relationships_issues":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "goals": ["Goal 1", "Goal 2", ...],
  "next": "relationships_issues | relationships_to_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main relationship issues and turn them into 2–3 positive, actionable goals (not just a description of the problem).
2. If goals is missing or unclear, politely ask again and set next to "relationships_issues".
3. If goals is provided, acknowledge and set next to "relationships_to_plan".
4. Do NOT ask about issues, people, or anything else at this step.
"""
    elif node.node_id == "relationships_to_plan":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just thank the user and inform them that a personalized plan will be generated next.
2. Set next to "generate_plan".
"""
    elif node.node_id == "self_growth_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "self_growth_goal"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just motivate and explain that you will ask about self-improvement goals next.
2. Set next to "self_growth_goal".
"""
    elif node.node_id == "self_growth_goal":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "self_growth_goal": "extracted self-improvement goal as a string or null if not provided",
  "next": "self_growth_goal | self_growth_obstacles"
}
CRITICAL RULES:
1. ONLY extract the user's main self-improvement goal.
2. If self_growth_goal is missing or unclear, politely ask again and set next to "self_growth_goal".
3. If self_growth_goal is provided, acknowledge and set next to "self_growth_obstacles".
4. Do NOT ask about obstacles, skills, or anything else at this step.
"""
    elif node.node_id == "self_growth_obstacles":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "goals": ["Goal 1", "Goal 2", ...],
  "next": "self_growth_obstacles | self_growth_to_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main self-growth obstacles and turn them into 2–3 positive, actionable goals (not just a description of the problem).
2. If goals is missing or unclear, politely ask again and set next to "self_growth_obstacles".
3. If goals is provided, acknowledge and set next to "self_growth_to_plan".
4. Do NOT ask about obstacles, skills, or anything else at this step.
"""
    elif node.node_id == "self_growth_to_plan":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just thank the user and inform them that a personalized plan will be generated next.
2. Set next to "generate_plan".
"""
    elif node.node_id == "no_goal_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "no_goal_reason"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just be supportive and explain that you'll help them explore possibilities.
2. Set next to "no_goal_reason".
"""
    elif node.node_id == "no_goal_reason":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "no_goal_reason": "extracted reason as a string or null if not provided",
  "next": "no_goal_reason | no_goal_to_plan"
}
CRITICAL RULES:
1. ONLY extract the user's reason for not having a specific goal.
2. If no_goal_reason is missing or unclear, politely ask again and set next to "no_goal_reason".
3. If no_goal_reason is provided, acknowledge and set next to "no_goal_to_plan".
4. Do NOT ask about goals, skills, or anything else at this step.
"""
    elif node.node_id == "no_goal_to_plan":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT ask any questions. Just thank the user and inform them that a personalized exploration plan will be generated next.
2. Set next to "generate_plan".
"""
    else:
        json_instructions = ""
    
    # Compose full prompt
    prompt = "\n".join([system] + history_lines + ([state_str] if state_str else []) + [json_instructions])
    return prompt 