# Интеграция с n8n - Автоматизация пайплайна

Руководство по созданию автоматизированных сценариев в n8n для генерации архитектурных решений и технических заданий.

## Предварительные требования

1. Установленный и запущенный API сервер: `uvicorn app.main:app --reload`
2. n8n установлен и доступен
3. Telegram бот (для Telegram триггеров) - опционально

## Сценарий 1: Автогенерация архитектуры из текстового запроса

### Описание
Пользователь отправляет текстовый запрос, система генерирует архитектурное решение и сохраняет его.

### Пайплайн n8n

#### Шаг 1: Telegram Trigger (или Webhook)
- **Тип:** Telegram Trigger / Webhook
- **Настройки:**
  - Для Telegram: подключите Telegram бота
  - Для Webhook: создайте webhook URL

#### Шаг 2: HTTP Request - Decision Engine
- **Метод:** POST
- **URL:** `http://localhost:8000/api/decision-engine/design`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (JSON):**
  ```json
  {
    "title": "{{ $json.message.text }}",
    "business_requirements": "{{ $json.message.text }}",
    "inputs": [],
    "outputs": [],
    "user_roles": [],
    "workflow_steps": [],
    "integration_targets": [],
    "ui_requirements": [],
    "constraints": []
  }
  ```
  Или более продвинутый вариант с парсингом:
  ```json
  {
    "title": "{{ $('Parse Text').item.json.title }}",
    "business_requirements": "{{ $json.message.text }}",
    "inputs": "{{ $('Parse Text').item.json.inputs }}",
    "outputs": "{{ $('Parse Text').item.json.outputs }}",
    "user_roles": "{{ $('Parse Text').item.json.roles }}",
    "workflow_steps": "{{ $('Parse Text').item.json.steps }}",
    "integration_targets": [],
    "ui_requirements": [],
    "constraints": []
  }
  ```

#### Шаг 3: Сохранение в PostgreSQL/Airtable/Notion
- **PostgreSQL:**
  - **Тип:** PostgreSQL
  - **Операция:** Insert
  - **Таблица:** `architectures` (создайте таблицу)
  - **Колонки:**
    - `id` - UUID
    - `user_id` - из Telegram
    - `architecture_json` - JSONB из ответа Decision Engine
    - `created_at` - timestamp

- **Airtable:**
  - **Тип:** Airtable
  - **Операция:** Create
  - **База:** ваша база
  - **Таблица:** Architectures

#### Шаг 4: Отправка черновика архитектуры
- **Тип:** Telegram / Send Message
- **Текст:**
  ```
  ✅ Архитектура сгенерирована!

  Типы решений: {{ $json.solution_type }}

  Уверенность: {{ $json.confidence * 100 }}%

  {{#if $json.process_design}}
  Процесс: {{ $json.process_design.process_name }}
  Шагов: {{ $json.process_design.steps.length }}
  {{/if}}

  {{#if $json.app_structure}}
  Приложение: {{ $json.app_structure.app_name }}
  Полей: {{ $json.app_structure.fields.length }}
  {{/if}}

  Нажмите /generate_ts для генерации ТЗ
  ```

### Пример JSON для тестирования
```json
{
  "title": "Согласование договора",
  "business_requirements": "Создать процесс согласования договоров с несколькими этапами",
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
```

---

## Сценарий 2: Автогенерация ТЗ

### Описание
Принимает архитектурное решение (или ID) и генерирует ТЗ в выбранном формате.

### Пайплайн n8n

#### Шаг 1: Webhook / Telegram Command
- **Тип:** Webhook / Telegram Command
- **Команда:** `/generate_ts` или `/ts`

#### Шаг 2: Получение архитектуры (если по ID)
- **Тип:** PostgreSQL / Airtable
- **Операция:** Get
- **ID:** из предыдущего шага или параметра

#### Шаг 3: HTTP Request - Генерация ТЗ
- **Метод:** POST
- **URL:** `http://localhost:8000/api/ts/generate/deterministic`
  или `http://localhost:8000/api/ts/generate/verbose`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:** Архитектура из шага 2 или предыдущего workflow

#### Шаг 4: HTTP Request - Экспорт в DOCX/PDF
- **Метод:** POST
- **URL:** `http://localhost:8000/api/ts/export/docx`
  или `http://localhost:8000/api/ts/export/pdf`
- **Query параметры:**
  - `mode=deterministic` или `mode=verbose`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body:** Та же архитектура

#### Шаг 5: Отправка файла пользователю
- **Тип:** Telegram / Send Document
- **Файл:** из ответа шага 4
- **Подпись:** "Техническое задание готово!"

### Альтернативный вариант: Выбор формата
Добавьте интерактивные кнопки в Telegram:
- Кнопка "PDF" → `/ts_pdf`
- Кнопка "DOCX" → `/ts_docx`
- Кнопка "HTML" → `/ts_html`

---

## Сценарий 3: "One-click TS" - Полный пайплайн

### Описание
Одна команда → готовое ТЗ. Полная автоматизация от текста до файла.

### Пайплайн n8n

#### Шаг 1: Telegram Trigger / Webhook
- **Тип:** Telegram Trigger
- **Текст:** пользовательский запрос

#### Шаг 2: HTTP Request - Decision Engine
- **Метод:** POST
- **URL:** `http://localhost:8000/api/decision-engine/design`
- **Body:** Парсинг текста в BusinessRequirements

#### Шаг 3: HTTP Request - Генерация ТЗ
- **Метод:** POST
- **URL:** `http://localhost:8000/api/ts/generate/deterministic`
- **Body:** Архитектура из шага 2

