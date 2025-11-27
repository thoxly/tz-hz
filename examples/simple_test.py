#!/usr/bin/env python3
"""
Простой тест без БД - проверка основных функций
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.utils import extract_doc_id, normalize_url, is_valid_help_url


def test_utils():
    """Тест утилит."""
    print("=" * 60)
    print("Тестирование утилит")
    print("=" * 60)
    
    # Тест extract_doc_id
    print("\n1. Тест extract_doc_id:")
    test_cases = [
        ("https://elma365.com/ru/help/platform/how_to_bind_app_to_proccess.html", "how_to_bind_app_to_proccess"),
        ("https://elma365.com/ru/help/platform/360008121732.html", "360008121732"),
    ]
    
    for url, expected in test_cases:
        doc_id = extract_doc_id(url)
        print(f"   URL: {url[:60]}...")
        print(f"   doc_id: {doc_id}")
        if doc_id == expected:
            print(f"   ✓ Ожидалось: {expected}")
        else:
            print(f"   ⚠ Получено: {doc_id}, ожидалось: {expected}")
    
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
    test_urls = [
        ("https://elma365.com/help/page.html", True),
        ("https://example.com/page.html", False),
        ("/help/page.html", True),
    ]
    for url, expected in test_urls:
        result = is_valid_help_url(url, base)
        status = "✓" if result == expected else "✗"
        print(f"   {status} {url[:50]:<50} -> {result} (ожидалось: {expected})")
    
    print("\n" + "=" * 60)
    print("Тесты утилит завершены!")
    print("=" * 60)


def test_normalizer_simple():
    """Простой тест нормализатора без БД."""
    print("\n" + "=" * 60)
    print("Тестирование нормализатора (упрощенный)")
    print("=" * 60)
    
    try:
        # Импортируем напрямую, минуя __init__.py чтобы избежать импорта БД
        import sys
        import importlib.util
        normalizer_path = Path(__file__).parent / "app" / "normalizer" / "normalizer.py"
        spec = importlib.util.spec_from_file_location("normalizer", normalizer_path)
        normalizer_module = importlib.util.module_from_spec(spec)
        sys.modules["normalizer"] = normalizer_module
        spec.loader.exec_module(normalizer_module)
        Normalizer = normalizer_module.Normalizer
        
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
        
        # Показать типы блоков
        block_types = {}
        for block in result.get('blocks', []):
            block_type = block.get('type', 'unknown')
            block_types[block_type] = block_types.get(block_type, 0) + 1
        
        print(f"  Типы блоков: {block_types}")
        
        # Показать примеры блоков
        print(f"\n  Примеры блоков:")
        for i, block in enumerate(result.get('blocks', [])[:5]):
            block_type = block.get('type', 'unknown')
            if block_type == 'header':
                print(f"    {i+1}. Header (level {block.get('level')}): {block.get('text', '')[:50]}")
            elif block_type == 'paragraph':
                print(f"    {i+1}. Paragraph: {block.get('text', '')[:50]}...")
            elif block_type == 'list':
                print(f"    {i+1}. List ({'ordered' if block.get('ordered') else 'unordered'}): {len(block.get('items', []))} items")
            elif block_type == 'code_block':
                print(f"    {i+1}. Code block ({block.get('language', 'unknown')}): {len(block.get('code', ''))} chars")
            elif block_type == 'special_block':
                print(f"    {i+1}. Special block ({block.get('kind')}): {block.get('heading', '')[:50]}")
        
        # Проверить специальные блоки
        special_blocks = [b for b in result.get('blocks', []) if b.get('type') == 'special_block']
        if special_blocks:
            print(f"\n  ✓ Найдено специальных блоков: {len(special_blocks)}")
            for sb in special_blocks:
                print(f"    - {sb.get('kind')}: {sb.get('heading', '')[:50]}")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_utils()
    test_normalizer_simple()
    print("\n" + "=" * 60)
    print("Все тесты завершены!")
    print("=" * 60)

