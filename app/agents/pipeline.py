"""
Pipeline - оркестратор для последовательного вызова агентов.
"""
from typing import Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import ProcessExtractRequest
from app.agents.process_extractor_v2 import ProcessExtractor
from app.agents.llm_client import LLMClient
from app.agents.mcp_integration import MCPIntegration
from app.agents.mcp_integration import MCPIntegration

logger = logging.getLogger(__name__)


class AgentPipeline:
    """
    Оркестратор для последовательного вызова агентов.
    
    Pipeline:
    Process Extractor → Architect Agent → Scope Agent
    """
    
    def __init__(self, session: AsyncSession, llm_client: LLMClient = None):
        """
        Инициализация pipeline.
        
        Args:
            session: Сессия базы данных
            llm_client: Клиент LLM (если None, создается новый)
        """
        self.session = session
        self.llm_client = llm_client or LLMClient()
        self.mcp = MCPIntegration(session)
        self.logger = logging.getLogger(__name__)
    
    async def process(self, request: ProcessExtractRequest) -> Dict[str, Any]:
        """
        Выполняет полный пайплайн обработки.
        
        Args:
            request: Запрос с транскрибацией
            
        Returns:
            Результаты всех трех агентов:
            {
                "as_is": ProcessAsIs,
                "architecture": str,  # Текст архитектуры
                "scope": str,  # Текст Scope ТЗ
                "metadata": {...}
            }
        """
        self.logger.info("Запуск полного пайплайна обработки")
        
        results = {
            "as_is": None,
            "architecture": None,
            "scope": None,
            "metadata": {}
        }
        
        try:
            # Шаг 1: Process Extractor
            self.logger.info("Шаг 1: Process Extractor")
            extractor = ProcessExtractor(self.session, self.llm_client)
            extract_response = await extractor.extract(request)
            results["as_is"] = extract_response.as_is
            results["metadata"]["extraction"] = extract_response.extraction_metadata
            
            # Шаг 2: Architect Agent
            self.logger.info("Шаг 2: Architect Agent")
            architecture_text = await self._run_architect_agent(extract_response.as_is)
            results["architecture"] = architecture_text
            results["metadata"]["architecture"] = {
                "length": len(architecture_text),
                "method": "llm"
            }
            
            # Шаг 3: Scope Agent
            self.logger.info("Шаг 3: Scope Agent")
            scope_text = await self._run_scope_agent(extract_response.as_is, architecture_text)
            results["scope"] = scope_text
            results["metadata"]["scope"] = {
                "length": len(scope_text),
                "method": "llm"
            }
            
            self.logger.info("Пайплайн успешно завершен")
            
        except Exception as e:
            self.logger.error(f"Ошибка в пайплайне: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    async def _run_architect_agent(self, as_is) -> str:
        """Запускает Architect Agent."""
        from app.agents.prompts import ARCHITECT_AGENT_SYSTEM_PROMPT
        
        # Формируем пользовательский промпт
        user_prompt = f"""AS-IS процесс:

Название: {as_is.process_name}
Цель: {as_is.goal}

Акторы:
{self._format_actors(as_is.actors)}

Сущности:
{self._format_entities(as_is.entities)}

Шаги процесса:
{self._format_steps(as_is.steps)}

Точки боли:
{self._format_pain_points(as_is.pain_points)}

Задача: Спроектируй архитектуру решения ELMA365 на основе этого AS-IS процесса.

Важно:
- Используй MCP для получения документации ELMA365
- Обоснуй каждый выбор
- Не предлагай ничего сверх AS-IS
- Укажи неизвестные места

Верни архитектурное решение в формате, указанном в системном промпте."""
        
        # Генерируем ответ
        architecture_text = await self.llm_client.generate(
            system_prompt=ARCHITECT_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4000
        )
        
        return architecture_text
    
    async def _run_scope_agent(self, as_is, architecture_text: str) -> str:
        """Запускает Scope Agent."""
        from app.agents.prompts import SCOPE_AGENT_SYSTEM_PROMPT
        
        # Формируем пользовательский промпт
        user_prompt = f"""AS-IS процесс:

Название: {as_is.process_name}
Цель: {as_is.goal}

Шаги процесса:
{self._format_steps(as_is.steps)}

Архитектурное решение:
{architecture_text}

Задача: Создай краткое ТЗ для согласования с заказчиком (1-2 страницы).

Важно:
- Формальный стиль
- Только факты из AS-IS и архитектуры
- Не включай дизайн интерфейсов, поля форм, TO-BE процессы, сроки, риски
- Краткость: 1-2 страницы

Верни ТЗ в формате, указанном в системном промпте."""
        
        # Генерируем ответ
        scope_text = await self.llm_client.generate(
            system_prompt=SCOPE_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=3000
        )
        
        return scope_text
    
    def _format_actors(self, actors) -> str:
        """Форматирует список акторов."""
        if not actors:
            return "- Нет акторов"
        return "\n".join([f"- {a.name} ({a.role})" for a in actors])
    
    def _format_entities(self, entities) -> str:
        """Форматирует список сущностей."""
        if not entities:
            return "- Нет сущностей"
        return "\n".join([f"- {e.name}: {e.description}" for e in entities])
    
    def _format_steps(self, steps) -> str:
        """Форматирует список шагов."""
        if not steps:
            return "- Нет шагов"
        lines = []
        for step in steps:
            lines.append(f"{step.id}. {step.action}")
            lines.append(f"   Актор: {step.actor}")
            lines.append(f"   Вход: {step.input}")
            lines.append(f"   Выход: {step.output}")
            if step.next:
                lines.append(f"   Следующий: {step.next}")
        return "\n".join(lines)
    
    def _format_pain_points(self, pain_points) -> str:
        """Форматирует точки боли."""
        if not pain_points:
            return "- Нет указанных проблем"
        return "\n".join([f"- {p}" for p in pain_points])

