from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import asyncio
import logging

from app.database import get_db
from app.database.models import Doc, Entity
from app.crawler import Crawler
from app.crawler.storage import Storage
from app.normalizer import Normalizer, EntityExtractor
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Global crawler instance
crawler_instance: Optional[Crawler] = None
crawler_task: Optional[asyncio.Task] = None


# Pydantic models for requests/responses
class CrawlStartRequest(BaseModel):
    start_url: Optional[str] = None


class CrawlUrlRequest(BaseModel):
    url: str


class CrawlStatusResponse(BaseModel):
    is_crawling: bool
    visited_count: int
    queue_size: int
    stats: dict


class DocResponse(BaseModel):
    id: int
    doc_id: str
    url: str
    title: Optional[str]
    section: Optional[str]
    created_at: Optional[str] = None
    last_crawled: Optional[str] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle datetime serialization."""
        data = {
            'id': obj.id,
            'doc_id': obj.doc_id,
            'url': obj.url,
            'title': obj.title,
            'section': obj.section,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'last_crawled': obj.last_crawled.isoformat() if obj.last_crawled else None,
        }
        return cls(**data)


class EntityResponse(BaseModel):
    id: int
    doc_id: str
    type: str
    data: dict
    created_at: str

    class Config:
        from_attributes = True


class PlainTextResponse(BaseModel):
    id: int
    doc_id: str
    plain_text: Optional[str]

    class Config:
        from_attributes = True


@router.post("/crawl/start")
async def start_crawl(
    request: CrawlStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start recursive crawl from /help/ or specified URL."""
    global crawler_instance, crawler_task
    
    if crawler_instance and crawler_instance.is_crawling:
        raise HTTPException(status_code=400, detail="Crawler is already running")
    
    crawler_instance = Crawler()
    storage = Storage()
    
    async def crawl_and_save():
        # Create a new database session for the background task
        from app.database import get_session_factory
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                async with crawler_instance:
                    docs = await crawler_instance.crawl_recursive(request.start_url)
                    
                    # Save each document
                    for doc_data in docs:
                        await storage.save(session, doc_data)
                        await session.commit()
                        logger.info(f"Successfully saved document: {doc_data.get('doc_id')}")
            except Exception as e:
                logger.error(f"Error in crawl_and_save: {e}", exc_info=True)
                await session.rollback()
    
    crawler_task = asyncio.create_task(crawl_and_save())
    
    return {
        "message": "Crawl started",
        "start_url": request.start_url or f"{settings.CRAWL_BASE_URL}/help/"
    }


@router.post("/crawl/url")
async def add_crawl_url(
    request: CrawlUrlRequest,
    db: AsyncSession = Depends(get_db)
):
    """Manually add URL to crawl queue."""
    global crawler_instance
    
    if not crawler_instance:
        crawler_instance = Crawler()
    
    crawler_instance.add_url(request.url)
    
    # If not crawling, start a crawl task
    if not crawler_instance.is_crawling:
        storage = Storage()
        
        async def crawl_and_save():
            # Create a new database session for the background task
            from app.database.database import get_session_factory
            session_factory = get_session_factory()
            async with session_factory() as session:
                try:
                    # Use async context manager for crawler to ensure HTTP session is open
                    async with crawler_instance:
                        doc_data = await crawler_instance._crawl_url(request.url, 0)
                        if doc_data:
                            await storage.save(session, doc_data)
                            await session.commit()
                            logger.info(f"Successfully saved document: {doc_data.get('doc_id')}")
                        else:
                            logger.warning(f"No data returned from crawl_url for: {request.url}")
                except Exception as e:
                    logger.error(f"Error in crawl_and_save: {e}", exc_info=True)
                    await session.rollback()
        
        asyncio.create_task(crawl_and_save())
    
    return {"message": f"URL added to queue: {request.url}"}


@router.get("/crawl/status", response_model=CrawlStatusResponse)
async def get_crawl_status():
    """Get current crawling status."""
    global crawler_instance
    
    if not crawler_instance:
        return CrawlStatusResponse(
            is_crawling=False,
            visited_count=0,
            queue_size=0,
            stats={}
        )
    
    status = crawler_instance.get_status()
    return CrawlStatusResponse(**status)


