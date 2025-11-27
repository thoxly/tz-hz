"""
MCP Integration - интеграция агентов с MCP для получения документации.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.mcp.tools import MCPTools

logger = logging.getLogger(__name__)


class MCPIntegration:
    """
    Интеграция агентов с MCP для получения документации ELMA365.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация MCP интеграции.
        
        Args:
            session: Сессия базы данных
        """
        self.session = session
        self.tools = MCPTools(session)
        self.logger = logging.getLogger(__name__)
    
    async def request(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Выполняет запрос к MCP.
        
        Args:
            query: Описание запроса (например, "найти статью о бизнес-процессах")
            limit: Максимальное количество результатов
            
        Returns:
            Результаты поиска в формате:
            {
                "query": "...",
                "results": [
                    {
                        "title": "...",
                        "url": "...",
                        "context": "...",
                        "doc_id": "..."
                    }
                ]
            }
        """
        self.logger.info(f"MCP запрос: {query}")
        
        try:
            # Ищем релевантные документы
            docs = await self.tools.find_relevant(query, limit=limit)
            
            # Форматируем результаты
            results = []
            for doc in docs:
                results.append({
                    "title": doc.get("title", ""),
                    "url": doc.get("url", ""),
                    "context": doc.get("context", ""),
                    "doc_id": doc.get("doc_id", ""),
                    "breadcrumbs": doc.get("breadcrumbs", [])
                })
            
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении MCP запроса: {e}", exc_info=True)
            return {
                "query": query,
                "results": [],
                "count": 0,
                "error": str(e)
            }
    
    async def get_doc(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает документ по ID.
        
        Args:
            doc_id: ID документа
            
        Returns:
            Структура документа или None
        """
        return await self.tools.get_doc(doc_id)
    
    async def search_entities(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ищет сущности в документации.
        
        Args:
            entity_type: Тип сущности (header, list, code_block, special_block)
            filters: Фильтры поиска
            
        Returns:
            Список найденных сущностей
        """
        return await self.tools.search_entities(entity_type, filters)

