# Архитектурные изменения

## Проблема
Узел `relationships_to_plan` был промежуточным узлом между `change_obstacles` и `generate_plan`, что создавало несогласованность в архитектуре. В то время как `improve_obstacles` сразу переходил к `generate_plan`, другие узлы `*_obstacles` использовали промежуточные узлы.

## Решение
Упростили архитектуру, сделав все узлы `*_obstacles` сразу переходить к `generate_plan`, как это уже было реализовано для `improve_obstacles`.

## Изменения

### 1. root_graph.py
- **Удален узел**: `relationships_to_plan`
- **Изменен переход**: `change_obstacles` теперь сразу переходит к `generate_plan`
- **Изменен переход**: `self_growth_obstacles` теперь сразу переходит к `generate_plan`
- **Удалены функции**: `get_relationships_to_plan_node()`, `get_self_growth_to_plan_node()`, `get_no_goal_to_plan_node()`

### 2. prompting.py
- **Удалена обработка**: `relationships_to_plan` узла
- **Логика сохранена**: Все узлы `*_obstacles` уже имели правильную логику перехода к `generate_plan`

### 3. state_manager.py
- **Удалена обработка**: `relationships_to_plan` узла
- **Логика сохранена**: `change_obstacles` и `self_growth_obstacles` уже имели правильную логику установки `next = "generate_plan"`

## Результат
Теперь архитектура единообразна:
- `improve_obstacles` → `generate_plan`
- `change_obstacles` → `generate_plan` 
- `self_growth_obstacles` → `generate_plan`
- `no_goal_reason` → `generate_plan`

Все узлы сбора информации сразу переходят к генерации плана, что упрощает архитектуру и делает её более понятной.

## Тестирование
Создан тест `test_simple_architecture.py`, который проверяет:
- ✅ Удаление промежуточных узлов
- ✅ Правильные переходы между узлами
- ✅ Сохранение всех необходимых узлов
- ✅ Корректную работу логики переходов
