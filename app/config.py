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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

