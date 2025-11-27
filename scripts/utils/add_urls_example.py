#!/usr/bin/env python3
"""
Пример скрипта для добавления списка ссылок в базу данных через API.
"""
import requests
import json
import sys

API_URL = "http://127.0.0.1:8000/api/crawl/urls"

def add_urls(urls):
    """Добавить список ссылок через API."""
    try:
        response = requests.post(
            API_URL,
            json={"urls": urls},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Успешно отправлено {len(urls)} ссылок на обработку!")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print("\nОбработка происходит в фоновом режиме.")
            print("Проверьте статус: http://127.0.0.1:8000/api/crawl/status")
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Не удалось подключиться к серверу.")
        print("Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python add_urls_example.py url1 url2 url3 ...")
        print("\nПример:")
        print('  python add_urls_example.py "https://elma365.com/ru/help/page1" "https://elma365.com/ru/help/page2"')
        print("\nИли создайте файл urls.txt и используйте:")
        print("  python add_urls_example.py --file urls.txt")
        sys.exit(1)
    
    urls = []
    
    # Чтение из файла
    if sys.argv[1] == '--file' and len(sys.argv) > 2:
        filename = sys.argv[2]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            print(f"Загружено {len(urls)} ссылок из файла {filename}")
        except FileNotFoundError:
            print(f"Файл не найден: {filename}")
            sys.exit(1)
    else:
        # URL из аргументов командной строки
        urls = sys.argv[1:]
    
    if not urls:
        print("Нет ссылок для обработки")
        sys.exit(1)
    
    print(f"\nОтправка {len(urls)} ссылок в API...")
    print(f"Ссылки:\n" + "\n".join(f"  - {url}" for url in urls) + "\n")
    
    success = add_urls(urls)
    
    if not success:
        sys.exit(1)

