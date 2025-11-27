#!/usr/bin/env python3
"""Тест шрифтов в PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
import os

# Регистрируем шрифты
try:
    arial_path = r'C:\Windows\Fonts\arial.ttf'
    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont('ArialRU', arial_path))
        print(f"✓ Шрифт Arial зарегистрирован: {arial_path}")
        font_name = 'ArialRU'
    else:
        print("✗ Arial не найден")
        font_name = 'Helvetica'
except Exception as e:
    print(f"✗ Ошибка регистрации шрифта: {e}")
    font_name = 'Helvetica'

# Создаем PDF
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)

styles = getSampleStyleSheet()
story = []

# Создаем стиль с кириллическим шрифтом
custom_style = ParagraphStyle(
    'Custom',
    parent=styles['Normal'],
    fontName=font_name,
    fontSize=12
)

# Тестовый текст с кириллицей
test_text = """
Техническое задание

## 1. Описание задачи

Это тестовый документ с кириллицей.

### Подраздел

- Пункт 1
- Пункт 2
- Пункт 3

**Жирный текст** и обычный текст.
"""

lines = test_text.strip().split('\n')
for line in lines:
    if not line.strip():
        story.append(Spacer(1, 6))
        continue
    
    if line.startswith('## '):
        style = ParagraphStyle('H2', parent=styles['Heading2'], fontName=font_name, fontSize=14)
        story.append(Paragraph(line[3:].strip(), style))
    elif line.startswith('### '):
        style = ParagraphStyle('H3', parent=styles['Heading3'], fontName=font_name, fontSize=12)
        story.append(Paragraph(line[4:].strip(), style))
    elif line.startswith('- '):
        story.append(Paragraph(f"• {line[2:].strip()}", custom_style))
    elif '**' in line:
        text = line.replace('**', '<b>').replace('**', '</b>')
        story.append(Paragraph(text, custom_style))
    else:
        story.append(Paragraph(line.strip(), custom_style))
    story.append(Spacer(1, 4))

doc.build(story)
buffer.seek(0)

with open("test_fonts.pdf", "wb") as f:
    f.write(buffer.getvalue())

print(f"✓ PDF создан: test_fonts.pdf ({len(buffer.getvalue())} байт)")
print(f"Использован шрифт: {font_name}")

