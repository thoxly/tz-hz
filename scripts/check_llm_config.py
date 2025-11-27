#!/usr/bin/env python3
"""
Проверка конфигурации LLM провайдеров.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def check_llm_config():
    """Проверяет настройку LLM провайдеров."""
    # Загружаем .env
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        print("[OK] .env файл найден и загружен")
    else:
        print("[WARNING] .env файл не найден")
        return
    
    print("\n=== Проверка переменных LLM ===\n")
    
    # Проверяем провайдер
    provider = os.getenv("LLM_PROVIDER", "не указан")
    print(f"LLM_PROVIDER: {provider}")
    
    # Проверяем ключи для каждого провайдера
    providers = {
        "openai": ("OPENAI_API_KEY", "OpenAI"),
        "anthropic": ("ANTHROPIC_API_KEY", "Anthropic"),
        "deepseek": ("DEEPSEEK_API_KEY", "DeepSeek"),
        "ollama": ("OLLAMA_BASE_URL", "Ollama")
    }
    
    print("\n--- Проверка ключей ---")
    
    for prov, (key_name, prov_name) in providers.items():
        value = os.getenv(key_name)
        if value:
            # Скрываем ключ, показываем только первые и последние символы
            if "KEY" in key_name and len(value) > 10:
                masked = value[:4] + "..." + value[-4:]
                print(f"[OK] {prov_name} ({key_name}): {masked}")
            else:
                print(f"[OK] {prov_name} ({key_name}): {value}")
        else:
            print(f"[--] {prov_name} ({key_name}): не установлен")
    
    # Проверяем выбранный провайдер
    print(f"\n--- Выбранный провайдер: {provider} ---")
    
    if provider in providers:
        key_name, prov_name = providers[provider]
        value = os.getenv(key_name)
        
        if value:
            print(f"[OK] {prov_name} настроен и готов к работе!")
            
            if provider == "ollama":
                print(f"[INFO] Убедитесь, что Ollama запущен: ollama serve")
        else:
            print(f"[ERROR] Для {prov_name} не установлен {key_name}")
            print(f"[INFO] Добавьте {key_name} в .env файл")
    else:
        print(f"[WARNING] Неизвестный провайдер: {provider}")
        print(f"[INFO] Доступные провайдеры: {', '.join(providers.keys())}")
    
    # Дополнительные настройки
    model = os.getenv("LLM_MODEL")
    if model:
        print(f"\n[INFO] Используемая модель: {model}")
    else:
        print(f"\n[INFO] Модель не указана, будет использована по умолчанию для {provider}")

if __name__ == "__main__":
    try:
        check_llm_config()
    except ImportError:
        print("[ERROR] python-dotenv не установлен")
        print("[INFO] Установите: pip install python-dotenv")
    except Exception as e:
        print(f"[ERROR] Ошибка при проверке: {e}")

