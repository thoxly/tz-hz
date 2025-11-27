"""
API Routes для агентов обработки требований.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.agents.process_extractor_v2 import ProcessExtractor
from app.agents.pipeline import AgentPipeline
from app.agents.llm_client import LLMClient
from app.agents.models import (
    ProcessExtractRequest,
    ProcessExtractResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/agents/process-extract", response_model=ProcessExtractResponse)
async def extract_process(
    request: ProcessExtractRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process Extractor - извлекает структурированный процесс AS-IS из транскрибации.
    
    Принимает транскрибацию встречи с клиентом и возвращает структурированный процесс:
    - Роли участников
    - Шаги процесса в правильном порядке
    - Бизнес-правила
    - Проблемы и боли
    - Неизвестные моменты
    """
    try:
        llm_client = LLMClient()
        extractor = ProcessExtractor(db, llm_client)
        response = await extractor.extract(request)
        return response
    except Exception as e:
        logger.error(f"Ошибка при извлечении процесса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении процесса: {str(e)}")


# Architect Agent и Scope Agent теперь вызываются через pipeline
# Используйте /agents/full-pipeline для полного пайплайна


@router.post("/agents/full-pipeline")
async def full_pipeline(
    request: ProcessExtractRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Полный пайплайн обработки: транскрибация → AS-IS → Архитектура → Scope ТЗ.
    
    Выполняет все три этапа последовательно с использованием LLM:
    1. Process Extractor - извлекает AS-IS (LLM)
    2. Architect Agent - проектирует архитектуру (LLM + MCP)
    3. Scope Agent - генерирует краткое ТЗ (LLM)
    """
    try:
        llm_client = LLMClient()
        pipeline = AgentPipeline(db, llm_client)
        results = await pipeline.process(request)
        
        return results
    except Exception as e:
        logger.error(f"Ошибка в полном пайплайне: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка в полном пайплайне: {str(e)}")

