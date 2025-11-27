#!/usr/bin/env python3
"""Тест Decision Engine через HTTP API."""
import requests
import json

BASE_URL = "http://localhost:8000/api/decision-engine"

def test_decision_engine_api():
    """Протестировать Decision Engine API."""
    print("🏗️  Тест Decision Engine API через HTTP")
    print("=" * 60)
    
    # Тест 1: Health check
    print("\n1. GET /api/decision-engine/health")
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
    
    # Тест 2: Проектирование процесса
    print("\n2. POST /api/decision-engine/design (процесс)")
    try:
        requirements = {
            "title": "Согласование договора",
            "business_requirements": "Создать процесс согласования договоров с несколькими этапами",
            "inputs": ["Договор", "Сумма"],
            "outputs": ["Согласованный договор"],
            "user_roles": ["Менеджер", "Директор"],
            "workflow_steps": [
                "Создание заявки",
                "Согласование менеджером",
                "Согласование директором"
            ],
            "integration_targets": [],
            "ui_requirements": [],
            "constraints": []
        }
        
        response = requests.post(
            f"{BASE_URL}/design",
            json=requirements,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            solution = response.json()
            print(f"   ✓ Типы решений: {solution['solution_type']}")
            print(f"   ✓ Уверенность: {solution['confidence']:.2f}")
            if solution.get('process_design'):
                print(f"   ✓ Процесс: {solution['process_design']['process_name']}")
                print(f"   ✓ Шагов: {len(solution['process_design']['steps'])}")
            print(f"   ✓ Релевантных документов: {len(solution['references'])}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # Тест 3: Проектирование приложения
    print("\n3. POST /api/decision-engine/design (приложение)")
    try:
        requirements = {
            "title": "Справочник контрагентов",
            "business_requirements": "Создать справочник для хранения информации о контрагентах",
            "inputs": ["Название", "ИНН", "Адрес"],
            "outputs": ["Карточка контрагента"],
            "user_roles": ["Администратор"],
            "workflow_steps": [],
            "integration_targets": [],
            "ui_requirements": ["Список", "Карточка"],
            "constraints": []
        }
        
        response = requests.post(
            f"{BASE_URL}/design",
            json=requirements
        )
        
        if response.status_code == 200:
            solution = response.json()
            print(f"   ✓ Типы решений: {solution['solution_type']}")
            if solution.get('app_structure'):
                print(f"   ✓ Приложение: {solution['app_structure']['app_name']}")
                print(f"   ✓ Полей: {len(solution['app_structure']['fields'])}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тесты Decision Engine API завершены!")
    print("=" * 60)
    print("\n📖 Документация: см. DECISION_ENGINE_API.md")

if __name__ == "__main__":
    test_decision_engine_api()

