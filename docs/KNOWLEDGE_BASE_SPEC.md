# Спецификация базы знаний ELMA365

**Версия:** v1.0  
**Дата:** 2025-01-30  
**Аудитория:** Backend разработчики, разработчики агентов, разработчики MCP инструментов, разработчики RAG систем

---

## 1. Общий подход

Документация ELMA365 хранится в PostgreSQL в нормализованном структурированном виде (JSONB). Каждая статья представляет собой отдельный документ с уникальным `normalized_path`, позволяющим выполнять внутренние переходы по ссылкам. Навигация между статьями основана на сопоставлении относительных ссылок внутри контента с полем `normalized_path`.

### Ключевые принципы

- **Детерминированная навигация**: Все ссылки нормализуются по единому алгоритму
- **Структурированное хранение**: Контент разбит на семантические блоки с метаданными
- **Связность статей**: Поддержка двунаправленной навигации через `outgoing_links`
- **Готовность к RAG/MCP**: Блоки содержат `token_count` и `semantic_role` для эффективного поиска

---

## 2. Структура таблицы docs

### Обязательные поля

#### Основные ключи документа

- **`id`** (Integer, PK) - Внутренний числовой идентификатор (автоинкремент)
- **`doc_id`** (String, UNIQUE, NOT NULL, INDEX) - Стабильный идентификатор документа
  - Извлекается из URL (например, `how_to_bind_app_to_proccess` из `/help/platform/how_to_bind_app_to_proccess.html`)
  - Fallback на UUID если паттерн не найден
- **`url`** (Text, UNIQUE, NOT NULL, INDEX) - Оригинальный URL статьи
- **`normalized_path`** (Text, UNIQUE, nullable, INDEX) - Нормализованный путь (ключ внутренней навигации)

#### Контент

- **`title`** (Text, nullable) - Заголовок статьи
- **`section`** (Text, nullable) - Сегмент категории (из breadcrumbs + URL segment)
- **`content`** (JSONB, nullable) - Структурированный контент с блоками (см. раздел 3)

#### Служебные

- **`created_at`** (DateTime, timezone=True) - Время создания записи (server_default: now())
- **`last_crawled`** (DateTime, timezone=True) - Время последнего обновления (server_default: now(), onupdate: now())

#### Индексные поля

- **`outgoing_links`** (ARRAY(Text), nullable) - Массив нормализованных путей, на которые ссылается документ
  - Индекс: GIN индекс для эффективных запросов `ANY(outgoing_links)`

### Индексы

```sql
CREATE UNIQUE INDEX ix_docs_doc_id ON docs(doc_id);
CREATE UNIQUE INDEX ix_docs_url ON docs(url);
CREATE UNIQUE INDEX ix_docs_normalized_path ON docs(normalized_path);
CREATE INDEX ix_docs_outgoing_links_gin ON docs USING GIN(outgoing_links);
```

### Пример normalized_path

```
Исходный URL: https://elma365.com/ru/help/business_solutions/create-plan.html
normalized_path: business_solutions/create-plan.html
```

---

## 3. Формат нормализованного контента (JSONB)

Структура поля `content`:

```json
{
  "blocks": [...],
  "metadata": {...}
}
```

### Структура metadata

```json
{
  "title": "Название статьи",
  "breadcrumbs": ["Платформа", "API"],
  "extracted_at": "2025-01-30T10:00:00",
  "special_blocks_count": 1,
  "word_count": 1250,
  "headers": [
    {
      "level": 1,
      "text": "Основной заголовок",
      "id": "osnovnoj-zagolovok"
    }
  ],
  "images_count": 3,
  "source_url": "https://elma365.com/ru/help/platform/api.html"
}
```

### Типы блоков

Блоки могут быть следующих типов:
- `header` - Заголовок (h1-h6)
- `paragraph` - Параграф (может содержать ссылки)
- `list` - Список (упорядоченный или нет)
- `code_block` - Блок кода
- `table` - Таблица
- `special_block` - Специальный блок (пример, предупреждение и т.д.)
- `image` - Изображение

