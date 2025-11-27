#!/usr/bin/env python3
"""
Проверка переменных в .env файле.
"""
from pathlib import Path

env_path = Path(".env")

if not env_path.exists():
    print("[ERROR] .env файл не найден!")
    exit(1)

print(f"[OK] .env файл найден: {env_path.absolute()}\n")
print("=== Содержимое .env (только LLM переменные) ===\n")

with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
    llm_vars = {}
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Убираем кавычки если есть
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            if any(x in key.upper() for x in ['LLM', 'DEEPSEEK', 'OPENAI', 'ANTHROPIC', 'OLLAMA']):
                llm_vars[key] = value
                # Показываем ключ, но скрываем значение
                if 'KEY' in key and value:
                    masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                    print(f"Строка {i}: {key}={masked}")
                else:
                    print(f"Строка {i}: {key}={value}")

print(f"\n=== Найдено {len(llm_vars)} LLM переменных ===\n")

# Проверяем обязательные
required = {
    'LLM_PROVIDER': 'Провайдер LLM',
    'DEEPSEEK_API_KEY': 'API ключ DeepSeek (если используете DeepSeek)'
}

for key, desc in required.items():
    if key in llm_vars:
        value = llm_vars[key]
        if value:
            print(f"[OK] {key}: установлен ({desc})")
        else:
            print(f"[WARNING] {key}: пустое значение ({desc})")
    else:
        print(f"[--] {key}: не найден ({desc})")