#### Шаг 4: HTTP Request - Экспорт в DOCX
- **Метод:** POST
- **URL:** `http://localhost:8000/api/ts/export/docx?mode=deterministic`
- **Body:** Архитектура из шага 2

#### Шаг 5: Сохранение в БД (опционально)
- **Тип:** PostgreSQL
- **Операция:** Insert
- **Таблица:** `technical_specifications`
- **Колонки:**
  - `id` - UUID
  - `user_id` - из Telegram
  - `architecture_json` - JSONB
  - `ts_markdown` - текст ТЗ
  - `file_path` - путь к файлу
  - `created_at` - timestamp

#### Шаг 6: Отправка файла пользователю
- **Тип:** Telegram / Send Document
- **Файл:** из шага 4
- **Подпись:** 
  ```
  ✅ Техническое задание готово!

  Типы решений: {{ $('HTTP Request - Decision Engine').item.json.solution_type }}

  Уверенность: {{ $('HTTP Request - Decision Engine').item.json.confidence * 100 }}%

  Файл сохранен в базе данных.
  ```

### Улучшенная версия с выбором формата

Добавьте после шага 3:

#### Шаг 3.5: Отправка кнопок выбора формата
- **Тип:** Telegram / Send Message
- **Текст:** "Выберите формат ТЗ:"
- **Inline Keyboard:**
  ```json
  [
    [
      {"text": "📄 DOCX", "callback_data": "format_docx"},
      {"text": "📄 PDF", "callback_data": "format_pdf"}
    ],
    [
      {"text": "🌐 HTML", "callback_data": "format_html"},
      {"text": "📝 Markdown", "callback_data": "format_markdown"}
    ]
  ]
  ```

#### Шаг 3.6: Обработка callback
- **Тип:** Telegram / Callback Query
- **Условие:** проверка `callback_data`
- **Действие:** переход к соответствующему экспорту

---

## SQL для создания таблиц в PostgreSQL

```sql
-- Таблица для сохранения архитектурных решений
CREATE TABLE IF NOT EXISTS architectures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT,
    user_name VARCHAR(255),
    title VARCHAR(500),
    architecture_json JSONB NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_architectures_user_id ON architectures(user_id);
CREATE INDEX idx_architectures_created_at ON architectures(created_at);

-- Таблица для сохранения технических заданий
CREATE TABLE IF NOT EXISTS technical_specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    architecture_id UUID REFERENCES architectures(id),
    user_id BIGINT,
    mode VARCHAR(20), -- deterministic или verbose
    format VARCHAR(10), -- pdf, docx, html, markdown
    ts_markdown TEXT,
    file_path VARCHAR(500),
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ts_architecture_id ON technical_specifications(architecture_id);
CREATE INDEX idx_ts_user_id ON technical_specifications(user_id);
CREATE INDEX idx_ts_created_at ON technical_specifications(created_at);
```

---

## Примеры n8n Workflow JSON

### Простой workflow: One-click TS

```json
{
  "name": "One-click TS Generator",
  "nodes": [
    {
      "name": "Telegram Trigger",
      "type": "n8n-nodes-base.telegramTrigger",
      "parameters": {}
    },
    {
      "name": "Decision Engine",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/api/decision-engine/design",
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify({\n  title: $json.message.text,\n  business_requirements: $json.message.text,\n  inputs: [],\n  outputs: [],\n  user_roles: [],\n  workflow_steps: [],\n  integration_targets: [],\n  ui_requirements: [],\n  constraints: []\n}) }}"
      }
    },
    {
      "name": "Generate TS",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/api/ts/generate/deterministic",
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify($json) }}"
      }
    },
    {
      "name": "Export DOCX",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/api/ts/export/docx?mode=deterministic",
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify($('Decision Engine').item.json) }}",
        "options": {
          "response": {
            "response": {
              "responseFormat": "file"
            }
          }
        }
      }
    },
    {
      "name": "Send Document",
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "operation": "sendDocument",
        "chatId": "={{ $('Telegram Trigger').item.json.message.chat.id }}",
        "binaryData": true,
        "file": "={{ $binary.data }}"
      }
    }
  ],
  "connections": {
    "Telegram Trigger": {
      "main": [[{"node": "Decision Engine"}]]
    },
    "Decision Engine": {
      "main": [[{"node": "Generate TS"}]]
    },
    "Generate TS": {
      "main": [[{"node": "Export DOCX"}]]
    },
    "Export DOCX": {
      "main": [[{"node": "Send Document"}]]
    }
  }
}
```

---

## Тестирование в n8n

1. **Импортируйте workflow** в n8n
2. **Настройте Telegram бота** (если используете Telegram)
3. **Проверьте URL API** - убедитесь, что сервер запущен
4. **Протестируйте каждый шаг** отдельно через "Execute Node"
5. **Запустите полный workflow** и проверьте результат

---

## Troubleshooting

### Проблема: API не отвечает
- Проверьте, что сервер запущен: `uvicorn app.main:app --reload`
- Проверьте URL в n8n: должен быть `http://localhost:8000` или ваш IP

### Проблема: Ошибка формата данных
- Убедитесь, что JSON правильно сформирован
- Проверьте структуру BusinessRequirements

### Проблема: Файл не отправляется
- Проверьте настройки "Response Format" в HTTP Request
- Убедитесь, что используется "file" формат для бинарных данных

---

## Дополнительные улучшения

1. **Парсинг текста** - используйте LLM для извлечения структурированных данных из текста
2. **Валидация** - добавьте проверку входных данных
3. **Уведомления** - отправляйте уведомления о статусе генерации
4. **История** - сохраняйте все запросы и результаты
5. **Шаблоны** - создайте шаблоны для часто используемых запросов

