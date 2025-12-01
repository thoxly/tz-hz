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
    
    # LLM settings
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # MCP settings
    MCP_SERVER_MODE: str = "http"  # stdin or http
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

