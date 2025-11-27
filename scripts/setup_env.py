#!/usr/bin/env python3
"""
Скрипт для настройки .env файла с переменными для LLM провайдеров.
"""
import os
from pathlib import Path

def setup_env():
    """Создает или обновляет .env файл с переменными для LLM."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    # Читаем шаблон
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        template = """# LLM Providers
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
"""
    
    # Проверяем существующий .env
    existing_vars = {}
    if env_path.exists():
        print("[INFO] Найден существующий .env файл")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key.strip()] = value.strip()
        
        # Сохраняем существующие значения
        if 'DEEPSEEK_API_KEY' in existing_vars:
            print("[OK] Найдена существующая переменная DEEPSEEK_API_KEY")
    
    # Создаем новый .env на основе шаблона
    lines = []
    for line in template.split('\n'):
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            # Сохраняем существующее значение, если есть
            if key in existing_vars:
                lines.append(f"{key}={existing_vars[key]}")
                print(f"[OK] Сохранено существующее значение для {key}")
            else:
                lines.append(line)
        else:
            lines.append(line)
    
    # Записываем обновленный .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n[OK] .env файл создан/обновлен: {env_path.absolute()}")
    print("\n[INFO] Следующие шаги:")
    print("1. Откройте .env файл")
    print("2. Укажите ваш DEEPSEEK_API_KEY (если еще не указан)")
    print("3. Установите LLM_PROVIDER=deepseek (или другой провайдер)")
    print("4. Сохраните файл")

if __name__ == "__main__":
    setup_env()

