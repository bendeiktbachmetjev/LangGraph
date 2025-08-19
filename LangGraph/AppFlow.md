# mentor.ai · FLOW (Plain English, for Cursor)

---

## Project Assumptions

- All session state is stored in MongoDB, identified by a unique session_id (UUID).
- After onboarding and plan generation, only summary data (goals and topics) is retained; full state for old sessions is deleted.
- No authentication at this stage; all sessions are anonymous. Authentication will be added later via Firebase tokens.
- LLM: OpenAI GPT-4. This is a true LLM agent with natural conversation - all user responses are analyzed through LLM.
- The agent uses natural conversation flow - no rigid validation, LLM analyzes and extracts information from user responses.
- Only main API endpoints are covered by tests.
- All interface text, questions, answers, and comments are in English.
- Backend is deployed to Render; frontend will be implemented in Swift.

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

1. **User starts with no access to any plan or goals.**  
   — The user has no plan, no goals set, nothing unlocked.

2. **User begins the onboarding chat (intro chat).**  
   — This is a single, guided conversation with the assistant (LLM agent).
   — The assistant first collects basic info (name, age, etc) through natural conversation.
   — Next, the assistant asks about user's main goal and analyzes the natural response:
       - Does the user have a goal?
       - If yes, which type: Career, Self-Growth, or Relationships?
       - If no, marks as "No Goal".

3. **Branch selection (implicit, but not diverging):**  
   — Depending on the LLM analysis of the user's natural response (Career, Self-Growth, Relationships, or No Goal),  
     the assistant continues down a dedicated linear sequence for that branch.
   — There are no further branches or splits;  
     each category leads to its own set of specific follow-up questions.

4. **Branch details (linear subflow):**  
   - *Career*:  
       - Asks about current position (LLM extracts from natural response)  
       - Asks about desired position (LLM extracts from natural response)  
       - Asks what obstacles the user sees (LLM extracts from natural response)  
   - *Relationships*:  
       - Asks who the relationship issues are with (LLM extracts from natural response)  
       - Asks about the nature of the issues (LLM extracts from natural response)  
   - *Self-Growth*:  
       - Asks what area of self-growth is important (LLM extracts from natural response)  
       - Asks which specific field (LLM extracts from natural response)
   - *No Goal*:  
       - Asks why there are no goals (LLM extracts from natural response)  
       - Asks about user's core values (LLM extracts from natural response)  
       - Suggests 3 example goals (LLM-generated)

5. **Throughout the flow:**  
   — After each user answer, the LLM analyzes the natural response and updates the state  
     (e.g., extracting goal type, details, obstacles, etc. from natural language).
   — All logic and questions are contained in this single, long onboarding chat.
   — The user never sees technical details or state—just the natural conversation.

6. **At the end of the intro chat:**  
   — The assistant, using all gathered information,  
     generates a plan: 3 main goals and 12 topics using JSON-structured LLM response.
   — The user is presented with their unlocked plan (UI shows 3 goals and 12 topics).

> **In summary:**  
> User starts from zero, unlocks their plan only after a single, adaptive onboarding chat.
> There are 4 possible main flows (Career, Self-Growth, Relationships, No Goal),  
> but no deep tree—each flow is linear and updates state after every step.
> All logic is contained in a single onboarding session with natural LLM conversation.

---

## Endpoints
- POST /session → starts onboarding session
- POST /chat/{session_id} → handles any user message through LLM agent
- POST /plan/{session_id} → auto-triggers after onboarding (LLM summary)
- GET /status/{session_id} → returns { phase, plan.goals, plan.topics }

---

## Notes
- All transitions linear — no branching after first category split
- Only plan.goals and plan.topics are shown to the user
- All summaries (plan raw text) are internal only
- This is a true LLM agent with natural conversation - no rigid validation
- All user responses are analyzed through LLM for information extraction

# mentor.ai · Полная спецификация Flow для Cursor AI

