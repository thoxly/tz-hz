# TS Generator API - Генератор Технических Заданий

Technical Specification Generator превращает архитектурные решения (ArchitectureSolution) от Decision Engine в формализованные технические задания в формате Markdown.

## Базовый URL

```
http://localhost:8000/api/ts
```

## Методы

### `POST /api/ts/generate`

Генерирует техническое задание на основе архитектурного решения с выбором режима.

**Тело запроса:**
```json
{
  "architecture": {
    "solution_type": ["process"],
    "process_design": {
      "process_name": "Согласование договора",
      "process_type": "workflow",
      "steps": [...],
      "roles": ["Менеджер", "Директор"]
    },
    "references": [...],
    "confidence": 0.75
  },
  "mode": "deterministic"
}
```

**Параметры:**
- `architecture` (ArchitectureSolution) - архитектурное решение от Decision Engine
- `mode` (string) - режим генерации: `"deterministic"` или `"verbose"` (по умолчанию: `"deterministic"`)

**Ответ:**
```json
{
  "markdown": "# Техническое задание\n\n...",
  "mode": "deterministic",
  "timestamp": "2025-11-27 10:34:21"
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/ts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "architecture": {
      "solution_type": ["process"],
      "process_design": {...},
      "confidence": 0.75
    },
    "mode": "deterministic"
  }'
```

---

### `POST /api/ts/generate/deterministic`

Генерирует строго формализованное ТЗ (deterministic режим).

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Ответ:**
```json
{
  "markdown": "# Техническое задание\n\n## 1. Описание задачи\n\n...",
  "mode": "deterministic",
  "timestamp": "2025-11-27 10:34:21"
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/ts/generate/deterministic \
  -H "Content-Type: application/json" \
  -d @architecture.json
```

---

### `POST /api/ts/generate/verbose`

Генерирует более человеческий текст ТЗ (verbose режим).

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Ответ:**
```json
{
  "markdown": "# Техническое задание\n\n## Введение\n\n...",
  "mode": "verbose",
  "timestamp": "2025-11-27 10:34:21"
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/ts/generate/verbose \
  -H "Content-Type: application/json" \
  -d @architecture.json
```

---

### `GET /api/ts/health`

Проверка работоспособности TS Generator.

**Ответ:**
```json
{
  "status": "healthy",
  "service": "Technical Specification Generator",
  "version": "1.0.0"
}
```

---

## Режимы генерации

### Deterministic (строгий)

Строго формализованное ТЗ с четкой структурой:

1. Описание задачи
2. Типы решений
3. Архитектура решения
   - 3.1. Бизнес-процесс
   - 3.2. Приложение
   - 3.3. Виджет
   - 3.4. Интеграция
4. Функциональные требования
5. Нефункциональные требования
6. Роли и права
7. Использованная документация ELMA365
8. Заключение
9. Приложения

**Особенности:**
- Таблицы для полей приложений
- Нумерованные списки
- Строгая структура разделов
- Формализованный язык

### Verbose (более человеческий)

Более читаемый текст с естественным языком:

1. Введение
2. Описание решения
3. Требования
4. Использованная документация
5. Заключение

**Особенности:**
- Естественный язык
- Описательные формулировки
- Меньше формализма
- Более читаемый текст

---

## Структура ТЗ

### Deterministic режим

```markdown
# Техническое задание

**Дата создания:** 2025-11-27 10:34:21
**Уверенность решения:** 75.0%

## 1. Описание задачи
...

## 2. Типы решений
- **Бизнес-процесс**

## 3. Архитектура решения

### 3.1. Бизнес-процесс

**Название процесса:** Согласование договора
**Тип процесса:** workflow

**Шаги процесса:**

1. **Создание заявки на согласование**
   - Тип: task
   - Исполнитель: Менеджер

2. **Согласование менеджером**
   - Тип: task
   - Исполнитель: Менеджер

**Роли в процессе:**
- Менеджер
- Директор
- Бухгалтер

## 4. Функциональные требования
...

## 5. Нефункциональные требования
...

## 6. Роли и права
...

## 7. Использованная документация ELMA365
...

## 8. Заключение
...

## 9. Приложения
...
```

---

## Примеры использования

### Полный пайплайн: Decision Engine → TS Generator

```python
import requests

# Шаг 1: Создать архитектурное решение
requirements = {
    "title": "Согласование договора",
    "business_requirements": "Создать процесс согласования",
    "workflow_steps": ["Создание заявки", "Согласование", "Завершение"],
    "user_roles": ["Менеджер", "Директор"]
}

response = requests.post(
    "http://localhost:8000/api/decision-engine/design",
    json=requirements
)
architecture = response.json()

# Шаг 2: Сгенерировать ТЗ
ts_request = {
    "architecture": architecture,
    "mode": "deterministic"
}

response = requests.post(
    "http://localhost:8000/api/ts/generate",
    json=ts_request
)
ts = response.json()

# Сохранить ТЗ
with open("technical_specification.md", "w", encoding="utf-8") as f:
    f.write(ts["markdown"])

print("ТЗ сгенерировано и сохранено!")
```

### Генерация ТЗ из существующего решения

```python
import requests
import json

# Загрузить архитектурное решение
with open("architecture.json", "r") as f:
    architecture = json.load(f)

# Сгенерировать ТЗ в verbose режиме
response = requests.post(
    "http://localhost:8000/api/ts/generate/verbose",
    json=architecture
)

ts = response.json()
print(ts["markdown"])
```

---

## Интеграция с n8n

Пайплайн для генерации ТЗ:

```
Telegram → Normalizer → Decision Engine → TS Generator → PNG/PDF → Telegram
```

**Пример n8n workflow:**

1. **Webhook** (Telegram) - получение бизнес-требований
2. **HTTP Request** - вызов `/api/decision-engine/design`
3. **HTTP Request** - вызов `/api/ts/generate`
4. **Markdown to PDF** - конвертация в PDF
5. **Send Message** (Telegram) - отправка ТЗ

---

## Особенности

1. **Без галлюцинаций**: ТЗ генерируется строго на основе ArchitectureSolution
2. **Ссылки на документацию**: Включает список использованных документов ELMA365
3. **Два режима**: Deterministic для формальных ТЗ, Verbose для читаемых документов
4. **Структурированный вывод**: Четкая структура разделов и подразделов
5. **Markdown формат**: Легко конвертируется в HTML, PDF, DOCX

---

## Статус

✅ TS Generator готов к использованию.

Все компоненты протестированы:
- Deterministic режим генерации
- Verbose режим генерации
- API endpoints
- Интеграция с Decision Engine

---

## Следующие шаги (опционально)

1. **Интеграция с LLM**: Для более красивого текста (опционально)
2. **Экспорт в другие форматы**: PDF, DOCX, HTML
3. **Шаблоны ТЗ**: Кастомные шаблоны для разных типов решений
4. **Валидация**: Проверка полноты и корректности ТЗ

