#!/usr/bin/env python3
"""Простой скрипт для запуска Telegram бота с подробным выводом."""
import asyncio
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота."""
    try:
        logger.info("=" * 60)
        logger.info("Запуск Telegram бота")
        logger.info("=" * 60)
        
        # Проверка конфигурации
        from app.telegram_bot.config import telegram_settings
        
        token = telegram_settings.TELEGRAM_BOT_TOKEN
        enabled = telegram_settings.TELEGRAM_BOT_ENABLED
        
        logger.info(f"Token установлен: {bool(token and token != 'your_bot_token_here')}")
        logger.info(f"Bot enabled: {enabled}")
        
        if not token or token == "your_bot_token_here":
            logger.error("ERROR: TELEGRAM_BOT_TOKEN не установлен!")
            logger.info("Получите токен у @BotFather и добавьте в .env файл")
            sys.exit(1)
        
        if not enabled:
            logger.error("ERROR: TELEGRAM_BOT_ENABLED=false")
            logger.info("Установите TELEGRAM_BOT_ENABLED=true в .env файле")
            sys.exit(1)
        
        # Импорт бота
        logger.info("Импорт модуля бота...")
        from app.telegram_bot.bot import TelegramBot
        
        logger.info("Создание экземпляра бота...")
        bot = TelegramBot(token)
        
        if not bot.has_telegram:
            logger.error("ERROR: python-telegram-bot не установлен")
            logger.info("Установите: pip install python-telegram-bot")
            sys.exit(1)
        
        logger.info("OK: Все проверки пройдены")
        logger.info("=" * 60)
        logger.info("Запуск бота...")
        logger.info("Бот должен отвечать на команды в Telegram")
        logger.info("Нажмите Ctrl+C для остановки")
        logger.info("=" * 60)
        
        # Запуск бота
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("\nОстановка бота...")
    except Exception as e:
        logger.error(f"ERROR: Ошибка при запуске бота: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")

