## Цель

Вставить перед узлом `generate_plan` новый узел `retrieve_reg`, который будет выполнять Retrieve (RAG) из корпуса коучинг‑пособий и передавать найденные релевантные фрагменты в генератор плана. Сделать это пошагово, без нарушения текущей архитектуры и с возможностью включать/отключать через фича‑флаг.

## Трекинг прогресса (живой чек‑лист)

- [x] Утвердить план реализации (этот файл)
- [ ] Шаг 1. Подготовка корпуса
  - [x] Созданы директории `LangGraph/RAG/corpus/{pdf,txt,meta}` и `LangGraph/RAG/index`
  - [ ] Загружены 3–5 приоритетных PDF и (опционально) метаданные JSON
- [x] Шаг 2. Модуль Retrieval (MVP)
  - [x] `schemas.py`, `vector_store.py`, `simple_store.py`, `retriever.py`, `pdf_reader.py`
- [x] Шаг 3. Конфиг и фича‑флаги
  - [x] `REG_ENABLED`, `EMBEDDINGS_*`, пути и лимиты, `PDF_*`
- [x] Шаг 4. Индексация (ingest)
  - [x] `ingest.py` + CLI, индекс собран в `LangGraph/RAG/index`
- [x] Шаг 5. Расширение Node/GraphProcessor
- [x] Шаг 6. Узел `retrieve_reg` и перенастройка переходов на него
- [x] Шаг 7. Prompting: использование контекста в `generate_plan`
- [x] Шаг 8. Типы и State
  - [x] Добавлен `RetrievalChunk` в `types.py`
  - [x] `StateManager` обновляет `retrieved_chunks` в состоянии
  - [x] Интеграция с `generate_plan` работает (есть проблема с форматированием)
- [ ] Шаг 9. Тесты (unit + integration)
- [ ] Шаг 10. Конфигурация и окружение (зависимости)
- [ ] Шаг 11. Наблюдаемость и безопасность
- [ ] Шаг 12. Релиз поэтапно (off → stage → on)

Примечание: чек‑лист строго соответствует нумерации и заголовкам в разделе «Хронологический план внедрения».

## Принципы

- **Минимальные изменения ядра**: расширяем `Node` и `GraphProcessor` так, чтобы появились «не‑LLM» узлы с собственным исполнителем, не ломая текущих путей.
- **Декомпозиция**: отдельный модуль `retrieval` для индексации и поиска; хранение индекса локально сначала (MVP), позже — опционально в `mongodb`.
- **Обратная совместимость**: при `REG_ENABLED=false` граф работает по‑старому, `retrieve_reg` пропускается.
- **Наблюдаемость**: логируем запросы/хиты/latency, режем и санитизируем контент.

## Хронологический план внедрения

### Шаг 1. Подготовка корпуса
- Создать каталог для корпуса: `LangGraph/RAG/corpus/` и подкаталоги: `pdf/`, `txt/`, `meta/`.
- Источники: PDF‑книги/гайдлайны (`pdf/`), дополнительные `.txt|.md` материалы (`txt/`).
- По возможности добавить метаданные для каждого источника (см. раздел «Требуется от вас»).

**Что делаю я:** Создаю структуру каталогов, ingest‑пайплайн.
**Что требуется от вас:**
- Положить 3–5 приоритетных PDF в `LangGraph/RAG/corpus/pdf/` (либо прислать архив/ссылку)
- По возможности добавить метаданные JSON в `LangGraph/RAG/corpus/meta/<filename>.json`:
```json
{
  "title": "Coaching Handbook",
  "authors": ["John Doe"],
  "year": 2020,
  "language": "en",
  "tags": ["coaching", "goals", "productivity"],
  "license": "owned_or_permitted",
  "source": "internal_library_or_url"
}
```

### Шаг 2. Модуль Retrieval (MVP)
- Создать пакет `LangGraph/mentor_ai/cursor/modules/retrieval/` с файлами:
  - `schemas.py` — Pydantic‑модели: `DocumentChunk`, `RetrievalResult`.
  - `ingest.py` — разметка на чанки, нормализация и построение индекса.
  - `vector_store.py` — интерфейс `VectorStore` (add, search, persist, load).
  - `faiss_store.py` (или `simple_store.py`) — локальный индекс (MVP: FAISS или cosine по Sentence/Embeddings; если библиотек нет — временно `simple_store.py` + `sklearn`/`numpy`).
  - `retriever.py` — `RegRetriever` со стратегией: формирование поисковых запросов из `state` и `user_message`, вызов `VectorStore.search`, пост‑фильтрация, дедупликация, тримминг по токенам.
  - `pdf_reader.py` — модуль извлечения текста из PDF (см. ниже).

Примечания:
- На MVP используем OpenAI `text-embedding-3-small` или аналог из локальных эмбеддингов (переключается в конфиге).
- Индекс и кеш — в `LangGraph/RAG/index/`.

**Что делаю я:** Весь код модуля retrieval.
**Что требуется от вас:** Ничего (ждём PDF от Шага 1).

