#!/usr/bin/env python3
"""Тест парсера на примере страницы календаря."""
import requests
from app.crawler.parser import HTMLParser

def test_parser(url):
    """Протестировать парсер на конкретной странице."""
    print(f"🔍 Тестирую парсер на странице: {url}")
    print("=" * 60)
    
    # Загружаем страницу
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get(url, timeout=30, allow_redirects=True)
    response.encoding = response.apparent_encoding or 'utf-8'
    html = response.text
    
    print(f"✓ Загружено: {len(html)} символов")
    
    # Парсим
    parser = HTMLParser("https://elma365.com")
    parsed = parser.parse(html, url)
    
    print(f"\n📄 Результаты парсинга:")
    print(f"  Заголовок: {parsed['title']}")
    print(f"  Breadcrumbs: {', '.join(parsed['breadcrumbs'])}")
    print(f"  Section: {parsed['section']}")
    print(f"  Найдено ссылок: {len(parsed['links'])}")
    
    print(f"\n📝 Извлеченный текст (первые 500 символов):")
    print("-" * 60)
    plain_text = parsed['plain_text']
    print(plain_text[:500])
    if len(plain_text) > 500:
        print(f"\n... (всего {len(plain_text)} символов)")
    
    print(f"\n📊 Статистика:")
    print(f"  Длина текста: {len(plain_text)} символов")
    print(f"  Количество строк: {len(plain_text.split(chr(10)))}")
    
    # Сохраняем в файл для просмотра
    with open('parsed_text_example.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"URL: {url}\n")
        f.write(f"Заголовок: {parsed['title']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(plain_text)
    
    print(f"\n✓ Полный текст сохранен в: parsed_text_example.txt")
    
    return parsed

if __name__ == "__main__":
    # Тестируем на странице календаря
    url = "https://elma365.com/ru/help/platform/calendar.html"
    test_parser(url)

