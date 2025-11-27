# Структура проекта

Этот документ описывает структуру проекта ELMA365 Technical Specification Generator.

## Общая структура

```
tz-hz/
├── app/                          # Основное приложение
│   ├── main.py                   # Точка входа FastAPI
│   ├── config.py                 # Конфигурация
│   ├── utils.py                  # Утилиты
│   ├── api/                      # API endpoints
│   │   └── routes.py             # Основные маршруты
│   ├── crawler/                  # Модуль краулера
│   │   ├── crawler.py            # Логика краулинга
│   │   ├── parser.py             # Парсинг HTML
│   │   └── storage.py            # Сохранение данных
│   ├── database/                 # Работа с БД
│   │   ├── database.py           # Подключение к БД
│   │   └── models.py             # SQLAlchemy модели
│   ├── normalizer/               # Нормализация контента
│   │   ├── normalizer.py          # Основная логика
│   │   ├── extractors.py         # Извлечение блоков
│   │   └── entity_extractor.py   # Извлечение сущностей
│   ├── mcp/                      # MCP Server
│   │   ├── tools.py              # MCP инструменты
│   │   └── routes.py             # MCP API routes
│   ├── decision_engine/          # Decision Engine (Агент-Архитектор)
│   │   ├── engine.py             # Основной движок
│   │   ├── analyzer.py           # Анализатор требований
│   │   ├── mcp_client.py         # Клиент MCP
│   │   ├── models.py             # Модели данных
│   │   └── routes.py             # API routes
│   ├── ts_generator/             # Генератор ТЗ
│   │   ├── generator.py          # Генератор Markdown
│   │   ├── exporter.py          # Экспорт в файлы
│   │   ├── pdf_exporter.py       # Экспорт в PDF (кириллица)
│   │   └── routes.py             # API routes
│   └── telegram_bot/             # Telegram бот
│       ├── bot.py                # Логика бота
│       └── config.py             # Конфигурация бота
│
├── scripts/                       # Утилитарные скрипты
│   ├── database/                 # Скрипты для БД
│   │   ├── create_db.py          # Создание БД
│   │   └── init_tables.py        # Инициализация таблиц
│   └── utils/                    # Вспомогательные скрипты
│       ├── add_urls.py          # Добавление URL
│       ├── crawl_all.py          # Полный краулинг
│       └── update_docs.py         # Обновление документов
│
├── tests/                         # Тесты
│   ├── unit/                     # Юнит-тесты
│   │   ├── test_crawler.py
│   │   ├── test_normalizer.py
│   │   └── test_parser.py
│   └── integration/              # Интеграционные тесты
│       ├── test_api.py
│       ├── test_mcp.py
│       ├── test_decision_engine.py
│       └── test_ts_generator.py
│
├── docs/                          # Документация
│   ├── API/                      # API документация
│   │   ├── MCP_API.md
│   │   ├── DECISION_ENGINE_API.md
│   │   ├── TS_GENERATOR_API.md
│   │   └── TS_EXPORT_API.md
│   ├── INTEGRATION/              # Интеграция
│   │   ├── N8N_INTEGRATION.md
│   │   ├── TELEGRAM_BOT.md
│   │   └── README_INTEGRATION.md
│   └── SETUP/                    # Настройка
│       └── ИНСТРУКЦИЯ_ЗАПУСКА_БОТА.md
│
├── examples/                      # Примеры
│   ├── data/                     # Примеры данных
│   │   ├── architecture_example.json
│   │   ├── ts_example.md
│   │   └── blocks_example.json
│   └── scripts/                  # Примеры скриптов
│       └── add_urls_example.py
│
├── data/                          # Данные (не в git)
│   └── crawled/                  # Скачанные страницы
│
├── alembic/                       # Миграции БД
│   ├── versions/
│   └── env.py
│
├── .env                           # Переменные окружения (не в git)
├── .env.example                   # Пример .env
├── requirements.txt               # Зависимости
├── README.md                      # Основной README
├── PROJECT_STRUCTURE.md           # Этот файл
│
└── run_*.py                       # Скрипты запуска
    ├── run_telegram_bot.py        # Запуск Telegram бота
    └── run_bot.py                 # Альтернативный запуск бота
```

## Описание компонентов

### app/ - Основное приложение

- **main.py** - FastAPI приложение, точка входа
- **config.py** - Конфигурация через pydantic-settings
- **utils.py** - Утилитарные функции

#### app/api/ - API endpoints
- Базовые маршруты для краулинга и нормализации

#### app/crawler/ - Краулер
- Рекурсивный обход страниц
- Парсинг HTML
- Сохранение в БД и файлы

#### app/normalizer/ - Нормализация
- Преобразование HTML в структурированные блоки
- Извлечение сущностей

#### app/mcp/ - MCP Server
- Интерфейс к документации для LLM
- Поиск документов и сущностей

#### app/decision_engine/ - Decision Engine
- Анализ бизнес-требований
- Генерация архитектурных решений

#### app/ts_generator/ - Генератор ТЗ
- Генерация технических заданий
- Экспорт в PDF, DOCX, HTML, Markdown

#### app/telegram_bot/ - Telegram бот
- UI для пользователей
- Интеграция с Decision Engine и TS Generator

### scripts/ - Утилитарные скрипты

- Скрипты для работы с БД
- Вспомогательные утилиты

### tests/ - Тесты

- Юнит-тесты компонентов
- Интеграционные тесты API

### docs/ - Документация

- API документация
- Инструкции по интеграции
- Руководства по настройке

### examples/ - Примеры

- Примеры данных
- Примеры использования

## Запуск

### API сервер
```bash
uvicorn app.main:app --reload
```

### Telegram бот
```bash
python run_telegram_bot.py
```

## Переменные окружения

См. `.env.example` для списка переменных.