### Шаг 3. Конфиг и фича‑флаги
- Расширить `LangGraph/mentor_ai/app/config.py`:
  - `REG_ENABLED: bool = False` (по умолчанию выключено)
  - `EMBEDDINGS_PROVIDER: str = "openai" | "local"`
  - `EMBEDDINGS_MODEL: str`
  - `RAG_INDEX_PATH: str = "LangGraph/RAG/index"`
  - `RAG_CORPUS_PATH: str = "LangGraph/RAG/corpus"`
  - ключи провайдера (через env), лимиты: `RETRIEVE_TOP_K`, `MAX_CHARS_PER_CHUNK`, `MAX_CONTEXT_CHARS`.
  - лимиты PDF‑парсинга: `PDF_MAX_PAGES`, `PDF_EXTRACTOR={pdfminer|pymupdf}`.

**Что делаю я:** Конфиги в коде.
**Что требуется от вас:**
- Выбрать провайдера эмбеддингов: `openai` или `local`
- Если `openai` — предоставить `OPENAI_API_KEY` (в окружение Railway/локально)
- Подтвердить право использовать материалы для векторного поиска (внутреннее использование)

### Шаг 4. Индексация (ingest)
- Реализовать `ingest.py`:
  - Пройтись по `RAG_CORPUS_PATH` → прочитать `.md|.txt|.pdf` (PDF через `pdf_reader.py`).
  - Счалнкать по размерам (символы/предложения) с overlap.
  - Посчитать эмбеддинги и положить в `VectorStore`.
  - Сохранить индекс в `RAG_INDEX_PATH`.
- Добавить CLI‑скрипт (в `start.sh` или отдельный `scripts/ingest_reg.sh`) для однократной индексации.

PDF‑парсинг (MVP):
- По умолчанию `pdfminer.six` (чистый Python, стабильная установка). Опционально `pymupdf` как быстрый вариант.
- Нормализация: удалить нефункциональные пробелы, сшить переносы, удалить колонтитулы/номера страниц эвристиками.

**Что делаю я:** Код индексации, CLI‑скрипт.
**Что требуется от вас:** Ничего (используем PDF от Шага 1).

### Шаг 5. Расширение Node/GraphProcessor (без поломки LLM‑пути)
- В `LangGraph/mentor_ai/cursor/core/root_graph.py` расширить `class Node` новым необязательным полем `executor: Optional[Callable] = None`.
- В `LangGraph/mentor_ai/cursor/core/graph_processor.py`:
  - Если у узла есть `executor`, выполнить его с `(user_message, current_state)` и получить `llm_data` без вызова LLM.
  - Иначе — текущий LLM‑путь без изменений.
  - Обновление состояния и вычисление `next` — как сейчас.
- Совместимость: все старые узлы без `executor` работают по‑прежнему.

**Что делаю я:** Весь код расширения архитектуры.
**Что требуется от вас:** Ничего.

### Шаг 6. Узел `retrieve_reg`
- В `root_graph.py` добавить `get_retrieve_reg_node()`:
  - `node_id="retrieve_reg"`
  - `outputs={"retrieved_chunks": list, "next": "generate_plan"}`
  - `executor` → функция, которая:
    - Проверяет `REG_ENABLED`. Если `false` → возвращает `{retrieved_chunks: [], next: "generate_plan", reply: ""}`.
    - Иначе инициирует `RegRetriever` (ленивая инициализация индекса), формирует запрос(ы) из `state` (цели/препятствия/интересы), делает поиск top‑k, возвращает `{retrieved_chunks: [...], next: "generate_plan", reply: ""}`.
- В узлах, которые раньше вели прямо к `generate_plan` (`improve_obstacles`, `change_obstacles`, `find_obstacles`, `lost_skills`), поменять `next_node` на `"retrieve_reg"`.

**Что делаю я:** Весь код узла и перенастройка переходов.
**Что требуется от вас:** Ничего.

### Шаг 7. Prompting: использование контекста в `generate_plan`
- В `LangGraph/mentor_ai/cursor/core/prompting.py` в ветке `node.node_id == "generate_plan"`:
  - Если в `state` есть `retrieved_chunks`, добавить к системной инструкции секцию "Knowledge snippets" (жёсткий лимит по символам/токенам).
  - Формат: нумерованный список, каждый пункт: короткий `title` + 1‑2 ключевых тезиса. Контент санитизировать (удалить markdown‑линки/HTML, обрезать).
  - Соблюдать прежние JSON‑требования к ответу.

**Что делаю я:** Весь код интеграции сниппетов в промпт.
**Что требуется от вас:** Ничего.

### Шаг 8. Типы и State
- В `LangGraph/mentor_ai/cursor/core/types.py` (или рядом) добавить `RetrievalChunk` с полями: `id`, `title`, `snippet`, `source`, `score`.
- В `StateManager.update_state` убедиться, что `retrieved_chunks` пишется в состояние (только нужные поля, без громоздких payload).

