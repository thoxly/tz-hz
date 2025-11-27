#!/usr/bin/env python3
"""
Добавляет шаблон LLM переменных в .env файл (если их там нет).
"""
from pathlib import Path

env_path = Path(".env")

# Шаблон переменных
template_vars = {
    "LLM_PROVIDER": "deepseek",
    "DEEPSEEK_API_KEY": "",  # Пользователь должен указать свой ключ
    "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "LLM_MODEL": ""
}

# Читаем существующий .env
existing_lines = []
existing_vars = {}

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        existing_lines = f.readlines()
        
        # Парсим существующие переменные
        for line in existing_lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()
                # Убираем кавычки
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                existing_vars[key] = value

# Добавляем недостающие переменные
new_lines = existing_lines.copy()
added_vars = []

# Проверяем, есть ли секция LLM
has_llm_section = any('LLM' in line.upper() for line in existing_lines)

if not has_llm_section:
    new_lines.append("\n# ============================================================================\n")
    new_lines.append("# LLM Settings\n")
    new_lines.append("# ============================================================================\n")

for key, default_value in template_vars.items():
    if key not in existing_vars:
        # Используем существующее значение или значение по умолчанию
        value = existing_vars.get(key, default_value)
        new_lines.append(f"{key}={value}\n")
        added_vars.append(key)
    else:
        print(f"[OK] {key} уже существует, сохраняем значение")

# Записываем обновленный .env
if added_vars:
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n[OK] Добавлено {len(added_vars)} переменных в .env:")
    for var in added_vars:
        print(f"  - {var}")
    
    print("\n[INFO] Следующий шаг:")
    print("  1. Откройте .env файл")
    print("  2. Укажите ваш DEEPSEEK_API_KEY (если еще не указан)")
    print("  3. Сохраните файл")
else:
    print("\n[INFO] Все переменные уже присутствуют в .env")

