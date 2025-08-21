# mentor.ai — FULL BACKEND IMPLEMENTATION PLAN FOR CURSOR AI

---

## Project Assumptions and Implementation Notes

- All session state is stored in MongoDB, identified by a unique `session_id` (UUID).
- After onboarding and plan generation, only summary data (goals and topics) is retained; full state for old sessions is deleted.
- No user authentication at this stage; all sessions are anonymous. Authentication will be added later via Firebase tokens.
- All LLM calls use OpenAI GPT-4. This is a true LLM agent with natural conversation - all user responses are analyzed through LLM.
- The agent uses natural conversation flow - no rigid validation, LLM analyzes and extracts information from user responses.
- Only main API endpoints are covered by tests. Full branch coverage is not required.
- All interface text, questions, answers, and comments are in English only.
- Backend is deployed to Render. Frontend will be implemented in Swift.

---

## Data Format and Storage Specifications

### Goals and Topics Format
- **goals:** Array of exactly 3 strings (["Goal 1", "Goal 2", "Goal 3"])
- **topics:** Array of exactly 12 strings (["Topic 1", ..., "Topic 12"])
- **summary:** Single string (raw_llm), not shown to user

### MongoDB Document Structure
```json
{
  "session_id": "uuid",
  "goals": ["Goal 1", "Goal 2", "Goal 3"],
  "topics": ["Topic 1", ..., "Topic 12"],
  "summary": "raw_llm_text",
  "phase": "incomplete" | "plan_ready",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### LLM Agent Requirements
- All user responses are analyzed through LLM for natural conversation
- LLM extracts and validates information (age, goals, values, etc.) from natural language
- All prompts return JSON-structured responses for consistent data extraction
- Always request exactly 3 goals and exactly 12 topics from LLM
- If LLM returns incorrect quantity, retry or return error
- Store raw LLM response as summary for internal use

### Session Management
- No re-taking onboarding with same session_id at this stage
- If session_id exists, return current session status
- Incomplete sessions remain with phase: "incomplete"
- Return empty goals/topics for incomplete sessions

### Logging
- Log key actions: session creation, plan generation, LLM errors
- Store logs in stdout or separate collection
- No personal data in logs

### Future Considerations
- Plan versioning: add plan_version field when needed
- Multi-language support: add language field when needed
- Re-taking onboarding: implement session reset functionality later

---

## 1. Project Initialization

- Project name: `mentor_ai`
- Python 3.11+ (venv or Poetry)
- Install: `langgraph`, `fastapi`, `uvicorn`, `openai`, `pydantic`, `python-dotenv`, `pytest`, `pymongo`
- Prepare `.env` and `example.env` with `OPENAI_API_KEY` and MongoDB connection string

---

## 2. Directory Structure
mentor_ai/
├─ cursor/
│   ├─ core/
│   ├─ modules/
│   └─ postprocessing/
├─ app/
│   ├─ graphs/
│   ├─ endpoints/
│   └─ storage/
└─ tests/

---

## 3. Flow Definition 

---

### 3.1 root_graph.md

```
# Node: collect_basic_info
## System
You are collecting the user's basic personal data through natural conversation.
## Assistant
Let's begin with a quick intro. What's your name and how old are you?
## Outputs
- reply: string
- state.user_name: string (extracted by LLM from natural response)
- state.user_age: int (extracted by LLM from natural response)
- next: classify_category

# Node: classify_category
## System
Ask the user whether they have a goal, and analyze their natural response to determine the category.
## Assistant
Do you currently have a main personal goal? If yes, what kind of goal is it?
## Outputs
- reply: string
- state.goal_type: "career" | "self_growth" | "relationships" | "no_goal" (determined by LLM analysis)
- next:
    if state.goal_type == "career" → improve_intro
    if state.goal_type == "self_growth" → find_intro
    if state.goal_type == "relationships" → change_intro
    if state.goal_type == "no_goal" → lost_intro

# Node: exit_to_plan
## System
You're ending the onboarding graph.
## Assistant
Great, I understand your context. Now I'll prepare your personalized roadmap.
## Outputs
- reply: string
- state.flags.graph_completed: true
- state.phase: await_plan

