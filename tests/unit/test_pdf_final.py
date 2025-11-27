#!/usr/bin/env python3
"""Финальный тест PDF с правильными шрифтами."""
import asyncio
from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
from app.ts_generator.generator import TechnicalDesigner
from app.ts_generator.exporter import TSExporter

async def test():
    session_factory = get_session_factory()
    async with session_factory() as session:
        engine = DecisionEngine(session)
        req = BusinessRequirements(
            title="Тест PDF",
            business_requirements="Тестовый процесс с кириллицей",
            workflow_steps=["Шаг 1", "Шаг 2"],
            user_roles=["Тестер"]
        )
        arch = await engine.design_solution(req)
        designer = TechnicalDesigner()
        md = designer.generate_ts(arch)
        exporter = TSExporter()
        pdf = exporter.export_to_pdf(md)
        with open('final_test.pdf', 'wb') as f:
            f.write(pdf)
        print(f"✓ PDF создан: final_test.pdf ({len(pdf)} байт)")
        print("Откройте файл и проверьте, что кириллица отображается правильно")

if __name__ == "__main__":
    asyncio.run(test())

