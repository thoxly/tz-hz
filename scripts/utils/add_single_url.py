#!/usr/bin/env python3
"""Добавить одну ссылку в БД напрямую."""
import asyncio
import sys
from app.crawler import Crawler
from app.crawler.storage import Storage
from app.database.database import get_session_factory

async def add_url_to_db(url):
    """Добавить URL в БД."""
    print(f"🚀 Обработка ссылки: {url}")
    
    crawler = Crawler()
    storage = Storage()
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            async with crawler:
                print("⏳ Загружаю страницу...")
                
                # Пробуем разные варианты обработки редиректов
                try:
                    # Вариант 1: с максимальными редиректами
                    async with crawler.session.get(url, allow_redirects=True, max_redirects=20) as response:
                        print(f"Статус: {response.status}")
                        if response.status == 200:
                            html = await response.text()
                            print(f"✓ Загружено {len(html)} символов")
                            
                            # Парсим данные
                            parsed_data = crawler.parser.parse(html, url)
                            
                            from app.utils import extract_doc_id
                            from datetime import datetime
                            
                            doc_data = {
                                'doc_id': extract_doc_id(url),
                                'url': str(response.url),  # Финальный URL после редиректов
                                'title': parsed_data['title'],
                                'breadcrumbs': parsed_data['breadcrumbs'],
                                'section': parsed_data['section'],
                                'html': parsed_data['html'],
                                'plain_text': parsed_data['plain_text'],
                                'last_crawled': datetime.now(),
                                'links': parsed_data['links'],
                                'depth': 0
                            }
                            
                            print(f"📄 Документ: {doc_data['doc_id']}")
                            print(f"📝 Заголовок: {doc_data['title']}")
                            print(f"🔗 Найдено ссылок: {len(doc_data['links'])}")
                            
                            # Сохраняем в БД
                            print("💾 Сохранение в базу данных...")
                            result = await storage.save(session, doc_data)
                            await session.commit()
                            
                            print(f"✅ Успешно сохранено в БД!")
                            print(f"   Doc ID: {doc_data['doc_id']}")
                            print(f"   URL: {doc_data['url']}")
                            return True
                        else:
                            print(f"✗ Ошибка: статус {response.status}")
                            return False
                            
                except Exception as e:
                    print(f"✗ Ошибка при загрузке: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
                    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    url = "https://elma365.com/ru/help"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = asyncio.run(add_url_to_db(url))
    if success:
        print("\n✓ Данные записаны в базу данных!")
        print("Проверьте: http://127.0.0.1:8000/api/docs")
    else:
        print("\n✗ Не удалось сохранить данные")
        sys.exit(1)

