# Decision Engine API - Агент-Архитектор

Decision Engine (Агент-Архитектор) генерирует архитектурные решения на основе бизнес-требований, используя документацию ELMA365 через MCP.

## Базовый URL

```
http://localhost:8000/api/decision-engine
```

## Методы

### `POST /api/decision-engine/design`

Генерирует архитектурное решение на основе бизнес-требований.

**Тело запроса:**
```json
{
  "title": "Согласование договора",
  "business_requirements": "Необходимо создать процесс согласования договоров с несколькими этапами",
  "inputs": ["Договор", "Сумма"],
  "outputs": ["Согласованный договор"],
  "user_roles": ["Менеджер", "Директор", "Бухгалтер"],
  "workflow_steps": [
    "Создание заявки на согласование",
    "Согласование менеджером",
    "Согласование директором",
    "Завершение процесса"
  ],
  "integration_targets": [],
  "ui_requirements": [],
  "constraints": ["Срок согласования не более 5 дней"]
}
```

**Ответ:**
```json
{
  "solution_type": ["process"],
  "process_design": {
    "process_name": "Согласование договора",
    "process_type": "workflow",
    "steps": [
      {
        "step_number": 1,
        "name": "Создание заявки на согласование",
        "type": "task",
        "assignee_role": "Менеджер"
      },
      {
        "step_number": 2,
        "name": "Согласование менеджером",
        "type": "task",
        "assignee_role": "Менеджер"
      }
    ],
    "roles": ["Менеджер", "Директор", "Бухгалтер"],
    "conditions": [],
    "timers": [],
    "notifications": []
  },
  "app_structure": null,
  "widget_design": null,
  "integration_points": null,
  "references": [
    {
      "doc_id": "process-design",
      "sections": [],
      "relevance": "high",
      "extracted_info": {
        "title": "Проектирование процессов",
        "context": "..."
      }
    }
  ],
  "reasoning": "На основе анализа бизнес-требований 'Согласование договора' определены следующие типы решений: process. Спроектирован бизнес-процесс 'Согласование договора' с 5 шагами. Использовано 3 релевантных документов из документации ELMA365.",
  "confidence": 0.75
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/decision-engine/design \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Справочник контрагентов",
    "business_requirements": "Создать справочник для хранения информации о контрагентах",
    "inputs": ["Название", "ИНН", "Адрес", "Телефон"],
    "outputs": ["Карточка контрагента"],
    "user_roles": ["Администратор", "Менеджер"],
    "workflow_steps": [],
    "integration_targets": [],
    "ui_requirements": ["Список контрагентов", "Карточка контрагента"],
    "constraints": []
  }'
```

---

### `GET /api/decision-engine/health`

Проверка работоспособности Decision Engine.

**Ответ:**
```json
{
  "status": "healthy",
  "service": "Decision Engine",
  "version": "1.0.0"
}
```

---

## Типы решений

Decision Engine определяет следующие типы решений:

### 1. `process` - Бизнес-процесс

Определяется по ключевым словам:
- "процесс", "согласование", "этап", "шаг", "workflow", "процедура", "маршрут", "approval"

**Структура `process_design`:**
- `process_name` - название процесса
- `process_type` - тип процесса (workflow, approval, etc.)
- `steps` - список шагов процесса
- `roles` - роли в процессе
- `conditions` - условия и ветвления
- `timers` - таймеры и дедлайны
- `notifications` - уведомления

### 2. `app` - Приложение

Определяется по ключевым словам:
- "приложение", "справочник", "карточка", "данные", "entity", "сущность", "список", "таблица"

**Структура `app_structure`:**
- `app_name` - название приложения
- `entity_type` - тип сущности (card, directory, etc.)
- `fields` - поля приложения
- `views` - представления (списки, карточки)
- `permissions` - права доступа по ролям
- `workflows` - связанные процессы

### 3. `widget` - Виджет

Определяется по ключевым словам:
- "форма", "виджет", "widget", "form", "интерфейс", "ui", "элемент", "компонент", "dashboard"

**Структура `widget_design`:**
- `widget_name` - название виджета
- `widget_type` - тип виджета (form, chart, table, dashboard)
- `fields` - поля виджета
- `data_source` - источник данных
- `layout` - расположение элементов
- `validation_rules` - правила валидации

### 4. `module` - Модуль интеграции

