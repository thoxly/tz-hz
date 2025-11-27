#!/usr/bin/env python3
"""Тест Decision Engine."""
import asyncio
from app.database.database import get_session_factory
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements
import json

async def test_decision_engine():
    """Протестировать Decision Engine."""
    print("🏗️  Тест Decision Engine (Агент-Архитектор)")
    print("=" * 60)
    
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        engine = DecisionEngine(session)
        
        # Тест 1: Процесс
        print("\n1. Тест: Проектирование бизнес-процесса")
        print("-" * 60)
        requirements_process = BusinessRequirements(
            title="Согласование договора",
            business_requirements="Необходимо создать процесс согласования договоров с несколькими этапами согласования",
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
        
        solution_process = await engine.design_solution(requirements_process)
        print(f"✓ Типы решений: {solution_process.solution_type}")
        print(f"✓ Уверенность: {solution_process.confidence:.2f}")
        if solution_process.process_design:
            print(f"✓ Процесс: {solution_process.process_design.process_name}")
            print(f"✓ Шагов: {len(solution_process.process_design.steps)}")
        print(f"✓ Релевантных документов: {len(solution_process.references)}")
        print(f"✓ Обоснование: {solution_process.reasoning[:100]}...")
        
        # Тест 2: Приложение
        print("\n2. Тест: Проектирование приложения")
        print("-" * 60)
        requirements_app = BusinessRequirements(
            title="Справочник контрагентов",
            business_requirements="Создать справочник для хранения информации о контрагентах",
            inputs=["Название", "ИНН", "Адрес", "Телефон"],
            outputs=["Карточка контрагента"],
            user_roles=["Администратор", "Менеджер"],
            workflow_steps=[],
            integration_targets=[],
            ui_requirements=["Список контрагентов", "Карточка контрагента"],
            constraints=[]
        )
        
        solution_app = await engine.design_solution(requirements_app)
        print(f"✓ Типы решений: {solution_app.solution_type}")
        print(f"✓ Уверенность: {solution_app.confidence:.2f}")
        if solution_app.app_structure:
            print(f"✓ Приложение: {solution_app.app_structure.app_name}")
            print(f"✓ Полей: {len(solution_app.app_structure.fields)}")
            print(f"✓ Представлений: {len(solution_app.app_structure.views)}")
        print(f"✓ Релевантных документов: {len(solution_app.references)}")
        
        # Тест 3: Интеграция
        print("\n3. Тест: Проектирование интеграции")
        print("-" * 60)
        requirements_integration = BusinessRequirements(
            title="Интеграция с 1С",
            business_requirements="Настроить интеграцию для синхронизации данных с 1С",
            inputs=["Данные из 1С"],
            outputs=["Данные в ELMA365"],
            user_roles=["Администратор"],
            workflow_steps=[],
            integration_targets=["1С:Предприятие", "1С:Бухгалтерия"],
            ui_requirements=[],
            constraints=["Синхронизация раз в час"]
        )
        
        solution_integration = await engine.design_solution(requirements_integration)
        print(f"✓ Типы решений: {solution_integration.solution_type}")
        print(f"✓ Уверенность: {solution_integration.confidence:.2f}")
        if solution_integration.integration_points:
            print(f"✓ Тип интеграции: {solution_integration.integration_points.integration_type}")
            print(f"✓ Целевые системы: {', '.join(solution_integration.integration_points.target_systems)}")
        print(f"✓ Релевантных документов: {len(solution_integration.references)}")
        
        # Сохраняем пример решения в JSON
        print("\n4. Сохранение примера решения")
        print("-" * 60)
        example_solution = {
            "requirements": requirements_process.model_dump(),
            "solution": solution_process.model_dump()
        }
        
        with open("decision_engine_example.json", "w", encoding="utf-8") as f:
            json.dump(example_solution, f, ensure_ascii=False, indent=2)
        
        print("✓ Пример решения сохранен в decision_engine_example.json")
        
        print("\n" + "=" * 60)
        print("✅ Все тесты Decision Engine пройдены!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_decision_engine())

