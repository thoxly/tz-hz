#!/usr/bin/env python3
"""Проверка конфигурации бота перед запуском."""
import sys
from app.telegram_bot.config import telegram_settings

print("=" * 60)
print("Проверка конфигурации Telegram бота")
print("=" * 60)

# Проверка токена
token = telegram_settings.TELEGRAM_BOT_TOKEN
if not token or token == "your_bot_token_here":
    print("❌ TELEGRAM_BOT_TOKEN не установлен или имеет значение по умолчанию")
    print("   Получите токен у @BotFather и добавьте в .env файл")
    sys.exit(1)
else:
    print(f"✓ Token установлен: {token[:10]}...{token[-5:]}")

# Проверка enabled
if not telegram_settings.TELEGRAM_BOT_ENABLED:
    print("⚠️  TELEGRAM_BOT_ENABLED=false - бот отключен")
    print("   Установите TELEGRAM_BOT_ENABLED=true в .env файле")
    sys.exit(1)
else:
    print("✓ Bot enabled: True")

# Проверка библиотеки
try:
    import telegram
    print(f"✓ python-telegram-bot установлен (версия: {telegram.__version__})")
except ImportError:
    print("❌ python-telegram-bot не установлен")
    print("   Установите: pip install python-telegram-bot")
    sys.exit(1)

print("=" * 60)
print("✅ Все проверки пройдены! Бот готов к запуску.")
print("=" * 60)

