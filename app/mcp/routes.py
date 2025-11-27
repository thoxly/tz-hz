"""
MCP API Routes - эндпоинты для агент-архитектора.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.database import get_db
from app.mcp.tools import MCPTools

router = APIRouter()


# Request/Response models
class GetDocResponse(BaseModel):
    title: Optional[str]
    breadcrumbs: List[str]
    blocks: List[Dict[str, Any]]
    plain_text: str
    url: str


class SearchEntitiesRequest(BaseModel):
    type: str  # header, list, code_block, special_block, paragraph
    filters: Optional[Dict[str, Any]] = None


class FindRelevantRequest(BaseModel):
    query: str
    limit: int = 20


class ListDocsBySectionRequest(BaseModel):
    section: str


@router.get("/mcp/doc/{doc_id}", response_model=GetDocResponse)
async def mcp_get_doc(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить документ по ID.
    Возвращает структурированные данные для LLM.
    """
    tools = MCPTools(db)
    doc = await tools.get_doc(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    return GetDocResponse(**doc)


@router.post("/mcp/entities/search")
async def mcp_search_entities(
    request: SearchEntitiesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск сущностей с фильтрами.
    
    Примеры запросов:
    - {"type": "header", "filters": {"level": 2}}
    - {"type": "list", "filters": {"breadcrumbs": ["Платформа"]}}
    - {"type": "code_block", "filters": {"language": "python"}}
    - {"type": "special_block", "filters": {"kind": "В этой статье"}}
    """
    tools = MCPTools(db)
    entities = await tools.search_entities(request.type, request.filters)
    
    return {
        "type": request.type,
        "count": len(entities),
        "entities": entities
    }


@router.post("/mcp/search")
async def mcp_find_relevant(
    request: FindRelevantRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Полнотекстовый поиск по документам.
    Детерминированный поиск без embeddings.
    """
    tools = MCPTools(db)
    results = await tools.find_relevant(request.query, request.limit)
    
    return {
        "query": request.query,
        "count": len(results),
        "results": results
    }


@router.get("/mcp/docs/section/{section}")
async def mcp_list_docs_by_section(
    section: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список документов по разделу.
    
    Примеры:
    - /mcp/docs/section/platform
    - /mcp/docs/section/crm
    - /mcp/docs/section/ecm
    """
    tools = MCPTools(db)
    docs = await tools.list_docs_by_section(section)
    
    return {
        "section": section,
        "count": len(docs),
        "docs": docs
    }


@router.get("/mcp/entities/headers")
async def mcp_get_headers(
    level: Optional[int] = Query(None, description="Уровень заголовка (1-6)"),
    breadcrumbs: Optional[str] = Query(None, description="Breadcrumbs через запятую"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Быстрый доступ к заголовкам.
    
    Примеры:
    - /mcp/entities/headers?level=2
    - /mcp/entities/headers?breadcrumbs=Платформа,Приложения
    """
    tools = MCPTools(db)
    
    filters = {}
    if level is not None:
        filters['level'] = level
    if breadcrumbs:
        filters['breadcrumbs'] = [b.strip() for b in breadcrumbs.split(',')]
    filters['limit'] = limit
    
    entities = await tools.search_entities('header', filters)
    
    return {
        "type": "header",
        "count": len(entities),
        "entities": entities
    }


@router.get("/mcp/entities/special-blocks")
async def mcp_get_special_blocks(
    kind: Optional[str] = Query(None, description="Тип блока (В этой статье, Важно, Пример)"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """
    Быстрый доступ к специальным блокам.
    
    Примеры:
    - /mcp/entities/special-blocks?kind=В этой статье
    - /mcp/entities/special-blocks?kind=Важно
    """
    tools = MCPTools(db)
    
    filters = {}
    if kind:
        filters['kind'] = kind
    filters['limit'] = limit
    
    entities = await tools.search_entities('special_block', filters)
    
    return {
        "type": "special_block",
        "count": len(entities),
        "entities": entities
    }


