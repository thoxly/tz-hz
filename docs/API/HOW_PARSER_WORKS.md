# Как работает парсер

## Обзор

Парсер (`app/crawler/parser.py`) извлекает структурированные данные из HTML страниц документации ELMA365.

## Что делает парсер:

1. **Загружает HTML** страницы
2. **Парсит HTML** с помощью BeautifulSoup
3. **Извлекает данные:**
   - Заголовок страницы (title)
   - Breadcrumbs (навигационные крошки)
   - Основной текст (plain_text)
   - Все ссылки на странице
   - HTML структура

## Методы парсера:

### `extract_title(soup)`
Ищет заголовок в таком порядке:
1. `<h1>` тег
2. `<title>` тег
3. Meta тег `og:title`

### `extract_plain_text(soup)`
**Главный метод для извлечения текста!**

Что делает:
1. ✅ Удаляет навигацию, меню, футер, хедер
2. ✅ Находит основной контент (main, article, .content)
3. ✅ Извлекает текст с сохранением структуры:
   - Заголовки (h1-h6)
   - Параграфы (p)
   - Списки (ul/ol)
4. ✅ Очищает от лишних пробелов и переносов

### `extract_breadcrumbs(soup)`
Ищет breadcrumbs в:
- `<nav>` с классом breadcrumb
- Списки с классом breadcrumb
- JSON-LD структурированные данные

### `extract_links(soup, url)`
Находит все ссылки `<a href="...">` и преобразует их в абсолютные URL.

## Пример использования:

```python
from app.crawler.parser import HTMLParser

parser = HTMLParser("https://elma365.com")
parsed = parser.parse(html_content, url)

# Результат:
# {
#     'title': 'Календарь',
#     'breadcrumbs': ['Платформа', 'Базовые возможности'],
#     'section': 'platform',
#     'html': '<html>...</html>',
#     'plain_text': 'Как устроен календарь\n\nС помощью личного...',
#     'links': ['https://...', 'https://...']
# }
```

## Где хранится извлеченный текст:

1. **В базе данных:**
   - Поле `content->>'plain_text'` в таблице `docs`
   - Доступно через API: `GET /api/docs/plain-text`

2. **В JSON файлах:**
   - Сохраняется в `data/crawled/*.json`

## Как получить текст из БД:

### Через API:
```bash
# Все документы с plain_text
curl http://127.0.0.1:8000/api/docs/plain-text

# Конкретный документ
curl http://127.0.0.1:8000/api/docs/{doc_id}
```

### Через Python:
```python
from app.database import get_db
from app.database.models import Doc

async with get_db() as db:
    doc = await db.get(Doc, doc_id="calendar")
    plain_text = doc.content.get('plain_text')
    print(plain_text)
```

## Улучшения парсера:

Парсер автоматически:
- ✅ Удаляет навигацию и меню
- ✅ Извлекает только основной контент
- ✅ Сохраняет структуру (заголовки, параграфы, списки)
- ✅ Правильно обрабатывает UTF-8 кодировку

## Тестирование:

Запустите тест на конкретной странице:
```bash
python test_parser_example.py
```

Это создаст файл `parsed_text_example.txt` с извлеченным текстом.

