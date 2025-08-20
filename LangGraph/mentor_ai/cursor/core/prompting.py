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
    
    # Add state verification instructions
    state_verification = """
CRITICAL STATE VERIFICATION RULES:
1. ALWAYS check the current state before accusing the user of not answering a question.
2. If you haven't asked a specific question yet, DO NOT accuse the user of not answering it.
3. Only ask for information that is actually missing from the state.
4. If the user provides information, acknowledge it and move to the next step.
5. Never assume the user didn't answer if you haven't explicitly asked the question.
"""
    
    # JSON instructions (как раньше)
    if node.node_id == "collect_basic_info":
        json_instructions = f"""
IMPORTANT: You are in the collect_basic_info node. Your ONLY task is to extract user_name and user_age.

Current state:
user_name: {state.get('user_name', None)}
user_age: {state.get('user_age', None)}

User message: "{user_message}"

Please respond in JSON format with EXACTLY this structure:
{{
  "reply": "Your response to the user",
  "user_name": "extracted name or null if not provided",
  "user_age": "extracted age (number) or 'unknown' if refused, or null if not provided",
  "next": "next node to go to"
}}

CRITICAL RULES:
1. Extract exactly two fields: user_name and user_age.
2. ALWAYS check the current state before asking questions:
   - If user_name is missing AND you haven't asked for it yet, ask ONLY for name
   - If user_name is present but user_age is missing AND you haven't asked for age yet, ask ONLY for age
   - If both are present, move to the next step
5. If user_name is present and user_age is present (or 'unknown'), your reply MUST thank the user and IMMEDIATELY ask about their work situation and goals. Present these 4 options tactfully: "Do you currently have a job? Which of these options suits you better: 1) I have a job and want to improve in my current role, 2) I have a job but want to change my career field completely, 3) I don't have a job and want to find my path, 4) I feel lost and don't know what I want yet." Set next to 'classify_category'.
6. IMPORTANT: Extract name from phrases like "I'm John", "My name is John", "John", etc. If user says "Hi, I'm John", extract "John" as user_name.
7. IMPORTANT: Extract age from phrases like "I'm 23", "I am 23 years old", "23", etc. If user says "I'm 23", extract "23" as user_age.
"""
    elif node.node_id == "classify_category":
        json_instructions = f"""
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{{
  "reply": "Your response to the user. If goal_type is clear, IMMEDIATELY ask the first question of the corresponding category.",
  "goal_type": "One of the four FULL DESCRIPTIONS listed in CRITICAL RULES (copy verbatim)",
  "next": "improve_intro | change_intro | find_intro | lost_intro"
}}

User message: "{user_message}"

CRITICAL RULES:
1. goal_type MUST be EXACTLY one of these full descriptions (copy verbatim):
   - "Improve in the current job: discover and develop your strongest qualities in your existing role, and grow where you already are."
   - "Change the job: transition to a new role or field that better matches your talents and natural abilities."
   - "Find strengths without a job: explore your core strengths and interests first to choose a meaningful direction."
   - "Feel lost: clarify life and professional goals step by step and define a path forward."
2. Determine which description fits best based on the user's intent. If unclear, politely ask a short clarifying question and set next to 'classify_category'.
3. If goal_type is clear, your reply MUST include a short transition and the first question of the next category.
4. Set next node strictly to one of: 'improve_intro', 'change_intro', 'find_intro', 'lost_intro' according to the selected description in the same order as above.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. All strings must be short and without line breaks.
"""
    elif node.node_id == "improve_intro":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Ask only for missing job details. No line breaks.",
  "job_circumstances": {
    "role": "current job title or null",
    "position": "seniority/level (e.g., junior, mid, senior, lead) or null",
    "industry": "industry/domain or null",
    "salary_value": "numeric value, range string, or null",
    "salary_currency": "e.g., USD/EUR or null",
    "salary_satisfaction": "satisfied | not_satisfied | neutral | null",
    "job_satisfaction": "satisfied | not_satisfied | neutral | null"
  },
  "next": "improve_intro | improve_skills"
}
CRITICAL RULES:
1. Goal: understand the user's current work context (who they are, their position, industry, salary if shared, and whether they are satisfied with pay and job overall).
2. Extract details from the user's message into job_circumstances. If a field is absent, set it to null.
3. Ask ONLY about missing fields. Do NOT ask about obstacles yet.
4. Decide yourself when information is sufficient to move on:
   - If role, position, and job_satisfaction are present (salary optional) → set next to 'improve_skills'.
   - OR if the user explicitly signals they don't want to share more details now (e.g., "that's enough", "prefer to move on", "not comfortable sharing salary") → acknowledge and set next to 'improve_skills'.
   - OR if the user sounds ready to proceed (e.g., asks for next steps) → set next to 'improve_skills'.
   - Otherwise, keep next as 'improve_intro' and politely ask for the most important missing item.
5. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""

    elif node.node_id == "improve_skills":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Reflect briefly and ask only for missing details. No line breaks.",
  "skills": ["skill 1", "skill 2", "..."],
  "interests": ["interest 1", "interest 2", "..."],
  "activities": ["activity 1", "activity 2", "..."],
  "exciting_topics": ["topic 1", "topic 2", "..."],
  "next": "improve_skills | improve_obstacles"
}
CRITICAL RULES:
1. Goal: understand the user's strengths and interests beyond the job: practical skills, topics they enjoy, and what they do in free time.
2. Additionally capture “exciting topics” — things that strongly energize the user (non‑sexual meaning): problems they are obsessed with, topics that make their eyes light up, areas they find especially “sexy” intellectually. Save them to 'exciting_topics'.
3. Extract items from the user's message into arrays. Use concise noun phrases. If something is absent, use an empty array.
4. Ask ONLY for the most important missing piece (e.g., "What skills do you use most confidently?", "What do you enjoy in your free time?", or "What topics really excite you?"). Avoid long lists of questions.
5. Decide yourself when information is sufficient to proceed:
   - If any TWO of these are non-empty: skills, interests, activities, exciting_topics → set next to 'improve_obstacles'.
   - OR if the user signals readiness to move on, or further probing brings diminishing returns → set next to 'improve_obstacles'.
   - Otherwise, keep next as 'improve_skills' and ask for the single most valuable missing piece.
6. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""
    elif node.node_id == "improve_obstacles":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Thank the user for sharing. Briefly reflect and explain that a personalized plan will be generated next. No line breaks.",
  "goals": ["Obstacle 1", "Obstacle 2", "..."],
  "negative_qualities": ["Trait 1", "Trait 2", "..."],
  "next": "improve_obstacles | generate_plan"
}
CRITICAL RULES:
1. Extract the user's main obstacles and reframe them into 2–3 positive, actionable points in 'goals' (e.g., "Procrastination" → "Build a consistent focus routine").
2. Separately capture self‑perceived negative qualities that may hinder progress in 'negative_qualities' (e.g., procrastination, fear of failure, perfectionism, low energy). Keep items concise; do not moralize.
3. If obstacles are unclear or missing, politely ask one clarifying question and set next to 'improve_obstacles'.
4. When there is enough clarity (goals not empty), acknowledge and set next to 'generate_plan'.
5. Do NOT include full lists inside the reply; keep the reply short and supportive.
"""
    elif node.node_id == "generate_plan":
        json_instructions = """
IMPORTANT: Your entire response MUST be valid JSON. Only output the JSON object, nothing else. No extra text.

Strictly follow this order and structure:
{
  "reply": "Shortly reflect on the onboarding chat, thank for sharing, and say the plan is ready.",
  "plan": {
    "week_1_topic": "...",
    "week_1_description": "2 personalized sentences tailored to the user's context.",
    "week_2_topic": "...",
    "week_2_description": "...",
    "week_3_topic": "...",
    "week_3_description": "...",
    "week_4_topic": "...",
    "week_4_description": "...",
    "week_5_topic": "...",
    "week_5_description": "...",
    "week_6_topic": "...",
    "week_6_description": "...",
    "week_7_topic": "...",
    "week_7_description": "...",
    "week_8_topic": "...",
    "week_8_description": "...",
    "week_9_topic": "...",
    "week_9_description": "...",
    "week_10_topic": "...",
    "week_10_description": "...",
    "week_11_topic": "...",
    "week_11_description": "...",
    "week_12_topic": "...",
    "week_12_description": "..."
  },
  "onboarding_chat_summary": "Summary of onboarding chat, max 3 sentences, no line breaks.",
  "next": "week1_chat"
}

PERSONALIZATION GUIDELINES:
- Use state fields to tailor topics and descriptions: goal_type (full description), job_circumstances (role, position, satisfaction), skills, interests, activities, exciting_topics, goals, negative_qualities, and any other context.
- Keep descriptions practical, motivating, and specific to the user's situation (e.g., if colleagues are an issue, mention reflection on concrete triggers and responses; if low energy, include gentle energy routines).
- Each description must be 2 short sentences without line breaks.

