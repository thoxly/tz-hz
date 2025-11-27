#!/usr/bin/env python3
"""Финальная версия запуска бота с правильной обработкой ошибок."""
import sys
import asyncio
import logging

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Главная функция."""
    try:
        logger.info("=" * 60)
        logger.info("Запуск Telegram бота")
        logger.info("=" * 60)
        
        # Проверка конфигурации
        from app.telegram_bot.config import telegram_settings
        
        token = telegram_settings.TELEGRAM_BOT_TOKEN
        if not token or token == "your_bot_token_here":
            logger.error("ERROR: TELEGRAM_BOT_TOKEN не установлен!")
            sys.exit(1)
        
        if not telegram_settings.TELEGRAM_BOT_ENABLED:
            logger.error("ERROR: TELEGRAM_BOT_ENABLED=false")
            sys.exit(1)
        
        logger.info("OK: Конфигурация проверена")
        
        # Импорт и создание бота
        from app.telegram_bot.bot import TelegramBot
        bot = TelegramBot(token)
        
        if not bot.has_telegram:
            logger.error("ERROR: python-telegram-bot не установлен")
            sys.exit(1)
        
        logger.info("OK: Бот создан")
        logger.info("=" * 60)
        logger.info("Запуск бота...")
        logger.info("Отправьте /start в Telegram для проверки")
        logger.info("Нажмите Ctrl+C для остановки")
        logger.info("=" * 60)
        
        # Запуск
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("\nОстановка бота...")
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Проверяем, есть ли уже запущенный event loop
    try:
        loop = asyncio.get_running_loop()
        # Если loop уже запущен, используем другой подход
        logger.warning("Event loop уже запущен, используем синхронный запуск")
        import sys
        sys.exit("Пожалуйста, запустите бота без asyncio.run()")
    except RuntimeError:
        # Нет запущенного loop, можно использовать asyncio.run()
        pass
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")