### Блок paragraph с ссылками

**Структура:**

```json
{
  "type": "paragraph",
  "children": [
    "Текст перед ссылкой ",
    {
      "type": "link",
      "text": "Создать лид",
      "target": "/crm/create-lead.html"
    },
    "."
  ],
  "token_count": 42,
  "semantic_role": "capability"
}
```

**Правила:**

- `paragraph` может содержать массив `children` (текст + link-объекты)
- `children` - массив строк и объектов `link`
- `link` содержит:
  - `type`: `"link"`
  - `text`: видимый текст ссылки
  - `target`: относительный путь (например, `/crm/create-lead.html`)
- Каждую ссылку надо нормализовывать перед навигацией через `normalize_path()`
- `token_count` - количество токенов в блоке (для RAG, опционально)
- `semantic_role` - семантическая роль (см. раздел 3.4)

**Пример paragraph без ссылок:**

```json
{
  "type": "paragraph",
  "text": "Простой текст параграфа без ссылок",
  "token_count": 15,
  "semantic_role": "definition"
}
```

### Блок list с ссылками

**Структура:**

```json
{
  "type": "list",
  "ordered": false,
  "items": [
    "Простой текстовый элемент списка",
    [
      "Текст перед ссылкой ",
      {
        "type": "link",
        "text": "ссылка на виджет",
        "target": "/platform/widget.html"
      },
      " продолжение текста"
    ],
    "Еще один простой элемент"
  ],
  "token_count": 67,
  "semantic_role": "list_item"
}
```

**Правила:**

- `items` - массив строк или массивов `children` (для элементов со ссылками)
- Если элемент содержит ссылки, он представлен как массив `children`
- Если элемент без ссылок, он представлен как строка

### Блок header

```json
{
  "type": "header",
  "level": 2,
  "text": "Заголовок раздела",
  "id": "zagolovok-razdela",
  "token_count": 3,
  "semantic_role": "section"
}
```

### Блок code_block

```json
{
  "type": "code_block",
  "language": "python",
  "code": "def example():\n    return True",
  "token_count": 12
}
```

### Блок table

```json
{
  "type": "table",
  "header": ["Колонка 1", "Колонка 2"],
  "rows": [
    ["Значение 1", "Значение 2"],
    ["Значение 3", "Значение 4"]
  ],
  "token_count": 25
}
```

### Блок special_block

```json
{
  "type": "special_block",
  "kind": "Пример",
  "heading": "Пример",
  "text": "Текст примера с описанием...",
  "token_count": 45,
  "semantic_role": "example"
}
```

### Блок image

```json
{
  "type": "image",
  "src": "https://elma365.com/images/example.png",
  "alt": "Описание изображения"
}
```

### Семантические роли (semantic_role)

Семантическая роль присваивается блокам для улучшения поиска и понимания контекста:

- **`section`** - Заголовок раздела (header)
- **`definition`** - Определение термина (параграф с паттернами "— это", "представляет собой", "является")
- **`capability`** - Описание возможностей (параграф с паттернами "позволяет", "можно", "возможность")
- **`configuration`** - Инструкция по настройке (параграф с паттернами "настройте", "перейдите в раздел")
- **`example`** - Пример использования (special_block с kind="Пример")
- **`warning`** - Предупреждение (special_block с kind="Внимание")
- **`important`** - Важная информация (special_block с kind="Важно")
- **`list_item`** - Элемент списка

**Правила присвоения:**

- `semantic_role` добавляется автоматически при нормализации через `_add_semantic_roles()`
- Не все блоки имеют `semantic_role` (опциональное поле)
- Используется для фильтрации в RAG и улучшения релевантности поиска

### Token count

- **`token_count`** - количество токенов в блоке (для RAG систем)
- Вычисляется через tokenizer (например, tiktoken)
- Добавляется автоматически при нормализации через `_add_token_counts()`
- Используется для:
  - Ограничения контекста в RAG запросах
  - Оценки размера блока
  - Оптимизации индексации

