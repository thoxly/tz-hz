#!/usr/bin/env python3
"""Исправить кодировку в существующих документах."""
import asyncio
import requests
from app.database.database import get_session_factory
from app.database.models import Doc
from app.crawler.parser import HTMLParser
from app.crawler.storage import Storage
from sqlalchemy import select
from datetime import datetime

async def fix_encoding():
    """Исправить кодировку во всех документах."""
    print("🔧 Исправление кодировки в документах...")
    print("=" * 60)
    
    session_factory = get_session_factory()
    parser = HTMLParser("https://elma365.com")
    storage = Storage()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9'
    })
    
    async with session_factory() as db_session:
        # Получаем все документы
        result = await db_session.execute(select(Doc))
        docs = result.scalars().all()
        
        print(f"Найдено документов: {len(docs)}")
        print("Начинаю исправление...\n")
        
        fixed_count = 0
        
        for i, doc in enumerate(docs, 1):
            try:
                print(f"[{i}/{len(docs)}] {doc.doc_id}...", end=" ")
                
                # Загружаем страницу заново с правильной кодировкой
                response = session.get(doc.url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding or 'utf-8'
                    html = response.text
                    
                    if isinstance(html, bytes):
                        html = html.decode('utf-8', errors='ignore')
                    
                    # Парсим заново
                    parsed_data = parser.parse(html, str(response.url))
                    
                    # Обновляем документ
                    doc.title = parsed_data['title'] or doc.title
                    doc.section = parsed_data['section'] or doc.section
                    doc.content = {
                        'html': parsed_data['html'],
                        'plain_text': parsed_data['plain_text'],
                        'breadcrumbs': parsed_data['breadcrumbs'],
                        'links': parsed_data['links'],
                        'raw_data': doc.content.get('raw_data', {}) if doc.content else {}
                    }
                    doc.last_crawled = datetime.now()
                    
                    await db_session.commit()
                    fixed_count += 1
                    print("✓")
                else:
                    print(f"✗ (статус {response.status_code})")
                    
            except Exception as e:
                print(f"✗ ({str(e)[:50]})")
                await db_session.rollback()
                continue
        
        print(f"\n" + "=" * 60)
        print(f"✅ Исправлено документов: {fixed_count} из {len(docs)}")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(fix_encoding())
    print("\n✓ Кодировка исправлена!")
    print("Проверьте: http://127.0.0.1:8000/api/docs")

