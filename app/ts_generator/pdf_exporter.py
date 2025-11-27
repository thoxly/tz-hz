"""
Модуль для экспорта в PDF с правильной поддержкой кириллицы.
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
import os
import re
import logging

logger = logging.getLogger(__name__)


def export_markdown_to_pdf(markdown_text: str) -> bytes:
    """
    Экспортирует Markdown в PDF с поддержкой кириллицы.
    
    Args:
        markdown_text: Текст в формате Markdown
        
    Returns:
        bytes - PDF документ
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Регистрируем шрифты с поддержкой кириллицы
    main_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    try:
        arial_path = r'C:\Windows\Fonts\arial.ttf'
        arial_bold_path = r'C:\Windows\Fonts\arialbd.ttf'
        
        if os.path.exists(arial_path):
            pdfmetrics.registerFont(TTFont('ArialRU', arial_path))
            main_font = 'ArialRU'
            if os.path.exists(arial_bold_path):
                pdfmetrics.registerFont(TTFont('ArialRUBold', arial_bold_path))
                bold_font = 'ArialRUBold'
            else:
                bold_font = 'ArialRU'
            logger.info("Используются шрифты Arial для кириллицы")
    except Exception as e:
        logger.warning(f"Не удалось загрузить Arial: {e}")
    
    styles = getSampleStyleSheet()
    story = []
    
    # Создаем стили с кириллическими шрифтами
    title_style = ParagraphStyle(
        'Title',
        fontName=main_font,
        fontSize=18,
        textColor='#2c3e50',
        spaceAfter=12,
        alignment=TA_LEFT,
        leading=22
    )
    
    h2_style = ParagraphStyle(
        'H2',
        fontName=main_font,
        fontSize=14,
        textColor='#34495e',
        spaceAfter=10,
        spaceBefore=12,
        leading=18
    )
    
    h3_style = ParagraphStyle(
        'H3',
        fontName=main_font,
        fontSize=12,
        textColor='#7f8c8d',
        spaceAfter=8,
        spaceBefore=10,
        leading=16
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        fontName=main_font,
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    # Парсим Markdown
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        
        # Заголовки
        if line.startswith('# '):
            text = escape_for_pdf(line[2:].strip())
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            text = escape_for_pdf(line[3:].strip())
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 10))
        elif line.startswith('### '):
            text = escape_for_pdf(line[4:].strip())
            story.append(Paragraph(text, h3_style))
            story.append(Spacer(1, 8))
        elif line.startswith('#### '):
            text = escape_for_pdf(line[5:].strip())
            h4_style = ParagraphStyle('H4', fontName=main_font, fontSize=11, leading=15)
            story.append(Paragraph(text, h4_style))
            story.append(Spacer(1, 6))
        # Жирный текст
        elif '**' in line:
            # Заменяем **текст** на <b>текст</b>
            text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
            text = escape_for_pdf(text)
            story.append(Paragraph(text, normal_style))
            story.append(Spacer(1, 6))
        # Списки
        elif line.startswith('- ') or line.startswith('* '):
            text = escape_for_pdf(line[2:].strip())
            story.append(Paragraph(f"• {text}", normal_style))
            story.append(Spacer(1, 4))
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line)
            text = escape_for_pdf(text)
            story.append(Paragraph(text, normal_style))
            story.append(Spacer(1, 4))
        # Обычный текст
        else:
            text = escape_for_pdf(line)
            story.append(Paragraph(text, normal_style))
            story.append(Spacer(1, 6))
    
    # Собираем PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def escape_for_pdf(text: str) -> str:
    """Экранирует XML символы, сохраняя HTML теги."""
    # Защищаем HTML теги
    protected = {}
    tag_pattern = r'<(/?)([biu]|br|p)[^>]*>'
    
    def protect(match):
        tag = match.group(0)
        key = f'__TAG_{len(protected)}__'
        protected[key] = tag
        return key
    
    # Защищаем теги
    text = re.sub(tag_pattern, protect, text)
    
    # Экранируем XML
    text = (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))
    
    # Восстанавливаем теги
    for key, tag in protected.items():
        text = text.replace(key, tag)
    
    return text