---

## 4. Функция normalize_path()

### Алгоритм нормализации

**Функция:** `app.utils.normalize_path(url: str) -> str`

**Правила:**

1. Удалить домен (https://elma365.com)
2. Удалить ведущий `/{lang}/help/` (например, `/ru/help/`, `/en/help/`)
3. Привести к нижнему регистру
4. Удалить query параметры (`?query`) и anchors (`#anchors`)
5. Удалить ведущие и дублирующиеся `/`

**Реализация:**

```python
def normalize_path(url: str) -> str:
    """
    Normalize URL path for navigation and linking.
    
    Rules:
    1. Remove domain: https://elma365.com/ru/help/... -> /ru/help/...
    2. Remove leading /{lang}/help prefix: /ru/help/business_solutions/... -> business_solutions/...
    3. Convert to lowercase
    4. Remove query parameters (? and #)
    
    Example:
        https://elma365.com/ru/help/business_solutions/create-plan.html?param=value#anchor
        -> business_solutions/create-plan.html
    """
    # Parse URL to extract path
    parsed = urlparse(url)
    path = parsed.path
    
    # Remove leading /{lang}/help/ pattern (e.g., /ru/help/, /en/help/)
    # Pattern: /{lang}/help/... or /help/...
    if '/help/' in path:
        help_index = path.find('/help/')
        if help_index != -1:
            # Get path after /help/
            path = path[help_index + len('/help/'):]
    
    # Remove leading and trailing slashes
    path = path.strip('/')
    
    # Convert to lowercase
    path = path.lower()
    
    # Return normalized path (already removed query and fragment via urlparse)
    return path
```

### Таблица соответствия

| Исходная ссылка | normalized_path |
|----------------|-----------------|
| `/crm/create-lead.html` | `crm/create-lead.html` |
| `../crm/create-lead.html` | `crm/create-lead.html` |
| `https://elma365.com/ru/help/crm/create-lead.html` | `crm/create-lead.html` |
| `https://elma365.com/ru/help/crm/create-lead.html?param=value#anchor` | `crm/create-lead.html` |
| `/ru/help/platform/widget.html` | `platform/widget.html` |
| `https://elma365.com/en/help/api/endpoints.html` | `api/endpoints.html` |
| `/help/business_solutions/create-plan.html` | `business_solutions/create-plan.html` |

**Важно:**

- Все ссылки должны нормализовываться через эту функцию перед сохранением в `outgoing_links`
- При навигации по ссылке из блока `link.target` также применяется `normalize_path()`
- Результат всегда в нижнем регистре и без ведущих/завершающих слешей

---

## 5. Правила внутренней навигации

### Как найти статью по ссылке

**Алгоритм:**

1. Извлечь `target` из блока `link` в `children`:
   ```python
   link_target = link_block.get('target')  # например, "/crm/create-lead.html"
   ```

2. Применить `normalize_path(target)`:
   ```python
   from app.utils import normalize_path
   normalized = normalize_path(link_target)  # "crm/create-lead.html"
   ```

3. Выполнить SQL запрос:
   ```sql
   SELECT * FROM docs
   WHERE normalized_path = :normalized_path
   LIMIT 1;
   ```

**Пример на Python (SQLAlchemy):**

```python
from sqlalchemy import select
from app.database.models import Doc
from app.utils import normalize_path

async def find_doc_by_link(link_target: str, db_session: AsyncSession) -> Optional[Doc]:
    """Найти документ по ссылке из блока link."""
    normalized = normalize_path(link_target)
    
    result = await db_session.execute(
        select(Doc).where(Doc.normalized_path == normalized)
    )
    return result.scalar_one_or_none()
```

### Обработка отсутствующих статей

**Правила:**

- Логировать как `broken_link` (не падать при загрузке документа)
- Опционально: хранить таблицу `link_errors` для отслеживания битых ссылок

**Пример обработки:**

```python
import logging

logger = logging.getLogger(__name__)

async def resolve_link(link_target: str, source_doc_id: str, db_session: AsyncSession):
    """Разрешить ссылку на документ."""
    normalized = normalize_path(link_target)
    doc = await find_doc_by_link(link_target, db_session)
    
    if not doc:
        logger.warning(
            f"Broken link in doc {source_doc_id}: "
            f"target={link_target}, normalized={normalized}"
        )
        # Опционально: сохранить в link_errors
        return None
    
    return doc
```

### Валидная ссылка

**Критерии валидности:**

- ✅ Только `.html` файлы
- ✅ Относительные пути (начинающиеся с `/`)
- ✅ Абсолютные URL с доменом elma365.com

**Исключения (не валидные):**

- ❌ Внешние домены (не elma365.com)
- ❌ `mailto:` и `tel:` ссылки
- ❌ Дивные пути (`/#/...`)
- ❌ Якоря (`#anchor` без пути)
- ❌ JavaScript ссылки (`javascript:`)

**Функция проверки:**

```python
def is_valid_help_url(url: str, base_url: str) -> bool:
    """
    Check if URL is a valid help documentation URL.
    Supports both /help/ and /{lang}/help/ patterns (e.g., /ru/help/, /en/help/).
    """
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    
    # Must be same domain
    if parsed.netloc and parsed.netloc != base_parsed.netloc:
        return False
    
    path = parsed.path
    
    # Must be under /help/ path (with or without language prefix)
    if '/help/' not in path:
        return False
    
    # Extract the part after /help/
    help_index = path.find('/help/')
    if help_index == -1:
        return False
    
    path_after_help = path[help_index + len('/help/'):]
    
    # Skip empty paths and root paths
    if not path_after_help or path_after_help == '/':
        return False
    
    # Should be HTML page (ends with .html)
    if path.endswith('.html'):
        return True
    
    # Also accept paths that don't end with /
    if not path.endswith('/'):
        if path_after_help and len(path_after_help.strip('/')) > 0:
            return True
    
    return False
```

---

## 6. outgoing_links

### Хранение

- **Поле:** `outgoing_links` (ARRAY(Text), nullable)
- **Формат:** массив нормализованных путей
- **Пример:** `['crm/create-lead.html', 'platform/widget.html']`
- **Индекс:** GIN индекс для эффективных запросов

### Заполнение

**Функция:** `app.utils.extract_outgoing_links(blocks: List[Dict]) -> List[str]`

**Алгоритм:**

1. Рекурсивно обойти все блоки в `content.blocks`
2. Извлечь все объекты `link` из `children` параграфов и списков
3. Нормализовать каждый `target` через `normalize_path()`
4. Вернуть отсортированный список уникальных путей

**Реализация:**

```python
def extract_outgoing_links(blocks: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all outgoing links from normalized blocks and return as list of normalized paths.
    
    Args:
        blocks: List of normalized blocks (from content.blocks)
    
    Returns:
        List of normalized paths (e.g., ['crm/create-lead.html', 'platform/widget.html'])
    """
    outgoing_links = set()  # Use set to avoid duplicates
    
    def extract_from_block(block: Dict[str, Any]):
        """Recursively extract links from a block."""
        block_type = block.get('type')
        
        if block_type == 'paragraph' and 'children' in block:
            # Extract links from children array
            for child in block.get('children', []):
                if isinstance(child, dict) and child.get('type') == 'link':
                    target = child.get('target', '')
                    if target:
                        # Normalize the target URL
                        normalized = normalize_path(target)
                        if normalized:  # Only add non-empty normalized paths
                            outgoing_links.add(normalized)
        
        elif block_type == 'list' and 'items' in block:
            # Extract links from list items
            for item in block.get('items', []):
                if isinstance(item, list):
                    # Item is a children array
                    for child in item:
                        if isinstance(child, dict) and child.get('type') == 'link':
                            target = child.get('target', '')
                            if target:
                                normalized = normalize_path(target)
                                if normalized:
                                    outgoing_links.add(normalized)
    
    # Process all blocks
    for block in blocks:
        extract_from_block(block)
    
    # Return as sorted list for consistency
    return sorted(list(outgoing_links))
```

**Обновление при нормализации:**

```python
# В процессе нормализации документа
normalizer = Normalizer()
normalized = normalizer.normalize(html, title=title, breadcrumbs=breadcrumbs)

# Извлечь outgoing_links
from app.utils import extract_outgoing_links
if 'blocks' in normalized:
    doc.outgoing_links = extract_outgoing_links(normalized['blocks'])
```

### Использование

#### Построение графа документации

```sql
-- Получить все документы с их исходящими ссылками
SELECT 
    doc_id,
    normalized_path,
    outgoing_links
FROM docs
WHERE outgoing_links IS NOT NULL;
```

#### Навигация в обе стороны

**Найти все статьи, которые ссылаются на X:**

```sql
SELECT 
    doc_id,
    normalized_path,
    title
FROM docs
WHERE 'crm/create-lead.html' = ANY(outgoing_links);
```

**Найти все статьи, на которые ссылается X:**

```sql
SELECT 
    doc_id,
    normalized_path,
    title
FROM docs
WHERE normalized_path = ANY(
    SELECT unnest(outgoing_links)
    FROM docs
    WHERE doc_id = 'source_doc_id'
);
```

#### Построение Knowledge Graph

```python
async def build_documentation_graph(db_session: AsyncSession) -> Dict[str, List[str]]:
    """Построить граф документации: doc_id -> [ссылающиеся doc_id]."""
    graph = {}
    
    # Получить все документы с outgoing_links
    result = await db_session.execute(
        select(Doc).where(Doc.outgoing_links.isnot(None))
    )
    docs = result.scalars().all()
    
    for doc in docs:
        graph[doc.doc_id] = []
        for target_path in doc.outgoing_links:
            # Найти doc_id по normalized_path
            target_doc = await db_session.execute(
                select(Doc).where(Doc.normalized_path == target_path)
            )
            target = target_doc.scalar_one_or_none()
            if target:
                graph[doc.doc_id].append(target.doc_id)
    
    return graph
```

---

## 7. Проверка ссылочной целостности

### Алгоритм валидации

**Шаги:**

1. Извлечь все `links` из всех `docs`
2. Применить `normalize_path()` для каждого
3. Проверить `EXISTS normalized_path` в таблице `docs`
4. Если отсутствует → `broken link`

### SQL запросы для проверки

#### Найти все битые ссылки

```sql
SELECT 
    d1.doc_id,
    d1.normalized_path as source_path,
    d1.title as source_title,
    unnest(d1.outgoing_links) as broken_target_path
FROM docs d1
WHERE d1.outgoing_links IS NOT NULL
  AND array_length(d1.outgoing_links, 1) > 0
  AND NOT EXISTS (
    SELECT 1 
    FROM docs d2
    WHERE d2.normalized_path = unnest(d1.outgoing_links)
  )
ORDER BY d1.doc_id;
```

#### Статистика битых ссылок

```sql
SELECT 
    COUNT(DISTINCT d1.doc_id) as docs_with_broken_links,
    COUNT(*) as total_broken_links
FROM docs d1
WHERE d1.outgoing_links IS NOT NULL
  AND EXISTS (
    SELECT 1
    FROM unnest(d1.outgoing_links) AS link_path
    WHERE NOT EXISTS (
      SELECT 1 FROM docs d2 WHERE d2.normalized_path = link_path
    )
  );
```

#### Найти документы без исходящих ссылок

```sql
SELECT 
    doc_id,
    normalized_path,
    title
FROM docs
WHERE outgoing_links IS NULL 
   OR array_length(outgoing_links, 1) IS NULL;
```

### Python инструмент для валидации

```python
import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Doc
from app.utils import normalize_path

logger = logging.getLogger(__name__)

async def validate_link_integrity(db_session: AsyncSession) -> Dict:
    """
    Проверить целостность всех ссылок в документации.
    
    Returns:
        {
            'total_docs': int,
            'docs_with_links': int,
            'total_links': int,
            'broken_links': int,
            'broken_links_list': List[Dict]
        }
    """
    # Получить все документы с outgoing_links
    result = await db_session.execute(
        select(Doc).where(Doc.outgoing_links.isnot(None))
    )
    docs = result.scalars().all()
    
    total_docs = await db_session.scalar(
        select(func.count(Doc.id))
    )
    
    broken_links = []
    total_links = 0
    
    for doc in docs:
        if not doc.outgoing_links:
            continue
        
        for target_path in doc.outgoing_links:
            total_links += 1
            # Проверить существование целевого документа
            target_result = await db_session.execute(
                select(Doc).where(Doc.normalized_path == target_path)
            )
            target_doc = target_result.scalar_one_or_none()
            
            if not target_doc:
                broken_links.append({
                    'source_doc_id': doc.doc_id,
                    'source_path': doc.normalized_path,
                    'source_title': doc.title,
                    'broken_target_path': target_path
                })
                logger.warning(
                    f"Broken link: {doc.doc_id} -> {target_path}"
                )
    
    return {
        'total_docs': total_docs,
        'docs_with_links': len(docs),
        'total_links': total_links,
        'broken_links': len(broken_links),
        'broken_links_list': broken_links
    }
```

### Сценарии использования

#### 1. Периодическая проверка crawler'ом

```python
# В cron job или scheduled task
async def scheduled_link_validation():
    async with get_session_factory() as db_session:
        result = await validate_link_integrity(db_session)
        if result['broken_links'] > 0:
            # Отправить уведомление
            send_alert(f"Found {result['broken_links']} broken links")
```

#### 2. Инструмент для разработчика

```python
# CLI команда
async def cli_validate_links():
    async with get_session_factory() as db_session:
        result = await validate_link_integrity(db_session)
        print(f"Total docs: {result['total_docs']}")
        print(f"Docs with links: {result['docs_with_links']}")
        print(f"Total links: {result['total_links']}")
        print(f"Broken links: {result['broken_links']}")
        
        if result['broken_links_list']:
            print("\nBroken links:")
            for link in result['broken_links_list']:
                print(f"  {link['source_doc_id']} -> {link['broken_target_path']}")
```

#### 3. Этап CI/CD

```python
# В pytest или другом тесте
async def test_link_integrity(db_session: AsyncSession):
    """Проверить целостность ссылок в тестах."""
    result = await validate_link_integrity(db_session)
    
    # Допускаем небольшой процент битых ссылок (например, из-за внешних ссылок)
    broken_ratio = result['broken_links'] / result['total_links'] if result['total_links'] > 0 else 0
    
    assert broken_ratio < 0.05, f"Too many broken links: {broken_ratio:.2%}"
```

### Опциональная таблица link_errors

Для отслеживания истории битых ссылок можно создать таблицу:

```sql
CREATE TABLE link_errors (
    id SERIAL PRIMARY KEY,
    source_doc_id VARCHAR NOT NULL,
    broken_target_path TEXT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (source_doc_id) REFERENCES docs(doc_id)
);

CREATE INDEX ix_link_errors_source_doc_id ON link_errors(source_doc_id);
CREATE INDEX ix_link_errors_resolved_at ON link_errors(resolved_at);
```

---

## 8. Версия документа и место хранения

### Место хранения

**Файл:** `/docs/KNOWLEDGE_BASE_SPEC.md`

### Аудитория

- **Backend разработчики** - работа с БД, нормализация, навигация
- **Разработчики агентов** (ProcessExtractor, ArchitectAgent, ScopeAgent) - использование документации через MCP
- **Разработчики MCP инструментов** - понимание структуры данных для инструментов поиска
- **Разработчики RAG систем** - использование `token_count` и `semantic_role` для индексации

### Версия

**Текущая версия:** v1.0  
**Дата создания:** 2025-01-30

### Процесс изменений

1. **Изменения вносятся через Pull Request**
   - Обязательна проверка кода ревьюерами
   - Обязательна проверка актуальности примеров

2. **При изменении структуры БД:**
   - Создать миграцию Alembic
   - Обновить раздел 2 (Структура таблицы docs)
   - Обновить примеры в разделе 3

3. **При изменении алгоритма нормализации:**
   - Обновить раздел 4 (Функция normalize_path)
   - Обновить таблицу соответствия
   - Обновить все примеры, использующие нормализацию

4. **При добавлении новых типов блоков:**
   - Обновить раздел 3 (Формат нормализованного контента)
   - Добавить примеры новых блоков
   - Обновить функцию `extract_outgoing_links` если необходимо

5. **Версионирование:**
   - При значительных изменениях увеличить версию (v1.1, v2.0)
   - Указать дату изменения
   - Добавить changelog в конец документа

---

## Приложение A: Полный пример документа

```json
{
  "id": 1,
  "doc_id": "create-lead",
  "url": "https://elma365.com/ru/help/crm/create-lead.html",
  "normalized_path": "crm/create-lead.html",
  "title": "Создание лида",
  "section": "CRM / Лиды",
  "outgoing_links": [
    "crm/leads-list.html",
    "platform/widget.html",
    "business_solutions/create-plan.html"
  ],
  "content": {
    "blocks": [
      {
        "type": "header",
        "level": 1,
        "text": "Создание лида",
        "id": "sozdanie-lida",
        "token_count": 3,
        "semantic_role": "section"
      },
      {
        "type": "paragraph",
        "children": [
          "Лид — это ",
          {
            "type": "link",
            "text": "потенциальный клиент",
            "target": "/crm/leads-list.html"
          },
          ", который может стать покупателем."
        ],
        "token_count": 12,
        "semantic_role": "definition"
      },
      {
        "type": "paragraph",
        "children": [
          "Система позволяет ",
          {
            "type": "link",
            "text": "создать лид",
            "target": "/crm/create-lead.html"
          },
          " несколькими способами."
        ],
        "token_count": 15,
        "semantic_role": "capability"
      },
      {
        "type": "list",
        "ordered": false,
        "items": [
          [
            "Через ",
            {
              "type": "link",
              "text": "виджет на сайте",
              "target": "/platform/widget.html"
            }
          ],
          "Вручную в интерфейсе",
          "Импорт из файла"
        ],
        "token_count": 25,
        "semantic_role": "list_item"
      },
      {
        "type": "special_block",
        "kind": "Пример",
        "heading": "Пример",
        "text": "Пример создания лида через API...",
        "token_count": 45,
        "semantic_role": "example"
      },
      {
        "type": "code_block",
        "language": "python",
        "code": "def create_lead(name, phone):\n    return {'name': name, 'phone': phone}",
        "token_count": 20
      }
    ],
    "metadata": {
      "title": "Создание лида",
      "breadcrumbs": ["CRM", "Лиды"],
      "extracted_at": "2025-01-30T10:00:00",
      "special_blocks_count": 1,
      "word_count": 250,
      "headers": [
        {
          "level": 1,
          "text": "Создание лида",
          "id": "sozdanie-lida"
        }
      ],
      "images_count": 0,
      "source_url": "https://elma365.com/ru/help/crm/create-lead.html"
    }
  },
  "created_at": "2025-01-30T09:00:00+00:00",
  "last_crawled": "2025-01-30T10:00:00+00:00"
}
```

---

## Приложение B: Changelog

### v1.0 (2025-01-30)

- Первая версия спецификации
- Описание структуры таблицы docs
- Формат нормализованного контента (JSONB)
- Функция normalize_path()
- Правила внутренней навигации
- outgoing_links поле
- Проверка ссылочной целостности

