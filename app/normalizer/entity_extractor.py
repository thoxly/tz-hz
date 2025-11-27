from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.models import Entity


class EntityExtractor:
    """Extract entities from normalized content and save to database."""
    
    def __init__(self):
        pass
    
    async def extract_and_save_entities(
        self,
        session: AsyncSession,
        doc_id: str,
        normalized_content: Dict,
        doc_url: Optional[str] = None,
        doc_breadcrumbs: Optional[List[str]] = None
    ) -> List[Entity]:
        """
        Extract entities from normalized content and save to database.
        
        Args:
            session: Database session
            doc_id: Document ID
            normalized_content: Normalized content dict with 'blocks' key
            doc_url: Document URL for metadata
            doc_breadcrumbs: Document breadcrumbs for metadata
        
        Returns:
            List of created Entity objects
        """
        blocks = normalized_content.get('blocks', [])
        
        # Clear existing entities for this document
        await session.execute(
            delete(Entity).where(Entity.doc_id == doc_id)
        )
        
        entities = []
        
        for block_index, block in enumerate(blocks):
            entity = self._block_to_entity(
                doc_id, 
                block, 
                block_index,
                doc_url=doc_url,
                doc_breadcrumbs=doc_breadcrumbs
            )
            if entity:
                entities.append(entity)
        
        # Bulk insert entities
        if entities:
            session.add_all(entities)
            await session.commit()
        
        return entities
    
    def _block_to_entity(
        self, 
        doc_id: str, 
        block: Dict, 
        block_index: int,
        doc_url: Optional[str] = None,
        doc_breadcrumbs: Optional[List[str]] = None
    ) -> Optional[Entity]:
        """Convert a block to an Entity object with full metadata."""
        block_type = block.get('type')
        text = block.get('text', '')
        
        # Базовые метаданные для всех сущностей
        base_metadata = {
            'block_index': block_index,
            'breadcrumbs': doc_breadcrumbs or [],
            'url': doc_url or ''
        }
        
        if block_type == 'header':
            level = block.get('level', 1)
            header_text = block.get('text', '')
            return Entity(
                doc_id=doc_id,
                type='header',
                data={
                    **base_metadata,
                    'level': level,
                    'text': header_text,
                    'anchor': block.get('id', '')
                }
            )
        
        elif block_type == 'code_block':
            code = block.get('code', '')
            language = block.get('language')
            return Entity(
                doc_id=doc_id,
                type='code_block',
                data={
                    **base_metadata,
                    'language': language,
                    'code': code,
                    'text': code[:200] if code else ''  # Первые 200 символов как text
                }
            )
        
        elif block_type == 'special_block':
            kind = block.get('kind', '')
            heading = block.get('heading', '')
            content = block.get('content', [])
            # Формируем text из heading и content
            special_text = heading
            if content:
                if isinstance(content, list):
                    special_text += ' ' + ' '.join(str(item) for item in content[:3])
                else:
                    special_text += ' ' + str(content)[:100]
            
            return Entity(
                doc_id=doc_id,
                type='special_block',
                data={
                    **base_metadata,
                    'kind': kind,
                    'heading': heading,
                    'content': content,
                    'text': special_text
                }
            )
        
        elif block_type == 'list':
            items = block.get('items', [])
            ordered = block.get('ordered', False)
            # Формируем text из элементов списка
            list_text = ' | '.join(str(item) for item in items[:5])
            if len(items) > 5:
                list_text += f' ... (еще {len(items) - 5} элементов)'
            
            return Entity(
                doc_id=doc_id,
                type='list',
                data={
                    **base_metadata,
                    'ordered': ordered,
                    'items': items,
                    'items_count': len(items),
                    'text': list_text
                }
            )
        
        elif block_type == 'paragraph':
            # Извлекаем параграфы только если они достаточно информативны
            para_text = block.get('text', '')
            if len(para_text) > 50:  # Только длинные параграфы
                return Entity(
                    doc_id=doc_id,
                    type='paragraph',
                    data={
                        **base_metadata,
                        'text': para_text
                    }
                )
            return None
        
        elif block_type == 'image':
            return Entity(
                doc_id=doc_id,
                type='image',
                data={
                    **base_metadata,
                    'src': block.get('src', ''),
                    'alt': block.get('alt', ''),
                    'text': block.get('alt', '')
                }
            )
        
        return None
    
    def _get_context(self, block: Dict) -> str:
        """Extract context for a block (surrounding text)."""
        # This is a placeholder - in a full implementation,
        # we'd look at surrounding blocks
        return ''

