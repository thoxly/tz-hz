#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API
"""
import asyncio
import aiohttp
import json


async def test_api():
    """Тестирование API endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. Проверка health endpoint
        print("1. Проверка health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Health check: {data}")
                else:
                    print(f"   ✗ Health check failed: {response.status}")
        except Exception as e:
            print(f"   ✗ Ошибка подключения: {e}")
            print("   Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
            return
        
        # 2. Проверка root endpoint
        print("\n2. Проверка root endpoint...")
        async with session.get(f"{base_url}/") as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✓ Root: {data}")
        
        # 3. Проверка статуса краулера
        print("\n3. Проверка статуса краулера...")
        async with session.get(f"{base_url}/api/crawl/status") as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✓ Crawl status: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 4. Тестовый запрос на добавление URL и ожидание записи в БД
        print("\n4. Тестовый запрос на добавление URL...")
        test_url = "https://elma365.com/ru/help/platform/how_to_create_an_app.html"
        payload = {"url": test_url}
        async with session.post(
            f"{base_url}/api/crawl/url",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✓ URL добавлен: {data}")
            else:
                error_text = await response.text()
                print(f"   ✗ Ошибка: {response.status} - {error_text}")
                return
        
        # 5. Ожидание завершения краулинга и записи в БД
        print("\n5. Ожидание завершения краулинга...")
        max_wait = 30  # максимум 30 секунд
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(2)
            waited += 2
            async with session.get(f"{base_url}/api/crawl/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    is_crawling = status_data.get("is_crawling", False)
                    visited = status_data.get("visited_count", 0)
                    print(f"   Статус: краулинг={'активен' if is_crawling else 'завершен'}, обработано: {visited}")
                    if not is_crawling and visited > 0:
                        print(f"   ✓ Краулинг завершен, обработано страниц: {visited}")
                        break
                    elif not is_crawling and visited == 0:
                        # Возможно краулинг еще не начался, подождем еще
                        continue
        else:
            print(f"   ⚠ Превышено время ожидания ({max_wait} сек), проверяем БД...")
        
        # 6. Проверка записи в БД
        print("\n6. Проверка записи данных в БД...")
        await asyncio.sleep(1)  # Небольшая задержка для финальной записи
        async with session.get(f"{base_url}/api/docs?limit=10") as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✓ Найдено документов в БД: {len(data)}")
                if data:
                    for i, doc in enumerate(data[:3], 1):
                        print(f"   Документ {i}:")
                        print(f"     - ID: {doc.get('doc_id', 'N/A')}")
                        print(f"     - Заголовок: {doc.get('title', 'N/A')}")
                        print(f"     - URL: {doc.get('url', 'N/A')}")
                        print(f"     - Создан: {doc.get('created_at', 'N/A')}")
                else:
                    print("   ⚠ Документы еще не записаны в БД")
            else:
                error_text = await response.text()
                print(f"   ✗ Ошибка: {response.status} - {error_text}")
        
        # 7. Проверка конкретного документа по URL
        print("\n7. Проверка конкретного документа...")
        # Извлекаем doc_id из URL для проверки
        doc_id_from_url = test_url.split('/')[-1].replace('.html', '')
        async with session.get(f"{base_url}/api/docs") as response:
            if response.status == 200:
                all_docs = await response.json()
                found_doc = None
                for doc in all_docs:
                    if test_url in doc.get('url', '') or doc_id_from_url in doc.get('doc_id', ''):
                        found_doc = doc
                        break
                
                if found_doc:
                    print(f"   ✓ Документ найден в БД:")
                    print(f"     - doc_id: {found_doc.get('doc_id')}")
                    print(f"     - title: {found_doc.get('title')}")
                    print(f"     - url: {found_doc.get('url')}")
                else:
                    print(f"   ⚠ Документ с URL '{test_url}' не найден в БД")
                    print(f"   Всего документов в БД: {len(all_docs)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Тестирование ELMA365 Crawler API")
    print("=" * 60)
    asyncio.run(test_api())
    print("\n" + "=" * 60)
    print("Тестирование завершено")
    print("=" * 60)

