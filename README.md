# ELMA365 Technical Specification Generator

Система автоматической генерации технических заданий на основе бизнес-требований с использованием документации ELMA365.

## 🎯 Возможности

- **📚 Сбор документации** - Автоматический краулинг и нормализация документации ELMA365
- **🔍 MCP Server** - Интерфейс к документации для LLM (Model Context Protocol)
- **🏗️ Decision Engine** - Агент-Архитектор для генерации архитектурных решений
- **📝 TS Generator** - Генератор технических заданий в форматах Markdown, PDF, DOCX, HTML
- **🤖 Telegram Bot** - Удобный UI для пользователей
- **🔗 n8n Integration** - Готовые workflows для автоматизации

## 📁 Структура проекта

```
tz-hz/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI точка входа
│   ├── crawler/           # Краулер документации
│   ├── normalizer/        # Нормализация контента
│   ├── mcp/               # MCP Server
│   ├── decision_engine/   # Decision Engine (Агент-Архитектор)
│   ├── ts_generator/      # Генератор ТЗ
│   └── telegram_bot/      # Telegram бот
├── scripts/                # Утилитарные скрипты
├── tests/                  # Тесты
├── docs/                   # Документация
├── examples/               # Примеры
└── data/                   # Данные (не в git)
```

Подробная структура: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создать БД
python scripts/database/create_db.py

# Инициализировать таблицы
python scripts/database/init_tables.py
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/elma365_crawler
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_BOT_ENABLED=true
```

### 4. Запуск API сервера

```bash
uvicorn app.main:app --reload
```

API будет доступен на `http://localhost:8000`

### 5. Запуск Telegram бота (опционально)

```bash
python run_telegram_bot.py
```

## 📖 Документация

### API

- [MCP API](docs/API/MCP_API.md) - Интерфейс к документации
- [Decision Engine API](docs/API/DECISION_ENGINE_API.md) - Генерация архитектуры
- [TS Generator API](docs/API/TS_GENERATOR_API.md) - Генерация ТЗ
- [TS Export API](docs/API/TS_EXPORT_API.md) - Экспорт файлов

### Интеграция

- [n8n Integration](docs/INTEGRATION/N8N_INTEGRATION.md) - Автоматизация через n8n
- [Telegram Bot](docs/INTEGRATION/TELEGRAM_BOT.md) - Использование бота
- [Integration Guide](docs/INTEGRATION/README_INTEGRATION.md) - Общее руководство

### Настройка

- [Инструкция запуска бота](docs/SETUP/ИНСТРУКЦИЯ_ЗАПУСКА_БОТА.md)
- [PDF Export Fix](docs/SETUP/PDF_EXPORT_FIXED.md)

## 🔄 Полный пайплайн

```
Бизнес-требования
    ↓
Decision Engine (Агент-Архитектор)
    ↓
Architecture Solution (JSON)
    ↓
TS Generator
    ↓
Technical Specification (Markdown)
    ↓
TS Exporter
    ↓
PDF / DOCX / HTML файл
```

## 🎮 Использование

### Через Telegram бота

1. Откройте бота в Telegram
2. Отправьте описание задачи
3. Получите архитектурное решение
4. Нажмите "Сгенерировать ТЗ"
5. Выберите формат (PDF, DOCX, HTML, Markdown)
6. Получите готовое ТЗ

### Через API

```python
import requests

# 1. Создать архитектурное решение
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

with open("technical_specification.docx", "wb") as f:
    f.write(response.content)
```

### Через n8n

См. [N8N Integration](docs/INTEGRATION/N8N_INTEGRATION.md) для готовых workflows.

## 🧪 Тестирование

```bash
# Все тесты
pytest

# Юнит-тесты
pytest tests/unit/

# Интеграционные тесты
pytest tests/integration/
```

## 📊 Статус системы

✅ **Все компоненты готовы:**

- ✅ Data Layer (docs + entities)
- ✅ MCP Server (интерфейс к документации)
- ✅ Decision Engine (генерация архитектуры)
- ✅ TS Generator (генерация ТЗ)
- ✅ TS Exporter (PDF, DOCX, HTML, Markdown)
- ✅ Telegram Bot (UI для пользователей)
- ✅ n8n Integration (автоматизация)

## 🔧 Технологии

- **FastAPI** - Web framework
- **PostgreSQL** - База данных
- **SQLAlchemy** - ORM
- **BeautifulSoup** - Парсинг HTML
- **reportlab** - Генерация PDF
- **python-docx** - Генерация DOCX
- **python-telegram-bot** - Telegram бот
- **Alembic** - Миграции БД

## 📝 Лицензия

[Укажите лицензию]

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи API сервера
2. Проверьте подключение к базе данных
3. Убедитесь, что все зависимости установлены
4. См. документацию в папке `docs/`
