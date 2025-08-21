# Обновление change_intro

## Изменение
Узел `change_intro` теперь работает аналогично `improve_intro`, но для смены карьеры вместо улучшения отношений.

## Детали изменений

### 1. prompting.py
**change_intro** теперь собирает структурированную информацию о карьере:
- `career_change_circumstances` с полями:
  - `current_role` - текущая должность
  - `current_industry` - текущая индустрия
  - `desired_role` - желаемая должность
  - `desired_industry` - желаемая индустрия
  - `years_experience` - опыт работы
  - `career_change_reason` - причина смены карьеры
  - `career_satisfaction` - удовлетворенность карьерой

**change_skills** теперь работает как `improve_skills`:
- Собирает `skills`, `interests`, `activities`, `exciting_topics`
- Переходит к `change_obstacles` при наличии достаточной информации

**change_obstacles** теперь работает как `improve_obstacles`:
- Собирает `goals` и `negative_qualities`
- Переходит к `generate_plan` при наличии целей

### 2. root_graph.py
- Обновлены outputs для `change_intro` и `change_skills`
- Изменена логика переходов
- Обновлены system_prompt для соответствия новой функциональности

### 3. state_manager.py
- Добавлена обработка `career_change_circumstances` для `change_intro`
- Обновлена обработка `change_skills` для сохранения skills/interests/activities
- Сохранена логика для `change_obstacles`

## Результат
Теперь `change_intro` работает единообразно с `improve_intro`:
1. Собирает структурированную информацию о текущей ситуации
2. Переходит к сбору навыков и интересов
3. Переходит к выявлению препятствий
4. Генерирует план

Архитектура стала более последовательной и понятной.
