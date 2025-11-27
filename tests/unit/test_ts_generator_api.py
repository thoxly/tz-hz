#!/usr/bin/env python3
"""Тест TS Generator через HTTP API."""
import requests
import json

BASE_URL = "http://localhost:8000/api/ts"

def test_ts_generator_api():
    """Протестировать TS Generator API."""
    print("📝 Тест TS Generator API через HTTP")
    print("=" * 60)
    
    # Загружаем пример архитектурного решения
    try:
        with open("decision_engine_example.json", "r", encoding="utf-8") as f:
            example_data = json.load(f)
        architecture_data = example_data["solution"]
    except FileNotFoundError:
        print("   ✗ Файл decision_engine_example.json не найден")
        print("   ⚠ Сначала запустите test_decision_engine.py")
        return
    
    # Тест 1: Health check
    print("\n1. GET /api/ts/health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Service: {data['service']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка подключения: {e}")
        print("   ⚠ Убедитесь, что сервер запущен: uvicorn app.main:app --reload")
        return
    
    # Тест 2: Генерация ТЗ (deterministic)
    print("\n2. POST /api/ts/generate/deterministic")
    try:
        response = requests.post(
            f"{BASE_URL}/generate/deterministic",
            json=architecture_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ ТЗ сгенерировано (deterministic)")
            print(f"   ✓ Длина: {len(result['markdown'])} символов")
            print(f"   ✓ Строк: {len(result['markdown'].splitlines())}")
            
            # Сохраняем результат
            with open("ts_api_deterministic.md", "w", encoding="utf-8") as f:
                f.write(result['markdown'])
            print("   ✓ Сохранено в ts_api_deterministic.md")
            
            # Показываем первые строки
            preview = result['markdown'].splitlines()[:10]
            print("   Предпросмотр:")
            for line in preview:
                print(f"     {line}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 3: Генерация ТЗ (verbose)
    print("\n3. POST /api/ts/generate/verbose")
    try:
        response = requests.post(
            f"{BASE_URL}/generate/verbose",
            json=architecture_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ ТЗ сгенерировано (verbose)")
            print(f"   ✓ Длина: {len(result['markdown'])} символов")
            
            # Сохраняем результат
            with open("ts_api_verbose.md", "w", encoding="utf-8") as f:
                f.write(result['markdown'])
            print("   ✓ Сохранено в ts_api_verbose.md")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 4: Генерация ТЗ (с выбором режима)
    print("\n4. POST /api/ts/generate (с выбором режима)")
    try:
        request_data = {
            "architecture": architecture_data,
            "mode": "deterministic"
        }
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ ТЗ сгенерировано (mode: {result['mode']})")
            print(f"   ✓ Timestamp: {result['timestamp']}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тесты TS Generator API завершены!")
    print("=" * 60)
    print("\n📖 Документация: см. TS_GENERATOR_API.md")

if __name__ == "__main__":
    test_ts_generator_api()

