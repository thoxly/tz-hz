#!/usr/bin/env python3
"""Тест TS Generator."""
import asyncio
import json
from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
from app.ts_generator.generator import TechnicalDesigner

async def test_ts_generator():
    """Протестировать TS Generator."""
    print("📝 Тест Technical Specification Generator")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        # Шаг 1: Создаем архитектурное решение
        print("\n1. Создание архитектурного решения")
        print("-" * 60)
        
        engine = DecisionEngine(session)
        requirements = BusinessRequirements(
            title="Согласование договора",
            business_requirements="Создать процесс согласования договоров с несколькими этапами",
            inputs=["Договор", "Сумма"],
            outputs=["Согласованный договор"],
            user_roles=["Менеджер", "Директор", "Бухгалтер"],
            workflow_steps=[
                "Создание заявки на согласование",
                "Согласование менеджером",
                "Согласование директором",
                "Согласование бухгалтером",
                "Завершение процесса"
            ],
            integration_targets=[],
            ui_requirements=[],
            constraints=["Срок согласования не более 5 дней"]
        )
        
        architecture = await engine.design_solution(requirements)
        print(f"✓ Архитектурное решение создано")
        print(f"✓ Типы решений: {architecture.solution_type}")
        
        # Шаг 2: Генерируем ТЗ в deterministic режиме
        print("\n2. Генерация ТЗ (deterministic режим)")
        print("-" * 60)
        
        designer = TechnicalDesigner()
        ts_deterministic = designer.generate_ts(architecture, mode="deterministic")
        
        print(f"✓ ТЗ сгенерировано (deterministic)")
        print(f"✓ Длина: {len(ts_deterministic)} символов")
        print(f"✓ Строк: {len(ts_deterministic.splitlines())}")
        
        # Сохраняем в файл
        with open("ts_example_deterministic.md", "w", encoding="utf-8") as f:
            f.write(ts_deterministic)
        print("✓ Сохранено в ts_example_deterministic.md")
        
        # Шаг 3: Генерируем ТЗ в verbose режиме
        print("\n3. Генерация ТЗ (verbose режим)")
        print("-" * 60)
        
        ts_verbose = designer.generate_ts(architecture, mode="verbose")
        
        print(f"✓ ТЗ сгенерировано (verbose)")
        print(f"✓ Длина: {len(ts_verbose)} символов")
        print(f"✓ Строк: {len(ts_verbose.splitlines())}")
        
        # Сохраняем в файл
        with open("ts_example_verbose.md", "w", encoding="utf-8") as f:
            f.write(ts_verbose)
        print("✓ Сохранено в ts_example_verbose.md")
        
        # Показываем первые строки
        print("\n4. Предпросмотр ТЗ (первые 20 строк)")
        print("-" * 60)
        preview_lines = ts_deterministic.splitlines()[:20]
        for line in preview_lines:
            print(line)
        print("...")
        
        print("\n" + "=" * 60)
        print("✅ Все тесты TS Generator пройдены!")
        print("=" * 60)
        print("\n📄 Сгенерированные файлы:")
        print("  - ts_example_deterministic.md")
        print("  - ts_example_verbose.md")

if __name__ == "__main__":
    asyncio.run(test_ts_generator())

