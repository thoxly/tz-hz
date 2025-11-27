#!/usr/bin/env python3
"""Тест извлечения чистого текста без тегов."""
import requests
from app.crawler.parser import HTMLParser

def test_clean_text(url):
    """Протестировать извлечение чистого текста."""
    print(f"🔍 Тест извлечения чистого текста: {url}")
    print("=" * 60)
    
    # Загружаем страницу
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get(url, timeout=30, allow_redirects=True)
    response.encoding = response.apparent_encoding or 'utf-8'
    html = response.text
    
    # Парсим
    parser = HTMLParser("https://elma365.com")
    parsed = parser.parse(html, url)
    
    plain_text = parsed['plain_text']
    
    print(f"\n📝 Извлеченный чистый текст (первые 500 символов):")
    print("-" * 60)
    print(plain_text[:500])
    if len(plain_text) > 500:
        print(f"\n... (всего {len(plain_text)} символов)")
    
    # Проверяем, что нет HTML тегов
    import re
    html_tags = re.findall(r'<[^>]+>', plain_text)
    if html_tags:
        print(f"\n⚠ ВНИМАНИЕ! Найдены HTML теги в тексте: {len(html_tags)}")
        print("Примеры:", html_tags[:5])
    else:
        print(f"\n✅ Отлично! В тексте нет HTML тегов - только чистый текст!")
    
    # Сохраняем в файл
    with open('clean_text_example.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"URL: {url}\n")
        f.write("Чистый текст без HTML тегов:\n")
        f.write("=" * 60 + "\n\n")
        f.write(plain_text)
    
    print(f"\n✓ Чистый текст сохранен в: clean_text_example.txt")
    
    return plain_text

if __name__ == "__main__":
    url = "https://elma365.com/ru/help/platform/calendar.html"
    test_clean_text(url)

