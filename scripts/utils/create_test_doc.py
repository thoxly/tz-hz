#!/usr/bin/env python3
"""Создать тестовую запись в БД для проверки."""
import asyncio
from app.database.database import get_session_factory
from app.database.models import Doc
from datetime import datetime

async def create_test_doc():
    """Создать тестовый документ в БД."""
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        # Создаем тестовый документ
        test_doc = Doc(
            doc_id="test_help_page",
            url="https://elma365.com/ru/help",
            title="Тестовая страница помощи",
            section="Тест",
            content={
                "html": "<html><body><h1>Тестовая страница</h1><p>Это тестовая запись для проверки работы базы данных.</p></body></html>",
                "plain_text": "Тестовая страница\n\nЭто тестовая запись для проверки работы базы данных.",
                "breadcrumbs": ["Главная", "Помощь"],
                "links": []
            },
            last_crawled=datetime.now()
        )
        
        session.add(test_doc)
        await session.commit()
        
        print("✅ Тестовая запись создана в БД!")
        print(f"   Doc ID: {test_doc.doc_id}")
        print(f"   URL: {test_doc.url}")
        print(f"   Title: {test_doc.title}")
        return True

if __name__ == "__main__":
    asyncio.run(create_test_doc())
    print("\n✓ Проверьте: http://127.0.0.1:8000/api/docs")

