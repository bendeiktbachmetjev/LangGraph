from typing import Dict, Any
from .root_graph import Node
from .memory_manager import MemoryManager

def generate_llm_prompt(node: Node, state: Dict[str, Any], user_message: str) -> str:
    """
    Generate a prompt for LLM based on the current node, state, and user message.
    Uses optimized prompt_context for memory efficiency while preserving full history for frontend.
    """
    # System prompt (for LLM context)
    system = f"System: {node.system_prompt}"
    
    # Get history for JSON instructions
    history = state.get("history", [])
    
    # Use optimized prompt_context if available, fallback to history for backward compatibility
    context_lines = []
    if "prompt_context" in state and state["prompt_context"]:
        # Use optimized memory context
        formatted_context = MemoryManager.format_prompt_context(state)
        if formatted_context:
            context_lines.append(formatted_context)
        else:
            # If prompt_context exists but is empty, fallback to history
            for msg in history:
                if not isinstance(msg, dict):
                    continue
                role = msg.get("role")
                content = msg.get("content")
                if not content:
                    continue
                if role == "user":
                    context_lines.append(f"User: {content}")
                elif role == "assistant":
                    context_lines.append(f"Assistant: {content}")
    else:
        # Fallback to original history method for backward compatibility
        for msg in history:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content")
            if not content:
                continue
            if role == "user":
                context_lines.append(f"User: {content}")
            elif role == "assistant":
                context_lines.append(f"Assistant: {content}")
    
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
        # Check if we have retrieved chunks to include
        retrieved_chunks = state.get("retrieved_chunks", [])
        
        knowledge_section = ""
        if retrieved_chunks:
            knowledge_section = "\n\nKNOWLEDGE SNIPPETS:\n"
            for i, chunk in enumerate(retrieved_chunks[:5], 1):  # Limit to 5 snippets
                title = chunk.get("title", "Unknown")
                content = chunk.get("content", "")[:200]  # Limit content length
                knowledge_section += f"{i}. {title}: {content}\n"
        
        json_instructions = f"""
IMPORTANT: Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

{knowledge_section}

Strictly follow this order and structure:
{{
  "reply": "Shortly reflect on the onboarding chat, thank for sharing the info and tell a person that his plan was created and he can close this chat window.",
  "plan": {{
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
  }},
  "onboarding_chat_summary": "Summary of onboarding chat, max 3 sentences, no line breaks.",
  "next": "week1_chat"
}}

EXAMPLE:
{{
  "reply": "Congratulations! Your 12-week plan is ready. Please start Week 1 chat.",
  "plan": {{
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
  }},
  "onboarding_chat_summary": "You want to grow in your career. Your main goal is to become a CTO. You are motivated and ready to start.",
  "next": "week1_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply and onboarding_chat_summary must be short and without line breaks.
3. All 12 week topics must be present and non-empty.
4. next must always be "week1_chat".
"""

    elif node.node_id == "change_intro":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Ask only for missing career change details. No line breaks.",
  "career_change_circumstances": {
    "current_role": "current job title or null",
    "current_industry": "current industry/domain or null",
    "desired_role": "target job title or null",
    "desired_industry": "target industry/domain or null",
    "years_experience": "years in current field or null",
    "career_change_reason": "why they want to change or null",
    "career_satisfaction": "satisfied | not_satisfied | neutral | null"
  },
  "next": "change_intro | change_skills"
}
CRITICAL RULES:
1. Goal: understand the user's current career context and desired career change (current role, desired role, why they want to change, and their satisfaction with current career).
2. Extract details from the user's message into career_change_circumstances. If a field is absent, set it to null.
3. Ask ONLY about missing fields. Do NOT ask about specific obstacles yet.
4. Decide yourself when information is sufficient to move on:
   - If current_role, desired_role, and career_change_reason are present → set next to 'change_skills'.
   - OR if the user explicitly signals they don't want to share more details now (e.g., "that's enough", "prefer to move on") → acknowledge and set next to 'change_skills'.
   - OR if the user sounds ready to proceed (e.g., asks for next steps) → set next to 'change_skills'.
   - Otherwise, keep next as 'change_intro' and politely ask for the most important missing item.
5. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""
    elif node.node_id == "change_skills":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Reflect briefly and ask only for missing details. No line breaks.",
  "skills": ["skill 1", "skill 2", "..."],
  "interests": ["interest 1", "interest 2", "..."],
  "activities": ["activity 1", "activity 2", "..."],
  "exciting_topics": ["topic 1", "topic 2", "..."],
  "next": "change_skills | change_obstacles"
}
CRITICAL RULES:
1. Goal: understand the user's strengths and interests for career change: practical skills, topics they enjoy, and what they do in free time.
2. Additionally capture "exciting topics" — things that strongly energize the user (non‑sexual meaning): problems they are obsessed with, topics that make their eyes light up, areas they find especially "sexy" intellectually. Save them to 'exciting_topics'.
3. Extract items from the user's message into arrays. Use concise noun phrases. If something is absent, use an empty array.
4. Ask ONLY for the most important missing piece (e.g., "What skills do you use most confidently?", "What do you enjoy in your free time?", or "What topics really excite you?"). Avoid long lists of questions.
5. Decide yourself when information is sufficient to proceed:
   - If any TWO of these are non-empty: skills, interests, activities, exciting_topics → set next to 'change_obstacles'.
   - OR if the user signals readiness to move on, or further probing brings diminishing returns → set next to 'change_obstacles'.
   - Otherwise, keep next as 'change_skills' and ask for the single most valuable missing piece.
6. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""
    elif node.node_id == "change_obstacles":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Thank the user for sharing. Briefly reflect and explain that a personalized plan will be generated next. No line breaks.",
  "goals": ["Obstacle 1", "Obstacle 2", "..."],
  "negative_qualities": ["Trait 1", "Trait 2", "..."],
  "next": "change_obstacles | generate_plan"
}
CRITICAL RULES:
1. Extract the user's main career change obstacles and reframe them into 2–3 positive, actionable points in 'goals' (e.g., "Fear of starting over" → "Build confidence in new skills").
2. Separately capture self‑perceived negative qualities that may hinder career change progress in 'negative_qualities' (e.g., fear of failure, lack of confidence, perfectionism, low energy). Keep items concise; do not moralize.
3. If obstacles are unclear or missing, politely ask one clarifying question and set next to 'change_obstacles'.
4. When there is enough clarity (goals not empty), acknowledge and set next to 'generate_plan'.
5. Do NOT include full lists inside the reply; keep the reply short and supportive.
"""

    elif node.node_id == "find_intro":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Ask only for missing background details. No line breaks.",
  "background_circumstances": {
    "formal_education": "degree, diploma, or null",
    "education_field": "field of study or null",
    "skills": "what they can do, practical abilities or null",
    "work_experience": "previous jobs, internships, or null",
    "volunteer_experience": "volunteer work or null",
    "hobbies_interests": "what they enjoy doing or null",
    "current_situation": "brief description of current status or null"
  },
  "next": "find_intro | find_skills"
}
CRITICAL RULES:
1. Goal: understand the user's background and current situation (education, skills, experience, interests) to help them find their path.
2. Extract details from the user's message into background_circumstances. If a field is absent, set it to null.
3. Ask ONLY about missing fields. Keep questions short and supportive.
4. Decide yourself when information is sufficient to move on:
   - If formal_education, skills, and current_situation are present → set next to 'find_skills'.
   - OR if the user explicitly signals they don't want to share more details now → acknowledge and set next to 'find_skills'.
   - OR if the user sounds ready to proceed → set next to 'find_skills'.
   - Otherwise, keep next as 'find_intro' and politely ask for the most important missing item.
5. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""
    elif node.node_id == "find_skills":
        json_instructions = """
