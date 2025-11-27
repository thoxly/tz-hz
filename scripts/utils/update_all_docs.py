#!/usr/bin/env python3
"""Обновить все документы в БД с улучшенным парсером."""
import asyncio
import requests
from app.database.database import get_session_factory
from app.database.models import Doc
from app.crawler.parser import HTMLParser
from app.crawler.storage import Storage
from sqlalchemy import select
from datetime import datetime

async def update_all_docs():
    """Обновить все документы в БД."""
    print("🔄 Обновление всех документов в базе данных...")
    print("=" * 60)
    
    session_factory = get_session_factory()
    parser = HTMLParser("https://elma365.com")
    storage = Storage()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    async with session_factory() as db_session:
        # Получаем все документы
        result = await db_session.execute(select(Doc))
        docs = result.scalars().all()
        
        total = len(docs)
        print(f"📊 Найдено документов для обновления: {total}")
        print("⏳ Начинаю обновление...\n")
        
        updated_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Сначала собираем все данные
        docs_to_update = []
        
        for i, doc in enumerate(docs, 1):
            try:
                print(f"[{i}/{total}] {doc.doc_id[:50]}...", end=" ")
                
                # Загружаем страницу заново
                try:
                    response = session.get(doc.url, timeout=30, allow_redirects=True)
                    
                    if response.status_code == 200:
                        # Убеждаемся в правильной кодировке
                        response.encoding = response.apparent_encoding or 'utf-8'
                        html = response.text
                        
                        if isinstance(html, bytes):
                            html = html.decode('utf-8', errors='ignore')
                        
                        # Парсим с улучшенным парсером
                        parsed_data = parser.parse(html, str(response.url))
                        
                        docs_to_update.append({
                            'doc_id': doc.doc_id,
                            'title': parsed_data['title'] or doc.title or 'Без названия',
                            'section': parsed_data['section'] or doc.section or '',
                            'content': {
                                'html': parsed_data['html'],
                                'plain_text': parsed_data['plain_text'],
                                'breadcrumbs': parsed_data['breadcrumbs'],
                                'links': parsed_data['links'],
                                'raw_data': (doc.content or {}).get('raw_data', {
                                    'depth': 0,
                                    'crawled_at': datetime.now().isoformat()
                                })
                            },
                            'url': str(response.url)
                        })
                        
                        updated_count += 1
                        print("✓")
                    else:
                        print(f"✗ (статус {response.status_code})")
                        failed_count += 1
                        
                except requests.exceptions.TooManyRedirects:
                    print("⚠ (редиректы)")
                    skipped_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"✗ ({str(e)[:30]})")
                    failed_count += 1
                except Exception as e:
                    print(f"✗ ({str(e)[:30]})")
                    failed_count += 1
                    
            except Exception as e:
                print(f"✗ Ошибка: {str(e)[:50]}")
                failed_count += 1
                continue
        
        # Теперь обновляем БД
        print(f"\n💾 Сохранение обновлений в БД...")
        for update_data in docs_to_update:
            try:
                result = await db_session.execute(
                    select(Doc).where(Doc.doc_id == update_data['doc_id'])
                )
                doc = result.scalar_one_or_none()
                
                if doc:
                    doc.title = update_data['title']
                    doc.section = update_data['section']
                    doc.content = update_data['content']
                    doc.url = update_data['url']
                    doc.last_crawled = datetime.now()
                    await db_session.commit()
            except Exception as e:
                print(f"Ошибка при сохранении {update_data['doc_id']}: {e}")
                await db_session.rollback()
        
        print(f"\n" + "=" * 60)
        print(f"✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО")
        print("=" * 60)
        print(f"📊 Статистика:")
        print(f"  Всего документов: {total}")
        print(f"  ✅ Обновлено: {updated_count}")
        print(f"  ⚠ Пропущено: {skipped_count}")
        print(f"  ✗ Ошибок: {failed_count}")
        print("=" * 60)
        
        if updated_count > 0:
            print(f"\n✓ {updated_count} документов обновлено с улучшенным парсером!")
            print("Теперь весь текст извлекается правильно, без иероглифов.")
        
        return updated_count > 0

if __name__ == "__main__":
    print("🚀 Запуск обновления базы данных...")
    print("Это может занять некоторое время в зависимости от количества документов.\n")
    
    success = asyncio.run(update_all_docs())
    
    if success:
        print("\n✓ База данных обновлена!")
        print("Проверьте результаты: http://127.0.0.1:8000/api/docs")
    else:
        print("\n⚠ Обновление завершено с ошибками")
        import sys
        sys.exit(1)

