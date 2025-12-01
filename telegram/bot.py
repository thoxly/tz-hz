import asyncio
import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session_factory
from agents.mcp_client import MCPClient
from pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)

# Store user states (waiting for text input)
user_states: Dict[int, bool] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Привет! Я бот для создания ТЗ на основе процессов ELMA365.\n\n"
        "Используй команду /run чтобы начать."
    )


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /run command."""
    user_id = update.effective_user.id
    user_states[user_id] = True
    
    await update.message.reply_text(
        "Отправь текст встречи или требования для анализа процесса.\n\n"
        "Я создам:\n"
        "1. AS-IS описание процесса\n"
        "2. Архитектуру ELMA365\n"
        "3. ТЗ на согласование"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user_id = update.effective_user.id
    
    # Check if user is waiting for text input
    if user_id not in user_states or not user_states[user_id]:
        await update.message.reply_text(
            "Используй команду /run чтобы начать анализ процесса."
        )
        return
    
    # Clear state
    user_states[user_id] = False
    
    text = update.message.text
    
    if not text or len(text.strip()) < 10:
        await update.message.reply_text(
            "Текст слишком короткий. Пожалуйста, отправь более подробное описание."
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("Обрабатываю... Это может занять некоторое время.")
    
    try:
        # Create database session
        session_factory = get_session_factory()
        async with session_factory() as db_session:
            # Create MCP client
            mcp_client = MCPClient(transport="http")
            
            # Create orchestrator
            orchestrator = PipelineOrchestrator(mcp_client=mcp_client)
            
            # Run pipeline
            result = await orchestrator.run_process_pipeline(
                text=text,
                db_session=db_session,
                user=str(user_id)
            )
            
            # Send results in 3 separate messages
            # 1. AS-IS
            as_is_text = f"📋 AS-IS Процесс:\n\n{_format_json(result['as_is'])}"
            await update.message.reply_text(as_is_text[:4096])  # Telegram limit
            
            # 2. Architecture
            arch_text = f"🏗️ Архитектура ELMA365:\n\n{_format_json(result['architecture'])}"
            await update.message.reply_text(arch_text[:4096])
            
            # 3. Scope
            scope_text = f"✅ ТЗ на согласование:\n\n{_format_json(result['scope'])}"
            await update.message.reply_text(scope_text[:4096])
            
            # Delete processing message
            await processing_msg.delete()
            
            await update.message.reply_text(
                f"✅ Готово! Результаты сохранены. Run ID: {result['run_id']}"
            )
    
    except Exception as e:
        logger.error(f"Error processing pipeline: {e}", exc_info=True)
        await processing_msg.edit_text(
            f"❌ Ошибка при обработке: {str(e)}\n\nПопробуй еще раз."
        )


def _format_json(data: Dict[str, Any]) -> str:
    """Format JSON data for Telegram message."""
    import json
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)


def create_bot() -> Application:
    """Create and configure Telegram bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")
    
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    return application


async def main():
    """Main entry point for Telegram bot."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    logger.info("Starting Telegram bot...")
    
    application = create_bot()
    
    # Run bot
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())

