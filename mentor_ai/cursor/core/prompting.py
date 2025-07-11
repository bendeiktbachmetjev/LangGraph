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
5. If both are provided (or unavailable/unknown), your reply MUST thank the user and smoothly transition to the next step: ask if the user currently has a main personal goal, and if so, which area it relates to — career, self-growth, relationships, or maybe they have no goal at all. Proceed to classify_category.
6. DO NOT ask about occupation, work, location, or anything else
7. ONLY ask for name and age
8. If user refuses to provide age, set user_age to "unknown" (string, not null) and proceed to next node.
"""
    elif node.node_id == "classify_category":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user. If goal_type is clear, IMMEDIATELY ask the first question of the corresponding category (career, self-growth, relationships, or no-goal).",
  "goal_type": "career | self_growth | relationships | no_goal",
  "next": "career_intro | self_growth_intro | relationships_intro | no_goal_intro"
}
CRITICAL RULES:
1. Analyze the user's answer and set goal_type accordingly.
2. If unclear, politely clarify and set next to 'classify_category'.
3. If goal_type is clear, your reply MUST include a transition and the first question of the next category (for example: 'Great! Let's talk about your career. What is your main career goal?').
4. Only use the allowed values for goal_type and next.
"""
    elif node.node_id == "career_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Motivate the user and ask ONLY about their main career goal. Do NOT ask about obstacles or challenges yet.",
  "next": "career_obstacles"
}
CRITICAL RULES:
1. Your reply MUST end with a clear question: 'What is your main career goal right now?'.
2. Do NOT ask about obstacles, challenges, or anything else at this step.
3. Set next to 'career_obstacles'.
"""
    elif node.node_id == "career_obstacles":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Thank the user for sharing obstacles. Clearly explain that a personalized plan will be generated next. If obstacles are unclear, politely ask again.",
  "goals": ["Obstacle 1", "Obstacle 2", ...],
  "next": "career_obstacles | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main career obstacles and turn them into 2–3 positive, actionable points.
2. If goals is missing or unclear, politely ask again and set next to 'career_obstacles'.
3. If goals is provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about obstacles, skills, or anything else at this step.
"""
    elif node.node_id == "generate_plan":
        json_instructions = """
IMPORTANT: Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Strictly follow this order and structure:
{
  "reply": "Short congratulation and instruction to start Week 1 chat. No more than 2 sentences. No line breaks.",
  "plan": {
    "week_1_topic": "...",
    "week_2_topic": "...",
    "week_3_topic": "...",
    "week_4_topic": "...",
    "week_5_topic": "...",
    "week_6_topic": "...",
    "week_7_topic": "...",
    "week_8_topic": "...",
    "week_9_topic": "...",
    "week_10_topic": "...",
    "week_11_topic": "...",
    "week_12_topic": "..."
  },
  "onboarding_chat_summary": "Summary of onboarding chat, max 3 sentences, no line breaks.",
  "next": "week1_chat"
}

EXAMPLE:
{
  "reply": "Congratulations! Your 12-week plan is ready. Please start Week 1 chat.",
  "plan": {
    "week_1_topic": "Wheel of Life",
    "week_2_topic": "Zone of Genius",
    "week_3_topic": "Networking",
    "week_4_topic": "Feedback",
    "week_5_topic": "Time Management",
    "week_6_topic": "Personal Branding",
    "week_7_topic": "Mentorship",
    "week_8_topic": "Emotional Intelligence",
    "week_9_topic": "Goal Setting",
    "week_10_topic": "Resilience",
    "week_11_topic": "Strategic Thinking",
    "week_12_topic": "Review & Celebrate"
  },
  "onboarding_chat_summary": "You want to grow in your career. Your main goal is to become a CTO. You are motivated and ready to start.",
  "next": "week1_chat"
}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply and onboarding_chat_summary must be short and without line breaks.
3. All 12 week topics must be present and non-empty.
4. next must always be "week1_chat".
"""
    elif node.node_id == "week1_chat":
        week1_history = state.get("week1_history", [])
        json_instructions = f'''
IMPORTANT: Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Strictly follow this order and structure:
{{
  "reply": "Short, focused on Week 1 topic and onboarding summary. No line breaks.",
  "week1_history": {week1_history if week1_history else []},
  "next": "week1_chat"
}}

EXAMPLE:
{{
  "reply": "Let's start Week 1! This week we will focus on persuasion.",
  "week1_history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 1."}}
  ],
  "next": "week1_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short and without line breaks.
3. All fields must be present and non-empty.
4. All strings must not contain unescaped quotes or special characters.
5. next must always be "week1_chat".
'''
    elif node.node_id == "relationships_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Motivate the user and IMMEDIATELY ask with whom they want to improve relationships.",
  "next": "relationships_people"
}
CRITICAL RULES:
1. Do NOT just motivate. Your reply MUST end with a clear question: 'With whom would you like to improve your relationships?'.
2. Set next to 'relationships_people'.
"""
    elif node.node_id == "relationships_people":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Your response to the user",
  "relation_people": "extracted people as a string or null if not provided",
  "next": "relationships_people | relationships_issues"
}
CRITICAL RULES:
1. ONLY extract with whom the user wants to improve relationships.
2. If relation_people is missing or unclear, politely ask again and set next to "relationships_people".
3. If relation_people is provided, acknowledge and set next to "relationships_issues".
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
  "reply": "Thank the user and clearly explain that a personalized plan will be generated next. Optionally, briefly explain what will happen after the plan (Week 1 chat).",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT just thank. Your reply MUST explain that a plan will be generated and what the next step is.
2. Set next to 'generate_plan'.
"""
    elif node.node_id == "self_growth_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Motivate the user and IMMEDIATELY ask about their main self-improvement goal.",
  "next": "self_growth_goal"
}
CRITICAL RULES:
1. Do NOT just motivate. Your reply MUST end with a clear question: 'What is your main self-improvement goal?'.
2. Set next to 'self_growth_goal'.
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
  "reply": "Thank the user and clearly explain that a personalized plan will be generated next. Optionally, briefly explain what will happen after the plan (Week 1 chat).",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT just thank. Your reply MUST explain that a plan will be generated and what the next step is.
2. Set next to 'generate_plan'.
"""
    elif node.node_id == "no_goal_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Be supportive and IMMEDIATELY ask why the user currently has no goal.",
  "next": "no_goal_reason"
}
CRITICAL RULES:
1. Do NOT just support. Your reply MUST end with a clear question: 'What do you think is the main reason you don't have a specific goal right now?'.
2. Set next to 'no_goal_reason'.
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
  "reply": "Thank the user and clearly explain that a personalized exploration plan will be generated next. Optionally, briefly explain what will happen after the plan (Week 1 chat).",
  "next": "generate_plan"
}
CRITICAL RULES:
1. Do NOT just thank. Your reply MUST explain that a plan will be generated and what the next step is.
2. Set next to 'generate_plan'.
"""
    else:
        json_instructions = ""
    
    # Compose full prompt
    prompt = "\n".join([system] + history_lines + ([state_str] if state_str else []) + [json_instructions])
    return prompt 