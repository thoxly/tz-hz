#!/usr/bin/env python3
"""Запуск бота без конфликта event loops."""
import sys
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

def main():
    """Главная функция - используем run_polling напрямую."""
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
        
        # Импорт библиотеки
        from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
        
        # Импорт обработчиков
        from app.telegram_bot.bot import TelegramBot
        bot_instance = TelegramBot(token)
        
        if not bot_instance.has_telegram:
            logger.error("ERROR: python-telegram-bot не установлен")
            sys.exit(1)
        
        # Создаем application
        application = Application.builder().token(token).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot_instance._cmd_start))
        application.add_handler(CommandHandler("help", bot_instance._cmd_help))
        application.add_handler(CommandHandler("new", bot_instance._cmd_new))
        application.add_handler(CommandHandler("generate_ts", bot_instance._cmd_generate_ts))
        application.add_handler(CommandHandler("history", bot_instance._cmd_history))
        application.add_handler(CallbackQueryHandler(bot_instance._handle_callback))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance._handle_message)
        )
        
        logger.info("OK: Бот создан и настроен")
        logger.info("=" * 60)
        logger.info("Запуск бота...")
        logger.info("Отправьте /start в Telegram для проверки")
        logger.info("Нажмите Ctrl+C для остановки")
        logger.info("=" * 60)
        
        # Запуск через run_polling (он сам создаст event loop)
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("\nОстановка бота...")
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

