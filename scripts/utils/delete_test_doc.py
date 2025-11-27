#!/usr/bin/env python3
"""Удалить тестовый документ."""
import asyncio
from app.database.database import get_session_factory
from app.database.models import Doc
from sqlalchemy import select, delete

async def delete_test_doc():
    """Удалить тестовый документ."""
    session_factory = get_session_factory()
    
    async with session_factory() as db_session:
        # Ищем тестовый документ
        result = await db_session.execute(
            select(Doc).where(Doc.doc_id == 'test_help_page')
        )
        doc = result.scalar_one_or_none()
        
        if doc:
            await db_session.delete(doc)
            await db_session.commit()
            print(f"✓ Тестовый документ '{doc.doc_id}' удален")
            return True
        else:
            print("⚠ Тестовый документ не найден")
            return False

if __name__ == "__main__":
    asyncio.run(delete_test_doc())

