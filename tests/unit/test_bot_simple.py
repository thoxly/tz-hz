#!/usr/bin/env python3
"""Простой тест запуска бота."""
import sys
import asyncio

# Настройка кодировки
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("Тест запуска Telegram бота")
print("=" * 60)

try:
    print("1. Проверка конфигурации...")
    from app.telegram_bot.config import telegram_settings
    
    token = telegram_settings.TELEGRAM_BOT_TOKEN
    enabled = telegram_settings.TELEGRAM_BOT_ENABLED
    
    if not token or token == "your_bot_token_here":
        print("   ERROR: Token не установлен")
        sys.exit(1)
    print(f"   OK: Token установлен ({token[:10]}...)")
    
    if not enabled:
        print("   ERROR: Bot disabled")
        sys.exit(1)
    print("   OK: Bot enabled")
    
    print("2. Проверка библиотеки telegram...")
    try:
        from telegram.ext import Application
        print("   OK: python-telegram-bot установлен")
    except ImportError as e:
        print(f"   ERROR: {e}")
        sys.exit(1)
    
    print("3. Импорт бота...")
    from app.telegram_bot.bot import TelegramBot
    print("   OK: Модуль бота импортирован")
    
    print("4. Создание экземпляра бота...")
    bot = TelegramBot(token)
    if not bot.has_telegram:
        print("   ERROR: has_telegram = False")
        sys.exit(1)
    print("   OK: Бот создан")
    
    print("5. Тест запуска (5 секунд)...")
    print("   Запускаю бота...")
    
    async def test_run():
        try:
            # Создаем application для теста
            from telegram.ext import Application
            app = Application.builder().token(token).build()
            
            # Добавляем простой handler
            async def start_handler(update, context):
                await update.message.reply_text("Test OK!")
            
            from telegram.ext import CommandHandler
            app.add_handler(CommandHandler("test", start_handler))
            
            # Запускаем на 5 секунд
            await app.initialize()
            await app.start()
            await app.updater.start_polling(allowed_updates=["message"])
            
            print("   OK: Бот запущен! Отправьте /test в Telegram")
            print("   Ожидание 5 секунд...")
            await asyncio.sleep(5)
            
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
            print("   OK: Бот остановлен")
            
        except Exception as e:
            print(f"   ERROR при запуске: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    asyncio.run(test_run())
    
    print("=" * 60)
    print("Все тесты пройдены!")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

