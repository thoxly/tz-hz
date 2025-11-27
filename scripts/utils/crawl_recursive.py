#!/usr/bin/env python3
"""
Скрипт для автоматического сбора всех ссылок из начальной страницы.
Просто укажите начальную ссылку, и скрипт автоматически найдет и добавит все страницы в базу данных.
"""
import requests
import json
import sys
import time

API_URL = "http://127.0.0.1:8000/api/crawl/start"
STATUS_URL = "http://127.0.0.1:8000/api/crawl/status"

def start_recursive_crawl(start_url):
    """Запустить рекурсивный краулинг с указанной начальной ссылки."""
    try:
        print(f"🚀 Запуск рекурсивного краулинга с: {start_url}")
        print("⏳ Это может занять некоторое время...\n")
        
        # Запускаем краулинг
        response = requests.post(
            API_URL,
            json={"start_url": start_url},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Краулинг запущен!")
            print(f"Начальная ссылка: {result.get('start_url', start_url)}")
            print(f"\nОбработка происходит в фоновом режиме.")
            print("Можете отслеживать прогресс через статус.\n")
            
            # Показываем статус каждые 5 секунд
            print("=" * 60)
            print("Статус обработки (обновляется каждые 5 секунд):")
            print("=" * 60)
            
            while True:
                try:
                    status_response = requests.get(STATUS_URL, timeout=5)
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        is_crawling = status.get('is_crawling', False)
                        visited = status.get('visited_count', 0)
                        queue = status.get('queue_size', 0)
                        stats = status.get('stats', {})
                        total_crawled = stats.get('total_crawled', 0)
                        total_failed = stats.get('total_failed', 0)
                        
                        print(f"\r📊 Обработано: {visited} | В очереди: {queue} | Успешно: {total_crawled} | Ошибок: {total_failed}", end="")
                        
                        if not is_crawling and queue == 0:
                            print("\n\n✓ Краулинг завершен!")
                            print(f"Всего обработано страниц: {visited}")
                            print(f"Успешно сохранено: {total_crawled}")
                            if total_failed > 0:
                                print(f"Ошибок: {total_failed}")
                            break
                    
                    time.sleep(5)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠ Прервано пользователем")
                    print("Краулинг продолжается в фоновом режиме.")
                    print("Проверьте статус: http://127.0.0.1:8000/api/crawl/status")
                    break
                except Exception as e:
                    print(f"\n⚠ Ошибка при проверке статуса: {e}")
                    time.sleep(5)
            
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
        print("  python crawl_recursive.py <начальная_ссылка>")
        print("\nПример:")
        print("  python crawl_recursive.py https://elma365.com/ru/help")
        print("\nСкрипт автоматически найдет и добавит ВСЕ ссылки,")
        print("начиная с указанной страницы, в базу данных.")
        sys.exit(1)
    
    start_url = sys.argv[1]
    
    # Проверяем, что это валидная ссылка
    if not start_url.startswith('http'):
        print("✗ Ошибка: Укажите полную ссылку (начинающуюся с http:// или https://)")
        sys.exit(1)
    
    print("=" * 60)
    print("РЕКУРСИВНЫЙ КРАУЛИНГ")
    print("=" * 60)
    print()
    
    success = start_recursive_crawl(start_url)
    
    if success:
        print("\n" + "=" * 60)
        print("Готово! Все страницы сохранены в базу данных.")
        print("Посмотреть результаты: http://127.0.0.1:8000/api/docs")
        print("=" * 60)
    else:
        sys.exit(1)

