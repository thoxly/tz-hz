# Быстрый старт

## Запуск Telegram бота

### Вариант 1: Пошагово

1. **Активируйте виртуальное окружение:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Запустите бота:**
   ```bash
   python scripts/run_telegram_bot.py
   ```

### Вариант 2: Одной командой

```powershell
.\venv\Scripts\Activate.ps1; python scripts/run_telegram_bot.py
```

### Проверка

После запуска вы увидите:
```
Запуск Telegram бота...
```

Отправьте `/start` боту в Telegram для проверки.

## Запуск API сервера

```bash
uvicorn app.main:app --reload
```

API будет доступен на `http://localhost:8000`

## Настройка

Убедитесь, что в файле `.env` указаны:
- `TELEGRAM_BOT_TOKEN` - токен от @BotFather
- `TELEGRAM_BOT_ENABLED=true` - включить бота
- `DATABASE_URL` - строка подключения к PostgreSQL

Подробная инструкция: [docs/SETUP/ИНСТРУКЦИЯ_ЗАПУСКА_БОТА.md](docs/SETUP/ИНСТРУКЦИЯ_ЗАПУСКА_БОТА.md)



