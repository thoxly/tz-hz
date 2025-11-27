# MCP API - Интерфейс для агент-архитектора

MCP (Model Context Protocol) сервер предоставляет строгий интерфейс к документации ELMA365 для работы агент-архитектора (LLM).

## Базовый URL

```
http://localhost:8000/api/mcp
```

## Методы

### 1. `GET /api/mcp/doc/{doc_id}`

Получить документ по ID.

**Параметры:**
- `doc_id` (path) - идентификатор документа

**Ответ:**
```json
{
  "title": "Календарь",
  "breadcrumbs": ["Платформа", "Календарь"],
  "blocks": [
    {
      "type": "header",
      "level": 2,
      "text": "Настройка календаря"
    },
    {
      "type": "paragraph",
      "text": "Для настройки календаря..."
    }
  ],
  "plain_text": "Настройка календаря\nДля настройки календаря...",
  "url": "https://elma365.com/ru/help/platform/calendar"
}
```

**Пример:**
```bash
curl http://localhost:8000/api/mcp/doc/calendar
```

---

### 2. `POST /api/mcp/entities/search`

Поиск сущностей с фильтрами.

**Тело запроса:**
```json
{
  "type": "header",
  "filters": {
    "level": 2,
    "breadcrumbs": ["Платформа"],
    "limit": 50
  }
}
```

**Типы сущностей:**
- `header` - заголовки
- `list` - списки
- `code_block` - блоки кода
- `special_block` - специальные блоки (В этой статье, Важно, Пример)
- `paragraph` - параграфы

**Фильтры для `header`:**
- `level` (int) - уровень заголовка (1-6)
- `breadcrumbs` (list) - список breadcrumbs
- `limit` (int) - максимальное количество результатов

**Фильтры для `list`:**
- `ordered` (bool) - упорядоченный список или нет
- `breadcrumbs` (list) - список breadcrumbs
- `limit` (int) - максимальное количество результатов

**Фильтры для `code_block`:**
- `language` (str) - язык программирования (python, javascript, sql, etc.)
- `breadcrumbs` (list) - список breadcrumbs
- `limit` (int) - максимальное количество результатов

**Фильтры для `special_block`:**
- `kind` (str) - тип блока ("В этой статье", "Важно", "Пример")
- `breadcrumbs` (list) - список breadcrumbs
- `limit` (int) - максимальное количество результатов

**Ответ:**
```json
{
  "type": "header",
  "count": 15,
  "entities": [
    {
      "doc_id": "calendar",
      "text": "Настройка календаря",
      "level": 2,
      "anchor": "calendar-setup",
      "breadcrumbs": ["Платформа", "Календарь"],
      "url": "https://elma365.com/ru/help/platform/calendar",
      "block_index": 3
    }
  ]
}
```

**Примеры запросов:**

```bash
# Все заголовки уровня 2
curl -X POST http://localhost:8000/api/mcp/entities/search \
  -H "Content-Type: application/json" \
  -d '{"type": "header", "filters": {"level": 2}}'

# Все блоки кода на Python
curl -X POST http://localhost:8000/api/mcp/entities/search \
  -H "Content-Type: application/json" \
  -d '{"type": "code_block", "filters": {"language": "python"}}'

# Все специальные блоки "В этой статье"
curl -X POST http://localhost:8000/api/mcp/entities/search \
  -H "Content-Type: application/json" \
  -d '{"type": "special_block", "filters": {"kind": "В этой статье"}}'
```

---

### 3. `POST /api/mcp/search`

Полнотекстовый поиск по документам.

**Тело запроса:**
```json
{
  "query": "календарь",
  "limit": 20
}
```

**Ответ:**
```json
{
  "query": "календарь",
  "count": 5,
  "results": [
    {
      "doc_id": "calendar",
      "title": "Календарь",
      "url": "https://elma365.com/ru/help/platform/calendar",
      "section": "Платформа > Календарь",
      "breadcrumbs": ["Платформа", "Календарь"],
      "context": "...настройка календаря...",
      "match_position": 123
    }
  ]
}
```

**Пример:**
```bash
curl -X POST http://localhost:8000/api/mcp/search \
  -H "Content-Type: application/json" \
  -d '{"query": "календарь", "limit": 10}'
```

---

### 4. `GET /api/mcp/docs/section/{section}`

Получить список документов по разделу.

**Параметры:**
- `section` (path) - название раздела (platform, crm, ecm, etc.)

**Ответ:**
```json
{
  "section": "platform",
  "count": 7,
  "docs": [
    {
      "doc_id": "calendar",
      "title": "Календарь",
      "url": "https://elma365.com/ru/help/platform/calendar",
      "section": "Платформа > Календарь",
      "breadcrumbs": ["Платформа", "Календарь"]
    }
  ]
}
```

**Пример:**
```bash
curl http://localhost:8000/api/mcp/docs/section/platform
```

---

### 5. `GET /api/mcp/entities/headers`

Быстрый доступ к заголовкам.

**Query параметры:**
- `level` (optional) - уровень заголовка (1-6)
- `breadcrumbs` (optional) - breadcrumbs через запятую
- `limit` (optional, default: 100) - максимальное количество результатов

**Примеры:**
```bash
# Все заголовки уровня 2
curl "http://localhost:8000/api/mcp/entities/headers?level=2"

# Заголовки в разделе "Платформа"
curl "http://localhost:8000/api/mcp/entities/headers?breadcrumbs=Платформа"

# Заголовки уровня 2 в разделе "Платформа"
curl "http://localhost:8000/api/mcp/entities/headers?level=2&breadcrumbs=Платформа&limit=50"
```

---

### 6. `GET /api/mcp/entities/special-blocks`

Быстрый доступ к специальным блокам.

**Query параметры:**
- `kind` (optional) - тип блока ("В этой статье", "Важно", "Пример")
- `limit` (optional, default: 100) - максимальное количество результатов

**Примеры:**
```bash
# Все блоки "В этой статье"
curl "http://localhost:8000/api/mcp/entities/special-blocks?kind=В этой статье"

# Все блоки "Важно"
curl "http://localhost:8000/api/mcp/entities/special-blocks?kind=Важно"
```

---

## Использование в LLM

### Пример для агент-архитектора:

```python
# 1. Найти все заголовки уровня 2 в разделе "Платформа"
headers = requests.post("http://localhost:8000/api/mcp/entities/search", json={
    "type": "header",
    "filters": {
        "level": 2,
        "breadcrumbs": ["Платформа"],
        "limit": 50
    }
}).json()

# 2. Получить конкретный документ
doc = requests.get("http://localhost:8000/api/mcp/doc/calendar").json()

# 3. Найти релевантные документы по запросу
results = requests.post("http://localhost:8000/api/mcp/search", json={
    "query": "настройка процесса",
    "limit": 10
}).json()

# 4. Получить все блоки кода на Python
code_blocks = requests.post("http://localhost:8000/api/mcp/entities/search", json={
    "type": "code_block",
    "filters": {
        "language": "python",
        "limit": 20
    }
}).json()
```

---

## Важные особенности

1. **Структурированные данные**: MCP возвращает только структурированные данные, без HTML
2. **Детерминированный поиск**: `find_relevant` использует ILIKE, без embeddings
3. **Контекст breadcrumbs**: Все сущности содержат breadcrumbs для понимания контекста
4. **Ограничения**: Все методы поддерживают `limit` для контроля размера ответа

---

## Статус

✅ MCP сервер готов к использованию агент-архитектором.

Все методы протестированы и работают с существующей базой данных (50 документов, 1147 сущностей).

