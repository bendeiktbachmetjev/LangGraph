# 🔄 Running Summary - Частота обновления

## 📊 Частота создания/обновления

**Running Summary создается/обновляется каждые 20 сообщений**

### 🎯 Детали:

1. **Триггер:** `message_count % 20 == 0`
2. **Частота:** Каждые 20 сообщений (10 пар user-assistant)
3. **Содержимое:** Сводка последних 20 сообщений
4. **Формат:** 1-2 предложения, сгенерированные LLM

### 📈 График обновлений:

```
Сообщение 1-19:  ❌ Нет Running Summary
Сообщение 20:    ✅ Running Summary СОЗДАН
Сообщение 21-39: ❌ Нет обновления
Сообщение 40:    ✅ Running Summary ОБНОВЛЕН
Сообщение 41-59: ❌ Нет обновления
Сообщение 60:    ✅ Running Summary ОБНОВЛЕН
...и так далее
```

---

## 🧠 Логика работы

### В MemoryManager.update_prompt_context():

```python
# Increment message counter
message_count = updated_state.get("message_count", 0) + 1

# Update running summary every 20 messages
if message_count % 20 == 0:
    running_summary = MemoryManager._create_running_summary(
        updated_state.get("history", [])
    )
    updated_state["prompt_context"]["running_summary"] = running_summary
    logger.info(f"Updated running summary for session {updated_state.get('session_id', 'unknown')}")
```

### В StateManager.update_state_with_memory():

```python
# Add messages to memory if provided
if user_message:
    new_message = {"role": "user", "content": user_message}
    updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
    
if assistant_reply:
    new_message = {"role": "assistant", "content": assistant_reply}
    updated_state = MemoryManager.update_prompt_context(updated_state, new_message)
```

---

## 📝 Содержимое Running Summary

### Что включается:
- **Последние 20 сообщений** из истории разговора
- **Сообщения пользователя и ассистента**
- **Основные темы и ключевые моменты**

### Пример промпта для LLM:
```
Create a brief 1-2 sentence summary of this conversation segment.
Focus on the main topic and key points discussed.

Conversation:
user: I want to become a CTO
assistant: That's great! Let's discuss your path to CTO.
user: I have 5 years of experience in software development
assistant: That's a good foundation. What leadership experience do you have?
...

Summary:
```

### Ожидаемый результат:
```
"User wants to become a CTO and is discussing career goals with assistant providing advice."
```

---

## 🗓️ Сравнение с Weekly Summary

| Тип | Частота | Триггер | Содержимое |
|-----|---------|---------|------------|
| **Running Summary** | Каждые 20 сообщений | `message_count % 20 == 0` | Последние 20 сообщений |
| **Weekly Summary** | При переходе между неделями | `node == weekX_chat` | Вся неделя разговора |

---

## 💡 Преимущества

### ✅ Эффективность токенов:
- Вместо хранения полной истории (100+ сообщений)
- Хранится только краткая сводка + последние 5 сообщений
- Значительная экономия токенов

### ✅ Качество контекста:
- Поддерживает контекст разговора
- Улучшает качество ответов AI
- Обрабатывает длинные разговоры эффективно

### ✅ Баланс:
- Частота (20 сообщений) оптимальна для баланса
- Не слишком часто (не тратит лишние токены)
- Не слишком редко (не теряет контекст)

---

## 🔍 Мониторинг

### В логах:
```
INFO: Updated running summary for session test-session-123
```

### В состоянии сессии:
```json
{
  "prompt_context": {
    "running_summary": "User wants to become a CTO and is discussing career goals...",
    "recent_messages": [...],
    "important_facts": [...],
    "weekly_summaries": {...}
  },
  "message_count": 20
}
```

### В API:
```bash
GET /chat/{session_id}/memory-stats
# Показывает running_summary_exists: true/false
```

---

## 🎯 Заключение

**Running Summary обновляется каждые 20 сообщений** - это оптимальная частота для:

- ✅ Поддержания контекста разговора
- ✅ Экономии токенов
- ✅ Улучшения качества ответов AI
- ✅ Эффективной обработки длинных разговоров

Система автоматически балансирует между памятью и эффективностью!
