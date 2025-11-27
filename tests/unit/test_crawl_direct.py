#!/usr/bin/env python3
"""Прямой тест краулера для отладки."""
import asyncio
import sys
from app.crawler import Crawler
from app.crawler.storage import Storage
from app.database.database import get_session_factory

async def test_crawl():
    """Тест краулинга."""
    start_url = "https://elma365.com/ru/help"
    print(f"Тестирую краулинг с: {start_url}")
    
    crawler = Crawler()
    storage = Storage()
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            async with crawler:
                print("Начинаю краулинг...")
                print("Проверяю подключение к сайту...")
                
                # Тест подключения
                import aiohttp
                try:
                    async with crawler.session.get(start_url) as response:
                        print(f"Статус ответа: {response.status}")
                        if response.status == 200:
                            html = await response.text()
                            print(f"Размер HTML: {len(html)} символов")
                        else:
                            print(f"Ошибка: статус {response.status}")
                except Exception as e:
                    print(f"Ошибка подключения: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                
                docs = await crawler.crawl_recursive(start_url)
                print(f"Найдено документов: {len(docs)}")
                
                for doc_data in docs:
                    print(f"Сохранение: {doc_data.get('doc_id')}")
                    await storage.save(session, doc_data)
                    await session.commit()
                    print(f"✓ Сохранено: {doc_data.get('doc_id')}")
                
                print(f"\n✓ Всего сохранено: {len(docs)}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_crawl())
    sys.exit(0 if success else 1)

