#!/usr/bin/env python3
"""
Простой тест LLM клиента.
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from app.agents.llm_client import LLMClient

async def test_llm():
    """Тестирует LLM клиент."""
    print("=== Тест LLM клиента ===\n")
    
    # Проверяем переменные окружения
    provider = os.getenv("LLM_PROVIDER", "deepseek")
    print(f"Провайдер из переменных окружения: {provider}")
    
    # Создаем клиент
    client = LLMClient(provider=provider)
    print(f"Инициализирован клиент: {client.provider} (модель: {client.model})")
    
    if not client.client:
        print("\n[WARNING] LLM клиент не инициализирован!")
        print("Возможные причины:")
        print("1. API ключ не установлен в .env")
        print("2. Библиотека провайдера не установлена")
        print("3. Неправильный провайдер")
        return
    
    print("\n[OK] LLM клиент инициализирован успешно!")
    
    # Тестовый запрос
    print("\n=== Тестовый запрос ===")
    try:
        response = await client.generate(
            system_prompt="Ты помощник. Отвечай кратко.",
            user_prompt="Скажи 'Привет' одним словом.",
            temperature=0.3,
            max_tokens=50
        )
        print(f"Ответ от LLM: {response[:100]}")
        print("\n[OK] LLM работает корректно!")
    except Exception as e:
        print(f"\n[ERROR] Ошибка при запросе к LLM: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())

