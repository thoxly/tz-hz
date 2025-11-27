#!/usr/bin/env python3
"""Тест экспорта ТЗ в различные форматы."""
import asyncio
import json
from pathlib import Path
from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
from app.ts_generator.generator import TechnicalDesigner
from app.ts_generator.exporter import TSExporter

async def test_ts_export():
    """Протестировать экспорт ТЗ."""
    print("📤 Тест экспорта ТЗ в различные форматы")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        # Шаг 1: Создаем архитектурное решение
        print("\n1. Создание архитектурного решения")
        print("-" * 60)
        
        engine = DecisionEngine(session)
        requirements = BusinessRequirements(
            title="Согласование договора",
            business_requirements="Создать процесс согласования договоров",
            inputs=["Договор", "Сумма"],
            outputs=["Согласованный договор"],
            user_roles=["Менеджер", "Директор"],
            workflow_steps=[
                "Создание заявки",
                "Согласование менеджером",
                "Согласование директором"
            ],
            integration_targets=[],
            ui_requirements=[],
            constraints=[]
        )
        
        architecture = await engine.design_solution(requirements)
        print(f"✓ Архитектурное решение создано")
        
        # Шаг 2: Генерируем ТЗ
        print("\n2. Генерация ТЗ")
        print("-" * 60)
        
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode="deterministic")
        print(f"✓ ТЗ сгенерировано ({len(markdown)} символов)")
        
        # Шаг 3: Тестируем экспорт
        print("\n3. Тестирование экспорта")
        print("-" * 60)
        
        exporter = TSExporter()
        
        # HTML
        print("\n3.1. Экспорт в HTML")
        try:
            html = exporter.export_to_html(markdown, include_style=True)
            html_path = Path("ts_export_example.html")
            html_path.write_text(html, encoding="utf-8")
            print(f"   ✓ HTML экспортирован: {html_path} ({len(html)} символов)")
        except Exception as e:
            print(f"   ✗ Ошибка экспорта HTML: {e}")
        
        # PDF
        print("\n3.2. Экспорт в PDF")
        try:
            pdf_bytes = exporter.export_to_pdf(markdown)
            pdf_path = Path("ts_export_example.pdf")
            pdf_path.write_bytes(pdf_bytes)
            print(f"   ✓ PDF экспортирован: {pdf_path} ({len(pdf_bytes)} байт)")
        except Exception as e:
            print(f"   ✗ Ошибка экспорта PDF: {e}")
            print(f"   ⚠ Установите weasyprint или pdfkit для экспорта в PDF")
        
        # DOCX
        print("\n3.3. Экспорт в DOCX")
        try:
            docx_bytes = exporter.export_to_docx(markdown)
            docx_path = Path("ts_export_example.docx")
            docx_path.write_bytes(docx_bytes)
            print(f"   ✓ DOCX экспортирован: {docx_path} ({len(docx_bytes)} байт)")
        except Exception as e:
            print(f"   ✗ Ошибка экспорта DOCX: {e}")
            print(f"   ⚠ Установите python-docx для экспорта в DOCX")
        
        # Markdown (сохранение)
        print("\n3.4. Сохранение Markdown")
        md_path = Path("ts_export_example.md")
        md_path.write_text(markdown, encoding="utf-8")
        print(f"   ✓ Markdown сохранен: {md_path}")
        
        print("\n" + "=" * 60)
        print("✅ Тесты экспорта завершены!")
        print("=" * 60)
        print("\n📄 Сгенерированные файлы:")
        print("  - ts_export_example.md")
        print("  - ts_export_example.html")
        if Path("ts_export_example.pdf").exists():
            print("  - ts_export_example.pdf")
        if Path("ts_export_example.docx").exists():
            print("  - ts_export_example.docx")

if __name__ == "__main__":
    asyncio.run(test_ts_export())

