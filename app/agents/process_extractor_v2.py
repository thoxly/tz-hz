"""
Process Extractor V2 - Аналитик с LLM, который превращает хаос в структуру.
"""
from typing import Dict, Any
import logging
import json

from app.agents.models import (
    ProcessExtractRequest,
    ProcessExtractResponse,
    ProcessAsIs,
    ProcessStep,
    Actor,
    Entity
)
from app.agents.llm_client import LLMClient
from app.agents.prompts import PROCESS_EXTRACTOR_SYSTEM_PROMPT
from app.agents.mcp_integration import MCPIntegration
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ProcessExtractor:
    """
    Агент для извлечения структурированного процесса AS-IS из транскрибации с использованием LLM.
    """
    
    def __init__(self, session: AsyncSession, llm_client: LLMClient = None):
        """
        Инициализация Process Extractor.
        
        Args:
            session: Сессия базы данных для MCP
            llm_client: Клиент LLM (если None, создается новый)
        """
        self.session = session
        self.mcp = MCPIntegration(session)
        self.llm_client = llm_client or LLMClient()
        self.logger = logging.getLogger(__name__)
    
    async def extract(self, request: ProcessExtractRequest) -> ProcessExtractResponse:
        """
        Извлекает структурированный процесс AS-IS из транскрибации с помощью LLM.
        
        Args:
            request: Запрос с транскрибацией
            
        Returns:
            ProcessExtractResponse с извлеченным процессом
        """
        self.logger.info("Начинаем извлечение процесса AS-IS из транскрибации с помощью LLM")
        
        # Формируем пользовательский промпт
        user_prompt = self._build_user_prompt(request)
        
        # Генерируем ответ от LLM
        try:
            response_json = await self.llm_client.generate_json(
                system_prompt=PROCESS_EXTRACTOR_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=4000
            )
        except Exception as e:
            self.logger.error(f"Ошибка при генерации ответа от LLM: {e}", exc_info=True)
            # Fallback на простую структуру
            response_json = self._create_fallback_response(request.transcript)
        
        # Преобразуем JSON в ProcessAsIs
        as_is = self._parse_response(response_json)
        
        metadata = {
            "transcript_length": len(request.transcript),
            "steps_count": len(as_is.steps),
            "actors_count": len(as_is.actors),
            "entities_count": len(as_is.entities),
            "pain_points_count": len(as_is.pain_points),
            "extraction_method": "llm"
        }
        
        self.logger.info(f"Извлечен процесс '{as_is.process_name}' с {len(as_is.steps)} шагами")
        
        return ProcessExtractResponse(
            as_is=as_is,
            extraction_metadata=metadata
        )
    
    def _build_user_prompt(self, request: ProcessExtractRequest) -> str:
        """Формирует пользовательский промпт для LLM."""
        prompt = f"""Транскрибация встречи с клиентом:

{request.transcript}

Задача: Извлеки структурированный процесс AS-IS из этой транскрибации.

Важно:
- Работайте строго на основе текста, ничего не придумывайте
- Если что-то неясно, укажите "неизвестно"
- Сохраняйте фрагменты исходного текста в source_fragment для каждого шага
- Связывайте шаги через поле "next" (ID следующего шага)

Верни результат в формате JSON согласно системному промпту."""
        
        if request.context:
            prompt += f"\n\nДополнительный контекст:\n{json.dumps(request.context, ensure_ascii=False, indent=2)}"
        
        return prompt
    
    def _parse_response(self, response_json: Dict[str, Any]) -> ProcessAsIs:
        """Парсит JSON ответ от LLM в ProcessAsIs."""
        try:
            # Парсим акторов
            actors = []
            for actor_data in response_json.get("actors", []):
                actors.append(Actor(
                    name=actor_data.get("name", ""),
                    role=actor_data.get("role", "")
                ))
            
            # Парсим сущности
            entities = []
            for entity_data in response_json.get("entities", []):
                entities.append(Entity(
                    name=entity_data.get("name", ""),
                    description=entity_data.get("description", "")
                ))
            
            # Парсим шаги
            steps = []
            for step_data in response_json.get("steps", []):
                steps.append(ProcessStep(
                    id=step_data.get("id", ""),
                    actor=step_data.get("actor", "неизвестно"),
                    action=step_data.get("action", ""),
                    input=step_data.get("input", "неизвестно"),
                    output=step_data.get("output", "неизвестно"),
                    business_rules=step_data.get("business_rules", []),
                    timeframe=step_data.get("timeframe", "неизвестно"),
                    next=step_data.get("next"),
                    source_fragment=step_data.get("source_fragment", "")
                ))
            
            return ProcessAsIs(
                process_name=response_json.get("process_name", "Неизвестный процесс"),
                goal=response_json.get("goal", ""),
                actors=actors,
                entities=entities,
                steps=steps,
                pain_points=response_json.get("pain_points", [])
            )
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге ответа: {e}", exc_info=True)
            return self._create_fallback_as_is(response_json)
    
    def _create_fallback_response(self, transcript: str) -> Dict[str, Any]:
        """Создает fallback ответ, если LLM не сработал."""
        return {
            "process_name": "Процесс из транскрибации",
            "goal": "Автоматизировать процесс",
            "actors": [],
            "entities": [],
            "steps": [
                {
                    "id": "AS1",
                    "actor": "неизвестно",
                    "action": "Обработка транскрибации",
                    "input": "неизвестно",
                    "output": "неизвестно",
                    "business_rules": [],
                    "timeframe": "неизвестно",
                    "next": None,
                    "source_fragment": transcript[:200]
                }
            ],
            "pain_points": []
        }
    
    def _create_fallback_as_is(self, response_json: Dict[str, Any]) -> ProcessAsIs:
        """Создает fallback ProcessAsIs при ошибке парсинга."""
        return ProcessAsIs(
            process_name=response_json.get("process_name", "Неизвестный процесс"),
            goal=response_json.get("goal", ""),
            actors=[],
            entities=[],
            steps=[],
            pain_points=response_json.get("pain_points", [])
        )