**Что делаю я:** Весь код типов и обновления состояния.
**Что требуется от вас:** Ничего.

### Шаг 9. Тесты
- Unit:
  - `tests/test_retriever.py`: поиск по искусственному корпусу, детерминированные хиты.
  - `tests/test_graph_processor.py`: выполнение `retrieve_reg` без LLM, переход к `generate_plan`.
  - `tests/test_prompting.py`: включение сниппетов в промпт для `generate_plan`, обрезка по лимиту.
- Интеграционные:
  - Сквозной прогон пути (например, `improve_*` → `retrieve_reg` → `generate_plan`).
  - Ветка с `REG_ENABLED=false`: поведение эквивалентно текущему.

**Что делаю я:** Весь код тестов.
**Что требуется от вас:** Ничего.

### Шаг 10. Конфигурация и окружение
- Добавить переменные в `.env`/Railway:
  - `REG_ENABLED`, `EMBEDDINGS_PROVIDER`, `EMBEDDINGS_MODEL`, ключи провайдера.
- В `requirements.txt` при необходимости добавить: `faiss-cpu` или альтернативы (`sentence-transformers`, `scikit-learn`). На MVP — минимальный набор.
  - Для PDF: `pdfminer.six` (обязательно), опционально `pymupdf`.

**Что делаю я:** Обновление requirements.txt, конфиги Railway.
**Что требуется от вас:** Ничего (ключи уже предоставлены в Шаге 3).

### Шаг 11. Наблюдаемость и безопасность
- Логировать: запросы к ретриверу, время ответа, кол-во чанков, усечение.
- Санитизация: вырезать HTML/скрипты, ограничивать длину сниппетов.
- Prompt‑injection: не исполнять содержимое сниппетов, подавать как справочный текст.

**Что делаю я:** Весь код логирования и санитизации.
**Что требуется от вас:** Ничего.

### Шаг 12. Релиз поэтапно
- Фича‑флаг по умолчанию `false` → деплой без изменений поведения.
- Прогнать тесты/стейдж с малым корпусом.
- Включить `REG_ENABLED=true` на стейдже, проверить latency/качество плана.
- Постепенно расширять корпус и включать на проде.

**Что делаю я:** Деплой с флагом off, тестирование на стейдже.
**Что требуется от вас:**
- Решение о включении `REG_ENABLED=true` на стейдже
- Решение о включении `REG_ENABLED=true` на проде
- Обратная связь по качеству планов с RAG vs без RAG

## Изменяемые файлы (на этапах 5–7)
- `LangGraph/mentor_ai/cursor/core/root_graph.py` — расширение `Node`, добавление `retrieve_reg`, перенастройка `next` у предшественников `generate_plan`.
- `LangGraph/mentor_ai/cursor/core/graph_processor.py` — ветка исполнения `executor` для не‑LLM узлов.
- `LangGraph/mentor_ai/cursor/core/prompting.py` — инъекция сниппетов в промпт `generate_plan`.
- `LangGraph/mentor_ai/cursor/core/types.py` — модели для чанков.
- `LangGraph/mentor_ai/app/config.py` — фича‑флаги и параметры.
- Новый модуль: `LangGraph/mentor_ai/cursor/modules/retrieval/*`.
- Скрипт индексации: `scripts/ingest_reg.sh` (опционально) и/или команды в `start.sh`.

## Резюме требований от вас

**Срочно (для Шагов 1, 3):**
- 3–5 приоритетных PDF в `LangGraph/RAG/corpus/pdf/`
- Метаданные JSON (опционально) в `LangGraph/RAG/corpus/meta/`
- Выбор провайдера эмбеддингов: `openai` или `local`
- `OPENAI_API_KEY` (если выбрали openai)
- Подтверждение прав на использование материалов

**Позже (для Шага 12):**
- Решения о включении `REG_ENABLED=true` на стейдже/проде
- Обратная связь по качеству планов

## Границы MVP по PDF

- Извлекаем только текстовые слои PDF. Сложная вёрстка/сканы без OCR — вне MVP. Если будут такие файлы — обсудим добавление OCR (например, `pytesseract`).
- Базовые эвристики по чистке текста; позднее можно добавить rule‑based секционные заголовки.

## Риски и снижения
- Производительность: ограничить K и длину сниппетов, кэшировать результаты на сессию.
- Качество: добавить простую эвристику формирования запросов (из `goals`, `obstacles`, `skills`, `exciting_topics`).
- Зависимости: начать с простого `simple_store.py`, избежать тяжёлых lib на первом проходе.

## Критерии готовности (DoD)
- При `REG_ENABLED=false` поведение идентично текущему, тесты зелёные.
- При `REG_ENABLED=true` узел `retrieve_reg` выполняется, состояние содержит `retrieved_chunks`, `generate_plan` использует сниппеты.
- Добавлены и проходят unit+integration тесты.
- Индекс собирается из `corpus`, хранится в `index`, логирование включено.