IMPORTANT: Respond ONLY in JSON with EXACTLY this structure:
{
  "reply": "Warm, concise and human. Ask about their passions and what excites them. No line breaks.",
  "passions": ["passion 1", "passion 2", "..."],
  "exciting_topics": ["topic 1", "topic 2", "..."],
  "content_consumption": ["YouTube channels", "books", "podcasts", "websites", "..."],
  "next": "find_skills | find_obstacles"
}
CRITICAL RULES:
1. Goal: discover what truly excites and energizes the user - their passions, interests, and what they consume.
2. Ask about what makes their eyes light up, what they could talk about for hours, what content they consume (YouTube, books, podcasts, etc.).
3. Extract items into arrays. Use concise phrases. If something is absent, use an empty array.
4. Ask ONLY for the most important missing piece. Be curious and supportive.
5. Decide yourself when information is sufficient to proceed:
   - If any TWO of these are non-empty: passions, exciting_topics, content_consumption → set next to 'find_obstacles'.
   - OR if the user signals readiness to move on → set next to 'find_obstacles'.
   - Otherwise, keep next as 'find_skills' and ask for the single most valuable missing piece.
6. Keep reply short, supportive, and clear. No accusations about unanswered questions.
"""
    elif node.node_id == "find_obstacles":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Thank the user for sharing their self-growth obstacles. Clearly explain that a personalized plan will be generated next. If obstacles are unclear, politely ask again.",
  "obstacles": ["Obstacle 1", "Obstacle 2", ...],
  "next": "find_obstacles | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's main self-growth obstacles and turn them into 2–3 positive, actionable points (not just a description of the problem).
2. If obstacles is missing or unclear, politely ask again and set next to 'find_obstacles'.
3. If obstacles are provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about obstacles, skills, or anything else at this step.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. If the user provides their self-growth obstacles, acknowledge them and move to the next step.
"""
    elif node.node_id == "lost_intro":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Be supportive and IMMEDIATELY ask why the user currently has no goal.",
  "next": "lost_skills"
}
CRITICAL RULES:
1. Do NOT just support. Your reply MUST end with a clear question: 'What do you think is the main reason you don't have a specific goal right now?'.
2. Set next to 'lost_skills'.
"""
    elif node.node_id == "lost_skills":
        json_instructions = """
