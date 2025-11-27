#!/usr/bin/env python3
"""Тест экспорта в PDF через reportlab."""
import asyncio
from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
from app.ts_generator.generator import TechnicalDesigner
from app.ts_generator.exporter import TSExporter

async def test_pdf():
    """Тест экспорта в PDF."""
    print("=" * 60)
    print("Тест экспорта в PDF")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        # Создаем простое решение
        engine = DecisionEngine(session)
        requirements = BusinessRequirements(
            title="Тест PDF",
            business_requirements="Тестовый процесс",
            workflow_steps=["Шаг 1", "Шаг 2"],
            user_roles=["Тестер"]
        )
        
        architecture = await engine.design_solution(requirements)
        
        # Генерируем ТЗ
        designer = TechnicalDesigner()
        markdown = designer.generate_ts(architecture, mode="deterministic")
        
        print(f"\nТЗ сгенерировано: {len(markdown)} символов")
        
        # Экспортируем в PDF
        exporter = TSExporter()
        print(f"\nreportlab доступен: {exporter.has_reportlab}")
        
        try:
            pdf_bytes = exporter.export_to_pdf(markdown)
            print(f"✓ PDF экспортирован: {len(pdf_bytes)} байт")
            
            # Сохраняем
            with open("test_export.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("✓ Файл сохранен: test_export.pdf")
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf())

