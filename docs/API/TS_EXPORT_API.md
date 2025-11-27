# TS Export API - Экспорт Технических Заданий

API для экспорта сгенерированных технических заданий в различные форматы: PDF, DOCX, HTML, Markdown.

## Базовый URL

```
http://localhost:8000/api/ts/export
```

## Методы

### `POST /api/ts/export/pdf`

Экспортирует ТЗ в PDF формат.

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Query параметры:**
- `mode` (optional) - режим генерации: `"deterministic"` или `"verbose"` (по умолчанию: `"deterministic"`)

**Ответ:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="technical_specification_YYYY-MM-DD_HH-MM-SS.pdf"`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/ts/export/pdf?mode=deterministic" \
  -H "Content-Type: application/json" \
  -d @architecture.json \
  --output technical_specification.pdf
```

**Примечание:** Для экспорта в PDF требуется установить одну из библиотек:
- `weasyprint` (рекомендуется, но на Windows может потребоваться GTK+)
- `pdfkit` (требует установки wkhtmltopdf)
- `pypandoc` (требует установки pandoc)

---

### `POST /api/ts/export/docx`

Экспортирует ТЗ в DOCX формат (Microsoft Word).

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Query параметры:**
- `mode` (optional) - режим генерации: `"deterministic"` или `"verbose"` (по умолчанию: `"deterministic"`)

**Ответ:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Content-Disposition: `attachment; filename="technical_specification_YYYY-MM-DD_HH-MM-SS.docx"`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/ts/export/docx?mode=deterministic" \
  -H "Content-Type: application/json" \
  -d @architecture.json \
  --output technical_specification.docx
```

**Требования:** Установить `python-docx`:
```bash
pip install python-docx
```

---

### `POST /api/ts/export/html`

Экспортирует ТЗ в HTML формат.

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Query параметры:**
- `mode` (optional) - режим генерации: `"deterministic"` или `"verbose"` (по умолчанию: `"deterministic"`)

**Ответ:**
- Content-Type: `text/html`
- Content-Disposition: `inline; filename="technical_specification_YYYY-MM-DD_HH-MM-SS.html"`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/ts/export/html?mode=deterministic" \
  -H "Content-Type: application/json" \
  -d @architecture.json \
  --output technical_specification.html
```

**Примечание:** HTML экспорт работает всегда, не требует дополнительных библиотек.

---

### `POST /api/ts/export/markdown`

Экспортирует ТЗ в Markdown формат.

**Тело запроса:**
```json
{
  "solution_type": ["process"],
  "process_design": {...},
  "confidence": 0.75
}
```

**Query параметры:**
- `mode` (optional) - режим генерации: `"deterministic"` или `"verbose"` (по умолчанию: `"deterministic"`)

**Ответ:**
- Content-Type: `text/markdown`
- Content-Disposition: `attachment; filename="technical_specification_YYYY-MM-DD_HH-MM-SS.md"`

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/ts/export/markdown?mode=deterministic" \
  -H "Content-Type: application/json" \
  -d @architecture.json \
  --output technical_specification.md
```

---

## Полный пайплайн

### Пример: Генерация и экспорт ТЗ

```python
import requests

# 1. Создать архитектурное решение
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

# 2. Экспортировать в DOCX
response = requests.post(
    "http://localhost:8000/api/ts/export/docx?mode=deterministic",
    json=architecture
)

with open("technical_specification.docx", "wb") as f:
    f.write(response.content)

print("ТЗ экспортировано в DOCX!")
```

### Пример: Экспорт в HTML для просмотра

```python
import requests

# Загрузить архитектурное решение
with open("architecture.json", "r") as f:
    architecture = json.load(f)

# Экспортировать в HTML
response = requests.post(
    "http://localhost:8000/api/ts/export/html?mode=verbose",
    json=architecture
)

with open("technical_specification.html", "wb") as f:
    f.write(response.content)

print("ТЗ экспортировано в HTML!")
```

---

## Установка зависимостей

### Минимальные зависимости (HTML, Markdown)

```bash
pip install markdown
```

### DOCX экспорт

```bash
pip install python-docx
```

### PDF экспорт (выберите один вариант)

**Вариант 1: WeasyPrint (рекомендуется для Linux/Mac)**
```bash
pip install weasyprint
# На Windows может потребоваться установка GTK+
```

**Вариант 2: pdfkit (требует wkhtmltopdf)**
```bash
pip install pdfkit
# Установите wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
```

**Вариант 3: pypandoc (требует pandoc)**
```bash
pip install pypandoc
# Установите pandoc: https://pandoc.org/installing.html
```

---

## Статус зависимостей

Проверить доступность зависимостей можно через health endpoint:

```bash
curl http://localhost:8000/api/ts/health
```

Ответ:
```json
{
  "status": "healthy",
  "service": "Technical Specification Generator",
  "version": "1.0.0",
  "dependencies": {
    "pdfkit": false,
    "weasyprint": false,
    "docx": true,
    "markdown": true,
    "pypandoc": false
  }
}
```

---

## Особенности

1. **HTML всегда доступен**: Экспорт в HTML работает без дополнительных библиотек
2. **DOCX работает с python-docx**: Установка одной библиотеки достаточна
3. **PDF требует дополнительных библиотек**: Выберите один из вариантов выше
4. **Markdown всегда доступен**: Базовый формат, не требует зависимостей
5. **Автоматическое именование файлов**: Имена файлов включают timestamp

---

## Интеграция с n8n

Пример workflow для экспорта ТЗ:

1. **Webhook** - получение архитектурного решения
2. **HTTP Request** - `POST /api/ts/export/docx`
3. **Save File** - сохранение DOCX файла
4. **Send Message** (Telegram/Email) - отправка файла

---

## Статус

✅ Экспорт ТЗ готов к использованию.

Работающие форматы:
- ✅ HTML (всегда доступен)
- ✅ DOCX (требует python-docx)
- ✅ Markdown (всегда доступен)
- ⚠️ PDF (требует weasyprint/pdfkit/pypandoc, на Windows может быть проблематично)

