# Исправление экспорта в PDF

## Проблема

На Windows экспорт в PDF не работал, так как:
- WeasyPrint требует GTK+ библиотеки (не работает на Windows без дополнительной установки)
- pdfkit требует wkhtmltopdf
- pypandoc требует pandoc

## Решение

Добавлена поддержка **reportlab** - библиотеки, которая работает на Windows без дополнительных зависимостей.

## Установка

```bash
pip install reportlab
```

## Статус

✅ **PDF экспорт теперь работает на Windows!**

Библиотека reportlab:
- ✅ Установлена
- ✅ Работает на Windows
- ✅ Не требует дополнительных системных библиотек
- ✅ Генерирует корректные PDF файлы

## Использование

Экспорт в PDF теперь работает через Telegram бота или API:

```bash
# Через API
curl -X POST "http://localhost:8000/api/ts/export/pdf?mode=deterministic" \
  -H "Content-Type: application/json" \
  -d @architecture.json \
  --output technical_specification.pdf
```

## Приоритет методов экспорта

1. **reportlab** (рекомендуется для Windows) - работает сразу
2. pypandoc - требует установки pandoc
3. weasyprint - требует GTK+ (не работает на Windows)
4. pdfkit - требует wkhtmltopdf

## Тестирование

Запустите тест:

```bash
python test_pdf_export.py
```

Должен создать файл `test_export.pdf`.

## Особенности reportlab

- Работает на Windows без дополнительных библиотек
- Поддерживает основные элементы Markdown (заголовки, списки, жирный текст)
- Генерирует PDF с правильным форматированием
- Размер файла оптимизирован

