"""
Telegram бот для генерации архитектурных решений и ТЗ.
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
import json
import signal

from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
from app.ts_generator.generator import TechnicalDesigner
from app.ts_generator.exporter import TSExporter

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот для работы с Decision Engine и TS Generator."""
    
    def __init__(self, token: str):
        """
        Инициализация бота.
        
        Args:
            token: Telegram Bot Token от @BotFather
        """
        self.token = token
        self.bot = None
        self.user_sessions: Dict[int, Dict[str, Any]] = {}  # {user_id: {architecture, ...}}
        
        # Инициализируем бота
        try:
            from telegram import Bot
            from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
            self.Bot = Bot
            self.Application = Application
            self.CommandHandler = CommandHandler
            self.MessageHandler = MessageHandler
            self.CallbackQueryHandler = CallbackQueryHandler
            self.filters = filters
            self.has_telegram = True
        except ImportError:
            logger.warning("python-telegram-bot не установлен. Установите: pip install python-telegram-bot")
            self.has_telegram = False
    
    async def start(self):
        """Запуск бота."""
        if not self.has_telegram:
            raise RuntimeError("python-telegram-bot не установлен")
        
        application = self.Application.builder().token(self.token).build()
        
        # Команды
        application.add_handler(self.CommandHandler("start", self._cmd_start))
        application.add_handler(self.CommandHandler("help", self._cmd_help))
        application.add_handler(self.CommandHandler("new", self._cmd_new))
        application.add_handler(self.CommandHandler("generate_ts", self._cmd_generate_ts))
        application.add_handler(self.CommandHandler("history", self._cmd_history))
        
        # Callback queries (кнопки)
        application.add_handler(self.CallbackQueryHandler(self._handle_callback))
        
        # Обработка текстовых сообщений
        application.add_handler(
            self.MessageHandler(self.filters.TEXT & ~self.filters.COMMAND, self._handle_message)
        )
        
        # Запуск
        logger.info("Telegram бот запущен")
        logger.info("Бот готов к работе. Отправьте /start в Telegram")
        
        # Используем ручной запуск для избежания конфликта event loops
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        # Ожидаем бесконечно (до Ctrl+C)
        try:
            # Создаем event для ожидания
            stop_event = asyncio.Event()
            await stop_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
    
    async def _cmd_start(self, update, context):
        """Обработка команды /start"""
        welcome_text = """
🤖 Добро пожаловать в бот генерации ТЗ!

Я помогу вам создать архитектурное решение и техническое задание для ELMA365.

📋 Доступные команды:
/new - Создать новый запрос
/generate_ts - Сгенерировать ТЗ из последнего запроса
/history - История запросов
/help - Справка

Просто напишите мне описание задачи, и я создам архитектурное решение!
        """
        await update.message.reply_text(welcome_text.strip())
    
    async def _cmd_help(self, update, context):
        """Обработка команды /help"""
        help_text = """
📖 Справка по использованию бота:

1. **Создание архитектуры:**
   Напишите описание задачи, например:
   "Нужен процесс согласования договоров с этапами: создание заявки, согласование менеджером, согласование директором"

2. **Генерация ТЗ:**
   После создания архитектуры используйте /generate_ts
   Или нажмите кнопку "Сгенерировать ТЗ" в сообщении с архитектурой

3. **Выбор формата:**
   После генерации ТЗ выберите формат файла (PDF, DOCX, HTML, Markdown)

4. **История:**
   Используйте /history для просмотра всех ваших запросов

💡 Совет: Чем подробнее описание задачи, тем точнее будет архитектурное решение!
        """
        await update.message.reply_text(help_text.strip())
    
    async def _cmd_new(self, update, context):
        """Обработка команды /new"""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {}
        await update.message.reply_text(
            "✨ Создан новый запрос. Опишите задачу, и я создам архитектурное решение!"
        )
    
    async def _handle_message(self, update, context):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not text or len(text) < 10:
            await update.message.reply_text(
                "❌ Пожалуйста, опишите задачу более подробно (минимум 10 символов)."
            )
            return
        
        # Показываем, что обрабатываем
        processing_msg = await update.message.reply_text("⏳ Обрабатываю запрос...")
        
        try:
            # Создаем бизнес-требования из текста
            requirements = BusinessRequirements(
                title=text[:100],  # Первые 100 символов как заголовок
                business_requirements=text,
                inputs=[],
                outputs=[],
                user_roles=[],
                workflow_steps=[],
                integration_targets=[],
                ui_requirements=[],
                constraints=[]
            )
            
            # Генерируем архитектурное решение
            session_factory = get_session_factory()
            async with session_factory() as session:
                engine = DecisionEngine(session)
                architecture = await engine.design_solution(requirements)
            
            # Сохраняем в сессию пользователя
            self.user_sessions[user_id] = {
                "architecture": architecture,
                "requirements": requirements
            }
            
            # Формируем ответ
            response_text = self._format_architecture_response(architecture)
            
            # Создаем кнопку для генерации ТЗ
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("📄 Сгенерировать ТЗ", callback_data="generate_ts")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(response_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Ошибка при создании архитектурного решения: {str(e)}\n\n"
                "Попробуйте описать задачу более подробно или используйте /help для справки."
            )
    
    async def _cmd_generate_ts(self, update, context):
        """Обработка команды /generate_ts"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or "architecture" not in self.user_sessions[user_id]:
            await update.message.reply_text(
                "❌ У вас нет сохраненного архитектурного решения.\n"
                "Сначала создайте архитектуру, описав задачу."
            )
            return
        
        await self._generate_ts_for_user(update, context, user_id)
    
    async def _handle_callback(self, update, context):
        """Обработка callback queries (кнопок)"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "generate_ts":
            await self._generate_ts_for_user(update, context, user_id, query=query)
        elif data.startswith("format_"):
            format_type = data.replace("format_", "")
            await self._export_ts(update, context, user_id, format_type, query=query)
    
    async def _generate_ts_for_user(self, update, context, user_id, query=None):
        """Генерация ТЗ для пользователя"""
        architecture = self.user_sessions[user_id]["architecture"]
        
        if query:
            await query.edit_message_text("⏳ Генерирую техническое задание...")
            message = query.message
        else:
            message = await update.message.reply_text("⏳ Генерирую техническое задание...")
        
        try:
            # Генерируем ТЗ
            designer = TechnicalDesigner()
            markdown = designer.generate_ts(architecture, mode="deterministic")
            
            # Сохраняем в сессию
            self.user_sessions[user_id]["ts_markdown"] = markdown
            
            # Создаем кнопки выбора формата
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("📄 DOCX", callback_data="format_docx"),
                    InlineKeyboardButton("📄 PDF", callback_data="format_pdf")
                ],
                [
                    InlineKeyboardButton("🌐 HTML", callback_data="format_html"),
                    InlineKeyboardButton("📝 Markdown", callback_data="format_markdown")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            preview = markdown[:500] + "..." if len(markdown) > 500 else markdown
            
            response_text = f"""
✅ Техническое задание сгенерировано!

📊 Статистика:
• Длина: {len(markdown)} символов
• Строк: {len(markdown.splitlines())}

📄 Предпросмотр:
```
{preview}
```

Выберите формат для экспорта:
            """
            
            if query:
                await query.edit_message_text(response_text.strip(), reply_markup=reply_markup)
            else:
                await message.edit_text(response_text.strip(), reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Ошибка при генерации ТЗ: {e}", exc_info=True)
            error_text = f"❌ Ошибка при генерации ТЗ: {str(e)}"
            if query:
                await query.edit_message_text(error_text)
            else:
                await message.edit_text(error_text)
    
    async def _export_ts(self, update, context, user_id, format_type, query=None):
        """Экспорт ТЗ в выбранный формат"""
        if user_id not in self.user_sessions or "ts_markdown" not in self.user_sessions[user_id]:
            await query.answer("❌ ТЗ не найдено. Сначала сгенерируйте ТЗ.")
            return
        
        architecture = self.user_sessions[user_id]["architecture"]
        markdown = self.user_sessions[user_id]["ts_markdown"]
        
        await query.edit_message_text(f"⏳ Экспортирую в {format_type.upper()}...")
        
        try:
            exporter = TSExporter()
            chat_id = query.message.chat.id
            
            if format_type == "markdown":
                # Отправляем Markdown как текстовый файл
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                    f.write(markdown)
                    file_path = f.name
                
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=f"technical_specification.{format_type}",
                        caption="✅ Техническое задание в формате Markdown"
                    )
                
                Path(file_path).unlink()
            
            elif format_type == "html":
                html = exporter.export_to_html(markdown, include_style=True)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html)
                    file_path = f.name
                
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=f"technical_specification.{format_type}",
                        caption="✅ Техническое задание в формате HTML"
                    )
                
                Path(file_path).unlink()
            
            elif format_type == "docx":
                docx_bytes = exporter.export_to_docx(markdown)
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False) as f:
                    f.write(docx_bytes)
                    file_path = f.name
                
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=f"technical_specification.{format_type}",
                        caption="✅ Техническое задание в формате DOCX"
                    )
                
                Path(file_path).unlink()
            
            elif format_type == "pdf":
                pdf_bytes = exporter.export_to_pdf(markdown)
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
                    f.write(pdf_bytes)
                    file_path = f.name
                
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=f"technical_specification.{format_type}",
                        caption="✅ Техническое задание в формате PDF"
                    )
                
                Path(file_path).unlink()
            
            await query.edit_message_text(f"✅ Файл отправлен в формате {format_type.upper()}!")
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте ТЗ: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ Ошибка при экспорте в {format_type.upper()}: {str(e)}\n\n"
                "Попробуйте другой формат или обратитесь к администратору."
            )
    
    async def _cmd_history(self, update, context):
        """Обработка команды /history"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions or not self.user_sessions[user_id]:
            await update.message.reply_text("📝 У вас пока нет истории запросов.")
            return
        
        session = self.user_sessions[user_id]
        history_text = "📜 История ваших запросов:\n\n"
        
        if "architecture" in session:
            arch = session["architecture"]
            history_text += f"✅ Архитектурное решение:\n"
            history_text += f"• Типы: {', '.join(arch.solution_type)}\n"
            history_text += f"• Уверенность: {arch.confidence:.1%}\n"
            if arch.process_design:
                history_text += f"• Процесс: {arch.process_design.process_name}\n"
            if arch.app_structure:
                history_text += f"• Приложение: {arch.app_structure.app_name}\n"
            history_text += "\n"
        
        if "ts_markdown" in session:
            history_text += "✅ Техническое задание сгенерировано\n"
        
        await update.message.reply_text(history_text)
    
    def _format_architecture_response(self, architecture) -> str:
        """Форматирует ответ с архитектурным решением"""
        lines = [
            "✅ Архитектурное решение создано!\n",
            f"📊 **Типы решений:** {', '.join(architecture.solution_type)}",
            f"🎯 **Уверенность:** {architecture.confidence:.1%}",
            ""
        ]
        
        if architecture.process_design:
            lines.append(f"🔄 **Процесс:** {architecture.process_design.process_name}")
            lines.append(f"   • Шагов: {len(architecture.process_design.steps)}")
            if architecture.process_design.roles:
                lines.append(f"   • Роли: {', '.join(architecture.process_design.roles)}")
            lines.append("")
        
        if architecture.app_structure:
            lines.append(f"📱 **Приложение:** {architecture.app_structure.app_name}")
            lines.append(f"   • Полей: {len(architecture.app_structure.fields)}")
            lines.append(f"   • Представлений: {len(architecture.app_structure.views)}")
            lines.append("")
        
        if architecture.widget_design:
            lines.append(f"🎨 **Виджет:** {architecture.widget_design.widget_name}")
            lines.append(f"   • Тип: {architecture.widget_design.widget_type}")
            lines.append("")
        
        if architecture.integration_points:
            lines.append(f"🔗 **Интеграция:** {architecture.integration_points.integration_type}")
            if architecture.integration_points.target_systems:
                lines.append(f"   • Системы: {', '.join(architecture.integration_points.target_systems)}")
            lines.append("")
        
        if architecture.references:
            lines.append(f"📚 **Использовано документов:** {len(architecture.references)}")
            lines.append("")
        
        lines.append("💡 Нажмите кнопку ниже для генерации ТЗ")
        
        return "\n".join(lines)

