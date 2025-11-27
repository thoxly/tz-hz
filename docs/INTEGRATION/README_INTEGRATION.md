# Интеграция и автоматизация - Полное руководство

Система генерации архитектурных решений и технических заданий для ELMA365 поддерживает два способа автоматизации:

1. **n8n Workflows** - для автоматизации через визуальные сценарии
2. **Telegram Bot** - для удобного UI через мессенджер

## Быстрый старт

### n8n интеграция

1. Убедитесь, что API сервер запущен:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Импортируйте workflow из `N8N_INTEGRATION.md`

3. Настройте Telegram бота (если используете Telegram триггеры)

4. Запустите workflow и протестируйте

### Telegram Bot

1. Получите токен у [@BotFather](https://t.me/BotFather)

2. Добавьте в `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_BOT_ENABLED=true
   ```

3. Установите зависимости:
   ```bash
   pip install python-telegram-bot
   ```

4. Запустите бота:
   ```bash
   python run_telegram_bot.py
   ```

## Архитектура системы

```
┌─────────────────┐
│   Пользователь  │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
    ▼        ▼
┌────────┐ ┌──────────┐
│  n8n   │ │ Telegram │
│Workflow│ │   Bot    │
└───┬────┘ └────┬─────┘
    │          │
    └────┬─────┘
         │
    ┌────▼─────────────────────┐
    │   FastAPI Server         │
    │                          │
    │  ┌────────────────────┐ │
    │  │ Decision Engine    │ │
    │  │ (Агент-Архитектор) │ │
    │  └──────────┬─────────┘ │
    │             │           │
    │  ┌──────────▼─────────┐ │
    │  │ TS Generator       │ │
    │  │ (Генератор ТЗ)     │ │
    │  └──────────┬─────────┘ │
    │             │           │
    │  ┌──────────▼─────────┐ │
    │  │ TS Exporter       │ │
    │  │ (Экспорт файлов)  │ │
    │  └────────────────────┘ │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────┐
    │   PostgreSQL        │
    │   (docs, entities)  │
    └─────────────────────┘
```

## Пайплайны

### Пайплайн 1: Автогенерация архитектуры

```
Telegram/Webhook 
  → Decision Engine API
  → Сохранение в БД
  → Отправка пользователю
```

### Пайплайн 2: Автогенерация ТЗ

```
Архитектура (ID/JSON)
  → TS Generator API
  → TS Exporter API
  → Отправка файла пользователю
```

### Пайплайн 3: One-click TS

```
Текст задачи
  → Decision Engine
  → TS Generator
  → TS Exporter
  → Отправка файла
```

## API Endpoints

### Decision Engine
- `POST /api/decision-engine/design` - генерация архитектуры

### TS Generator
- `POST /api/ts/generate` - генерация ТЗ
- `POST /api/ts/generate/deterministic` - строгое ТЗ
- `POST /api/ts/generate/verbose` - читаемое ТЗ

### TS Exporter
- `POST /api/ts/export/pdf` - экспорт в PDF
- `POST /api/ts/export/docx` - экспорт в DOCX
- `POST /api/ts/export/html` - экспорт в HTML
- `POST /api/ts/export/markdown` - экспорт в Markdown

### MCP Server
- `GET /api/mcp/doc/{doc_id}` - получить документ
- `POST /api/mcp/entities/search` - поиск сущностей
- `POST /api/mcp/search` - полнотекстовый поиск

## Документация

- **N8N_INTEGRATION.md** - интеграция с n8n
- **TELEGRAM_BOT.md** - использование Telegram бота
- **TS_GENERATOR_API.md** - API генератора ТЗ
- **TS_EXPORT_API.md** - API экспорта файлов
- **DECISION_ENGINE_API.md** - API Decision Engine
- **MCP_API.md** - API MCP сервера

## Примеры использования

### Пример 1: n8n Workflow

См. `N8N_INTEGRATION.md` для полных примеров workflow.

### Пример 2: Telegram Bot

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Опишите задачу: "Нужен процесс согласования договоров"
4. Нажмите "Сгенерировать ТЗ"
5. Выберите формат (DOCX, PDF, HTML, Markdown)
6. Получите файл

### Пример 3: Прямой API вызов

```python
import requests

# 1. Создать архитектуру
response = requests.post(
    "http://localhost:8000/api/decision-engine/design",
    json={
        "title": "Согласование договора",
        "business_requirements": "Создать процесс согласования",
        "workflow_steps": ["Создание заявки", "Согласование", "Завершение"],
        "user_roles": ["Менеджер", "Директор"]
    }
)
architecture = response.json()

# 2. Экспортировать в DOCX
response = requests.post(
    "http://localhost:8000/api/ts/export/docx?mode=deterministic",
    json=architecture
)

with open("ts.docx", "wb") as f:
    f.write(response.content)
```

## Статус системы

✅ **Все компоненты готовы к использованию:**

- ✅ Data Layer (docs + entities)
- ✅ MCP Server (интерфейс к документации)
- ✅ Decision Engine (генерация архитектуры)
- ✅ TS Generator (генерация ТЗ)
- ✅ TS Exporter (экспорт файлов)
- ✅ n8n интеграция (документация и примеры)
- ✅ Telegram Bot (UI для пользователей)

## Следующие шаги

1. **Настройте n8n workflows** по документации
2. **Запустите Telegram бота** для удобного доступа
3. **Настройте сохранение истории** в PostgreSQL
4. **Добавьте уведомления** о статусе генерации
5. **Настройте мониторинг** и логирование

## Поддержка

При возникновении проблем:
1. Проверьте логи API сервера
2. Проверьте логи Telegram бота
3. Проверьте подключение к базе данных
4. Убедитесь, что все зависимости установлены

