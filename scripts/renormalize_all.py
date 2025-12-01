#!/usr/bin/env python3
"""
Скрипт для перенормализации всех документов в базе данных.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from app.database.database import get_session_factory
from app.database.models import Doc
from app.normalizer.normalizer import Normalizer
from app.normalizer.entity_extractor import EntityExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def renormalize_all(force: bool = True):
    """Перенормализовать все документы в базе данных."""
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        try:
            # Get all documents
            result = await session.execute(select(Doc))
            all_docs = result.scalars().all()
            total_docs = len(all_docs)
            
            logger.info(f"Found {total_docs} documents in database")
            
            if total_docs == 0:
                logger.warning("No documents found in database")
                return
            
            normalizer = Normalizer()
            entity_extractor = EntityExtractor()
            
            processed = 0
            errors = 0
            skipped = 0
            
            for doc in all_docs:
                try:
                    content = doc.content or {}
                    html = content.get('html', '')
                    
                    # Skip if no HTML
                    if not html:
                        skipped += 1
                        logger.debug(f"Skipping {doc.doc_id}: no HTML content")
                        continue
                    
                    # Skip if already normalized (unless force=True)
                    if not force and 'blocks' in content:
                        skipped += 1
                        logger.debug(f"Skipping {doc.doc_id}: already normalized")
                        continue
                    
                    logger.info(f"Normalizing {doc.doc_id} ({doc.url})...")
                    
                    # Normalize
                    normalized = normalizer.normalize(
                        html,
                        title=doc.title,
                        breadcrumbs=content.get('breadcrumbs', []),
                        source_url=doc.url
                    )
                    
                    # Update document
                    doc.content = normalized
                    await session.commit()
                    
                    # Extract entities
                    await entity_extractor.extract_and_save_entities(
                        session,
                        doc.doc_id,
                        normalized
                    )
                    
                    processed += 1
                    if processed % 10 == 0:
                        logger.info(f"Progress: {processed}/{total_docs} processed, {skipped} skipped, {errors} errors")
                
                except Exception as e:
                    errors += 1
                    logger.error(f"Error normalizing {doc.doc_id}: {e}", exc_info=True)
                    await session.rollback()
            
            logger.info(f"Normalization completed!")
            logger.info(f"  Processed: {processed}")
            logger.info(f"  Skipped: {skipped}")
            logger.info(f"  Errors: {errors}")
        
        except Exception as e:
            logger.error(f"Error in renormalize_all: {e}", exc_info=True)
            await session.rollback()
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Renormalize all documents in database")
    parser.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Renormalize all documents even if already normalized (default: True)"
    )
    parser.add_argument(
        "--no-force",
        action="store_false",
        dest="force",
        help="Skip already normalized documents"
    )
    
    args = parser.parse_args()
    
    asyncio.run(renormalize_all(force=args.force))

