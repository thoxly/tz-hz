#!/usr/bin/env python3
"""Добавить ссылку в БД используя requests (обход проблемы с редиректами)."""
import requests
import asyncio
import sys
from bs4 import BeautifulSoup
from app.crawler.parser import HTMLParser
from app.crawler.storage import Storage
from app.database.database import get_session_factory
from app.utils import extract_doc_id
from datetime import datetime

async def add_url_to_db(url):
    """Добавить URL в БД используя requests."""
    print(f"🚀 Обработка ссылки: {url}")
    
    storage = Storage()
    session_factory = get_session_factory()
    parser = HTMLParser("https://elma365.com")
    
    try:
        # Используем requests для обхода проблемы с редиректами
        print("⏳ Загружаю страницу через requests...")
        session = requests.Session()
        session.max_redirects = 20
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        })
        
        response = session.get(url, timeout=30, allow_redirects=True)
        print(f"✓ Статус: {response.status_code}")
        print(f"✓ Финальный URL: {response.url}")
        print(f"✓ Размер: {len(response.text)} символов")
        
        if response.status_code == 200:
            # Парсим данные
            parsed_data = parser.parse(response.text, str(response.url))
            
            doc_data = {
                'doc_id': extract_doc_id(str(response.url)),
                'url': str(response.url),
                'title': parsed_data['title'],
                'breadcrumbs': parsed_data['breadcrumbs'],
                'section': parsed_data['section'],
                'html': parsed_data['html'],
                'plain_text': parsed_data['plain_text'],
                'last_crawled': datetime.now(),
                'links': parsed_data['links'],
                'depth': 0
            }
            
            print(f"\n📄 Документ: {doc_data['doc_id']}")
            print(f"📝 Заголовок: {doc_data['title']}")
            print(f"🔗 Найдено ссылок: {len(doc_data['links'])}")
            
            # Сохраняем в БД
            print("\n💾 Сохранение в базу данных...")
            async with session_factory() as db_session:
                result = await storage.save(db_session, doc_data)
                await db_session.commit()
                
                print(f"✅ Успешно сохранено в БД!")
                print(f"   Doc ID: {doc_data['doc_id']}")
                print(f"   URL: {doc_data['url']}")
                print(f"   Найдено ссылок на странице: {len(doc_data['links'])}")
                
                # Показываем первые несколько ссылок
                if doc_data['links']:
                    print(f"\n📋 Первые ссылки на странице:")
                    for i, link in enumerate(doc_data['links'][:5], 1):
                        print(f"   {i}. {link}")
                    if len(doc_data['links']) > 5:
                        print(f"   ... и еще {len(doc_data['links']) - 5} ссылок")
                
                return True
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    url = "https://elma365.com/ru/help"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = asyncio.run(add_url_to_db(url))
    if success:
        print("\n" + "="*60)
        print("✓ ДАННЫЕ ЗАПИСАНЫ В БАЗУ ДАННЫХ!")
        print("="*60)
        print("Проверьте результаты:")
        print("  http://127.0.0.1:8000/api/docs")
        print("="*60)
    else:
        print("\n✗ Не удалось сохранить данные")
        sys.exit(1)

