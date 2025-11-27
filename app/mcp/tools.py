"""
MCP Tools - методы для доступа к документации.
Строгий интерфейс для агент-архитектора (LLM).
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, Integer, Boolean, cast
from sqlalchemy.dialects.postgresql import JSONB
from app.database.models import Doc, Entity


class MCPTools:
    """Инструменты MCP для доступа к документации."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_doc(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить документ по ID.
        
        Returns:
            {
                "title": str,
                "breadcrumbs": List[str],
                "blocks": List[Dict],
                "plain_text": str,
                "url": str
            }
        """
        result = await self.session.execute(
            select(Doc).where(Doc.doc_id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return None
        
        content = doc.content or {}
        
        return {
            "title": doc.title,
            "breadcrumbs": content.get('breadcrumbs', []),
            "blocks": content.get('blocks', []),
            "plain_text": content.get('plain_text', ''),
            "url": doc.url
        }
    
    async def search_entities(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск сущностей с фильтрами.
        
        Args:
            entity_type: тип сущности (header, list, code_block, special_block, paragraph)
            filters: фильтры:
                - level (для header): уровень заголовка
                - breadcrumbs (для всех): список breadcrumbs
                - language (для code_block): язык программирования
                - kind (для special_block): тип специального блока
                - ordered (для list): упорядоченный список или нет
                - limit: максимальное количество результатов
        
        Returns:
            List[Dict] - список сущностей со структурированными данными
        """
        filters = filters or {}
        limit = filters.get('limit', 100)
        
        # Базовый запрос
        query = select(Entity).where(Entity.type == entity_type)
        
        # Применяем фильтры
        conditions = []
        
        # Фильтр по уровню заголовка
        if entity_type == 'header' and 'level' in filters:
            level = filters['level']
            try:
                query = query.where(
                    cast(Entity.data['level'].astext, Integer) == level
                )
            except:
                # Альтернативный способ для PostgreSQL
                query = query.where(
                    Entity.data['level'].astext == str(level)
                )
        
        # Фильтр по breadcrumbs
        if 'breadcrumbs' in filters:
            breadcrumbs = filters['breadcrumbs']
            if isinstance(breadcrumbs, list) and breadcrumbs:
                # Ищем документы, где breadcrumbs содержат указанные элементы
                try:
                    query = query.where(
                        Entity.data['breadcrumbs'].contains(breadcrumbs)
                    )
                except:
                    # Альтернативный способ - поиск по тексту
                    breadcrumb_text = ' '.join(breadcrumbs)
                    query = query.where(
                        Entity.data['breadcrumbs'].astext.ilike(f"%{breadcrumb_text}%")
                    )
        
        # Фильтр по языку для code_block
        if entity_type == 'code_block' and 'language' in filters:
            language = filters['language']
            query = query.where(
                Entity.data['language'].astext == language
            )
        
        # Фильтр по типу специального блока
        if entity_type == 'special_block' and 'kind' in filters:
            kind = filters['kind']
            query = query.where(
                Entity.data['kind'].astext == kind
            )
        
        # Фильтр по ordered для list
        if entity_type == 'list' and 'ordered' in filters:
            ordered = filters['ordered']
            try:
                query = query.where(
                    cast(Entity.data['ordered'].astext, Boolean) == ordered
                )
            except:
                # Альтернативный способ
                query = query.where(
                    Entity.data['ordered'].astext == str(ordered).lower()
                )
        
        # Ограничение количества
        query = query.limit(limit)
        
        result = await self.session.execute(query)
        entities = result.scalars().all()
        
        # Формируем структурированный ответ
        structured_entities = []
        for entity in entities:
            data = entity.data or {}
            
            if entity_type == 'header':
                structured_entities.append({
                    "doc_id": entity.doc_id,
                    "text": data.get('text', ''),
                    "level": data.get('level'),
                    "anchor": data.get('anchor', ''),
                    "breadcrumbs": data.get('breadcrumbs', []),
                    "url": data.get('url', ''),
                    "block_index": data.get('block_index')
                })
            
            elif entity_type == 'list':
                structured_entities.append({
                    "doc_id": entity.doc_id,
                    "items": data.get('items', []),
                    "ordered": data.get('ordered', False),
                    "items_count": data.get('items_count', 0),
                    "text": data.get('text', ''),
                    "breadcrumbs": data.get('breadcrumbs', []),
                    "url": data.get('url', ''),
                    "block_index": data.get('block_index')
                })
            
            elif entity_type == 'code_block':
                structured_entities.append({
                    "doc_id": entity.doc_id,
                    "language": data.get('language'),
                    "code": data.get('code', ''),
                    "text": data.get('text', ''),
                    "breadcrumbs": data.get('breadcrumbs', []),
                    "url": data.get('url', ''),
                    "block_index": data.get('block_index')
                })
            
            elif entity_type == 'special_block':
                structured_entities.append({
                    "doc_id": entity.doc_id,
                    "kind": data.get('kind', ''),
                    "heading": data.get('heading', ''),
                    "content": data.get('content', []),
                    "text": data.get('text', ''),
                    "breadcrumbs": data.get('breadcrumbs', []),
                    "url": data.get('url', ''),
                    "block_index": data.get('block_index')
                })
            
            elif entity_type == 'paragraph':
                structured_entities.append({
                    "doc_id": entity.doc_id,
                    "text": data.get('text', ''),
                    "breadcrumbs": data.get('breadcrumbs', []),
                    "url": data.get('url', ''),
                    "block_index": data.get('block_index')
                })
        
        return structured_entities
    
    async def find_relevant(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Полнотекстовый поиск по документам.
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            List[Dict] - список релевантных документов
        """
        # Используем ILIKE для поиска в plain_text
        search_pattern = f"%{query}%"
        
        result = await self.session.execute(
            select(
                Doc.id,
                Doc.doc_id,
                Doc.title,
                Doc.url,
                Doc.content['plain_text'].astext.label('plain_text'),
                Doc.content['breadcrumbs'].label('breadcrumbs'),
                Doc.section
            )
            .where(
                Doc.content['plain_text'].astext.ilike(search_pattern)
            )
            .limit(limit)
            .order_by(Doc.title)
        )
        
        rows = result.all()
        
        # Формируем результаты с подсветкой найденного текста
        results = []
        for row in rows:
            plain_text = row.plain_text or ''
            # Находим позицию запроса в тексте
            query_lower = query.lower()
            text_lower = plain_text.lower()
            pos = text_lower.find(query_lower)
            
            # Вырезаем контекст вокруг найденного текста
            context_start = max(0, pos - 100)
            context_end = min(len(plain_text), pos + len(query) + 100)
            context = plain_text[context_start:context_end]
            
            results.append({
                "doc_id": row.doc_id,
                "title": row.title,
                "url": row.url,
                "section": row.section,
                "breadcrumbs": row.breadcrumbs or [],
                "context": context,
                "match_position": pos if pos >= 0 else None
            })
        
        return results
    
    async def list_docs_by_section(self, section: str) -> List[Dict[str, Any]]:
        """
        Получить список документов по разделу.
        
        Args:
            section: название раздела (например, "platform", "crm", "ecm")
        
        Returns:
            List[Dict] - список документов
        """
        # Ищем документы, где section содержит указанный раздел
        result = await self.session.execute(
            select(Doc)
            .where(
                or_(
                    Doc.section.ilike(f"%{section}%"),
                    Doc.content['breadcrumbs'].astext.ilike(f"%{section}%")
                )
            )
            .order_by(Doc.title)
        )
        
        docs = result.scalars().all()
        
        return [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "url": doc.url,
                "section": doc.section,
                "breadcrumbs": (doc.content or {}).get('breadcrumbs', [])
            }
            for doc in docs
        ]

