#!/usr/bin/env python3
"""Добавить ссылку в БД с обходом редиректов."""
import requests
import asyncio
import sys
from app.crawler.parser import HTMLParser
from app.crawler.storage import Storage
from app.database.database import get_session_factory
from app.utils import extract_doc_id
from datetime import datetime

async def add_url_to_db(url):
    """Добавить URL в БД с обработкой редиректов."""
    print(f"🚀 Обработка ссылки: {url}")
    
    storage = Storage()
    session_factory = get_session_factory()
    parser = HTMLParser("https://elma365.com")
    
    try:
        print("⏳ Загружаю страницу...")
        
        # Используем requests с ручной обработкой редиректов
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9'
        })
        
        # Обрабатываем редиректы вручную
        final_url = url
        max_redirects = 5
        redirect_count = 0
        
        while redirect_count < max_redirects:
            try:
                response = session.get(final_url, timeout=30, allow_redirects=False)
                print(f"Статус: {response.status_code}, URL: {final_url}")
                
                if response.status_code == 200:
                    break
                elif response.status_code in [301, 302, 303, 307, 308]:
                    redirect_url = response.headers.get('Location', '')
                    if redirect_url:
                        if redirect_url.startswith('/'):
                            from urllib.parse import urlparse
                            parsed = urlparse(final_url)
                            redirect_url = f"{parsed.scheme}://{parsed.netloc}{redirect_url}"
                        print(f"  → Редирект на: {redirect_url}")
                        final_url = redirect_url
                        redirect_count += 1
                    else:
                        break
                else:
                    break
            except Exception as e:
                print(f"Ошибка при загрузке: {e}")
                # Пробуем с автоматическими редиректами
                response = session.get(final_url, timeout=30, allow_redirects=True)
                break
        
        if redirect_count >= max_redirects:
            print("⚠ Достигнут лимит редиректов. Использую последний URL с автоматическими редиректами...")
            response = session.get(final_url, timeout=30, allow_redirects=True)
        
        print(f"✓ Финальный статус: {response.status_code}")
        final_url = str(response.url) if hasattr(response, 'url') else final_url
        print(f"✓ Финальный URL: {final_url}")
        
        if response.status_code == 200:
            print(f"✓ Размер: {len(response.text)} символов")
            
            # Парсим данные
            parsed_data = parser.parse(response.text, final_url)
            
            doc_data = {
                'doc_id': extract_doc_id(final_url),
                'url': final_url,
                'title': parsed_data['title'] or "Страница помощи",
                'breadcrumbs': parsed_data['breadcrumbs'],
                'section': parsed_data['section'] or "Помощь",
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
                
                return True
        else:
            print(f"✗ Ошибка: статус {response.status_code}")
            # Все равно создадим запись с базовой информацией
            print("Создаю запись с базовой информацией...")
            doc_data = {
                'doc_id': extract_doc_id(url),
                'url': url,
                'title': "Страница помощи (не удалось загрузить)",
                'breadcrumbs': [],
                'section': "Помощь",
                'html': f"<html><body><p>Не удалось загрузить страницу. Статус: {response.status_code}</p></body></html>",
                'plain_text': f"Не удалось загрузить страницу. Статус: {response.status_code}",
                'last_crawled': datetime.now(),
                'links': [],
                'depth': 0
            }
            
            async with session_factory() as db_session:
                result = await storage.save(db_session, doc_data)
                await db_session.commit()
                print("✅ Базовая запись создана в БД")
                return True
            
    except requests.exceptions.TooManyRedirects:
        print("⚠ Слишком много редиректов. Создаю запись с информацией о проблеме...")
        # Создаем запись о проблеме
        doc_data = {
            'doc_id': extract_doc_id(url),
            'url': url,
            'title': "Страница помощи (проблема с редиректами)",
            'breadcrumbs': [],
            'section': "Помощь",
            'html': "<html><body><p>Не удалось загрузить страницу из-за бесконечных редиректов.</p></body></html>",
            'plain_text': "Не удалось загрузить страницу из-за бесконечных редиректов.",
            'last_crawled': datetime.now(),
            'links': [],
            'depth': 0
        }
        
        async with session_factory() as db_session:
            result = await storage.save(db_session, doc_data)
            await db_session.commit()
            print("✅ Запись создана в БД (с информацией о проблеме)")
            return True
            
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

