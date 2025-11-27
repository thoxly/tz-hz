#!/usr/bin/env python3
"""Простой тест PDF с кириллицей."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os

print("Тест PDF с кириллицей")
print("=" * 60)

# Регистрируем Arial
arial_path = r'C:\Windows\Fonts\arial.ttf'
if os.path.exists(arial_path):
    pdfmetrics.registerFont(TTFont('ArialRU', arial_path))
    font_name = 'ArialRU'
    print(f"✓ Шрифт Arial зарегистрирован")
else:
    font_name = 'Helvetica'
    print("✗ Arial не найден, используем Helvetica")

# Создаем PDF
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)

styles = getSampleStyleSheet()
story = []

# Создаем стиль
custom_style = ParagraphStyle(
    'Custom',
    parent=styles['Normal'],
    fontName=font_name,
    fontSize=12
)

# Тестовый текст
test_lines = [
    "Техническое задание",
    "",
    "## Описание задачи",
    "",
    "Это тестовый документ с кириллицей.",
    "",
    "### Подраздел",
    "",
    "- Пункт 1",
    "- Пункт 2",
    "- Пункт 3",
    "",
    "**Жирный текст** и обычный текст.",
    "",
    "Русский текст должен отображаться правильно."
]

for line in test_lines:
    if not line:
        story.append(Spacer(1, 6))
        continue
    
    if line.startswith('## '):
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName=font_name, fontSize=14)
        story.append(Paragraph(line[3:], h2_style))
    elif line.startswith('### '):
        h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontName=font_name, fontSize=12)
        story.append(Paragraph(line[4:], h3_style))
    elif line.startswith('- '):
        story.append(Paragraph(f"• {line[2:]}", custom_style))
    elif '**' in line:
        import re
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
        story.append(Paragraph(text, custom_style))
    else:
        story.append(Paragraph(line, custom_style))
    story.append(Spacer(1, 4))

doc.build(story)
buffer.seek(0)

with open("test_simple_fonts.pdf", "wb") as f:
    f.write(buffer.getvalue())

print(f"✓ PDF создан: test_simple_fonts.pdf")
print(f"  Размер: {len(buffer.getvalue())} байт")
print(f"  Шрифт: {font_name}")
print("=" * 60)
print("Откройте test_simple_fonts.pdf и проверьте, что кириллица отображается правильно")