**Описание:**
Это приложение — диалоговый коучинг-бот.  
В начале у пользователя нет открытых тем, целей или плана.  
Вся логика диалога и структуры проекта описана ниже.  
Cursor AI должен реализовать backend и структуру файлов **точно по этому сценарию**.

---

## 1. Общая структура модулей

- Есть корневой граф (onboarding/intro).
- Есть четыре линейных подграфа (ветки):
  - "No Goal"
  - "Career"
  - "Relationships"
  - "Self-Growth"
- После завершения интро генерируется скрытый LLM summary (plan), на основании которого открываются 12 недель (тем) и 3 основные цели.
- Каждая неделя — отдельная сессия (topic), работающая по общему шаблону (модуль недели).
- Все state-ключи — в snake_case.

---

## 2. Flow по шагам

### 2.1. Onboarding (Intro Chat)

1. Сбор основной информации (имя, возраст).
2. Вопрос: «Есть ли у тебя цель?»  
   Варианты:
   - Нет цели → "No Goal"
   - Есть цель:  
     • Карьера → "Career"  
     • Отношения → "Relationships"  
     • Личностный рост → "Self-Growth"

### 2.2. No Goal (Линейно)

- Почему нет цели?
- Какие ценности для тебя важны?
- LLM предлагает 3 примерных цели (на основании ценностей).

### 2.3. Career (Линейно)

- Твоя текущая позиция?
- Какой позиции ты хочешь достичь?
- Какие основные препятствия ты видишь?

### 2.4. Relationships (Линейно)

- С кем главные сложности (партнёр, семья, коллеги)?
- В чём главная проблема (коммуникация, доверие, время и др.)?

### 2.5. Self-Growth (Линейно)

- В чём хочешь развиваться (навыки, мировоззрение)?
- Какое направление или сфера (например, публичные выступления, дисциплина и т.д.)?

---

## 3. После Intro

- После окончания любого из 4 сценариев собирается state с ключами (goal_type, values, career_now, career_goal и т.д.).
- LLM автоматически формирует summary (не показывается пользователю полностью), а для UI возвращает:
  - 3 главные цели (goals)
  - 12 тем (topics)
- UI показывает 3 цели и 12 разблокированных тем.

---

## 4. Week Module (Одна тема)

- Каждая тема — отдельная сессия, state хранит week-summary (не показывается пользователю, но используется для следующей темы).
- Прогресс по каждой неделе и итог недели хранятся в state и контексте.

---

## 5. State

Все state-ключи строго snake_case, например:
- phase, flags, plan.goals, plan.topics, plan.raw_llm
- weeks["week-01"].summary, weeks["week-01"].status
- context.week_summaries
- goal_type, values, career_now, career_goal, obstacles, relation_people, relation_issue, growth_area, growth_field

---

## 6. Фазы приложения

- Начало: все темы закрыты, план не сгенерирован.
- Onboarding (intro chat): только этот чат доступен.
- После summary: UI получает 3 цели и 12 тем, открывает их пользователю.
- Каждая неделя — отдельная сессия с week-summary.

---

## 7. Backend Flow

- Для всего интро и каждой недели — один endpoint `/session`, который создаёт новую сессию (onboarding или week).
- Вся логика и вопросы определяются только по этому сценарию.
- Нет ручного выбора или создания модулей.
- Каждый модуль (intro, career, relationships, self-growth, no-goal, week) создаётся Cursor AI автоматически по данному flow.

---

**Требования:**
- Ни один этап не требует ручного создания .md файлов — все ветки, вопросы и их порядок заданы выше.
- Все вопросы и ветки строго линейны внутри своей категории, без дополнительных разветвлений.
- После onboarding чат автоматически генерирует цели и темы, UI их показывает, темы становятся открытыми.
- Итоги недели не показываются пользователю, но доступны LLM для следующих недель.

---

**Весь backend, структура папок, модули, state-ключи, все вопросы и flow должны быть построены строго по этому описанию.**