3.2 modules/no_goals.md
# Node: ask_absence_reason
## System
Ask why the user currently feels they have no clear goals and analyze their natural response.
## Assistant
What do you think is the reason you don't currently have a goal?
## Outputs
- reply: string
- state.lost_skills: string (extracted by LLM from natural response)
- next: ask_personal_values

# Node: ask_personal_values
## System
Ask which personal values are most important to the user and extract them from natural language.
## Assistant
Which 2–3 personal values are most important to you in life?
## Outputs
- reply: string
- state.values: list (extracted by LLM from natural response)
- next: suggest_possible_goals

# Node: suggest_possible_goals
## System
Generate 3 sample goals based on the user's values.
## Assistant
Based on what you've shared, here are 3 goals you might consider...
## Outputs
- reply: string
- state.seed_goals: list
- next: exit_to_plan

3.3 modules/career.md
# Node: ask_current_position
## System
Ask the user's current work position and extract it from natural response.
## Assistant
What is your current job or professional role?
## Outputs
- reply: string
- state.career_now: string (extracted by LLM from natural response)
- next: ask_target_position

# Node: ask_target_position
## System
Ask the user's target career role and extract it from natural response.
## Assistant
What position or career goal do you want to reach in 1–2 years?
## Outputs
- reply: string
- state.career_goal: string (extracted by LLM from natural response)
- next: ask_obstacles

# Node: ask_obstacles
## System
Ask what is preventing the user from reaching that goal and extract obstacles from natural response.
## Assistant
What are the 2–3 main obstacles preventing you from achieving that career goal?
## Outputs
- reply: string
- state.improve_obstacles: list (extracted by LLM from natural response)
- next: exit_to_plan

3.4 modules/relationships.md
# Node: ask_people_involved
## System
Ask which people are involved in the relationship issues and extract from natural response.
## Assistant
With whom are you experiencing relationship difficulties? (e.g., partner, family, colleagues)
## Outputs
- reply: string
- state.relation_people: string (extracted by LLM from natural response)
- next: ask_issue_type

# Node: ask_issue_type
## System
Ask about the type of problem in that relationship and extract from natural response.
## Assistant
What's the core issue: communication, trust, boundaries, or something else?
## Outputs
- reply: string
- state.relation_issue: string (extracted by LLM from natural response)
- next: exit_to_plan

3.5 modules/self_growth.md
# Node: ask_growth_area
## System
Ask which area of growth the user wants and extract from natural response.
## Assistant
In which area of personal growth are you most interested right now?
## Outputs
- reply: string
- state.growth_area: string (extracted by LLM from natural response)
- next: ask_growth_field

# Node: ask_growth_field
## System
Ask for specific field and extract from natural response.
## Assistant
Can you be more specific? Is it discipline, public speaking, emotional control, etc.?
## Outputs
- reply: string
- state.growth_field: string (extracted by LLM from natural response)
- next: exit_to_plan

3.6 postprocessing/generate_plan_summary.md
# Node: generate_plan
## System
You are a strategic planner. Given the user's goal type and answers, generate a 3-goal summary and 12-topic plan using JSON structure.
## Assistant
Using the collected information, generate exactly 3 goals and 12 topics. Return in JSON format:
{
  "goals": ["Goal 1", "Goal 2", "Goal 3"],
  "topics": ["Topic 1", "Topic 2", ..., "Topic 12"],
  "raw_llm": "Full analysis and reasoning text"
}
## Outputs
- state.plan.goals: list
- state.plan.topics: list
- state.plan.raw_llm: string
- state.phase: plan_ready
```

---

## 4. Endpoints
- POST /session → starts onboarding session
- POST /chat/{session_id} → handles any user message through LLM agent
- POST /plan/{session_id} → auto-triggers after onboarding (LLM summary)
- GET /status/{session_id} → returns { phase, plan.goals, plan.topics }

---

## 5. Final Notes
- All Markdown nodes use System / Assistant / Outputs
- All transitions linear — no branching after first category split
- Only plan.goals and plan.topics are shown to the user
- All summaries (plan raw text) are internal only
- This is a true LLM agent with natural conversation - no rigid validation
- All user responses are analyzed through LLM for information extraction