EXAMPLE (truncated):
{
  "reply": "Congratulations! Your 12-week plan is ready. Please start Week 1 chat.",
  "plan": {
    "week_1_topic": "Environment Audit",
    "week_1_description": "Map situations at work that drain or energize you. Focus on interactions with colleagues you mentioned and note exact triggers.",
    "week_2_topic": "Strengths Spotlight",
    "week_2_description": "Double down on two skills you enjoy most. Design a micro‑project at work to apply them this week.",
    "week_3_topic": "Anti‑Procrastination Routines",
    "week_3_description": "Test a 15‑minute focus protocol tailored to your schedule. Track energy peaks and use them for deep work.",
    "week_4_topic": "Feedback Debrief",
    "week_4_description": "Collect one piece of feedback from a trusted colleague. Translate it into one tiny behavior change.",
    "week_5_topic": "Time Management",
    "week_5_description": "...",
    "week_6_topic": "Personal Branding",
    "week_6_description": "...",
    "week_7_topic": "Mentorship",
    "week_7_description": "...",
    "week_8_topic": "Emotional Intelligence",
    "week_8_description": "...",
    "week_9_topic": "Goal Setting",
    "week_9_description": "...",
    "week_10_topic": "Resilience",
    "week_10_description": "...",
    "week_11_topic": "Strategic Thinking",
    "week_11_description": "...",
    "week_12_topic": "Review & Celebrate",
    "week_12_description": "..."
  },
  "onboarding_chat_summary": "You aim to grow in your current role and reduce friction with colleagues while building focus routines.",
  "next": "week1_chat"
}

CRITICAL RULES:
1. Output ONLY the JSON object.
2. reply and onboarding_chat_summary must be short and without line breaks.
3. All 12 week topics AND 12 week descriptions must be present and non-empty.
4. Descriptions must be personalized using the state. No generic filler.
5. next must always be "week1_chat".
"""
    elif node.node_id == "week1_chat":
        json_instructions = f'''
IMPORTANT: You are a real human coach. Your main goal is to help the user reflect, grow, and take action. Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions. Encourage the user to share their thoughts, feelings, and experiences. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Sometimes ask a deep or reflective question. No line breaks.",
  "history": {history if history else []},
  "next": "week1_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 1! This week is about persuasion. What does persuasion mean to you personally? Can you recall a time when you influenced someone or changed their mind?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 1."}}
  ],
  "next": "week1_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Do not be robotic or repetitive. Vary your questions and style.
4. Sometimes ask open, deep, or reflective questions, but not every time.
5. Encourage the user to think, reflect, and share, but keep the tone supportive and human.
6. All fields must be present and non-empty.
7. All strings must not contain unescaped quotes or special characters.
8. next must always be "week1_chat".
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
3. If relation_people is provided, acknowledge, ask what issues does the user have with these people and set next to "relationships_issues".
4. NEVER accuse the user of not answering a question you haven't asked yet.
5. If the user provides the people they want to improve relationships with, acknowledge it and move to the next step.
"""
    elif node.node_id == "relationships_issues":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Thank the user for sharing their relationship issues. Clearly TELL that a personalized plan will be generated next. If issues are unclear, politely ask again.",
  "goals": ["Goal 1", "Goal 2", ...],
  "next": "relationships_issues | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main relationship issues to "goals" in JSON file (but don't include "goals" in the reply)
2. If goals is missing or unclear, politely ask again and set next to 'relationships_issues'.
3. If goals is provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about issues, people, or anything else at this step.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. If the user provides their relationship issues, acknowledge them and move to the next step.
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
  "goals": ["Goal 1", "Goal 2", ...],
  "next": "self_growth_goal or self_growth_obstacles"
}
CRITICAL RULES:
1. ONLY extract the user's main self-improvement goals.
2. If "goals" is missing or unclear, politely ask again and set next to "self_growth_goal".
3. If "goals" is provided, acknowledge, ask about obstacles and set next to "self_growth_obstacles".
4. NEVER accuse the user of not answering a question you haven't asked yet.
5. If the user provides their self-improvement goals, acknowledge them and move to the next step.
"""
    elif node.node_id == "self_growth_obstacles":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Thank the user for sharing their self-growth obstacles. Clearly explain that a personalized plan will be generated next. If obstacles are unclear, politely ask again.",
  "obstacles": ["Obstacle 1", "Obstacle 2", ...],
  "next": "self_growth_obstacles | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main self-growth obstacles and turn them into 2–3 positive, actionable points (not just a description of the problem).
2. If obstacles is missing or unclear, politely ask again and set next to 'self_growth_obstacles'.
3. If obstacles are provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about obstacles, skills, or anything else at this step.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. If the user provides their self-growth obstacles, acknowledge them and move to the next step.
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
  "reply": "Thank the user for sharing their reason for not having a goal. Clearly explain that a personalized exploration plan will be generated next. If the reason is unclear, politely ask again.",
  "no_goal_reason": "extracted reason as a string or null if not provided",
  "next": "no_goal_reason | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's reason for not having a specific goal.
2. If no_goal_reason is missing or unclear, politely ask again and set next to 'no_goal_reason'.
3. If no_goal_reason is provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about goals, skills, or anything else at this step.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. If the user provides their reason for not having a goal, acknowledge it and move to the next step.
"""
    else:
        json_instructions = ""
    
    # Compose full prompt
    prompt = "\n".join([system] + history_lines + ([state_str] if state_str else []) + [state_verification] + [json_instructions])
    return prompt 