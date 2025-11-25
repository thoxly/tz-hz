import json
import os
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.database.models import Doc

logger = logging.getLogger(__name__)


class Storage:
    """Storage handler for crawled documents."""
    
    def __init__(self):
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_to_db(self, session: AsyncSession, doc_data: Dict) -> Optional[Doc]:
        """Save or update document in PostgreSQL."""
        try:
            # Prepare data for JSONB content field
            content_data = {
                'html': doc_data.get('html'),
                'plain_text': doc_data.get('plain_text'),
                'breadcrumbs': doc_data.get('breadcrumbs', []),
                'links': doc_data.get('links', []),
                'raw_data': {
                    'depth': doc_data.get('depth', 0),
                    'crawled_at': doc_data.get('last_crawled').isoformat() if doc_data.get('last_crawled') else None
                }
            }
            
            # Use PostgreSQL upsert (INSERT ... ON CONFLICT)
            stmt = insert(Doc).values(
                doc_id=doc_data['doc_id'],
                url=doc_data['url'],
                title=doc_data.get('title'),
                section=doc_data.get('section'),
                content=content_data,
                last_crawled=doc_data.get('last_crawled', datetime.now())
            )
            
            stmt = stmt.on_conflict_do_update(
                index_elements=['doc_id'],
                set_=dict(
                    url=stmt.excluded.url,
                    title=stmt.excluded.title,
                    section=stmt.excluded.section,
                    content=stmt.excluded.content,
                    last_crawled=stmt.excluded.last_crawled
                )
            )
            
            await session.execute(stmt)
            await session.commit()
            
            # Fetch the saved document
            result = await session.execute(
                select(Doc).where(Doc.doc_id == doc_data['doc_id'])
            )
            doc = result.scalar_one_or_none()
            
            logger.info(f"Saved document to DB: {doc_data['doc_id']}")
            return doc
        
        except Exception as e:
            logger.error(f"Error saving document to DB: {e}")
            await session.rollback()
            return None
    
    def save_to_json(self, doc_data: Dict) -> Optional[str]:
        """Save document to local JSON file."""
        try:
            doc_id = doc_data['doc_id']
            # Sanitize filename
            safe_filename = doc_id.replace('/', '_').replace('\\', '_')
            filepath = self.output_dir / f"{safe_filename}.json"
            
            # Prepare JSON data
            json_data = {
                'doc_id': doc_data['doc_id'],
                'url': doc_data['url'],
                'title': doc_data.get('title'),
                'breadcrumbs': doc_data.get('breadcrumbs', []),
                'section': doc_data.get('section'),
                'html': doc_data.get('html'),
                'plain_text': doc_data.get('plain_text'),
                'links': doc_data.get('links', []),
                'last_crawled': doc_data.get('last_crawled').isoformat() if doc_data.get('last_crawled') else None,
                'metadata': {
                    'depth': doc_data.get('depth', 0),
                    'saved_at': datetime.now().isoformat()
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved document to JSON: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error saving document to JSON: {e}")
            return None
    
    async def save(self, session: AsyncSession, doc_data: Dict) -> Dict:
        """Save document to both database and local JSON file."""
        db_doc = await self.save_to_db(session, doc_data)
        json_path = self.save_to_json(doc_data)
        
        return {
            'doc_id': doc_data['doc_id'],
            'db_saved': db_doc is not None,
            'json_saved': json_path is not None,
            'json_path': json_path
        }

