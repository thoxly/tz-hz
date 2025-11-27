from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/elma365_crawler"
    
    # Crawler settings
    CRAWL_BASE_URL: str = "https://elma365.com"
    CRAWL_MAX_DEPTH: int = 10
    CRAWL_DELAY: float = 1.0  # seconds between requests
    CRAWL_MAX_CONCURRENT: int = 5
    
    # Output settings
    OUTPUT_DIR: str = "data/crawled"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Telegram Bot (optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_BOT_ENABLED: bool = False
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_PROVIDER: str = "ollama"  # openai, anthropic, deepseek, ollama
    LLM_MODEL: Optional[str] = None  # Если None, используется по умолчанию для провайдера
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

