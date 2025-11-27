"""
Клиент для работы с MCP API.
"""
from typing import List, Dict, Optional, Any
from app.mcp.tools import MCPTools
from sqlalchemy.ext.asyncio import AsyncSession


class MCPClient:
    """Клиент для поиска документации через MCP."""
    
    def __init__(self, session: AsyncSession):
        self.tools = MCPTools(session)
    
    async def find_relevant_docs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Найти релевантные документы по запросу."""
        return await self.tools.find_relevant(query, limit)
    
    async def search_headers(self, keywords: List[str], level: Optional[int] = None) -> List[Dict[str, Any]]:
        """Поиск заголовков по ключевым словам."""
        all_headers = []
        
        for keyword in keywords:
            # Ищем заголовки, содержащие ключевое слово
            filters = {"limit": 20}
            if level:
                filters["level"] = level
            
            headers = await self.tools.search_entities("header", filters)
            
            # Фильтруем по тексту
            matching_headers = [
                h for h in headers 
                if keyword.lower() in h.get("text", "").lower()
            ]
            all_headers.extend(matching_headers)
        
        # Удаляем дубликаты
        seen = set()
        unique_headers = []
        for header in all_headers:
            key = (header.get("doc_id"), header.get("text"))
            if key not in seen:
                seen.add(key)
                unique_headers.append(header)
        
        return unique_headers[:50]
    
    async def search_code_examples(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Поиск примеров кода."""
        filters = {"limit": 20}
        if language:
            filters["language"] = language
        
        return await self.tools.search_entities("code_block", filters)
    
    async def search_special_blocks(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """Поиск специальных блоков (В этой статье, Важно, Пример)."""
        filters = {"limit": 30}
        if kind:
            filters["kind"] = kind
        
        return await self.tools.search_entities("special_block", filters)
    
    async def get_doc_structure(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Получить структуру документа."""
        return await self.tools.get_doc(doc_id)
    
    async def find_process_docs(self) -> List[Dict[str, Any]]:
        """Найти документы о процессах."""
        return await self.find_relevant_docs("процесс бизнес-процесс workflow", limit=20)
    
    async def find_app_docs(self) -> List[Dict[str, Any]]:
        """Найти документы о приложениях."""
        return await self.find_relevant_docs("приложение справочник карточка entity", limit=20)
    
    async def find_integration_docs(self) -> List[Dict[str, Any]]:
        """Найти документы об интеграциях."""
        return await self.find_relevant_docs("интеграция api webhook connector", limit=20)
    
    async def find_widget_docs(self) -> List[Dict[str, Any]]:
        """Найти документы о виджетах."""
        return await self.find_relevant_docs("виджет форма widget form", limit=20)
    
    async def extract_doc_entities(self, doc_id: str) -> Dict[str, Any]:
        """Извлекает все сущности из документа."""
        result = {
            "headers": [],
            "lists": [],
            "code_blocks": [],
            "special_blocks": []
        }
        
        # Получаем все сущности для этого документа
        for entity_type in ["header", "list", "code_block", "special_block"]:
            entities = await self.tools.search_entities(entity_type, {"limit": 50})
            doc_entities = [e for e in entities if e.get("doc_id") == doc_id]
            key = entity_type.replace("_block", "_blocks") if "_block" in entity_type else f"{entity_type}s"
            result[key] = doc_entities
        
        return result

