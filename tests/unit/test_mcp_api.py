#!/usr/bin/env python3
"""Тест MCP API через HTTP запросы."""
import requests
import json

BASE_URL = "http://localhost:8000/api/mcp"

def test_mcp_api():
    """Протестировать MCP API."""
    print("🔍 Тест MCP API через HTTP")
    print("=" * 60)
    
    # Тест 1: get_doc
    print("\n1. GET /api/mcp/doc/calendar")
    try:
        response = requests.get(f"{BASE_URL}/doc/calendar")
        if response.status_code == 200:
            doc = response.json()
            print(f"   ✓ Документ найден: {doc['title']}")
            print(f"   ✓ Blocks: {len(doc['blocks'])}")
            print(f"   ✓ Plain text: {len(doc['plain_text'])} символов")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка подключения: {e}")
        print("   ⚠ Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        return
    
    # Тест 2: search_entities - заголовки
    print("\n2. POST /api/mcp/entities/search (headers level 2)")
    try:
        response = requests.post(
            f"{BASE_URL}/entities/search",
            json={"type": "header", "filters": {"level": 2, "limit": 5}}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Найдено заголовков: {data['count']}")
            if data['entities']:
                print(f"   Пример: {data['entities'][0]['text'][:60]}...")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 3: find_relevant
    print("\n3. POST /api/mcp/search (query: 'календарь')")
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": "календарь", "limit": 3}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Найдено документов: {data['count']}")
            if data['results']:
                print(f"   Пример: {data['results'][0]['title']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 4: list_docs_by_section
    print("\n4. GET /api/mcp/docs/section/platform")
    try:
        response = requests.get(f"{BASE_URL}/docs/section/platform")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Найдено документов: {data['count']}")
            if data['docs']:
                print(f"   Примеры:")
                for doc in data['docs'][:3]:
                    print(f"     - {doc['doc_id']}: {doc['title']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 5: GET headers
    print("\n5. GET /api/mcp/entities/headers?level=2")
    try:
        response = requests.get(f"{BASE_URL}/entities/headers?level=2&limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Найдено заголовков: {data['count']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 6: GET special-blocks
    print("\n6. GET /api/mcp/entities/special-blocks")
    try:
        response = requests.get(f"{BASE_URL}/entities/special-blocks?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Найдено специальных блоков: {data['count']}")
            if data['entities']:
                print(f"   Пример: {data['entities'][0]['kind']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тесты MCP API завершены!")
    print("=" * 60)
    print("\n📖 Документация: см. MCP_API.md")

if __name__ == "__main__":
    test_mcp_api()