Определяется по ключевым словам:
- "интеграция", "модуль", "api", "webhook", "connector", "интегратор", "синхронизация"

**Структура `integration_points`:**
- `integration_type` - тип интеграции (api, webhook, connector)
- `target_systems` - целевые системы
- `data_mapping` - маппинг данных
- `triggers` - триггеры интеграции
- `authentication` - настройки аутентификации

---

## Логика работы

1. **Анализ требований**: RequirementAnalyzer анализирует бизнес-требования и определяет типы решений на основе ключевых слов.

2. **Поиск документации**: MCPClient ищет релевантные документы через MCP API:
   - По типу решения (процессы, приложения, интеграции, виджеты)
   - По ключевым словам из требований

3. **Генерация решения**: DecisionEngine генерирует архитектурное решение:
   - Проектирует процесс (если `process` в solution_type)
   - Проектирует приложение (если `app` в solution_type)
   - Проектирует виджет (если `widget` в solution_type)
   - Проектирует интеграцию (если `module` в solution_type)

4. **Формирование обоснования**: Генерируется текстовое обоснование решения с указанием использованных документов.

---

## Примеры использования

### Пример 1: Проектирование процесса

```python
import requests

requirements = {
    "title": "Согласование договора",
    "business_requirements": "Создать процесс согласования договоров",
    "inputs": ["Договор", "Сумма"],
    "outputs": ["Согласованный договор"],
    "user_roles": ["Менеджер", "Директор"],
    "workflow_steps": [
        "Создание заявки",
        "Согласование менеджером",
        "Согласование директором"
    ],
    "integration_targets": [],
    "ui_requirements": [],
    "constraints": []
}

response = requests.post(
    "http://localhost:8000/api/decision-engine/design",
    json=requirements
)

solution = response.json()
print(f"Тип решения: {solution['solution_type']}")
print(f"Процесс: {solution['process_design']['process_name']}")
print(f"Шагов: {len(solution['process_design']['steps'])}")
```

### Пример 2: Проектирование приложения

```python
requirements = {
    "title": "Справочник контрагентов",
    "business_requirements": "Создать справочник для хранения информации о контрагентах",
    "inputs": ["Название", "ИНН", "Адрес"],
    "outputs": ["Карточка контрагента"],
    "user_roles": ["Администратор"],
    "workflow_steps": [],
    "integration_targets": [],
    "ui_requirements": ["Список", "Карточка"],
    "constraints": []
}

response = requests.post(
    "http://localhost:8000/api/decision-engine/design",
    json=requirements
)

solution = response.json()
print(f"Приложение: {solution['app_structure']['app_name']}")
print(f"Полей: {len(solution['app_structure']['fields'])}")
```

### Пример 3: Проектирование интеграции

```python
requirements = {
    "title": "Интеграция с 1С",
    "business_requirements": "Настроить интеграцию для синхронизации данных",
    "inputs": ["Данные из 1С"],
    "outputs": ["Данные в ELMA365"],
    "user_roles": ["Администратор"],
    "workflow_steps": [],
    "integration_targets": ["1С:Предприятие"],
    "ui_requirements": [],
    "constraints": []
}

response = requests.post(
    "http://localhost:8000/api/decision-engine/design",
    json=requirements
)

solution = response.json()
print(f"Тип интеграции: {solution['integration_points']['integration_type']}")
```

---

## Уверенность в решении

Поле `confidence` (0-1) показывает уверенность Decision Engine в решении:

- **0.5-0.6**: Базовая уверенность, минимальные требования
- **0.6-0.7**: Средняя уверенность, есть детальные требования
- **0.7-0.8**: Высокая уверенность, детальные требования + релевантные документы
- **0.8-1.0**: Очень высокая уверенность, полная информация + множество релевантных документов

---

## Ссылки на документацию

Поле `references` содержит список релевантных документов из базы документации ELMA365:

- `doc_id` - идентификатор документа
- `relevance` - релевантность (high, medium, low)
- `extracted_info` - извлеченная информация (title, context)

Эти ссылки можно использовать для получения полной информации через MCP API:
```bash
GET /api/mcp/doc/{doc_id}
```

---

## Статус

✅ Decision Engine готов к использованию.

Все компоненты протестированы:
- Анализ требований
- Поиск документации через MCP
- Генерация архитектурных решений
- Формирование обоснований

