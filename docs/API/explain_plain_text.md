# Что такое поле plain_text?

## Структура базы данных

В таблице `docs` есть поле `content` типа **JSONB** (JSON Binary в PostgreSQL), которое содержит структурированные данные:

```json
{
  "html": "<html>...</html>",           // Полный HTML страницы
  "plain_text": "Чистый текст...",      // ← ВОТ ЭТО ПОЛЕ!
  "breadcrumbs": ["Платформа", "..."],
  "links": ["https://...", "..."],
  "raw_data": {...}
}
```

## Где находится plain_text?

**В базе данных PostgreSQL:**
- Таблица: `docs`
- Поле: `content` (тип JSONB)
- Путь к тексту: `content->>'plain_text'`

**Структура:**
```
docs
├── id (integer)
├── doc_id (string)
├── url (text)
├── title (text)
├── section (text)
├── content (JSONB) ← здесь хранится plain_text
│   ├── html
│   ├── plain_text ← ВОТ ОНО!
│   ├── breadcrumbs
│   ├── links
│   └── raw_data
├── created_at
└── last_crawled
```

## Что содержит plain_text?

**Чистый текст страницы БЕЗ HTML тегов:**
- ✅ Весь текст статьи
- ✅ Заголовки
- ✅ Параграфы
- ✅ Списки
- ❌ БЕЗ HTML тегов (<div>, <p>, <h1> и т.д.)
- ❌ БЕЗ навигации и меню
- ❌ БЕЗ скриптов и стилей

## Как получить plain_text?

### 1. Через API (рекомендуется):

```bash
# Все документы с plain_text
GET http://127.0.0.1:8000/api/docs/plain-text

# Конкретный документ
GET http://127.0.0.1:8000/api/docs/{doc_id}
# В ответе будет поле content.plain_text
```

### 2. Через SQL запрос:

```sql
SELECT 
    doc_id,
    title,
    content->>'plain_text' as plain_text
FROM docs;
```

### 3. Через Python:

```python
from app.database import get_db
from app.database.models import Doc

async with get_db() as db:
    doc = await db.get(Doc, doc_id="calendar")
    plain_text = doc.content.get('plain_text')
    print(plain_text)
```

## Пример данных:

```json
{
  "id": 1,
  "doc_id": "calendar",
  "title": "Календарь",
  "content": {
    "html": "<html><body><h1>Календарь</h1><p>Текст...</p></body></html>",
    "plain_text": "Календарь\n\nТекст статьи без HTML тегов...",
    "breadcrumbs": ["Платформа", "Базовые возможности"],
    "links": ["https://...", "https://..."]
  }
}
```

## Зачем нужно plain_text?

1. **Поиск по тексту** - легче искать в чистом тексте
2. **Анализ контента** - обработка текста без HTML
3. **Экспорт данных** - удобно экспортировать текст
4. **ML/AI обработка** - модели работают с чистым текстом
5. **Индексация** - быстрее индексировать текст без тегов

## Разница между html и plain_text:

- **html**: `<h1>Заголовок</h1><p>Текст параграфа</p>`
- **plain_text**: `Заголовок\n\nТекст параграфа`

