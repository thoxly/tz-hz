#!/usr/bin/env python3
"""Запуск Telegram бота."""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from app.telegram_bot.bot import TelegramBot
from app.telegram_bot.config import telegram_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота."""
    token = telegram_settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в переменных окружения или .env файле")
        logger.info("Получите токен у @BotFather в Telegram и добавьте в .env:")
        logger.info("TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)
    
    if not telegram_settings.TELEGRAM_BOT_ENABLED:
        logger.warning("Telegram бот отключен (TELEGRAM_BOT_ENABLED=false)")
        sys.exit(0)
    
    bot = TelegramBot(token)
    
    try:
        logger.info("Запуск Telegram бота...")
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")



