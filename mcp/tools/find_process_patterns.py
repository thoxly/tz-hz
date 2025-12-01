from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database.models import Doc, Entity
import logging

logger = logging.getLogger(__name__)

# Pattern keywords mapping
PATTERN_KEYWORDS = {
    "согласование": ["согласование", "согласовать", "approval", "approve", "согласован"],
    "поручение": ["поручение", "поручить", "task", "assignment", "задача"],
    "регистрация": ["регистрация", "зарегистрировать", "registration", "register", "регистр"],
    "архивирование": ["архивирование", "архив", "archive", "archiving", "архивировать"],
    "SLA": ["sla", "service level", "уровень обслуживания", "соглашение об уровне"]
}


async def find_process_patterns(input_data: Dict[str, Any], db_session: AsyncSession) -> Dict[str, Any]:
    """
    Find process patterns in documentation.
    
    Args:
        input_data: Dict with 'pattern_type' key
        db_session: Database session
    
    Returns:
        Dict with 'patterns' key containing list of process patterns
    """
    pattern_type = input_data.get("pattern_type", "").strip()
    
    if not pattern_type:
        raise ValueError("pattern_type is required")
    
    # Get keywords for this pattern type
    keywords = PATTERN_KEYWORDS.get(pattern_type.lower(), [pattern_type])
    
    if not keywords:
        return {"patterns": []}
    
    try:
        patterns = []
        
        # Search in documents content (plain_text)
        search_patterns = [f"%{kw}%" for kw in keywords]
        
        stmt = select(
            Doc.doc_id,
            Doc.title,
            Doc.section,
            Doc.content
        ).where(
            or_(*[
                Doc.content['plain_text'].astext.ilike(pattern)
                for pattern in search_patterns
            ])
        ).limit(20)
        
        result = await db_session.execute(stmt)
        docs = result.all()
        
        for doc in docs:
            # Extract relevant content
            content = doc.content or {}
            plain_text = content.get("plain_text", "")
            
            # Check if any keyword is in the text
            plain_text_lower = plain_text.lower()
            if any(kw.lower() in plain_text_lower for kw in keywords):
                patterns.append({
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "section": doc.section,
                    "pattern_type": pattern_type,
                    "snippet": _extract_snippet(plain_text, keywords[0], max_length=300)
                })
        
        # Also search in entities (special blocks, code blocks)
        entity_stmt = select(Entity).where(
            or_(*[
                Entity.data['kind'].astext.ilike(f"%{kw}%")
                for kw in keywords
            ])
        ).limit(10)
        
        entity_result = await db_session.execute(entity_stmt)
        entities = entity_result.scalars().all()
        
        for entity in entities:
            data = entity.data or {}
            content_text = str(data).lower()
            
            if any(kw.lower() in content_text for kw in keywords):
                patterns.append({
                    "doc_id": entity.doc_id,
                    "type": entity.type,
                    "pattern_type": pattern_type,
                    "data": data
                })
        
        logger.info(f"Found {len(patterns)} patterns of type '{pattern_type}'")
        return {"patterns": patterns}
    
    except Exception as e:
        logger.error(f"Error finding process patterns: {e}", exc_info=True)
        raise


def _extract_snippet(text: str, keyword: str, max_length: int = 300) -> str:
    """Extract a snippet around the keyword match."""
    if not text:
        return ""
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    idx = text_lower.find(keyword_lower)
    
    if idx == -1:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    start = max(0, idx - 100)
    end = min(len(text), idx + len(keyword) + 100)
    
    snippet = text[start:end]
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    return snippet

