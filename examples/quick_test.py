#!/usr/bin/env python3
"""
Быстрый тест без запуска сервера - проверка основных функций
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.utils import extract_doc_id, normalize_url, is_valid_help_url
from app.config import settings


def test_utils():
    """Тест утилит."""
    print("=" * 60)
    print("Тестирование утилит")
    print("=" * 60)
    
    # Тест extract_doc_id
    print("\n1. Тест extract_doc_id:")
    url1 = "https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html"
    doc_id1 = extract_doc_id(url1)
    print(f"   URL: {url1}")
    print(f"   doc_id: {doc_id1}")
    assert doc_id1 == "how_to_bind_app_to_proccess", f"Ожидалось 'how_to_bind_app_to_proccess', получено '{doc_id1}'"
    print("   ✓ Тест пройден")
    
    url2 = "https://elma365.com/ru/help/platform/360008121732.html"
    doc_id2 = extract_doc_id(url2)
    print(f"\n   URL: {url2}")
    print(f"   doc_id: {doc_id2}")
    assert doc_id2 == "360008121732", f"Ожидалось '360008121732', получено '{doc_id2}'"
    print("   ✓ Тест пройден")
    
    # Тест normalize_url
    print("\n2. Тест normalize_url:")
    base = "https://elma365.com"
    relative = "/help/page.html"
    normalized = normalize_url(relative, base)
    print(f"   Base: {base}")
    print(f"   Relative: {relative}")
    print(f"   Normalized: {normalized}")
    assert normalized == "https://elma365.com/help/page.html"
    print("   ✓ Тест пройден")
    
    # Тест is_valid_help_url
    print("\n3. Тест is_valid_help_url:")
    valid_url = "https://elma365.com/help/page.html"
    invalid_url = "https://example.com/page.html"
    print(f"   Valid URL: {valid_url} -> {is_valid_help_url(valid_url, base)}")
    print(f"   Invalid URL: {invalid_url} -> {is_valid_help_url(invalid_url, base)}")
    assert is_valid_help_url(valid_url, base) == True
    assert is_valid_help_url(invalid_url, base) == False
    print("   ✓ Тест пройден")
    
    print("\n" + "=" * 60)
    print("Все тесты утилит пройдены успешно!")
    print("=" * 60)


async def test_crawler_single():
    """Тест краулера на одном URL."""
    print("\n" + "=" * 60)
    print("Тестирование краулера (один URL)")
    print("=" * 60)
    
    try:
        from app.crawler import Crawler
        
        url = "https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html"
        print(f"\nКраулинг URL: {url}")
        
        async with Crawler() as crawler:
            result = await crawler.crawl_url(url)
            
            if result:
                print(f"✓ Успешно получен документ:")
                print(f"  doc_id: {result.get('doc_id')}")
                print(f"  title: {result.get('title', 'N/A')}")
                print(f"  section: {result.get('section', 'N/A')}")
                print(f"  breadcrumbs: {result.get('breadcrumbs', [])}")
                print(f"  HTML длина: {len(result.get('html', ''))} символов")
                print(f"  Plain text длина: {len(result.get('plain_text', ''))} символов")
            else:
                print("✗ Не удалось получить документ")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


async def test_normalizer():
    """Тест нормализатора."""
    print("\n" + "=" * 60)
    print("Тестирование нормализатора")
    print("=" * 60)
    
    try:
        from app.normalizer import Normalizer
        
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Navigation</nav>
                <header>Header</header>
                <main>
                    <h1>Main Title</h1>
                    <p>First paragraph with content.</p>
                    <h2>В этой статье</h2>
                    <ul>
                        <li>Point 1</li>
                        <li>Point 2</li>
                    </ul>
                    <pre><code>def example():
    return "test"</code></pre>
                </main>
                <footer>Footer</footer>
            </body>
        </html>
        """
        
        normalizer = Normalizer()
        result = normalizer.normalize(html, title="Test Page", breadcrumbs=["Test", "Page"])
        
        print(f"\n✓ Нормализация завершена:")
        print(f"  Блоков: {len(result.get('blocks', []))}")
        print(f"  Метаданные: {result.get('metadata', {})}")
        
        # Показать типы блоков
        block_types = {}
        for block in result.get('blocks', []):
            block_type = block.get('type', 'unknown')
            block_types[block_type] = block_types.get(block_type, 0) + 1
        
        print(f"  Типы блоков: {block_types}")
        
        # Проверить специальные блоки
        special_blocks = [b for b in result.get('blocks', []) if b.get('type') == 'special_block']
        if special_blocks:
            print(f"  Специальные блоки: {[b.get('kind') for b in special_blocks]}")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Главная функция."""
    # Тест утилит (синхронный)
    test_utils()
    
    # Тест краулера (асинхронный)
    await test_crawler_single()
    
    # Тест нормализатора (асинхронный)
    await test_normalizer()
    
    print("\n" + "=" * 60)
    print("Все тесты завершены!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

