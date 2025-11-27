#!/usr/bin/env python3
"""Запуск краулинга с записью в БД."""
import asyncio
import sys
from app.crawler import Crawler
from app.crawler.storage import Storage
from app.database.database import get_session_factory

async def run_crawl(start_url):
    """Запустить краулинг и сохранить в БД."""
    print(f"🚀 Запуск краулинга: {start_url}")
    print("=" * 60)
    
    crawler = Crawler()
    storage = Storage()
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            async with crawler:
                print("⏳ Начинаю обработку...")
                docs = await crawler.crawl_recursive(start_url)
                print(f"\n📊 Найдено документов: {len(docs)}")
                
                if len(docs) == 0:
                    print("⚠ Не найдено документов. Возможно, проблема с подключением к сайту.")
                    print("Попробую обработать URL напрямую...")
                    
                    # Попробуем обработать URL напрямую
                    doc_data = await crawler._crawl_url(start_url, 0)
                    if doc_data:
                        docs = [doc_data]
                        print(f"✓ Найден документ: {doc_data.get('doc_id')}")
                
                saved_count = 0
                for i, doc_data in enumerate(docs, 1):
                    try:
                        print(f"[{i}/{len(docs)}] Сохранение: {doc_data.get('doc_id')}...", end=" ")
                        result = await storage.save(session, doc_data)
                        await session.commit()
                        saved_count += 1
                        print("✓")
                    except Exception as e:
                        print(f"✗ Ошибка: {e}")
                        await session.rollback()
                
                print(f"\n✅ Готово! Сохранено документов: {saved_count} из {len(docs)}")
                return saved_count > 0
                
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    start_url = "https://elma365.com/ru/help"
    if len(sys.argv) > 1:
        start_url = sys.argv[1]
    
    success = asyncio.run(run_crawl(start_url))
    if success:
        print("\n✓ Данные записаны в базу данных!")
        print("Проверьте: http://127.0.0.1:8000/api/docs")
    else:
        print("\n✗ Не удалось сохранить данные")
        sys.exit(1)

