"""
Конфигурация для Telegram бота.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class TelegramBotSettings(BaseSettings):
    """Настройки Telegram бота."""
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля из .env


telegram_settings = TelegramBotSettings()

