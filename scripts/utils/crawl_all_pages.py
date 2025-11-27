#!/usr/bin/env python3
"""Получить все страницы из https://elma365.com/ru/help."""
import requests
import asyncio
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.crawler.parser import HTMLParser
from app.crawler.storage import Storage
from app.database.database import get_session_factory
from app.utils import extract_doc_id, normalize_url, is_valid_help_url
from datetime import datetime
from typing import Set, List

async def crawl_all_pages(start_url):
    """Получить все страницы из раздела помощи."""
    print(f"🚀 Начинаю сбор всех страниц из: {start_url}")
    print("=" * 60)
    
    storage = Storage()
    session_factory = get_session_factory()
    parser = HTMLParser("https://elma365.com")
    
    # Создаем сессию с правильными заголовками
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    visited_urls: Set[str] = set()
    urls_to_process: List[str] = [start_url]
    base_url = "https://elma365.com"
    saved_count = 0
    
    try:
        # Пробуем получить главную страницу, обходя редиректы
        print("⏳ Получаю главную страницу...")
        
        # Пробуем разные варианты URL
        test_urls = [
            "https://elma365.com/ru/help/",
            "http://elma365.com/ru/help/",
            "https://elma365.com/help/",
            "https://elma365.com/ru/help"
        ]
        
        main_page_html = None
        main_page_url = None
        
        for test_url in test_urls:
            try:
                print(f"  Пробую: {test_url}")
                response = session.get(test_url, timeout=30, allow_redirects=True)
                if response.status_code == 200 and len(response.text) > 1000:
                    main_page_html = response.text
                    main_page_url = str(response.url)
                    print(f"  ✓ Успешно загружено: {main_page_url} ({len(main_page_html)} символов)")
                    break
            except Exception as e:
                print(f"  ✗ Ошибка: {e}")
                continue
        
        if not main_page_html:
            print("⚠ Не удалось загрузить главную страницу через requests")
            print("Пробую использовать BeautifulSoup напрямую...")
            
            # Попробуем через другой метод
            try:
                response = session.get("https://elma365.com", timeout=30)
                if response.status_code == 200:
                    # Попробуем найти ссылку на help
                    soup = BeautifulSoup(response.text, 'html.parser')
                    help_link = soup.find('a', href=lambda x: x and '/help' in x)
                    if help_link:
                        help_url = urljoin("https://elma365.com", help_link['href'])
                        print(f"Найдена ссылка на help: {help_url}")
                        response = session.get(help_url, timeout=30, allow_redirects=True)
                        if response.status_code == 200:
                            main_page_html = response.text
                            main_page_url = str(response.url)
            except Exception as e:
                print(f"Ошибка: {e}")
        
        if not main_page_html:
            print("❌ Не удалось загрузить главную страницу")
            print("Создаю запись с информацией о проблеме...")
            
            # Создаем базовую запись
            doc_data = {
                'doc_id': 'help_main',
                'url': start_url,
                'title': 'Главная страница помощи (не удалось загрузить)',
                'breadcrumbs': [],
                'section': 'Помощь',
                'html': '<html><body><p>Не удалось загрузить страницу из-за проблем с редиректами.</p></body></html>',
                'plain_text': 'Не удалось загрузить страницу из-за проблем с редиректами.',
                'last_crawled': datetime.now(),
                'links': [],
                'depth': 0
            }
            
            async with session_factory() as db_session:
                await storage.save(db_session, doc_data)
                await db_session.commit()
                print("✓ Базовая запись создана")
            
            return False
        
        # Парсим главную страницу
        print(f"\n📄 Парсинг главной страницы...")
        parsed_data = parser.parse(main_page_html, main_page_url)
        
        print(f"  Заголовок: {parsed_data['title']}")
        print(f"  Найдено ссылок: {len(parsed_data['links'])}")
        
        # Сохраняем главную страницу
        doc_data = {
            'doc_id': extract_doc_id(main_page_url),
            'url': main_page_url,
            'title': parsed_data['title'] or 'Главная страница помощи',
            'breadcrumbs': parsed_data['breadcrumbs'],
            'section': parsed_data['section'] or 'Помощь',
            'html': parsed_data['html'],
            'plain_text': parsed_data['plain_text'],
            'last_crawled': datetime.now(),
            'links': parsed_data['links'],
            'depth': 0
        }
        
        async with session_factory() as db_session:
            await storage.save(db_session, doc_data)
            await db_session.commit()
            saved_count += 1
            print(f"✓ Главная страница сохранена: {doc_data['doc_id']}")
        
        visited_urls.add(main_page_url)
        
        # Собираем все ссылки
        all_links = set()
        for link in parsed_data['links']:
            normalized = normalize_url(link, base_url)
            if is_valid_help_url(normalized, base_url) or '/help' in normalized:
                all_links.add(normalized)
        
        print(f"\n🔗 Найдено уникальных ссылок: {len(all_links)}")
        print(f"⏳ Начинаю обработку ссылок...\n")
        
        # Обрабатываем все найденные ссылки
        for i, link_url in enumerate(sorted(all_links), 1):
            if link_url in visited_urls:
                continue
            
            try:
                print(f"[{i}/{len(all_links)}] Обработка: {link_url[:80]}...", end=" ")
                
                response = session.get(link_url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    final_url = str(response.url)
                    # Убеждаемся, что текст правильно декодирован
                    response.encoding = response.apparent_encoding or 'utf-8'
                    html = response.text
                    # Дополнительная проверка кодировки
                    if isinstance(html, bytes):
                        html = html.decode('utf-8', errors='ignore')
                    
                    if len(html) > 500:  # Проверяем, что это реальная страница
                        parsed = parser.parse(html, final_url)
                        
                        doc_data = {
                            'doc_id': extract_doc_id(final_url),
                            'url': final_url,
                            'title': parsed['title'] or 'Страница помощи',
                            'breadcrumbs': parsed['breadcrumbs'],
                            'section': parsed['section'] or 'Помощь',
                            'html': parsed['html'],
                            'plain_text': parsed['plain_text'],
                            'last_crawled': datetime.now(),
                            'links': parsed['links'],
                            'depth': 1
                        }
                        
                        async with session_factory() as db_session:
                            await storage.save(db_session, doc_data)
                            await db_session.commit()
                            saved_count += 1
                        
                        visited_urls.add(final_url)
                        print("✓")
                    else:
                        print("⚠ (слишком короткая)")
                else:
                    print(f"✗ (статус {response.status_code})")
                    
            except Exception as e:
                print(f"✗ ({str(e)[:50]})")
                continue
        
        print(f"\n" + "=" * 60)
        print(f"✅ ГОТОВО! Сохранено документов: {saved_count}")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    start_url = "https://elma365.com/ru/help"
    
    success = asyncio.run(crawl_all_pages(start_url))
    
    if success:
        print("\n✓ Все страницы записаны в базу данных!")
        print("Проверьте: http://127.0.0.1:8000/api/docs")
    else:
        print("\n⚠ Завершено с ошибками")
        sys.exit(1)