@router.post("/normalize/{doc_id}")
async def normalize_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Normalize a specific document."""
    # Get document from database
    result = await db.execute(
        select(Doc).where(Doc.doc_id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get HTML from content JSONB
    content = doc.content or {}
    html = content.get('html', '')
    
    if not html:
        raise HTTPException(status_code=400, detail="Document has no HTML content")
    
    # Normalize
    normalizer = Normalizer()
    normalized = normalizer.normalize(
        html,
        title=doc.title,
        breadcrumbs=content.get('breadcrumbs', [])
    )
    
    # Update document content
    doc.content = normalized
    await db.commit()
    await db.refresh(doc)
    
    # Extract entities
    entity_extractor = EntityExtractor()
    entities = await entity_extractor.extract_and_save_entities(
        db,
        doc_id,
        normalized
    )
    
    return {
        "doc_id": doc_id,
        "normalized": True,
        "blocks_count": len(normalized.get('blocks', [])),
        "entities_count": len(entities)
    }


@router.post("/normalize/all")
async def normalize_all(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Normalize all crawled documents."""
    # Get all documents
    result = await db.execute(select(Doc))
    docs = result.scalars().all()
    
    async def normalize_docs():
        normalizer = Normalizer()
        entity_extractor = EntityExtractor()
        
        for doc in docs:
            try:
                content = doc.content or {}
                html = content.get('html', '')
                
                if not html:
                    continue
                
                # Normalize
                normalized = normalizer.normalize(
                    html,
                    title=doc.title,
                    breadcrumbs=content.get('breadcrumbs', [])
                )
                
                # Update document
                doc.content = normalized
                await db.commit()
                
                # Extract entities
                await entity_extractor.extract_and_save_entities(
                    db,
                    doc.doc_id,
                    normalized
                )
                
                logger.info(f"Normalized document: {doc.doc_id}")
            
            except Exception as e:
                logger.error(f"Error normalizing {doc.doc_id}: {e}")
                await db.rollback()
    
    asyncio.create_task(normalize_docs())
    
    return {
        "message": "Normalization started for all documents",
        "total_docs": len(docs)
    }


@router.get("/docs", response_model=List[DocResponse])
async def list_docs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all documents."""
    result = await db.execute(
        select(Doc).offset(skip).limit(limit).order_by(Doc.created_at.desc())
    )
    docs = result.scalars().all()
    return [DocResponse.from_orm(doc) for doc in docs]


@router.get("/docs/{doc_id}", response_model=DocResponse)
async def get_doc(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get document details."""
    result = await db.execute(
        select(Doc).where(Doc.doc_id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocResponse.from_orm(doc)


@router.get("/entities/{doc_id}", response_model=List[EntityResponse])
async def get_entities(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get entities for a document."""
    # Verify document exists
    doc_result = await db.execute(
        select(Doc).where(Doc.doc_id == doc_id)
    )
    doc = doc_result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get entities
    result = await db.execute(
        select(Entity).where(Entity.doc_id == doc_id).order_by(Entity.created_at)
    )
    entities = result.scalars().all()
    return entities


@router.get("/docs/plain-text", response_model=List[PlainTextResponse])
async def get_docs_plain_text(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get only plain_text from documents content (normalized data)."""
    # Extract plain_text from JSONB content field using PostgreSQL JSONB operators
    # content->>'plain_text' extracts plain_text as text
    # Using .astext to extract as text (equivalent to ->> operator)
    result = await db.execute(
        select(
            Doc.id,
            Doc.doc_id,
            Doc.content['plain_text'].astext.label('plain_text')
        )
        .offset(skip)
        .limit(limit)
        .order_by(Doc.id.asc())
    )
    
    rows = result.all()
    return [
        PlainTextResponse(
            id=row.id,
            doc_id=row.doc_id,
            plain_text=row.plain_text
        )
        for row in rows
    ]

