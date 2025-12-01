from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.database.models import Doc
import logging

logger = logging.getLogger(__name__)


async def search_docs(input_data: Dict[str, Any], db_session: AsyncSession) -> Dict[str, Any]:
    """
    Search ELMA365 documentation by query.
    
    Args:
        input_data: Dict with 'query' key
        db_session: Database session
    
    Returns:
        Dict with 'results' key containing list of matching documents
    """
    query = input_data.get("query", "").strip()
    
    if not query:
        return {"results": []}
    
    try:
        # Search in title, section, and plain_text using ILIKE (case-insensitive)
        # Extract plain_text from JSONB content field
        search_pattern = f"%{query}%"
        
        # Build query to search across multiple fields
        stmt = select(
            Doc.doc_id,
            Doc.title,
            Doc.section,
            Doc.content['plain_text'].astext.label('plain_text')
        ).where(
            or_(
                Doc.title.ilike(search_pattern),
                Doc.section.ilike(search_pattern),
                Doc.content['plain_text'].astext.ilike(search_pattern)
            )
        ).limit(50)  # Limit results
        
        result = await db_session.execute(stmt)
        rows = result.all()
        
        results = []
        for row in rows:
            # Extract snippet from plain_text
            plain_text = row.plain_text or ""
            snippet = _extract_snippet(plain_text, query, max_length=200)
            
            results.append({
                "doc_id": row.doc_id,
                "title": row.title or "",
                "section": row.section or "",
                "snippet": snippet
            })
        
        logger.info(f"Search for '{query}' returned {len(results)} results")
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error searching docs: {e}", exc_info=True)
        raise


def _extract_snippet(text: str, query: str, max_length: int = 200) -> str:
    """Extract a snippet around the query match."""
    if not text:
        return ""
    
    text_lower = text.lower()
    query_lower = query.lower()
    
    # Find first occurrence
    idx = text_lower.find(query_lower)
    
    if idx == -1:
        # No match, return beginning
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Extract context around match
    start = max(0, idx - 50)
    end = min(len(text), idx + len(query) + 50)
    
    snippet = text[start:end]
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    return snippet