IMPORTANT: Respond in JSON format with EXACTLY this structure:
{
  "reply": "Thank the user for sharing their reason for not having a goal. Clearly explain that a personalized exploration plan will be generated next. If the reason is unclear, politely ask again.",
  "lost_skills": "extracted reason as a string or null if not provided",
  "next": "lost_skills | generate_plan"
}
CRITICAL RULES:
1. ONLY extract the user's reason for not having a specific goal.
2. If lost_skills is missing or unclear, politely ask again and set next to 'lost_skills'.
3. If lost_skills is provided, acknowledge and set next to 'generate_plan'.
4. Do NOT ask about goals, skills, or anything else at this step.
5. NEVER accuse the user of not answering a question you haven't asked yet.
6. If the user provides their reason for not having a goal, acknowledge it and move to the next step.
"""
    elif node.node_id == "week1_chat":
        # Get week 1 topic from plan
        plan = state.get("plan", {})
        week1_topic = plan.get("week_1_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 1 and move to Week 2. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Great work on Week 1! You've made excellent progress on {week1_topic}. Let's move to Week 2 where we'll focus on a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week2_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week2_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
You are a coach for Week 1 focusing on: {week1_topic}. Be supportive and natural.

Respond ONLY with this JSON structure:
{{
  "reply": "Your response here - keep it short and focused on {week1_topic}",
  "history": {history if history else []},
  "next": "week1_chat"
}}

RULES:
- Only output valid JSON
- Keep reply under 200 characters
- No line breaks in reply
- No quotes or special characters in reply
- Always set next to "week1_chat"
'''
    elif node.node_id == "week2_chat":
        # Get week 2 topic from plan
        plan = state.get("plan", {})
        week2_topic = plan.get("week_2_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 2 and move to Week 3. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Excellent work on Week 2! You've made great progress on {week2_topic}. Let's move to Week 3 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week3_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week3_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 2. Your main goal is to help the user reflect, grow, and take action on the topic: "{week2_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week2_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week2_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week2_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 2! This week we're focusing on {week2_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 2."}}
  ],
  "next": "week2_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week2_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week2_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week2_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week2_chat".
'''
    elif node.node_id == "week3_chat":
        # Get week 3 topic from plan
        plan = state.get("plan", {})
        week3_topic = plan.get("week_3_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 3 and move to Week 4. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Fantastic work on Week 3! You've made excellent progress on {week3_topic}. Let's move to Week 4 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week4_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week4_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 3. Your main goal is to help the user reflect, grow, and take action on the topic: "{week3_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week3_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week3_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week3_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 3! This week we're focusing on {week3_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 3."}}
  ],
  "next": "week3_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week3_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week3_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week3_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week3_chat".
'''
    elif node.node_id == "week4_chat":
        # Get week 4 topic from plan
        plan = state.get("plan", {})
        week4_topic = plan.get("week_4_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 4 and move to Week 5. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Excellent work on Week 4! You've made great progress on {week4_topic}. Let's move to Week 5 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week5_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week5_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 4. Your main goal is to help the user reflect, grow, and take action on the topic: "{week4_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week4_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week4_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week4_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 4! This week we're focusing on {week4_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 4."}}
  ],
  "next": "week4_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week4_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week4_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week4_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week4_chat".
'''
    elif node.node_id == "week5_chat":
        # Get week 5 topic from plan
        plan = state.get("plan", {})
        week5_topic = plan.get("week_5_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no comments, no extra text.

The user wants to finish Week 5 and move to Week 6. Provide a brief summary and transition message.

EXACT JSON STRUCTURE (copy this exactly and replace the values):
{{
  "reply": "Great work on Week 5! You've made excellent progress on {week5_topic}. Let's move to Week 6 where we'll explore a new topic.",
  "history": {history if history else []},
  "next": "week6_chat"
}}

CRITICAL JSON RULES:
1. ONLY output the JSON object - nothing before or after
2. Use ONLY standard quotes (") not fancy quotes (", ")
3. Escape any quotes inside strings with backslash: \\"
4. No line breaks inside string values
5. No trailing commas
6. All strings must be properly quoted
7. All fields must be present and non-empty
8. next must be "week6_chat"
'''
        else:
            json_instructions = f'''
CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no comments, no extra text.

You are a real human coach for Week 5. Your main goal is to help the user reflect, grow, and take action on the topic: "{week5_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week5_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible.

Context: {onboarding_summary}

EXACT JSON STRUCTURE (copy this exactly and replace the values):
{{
  "reply": "Your response here - keep it short and natural, focus on {week5_topic}. No line breaks or special characters.",
  "history": {history if history else []},
  "next": "week5_chat"
}}

CRITICAL JSON RULES:
1. ONLY output the JSON object - nothing before or after
2. Use ONLY double quotes (") for ALL strings - NEVER use single quotes (')
3. Escape any quotes inside strings with backslash: \\"
4. No line breaks inside string values
5. No trailing commas
6. All strings must be properly quoted with double quotes
7. All fields must be present and non-empty
8. next must always be "week5_chat"
9. Example of correct format: {"key": "value", "array": [{"role": "user", "content": "text"}]}
'''
    elif node.node_id == "week6_chat":
        # Get week 6 topic from plan
        plan = state.get("plan", {})
        week6_topic = plan.get("week_6_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 6 and move to Week 7. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Excellent work on Week 6! You've made great progress on {week6_topic}. Let's move to Week 7 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week7_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week7_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no comments, no extra text.

You are a real human coach for Week 6. Your main goal is to help the user reflect, grow, and take action on the topic: "{week6_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week6_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible.

Context: {onboarding_summary}

EXACT JSON STRUCTURE (copy this exactly and replace the values):
{{
  "reply": "Your response here - keep it short and natural, focus on {week6_topic}. No line breaks or special characters.",
  "history": {history if history else []},
  "next": "week6_chat"
}}

CRITICAL JSON RULES:
1. ONLY output the JSON object - nothing before or after
2. Use ONLY double quotes (") for ALL strings - NEVER use single quotes (')
3. Escape any quotes inside strings with backslash: \\"
4. No line breaks inside string values
5. No trailing commas
6. All strings must be properly quoted with double quotes
7. All fields must be present and non-empty
8. next must always be "week6_chat"
9. Example of correct format: {"key": "value", "array": [{"role": "user", "content": "text"}]}
'''
    elif node.node_id == "week7_chat":
        # Get week 7 topic from plan
        plan = state.get("plan", {})
        week7_topic = plan.get("week_7_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 7 and move to Week 8. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Fantastic work on Week 7! You've made excellent progress on {week7_topic}. Let's move to Week 8 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week8_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week8_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 7. Your main goal is to help the user reflect, grow, and take action on the topic: "{week7_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week7_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week7_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week7_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 7! This week we're focusing on {week7_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 7."}}
  ],
  "next": "week7_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week7_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week7_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week7_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week7_chat".
'''
    elif node.node_id == "week8_chat":
        # Get week 8 topic from plan
        plan = state.get("plan", {})
        week8_topic = plan.get("week_8_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 8 and move to Week 9. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Excellent work on Week 8! You've made great progress on {week8_topic}. Let's move to Week 9 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week9_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week9_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 8. Your main goal is to help the user reflect, grow, and take action on the topic: "{week8_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week8_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week8_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week8_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 8! This week we're focusing on {week8_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 8."}}
  ],
  "next": "week8_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week8_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week8_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week8_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week8_chat".
'''
    elif node.node_id == "week9_chat":
        # Get week 9 topic from plan
        plan = state.get("plan", {})
        week9_topic = plan.get("week_9_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 9 and move to Week 10. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Great work on Week 9! You've made excellent progress on {week9_topic}. Let's move to Week 10 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week10_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week10_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 9. Your main goal is to help the user reflect, grow, and take action on the topic: "{week9_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week9_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week9_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week9_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 9! This week we're focusing on {week9_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 9."}}
  ],
  "next": "week9_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week9_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week9_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week9_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week9_chat".
'''
    elif node.node_id == "week10_chat":
        # Get week 10 topic from plan
        plan = state.get("plan", {})
        week10_topic = plan.get("week_10_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 10 and move to Week 11. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Excellent work on Week 10! You've made great progress on {week10_topic}. Let's move to Week 11 where we'll explore a new topic. No line breaks.",
  "history": {history if history else []},
  "next": "week11_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week11_chat" to transition to the next week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 10. Your main goal is to help the user reflect, grow, and take action on the topic: "{week10_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week10_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week10_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week10_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 10! This week we're focusing on {week10_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 10."}}
  ],
  "next": "week10_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week10_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week10_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week10_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week10_chat".
'''
    elif node.node_id == "week11_chat":
        # Get week 11 topic from plan
        plan = state.get("plan", {})
        week11_topic = plan.get("week_11_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to move to next week
        if "move to next week" in user_message.lower() or "next week" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 11 and move to Week 12. Provide a brief summary and transition message.

Strictly follow this order and structure:
{{
  "reply": "Fantastic work on Week 11! You've made excellent progress on {week11_topic}. Let's move to Week 12, our final week! No line breaks.",
  "history": {history if history else []},
  "next": "week12_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, supportive, and acknowledge their progress.
3. next must be "week12_chat" to transition to the final week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 11. Your main goal is to help the user reflect, grow, and take action on the topic: "{week11_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week11_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week11_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week11_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 11! This week we're focusing on {week11_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 11."}}
  ],
  "next": "week11_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week11_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week11_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week11_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week11_chat".
'''
    elif node.node_id == "week12_chat":
        # Get week 12 topic from plan
        plan = state.get("plan", {})
        week12_topic = plan.get("week_12_topic", "personal development")
        onboarding_summary = state.get("onboarding_chat_summary", "")
        
        # Check if user wants to finish the program
        if "move to next week" in user_message.lower() or "next week" in user_message.lower() or "finish program" in user_message.lower():
            json_instructions = f'''
IMPORTANT: The user wants to finish Week 12 and complete the program. Provide a final summary and congratulations message.

Strictly follow this order and structure:
{{
  "reply": "Congratulations! You've completed all 12 weeks of your coaching program. You've made incredible progress on {week12_topic} and your overall development. This is a significant achievement! No line breaks.",
  "history": {history if history else []},
  "next": "week12_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be celebratory and acknowledge their completion of the program.
3. next must remain "week12_chat" since this is the final week.
4. All fields must be present and non-empty.
'''
        else:
            json_instructions = f'''
IMPORTANT: You are a real human coach for Week 12. Your main goal is to help the user reflect, grow, and take action on the topic: "{week12_topic}". Always respond in a natural, conversational, and supportive way. Sometimes ask open-ended, deep, or philosophical questions related to this week's topic. Encourage the user to share their thoughts, feelings, and experiences about {week12_topic}. Vary your questions and style, avoid being repetitive or robotic. Support, motivate, and challenge the user to think and act. Make the conversation as human and engaging as possible. Your entire response MUST be valid JSON. Do not include any explanations, comments, or extra text. Only output the JSON object. Do NOT include line breaks, tabs, or extra spaces inside any JSON string. If you are unsure, return an empty string for any field. All fields are required.

Context: {onboarding_summary}

Strictly follow this order and structure:
{{
  "reply": "Short, natural, supportive, and human. Focus on the topic: {week12_topic}. Sometimes ask a deep or reflective question about this topic. No line breaks.",
  "history": {history if history else []},
  "next": "week12_chat"
}}

EXAMPLE:
{{
  "reply": "Welcome to Week 12! This week we're focusing on {week12_topic}. What does this topic mean to you personally? Can you share a recent experience related to this?",
  "history": [
    {{"role": "user", "content": "Hello!"}},
    {{"role": "assistant", "content": "Welcome to Week 12."}}
  ],
  "next": "week12_chat"
}}

CRITICAL RULES:
1. Only output the JSON object, nothing else.
2. reply must be short, natural, and without line breaks.
3. Always focus your questions and responses on the topic: {week12_topic}.
4. Do not be robotic or repetitive. Vary your questions and style.
5. Sometimes ask open, deep, or reflective questions about {week12_topic}, but not every time.
6. Encourage the user to think, reflect, and share about {week12_topic}, but keep the tone supportive and human.
7. All fields must be present and non-empty.
8. All strings must not contain unescaped quotes or special characters.
9. next must always be "week12_chat".
'''
    else:
        json_instructions = ""
    
    # Compose full prompt
    prompt_parts = [system]
    
    # Add context (either optimized or fallback)
    prompt_parts.extend(context_lines)
    
    # Add state and instructions
    if state_str:
        prompt_parts.append(state_str)
    prompt_parts.append(state_verification)
    prompt_parts.append(json_instructions)
    
    prompt = "\n".join(prompt_parts)
    return prompt

def generate_llm_prompt_with_history(node: Node, state: Dict[str, Any], user_message: str) -> str:
    """
    Generate a prompt using full history (for backward compatibility or when memory is disabled).
    This is the original implementation preserved for fallback scenarios.
    """
    # System prompt (for LLM context)
    system = f"System: {node.system_prompt}"
    
    # Собираем историю сообщений (original method)
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
    
    # State and instructions (same as before)
    state_str = f"Current state: {state}" if state else ""
    
    state_verification = """
CRITICAL STATE VERIFICATION RULES:
1. ALWAYS check the current state before accusing the user of not answering a question.
2. If you haven't asked a specific question yet, DO NOT accuse the user of not answering it.
3. Only ask for information that is actually missing from the state.
4. If the user provides information, acknowledge it and move to the next step.
5. Never assume the user didn't answer if you haven't explicitly asked the question.
"""
    
    # Simple JSON instructions for fallback
    json_instructions = f"""
User message: "{user_message}"

Please respond in JSON format with appropriate fields for this node.
"""
    
    # Compose full prompt using original method
    prompt = "\n".join([system] + history_lines + ([state_str] if state_str else []) + [state_verification] + [json_instructions])
    return prompt 