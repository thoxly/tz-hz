"""
Architect Agent - Инженер ELMA365, который превращает AS-IS в решение.

Берёт структурированный AS-IS и разрабатывает архитектуру решения,
определяя как именно оно будет реализовано в ELMA365.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.agents.models import (
    ArchitectRequest,
    ArchitectResponse,
    ELMAArchitecture,
    ELMAComponent,
    RoleDesign,
    EntityRelation
)
from app.agents.models import ProcessAsIs
from app.decision_engine.engine import DecisionEngine
from app.decision_engine.models import BusinessRequirements

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """
    Агент для проектирования архитектуры ELMA365 на основе AS-IS процесса.
    
    Задачи:
    - Анализирует сложность задачи
    - Выбирает минимально достаточный набор инструментов ELMA365
    - Формирует понятную и обоснованную архитектуру
    - Объясняет почему выбран именно такой подход
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация Architect Agent.
        
        Args:
            session: Сессия базы данных для доступа к MCP
        """
        self.session = session
        self.decision_engine = DecisionEngine(session)
        self.logger = logging.getLogger(__name__)
    
    async def design(self, request: ArchitectRequest) -> ArchitectResponse:
        """
        Проектирует архитектуру решения на основе AS-IS процесса.
        
        Args:
            request: Запрос с AS-IS процессом
            
        Returns:
            ArchitectResponse с архитектурным решением
        """
        self.logger.info(f"Начинаем проектирование архитектуры для процесса '{request.as_is.process_name}'")
        
        # Преобразуем AS-IS в BusinessRequirements для Decision Engine
        business_req = self._convert_as_is_to_requirements(request.as_is)
        
        # Используем Decision Engine для генерации архитектуры
        solution = await self.decision_engine.design_solution(business_req)
        
        # Преобразуем решение Decision Engine в нашу модель ELMAArchitecture
        architecture = self._convert_solution_to_architecture(
            solution,
            request.as_is
        )
        
        # Определяем сложность
        complexity = self._assess_complexity(architecture)
        architecture.complexity = complexity
        
        metadata = {
            "components_count": len(architecture.components),
            "roles_count": len(architecture.roles),
            "relations_count": len(architecture.entity_relations),
            "confidence": architecture.confidence
        }
        
        self.logger.info(f"Архитектура спроектирована: {len(architecture.components)} компонентов, сложность: {complexity}")
        
        return ArchitectResponse(
            architecture=architecture,
            design_metadata=metadata
        )
    
    def _convert_as_is_to_requirements(self, as_is: ProcessAsIs) -> BusinessRequirements:
        """Преобразует AS-IS процесс в BusinessRequirements."""
        # Собираем входные данные из шагов
        all_inputs = set()
        for step in as_is.steps:
            all_inputs.update(step.inputs)
        
        # Собираем выходные данные из шагов
        all_outputs = set()
        for step in as_is.steps:
            all_outputs.update(step.outputs)
        
        # Формируем шаги процесса
        workflow_steps = [step.name for step in as_is.steps]
        
        # Формируем описание требований
        business_desc = f"{as_is.process_description}\n\n"
        if as_is.problems:
            business_desc += f"Проблемы: {', '.join(as_is.problems[:3])}\n"
        if as_is.business_rules:
            business_desc += f"Бизнес-правила: {', '.join([r.rule_text[:50] for r in as_is.business_rules[:2]])}"
        
        return BusinessRequirements(
            title=as_is.process_name,
            business_requirements=business_desc,
            inputs=list(all_inputs)[:10],
            outputs=list(all_outputs)[:10],
            user_roles=as_is.roles,
            workflow_steps=workflow_steps,
            integration_targets=[],
            ui_requirements=[],
            constraints=[f"Учесть проблемы: {p}" for p in as_is.problems[:3]]
        )
    
    def _convert_solution_to_architecture(
        self,
        solution,
        as_is: ProcessAsIs
    ) -> ELMAArchitecture:
        """Преобразует решение Decision Engine в ArchitectureSolution."""
        components = []
        roles = []
        entity_relations = []
        
        # Преобразуем process_design в компоненты
        if solution.process_design:
            components.append(ELMAComponent(
                component_type="process",
                name=solution.process_design.process_name,
                description=f"Бизнес-процесс типа {solution.process_design.process_type}",
                purpose="Автоматизация процесса",
                related_steps=[i+1 for i in range(len(solution.process_design.steps))]
            ))
        
        # Преобразуем app_structure в компоненты
        if solution.app_structure:
            components.append(ELMAComponent(
                component_type="app",
                name=solution.app_structure.app_name,
                description=f"Приложение типа {solution.app_structure.entity_type}",
                purpose="Хранение и управление данными",
                related_steps=[]
            ))
            
            # Добавляем представления как отдельные компоненты
            for view in solution.app_structure.views:
                components.append(ELMAComponent(
                    component_type="page",
                    name=f"{solution.app_structure.app_name} - {view.get('name', 'view')}",
                    description=f"Представление типа {view.get('type', 'unknown')}",
                    purpose="Отображение данных",
                    related_steps=[]
                ))
        
        # Преобразуем widget_design в компоненты
        if solution.widget_design:
            components.append(ELMAComponent(
                component_type="widget",
                name=solution.widget_design.widget_name,
                description=f"Виджет типа {solution.widget_design.widget_type}",
                purpose="Интерактивный элемент интерфейса",
                related_steps=[]
            ))
        
        # Преобразуем integration_points в компоненты
        if solution.integration_points:
            components.append(ELMAComponent(
                component_type="integration",
                name=f"Интеграция {solution.integration_points.integration_type}",
                description=f"Интеграция с системами: {', '.join(solution.integration_points.target_systems)}",
                purpose="Интеграция с внешними системами",
                related_steps=[]
            ))
        
        # Формируем роли
        all_roles = set()
        if solution.process_design and solution.process_design.roles:
            all_roles.update(solution.process_design.roles)
        if solution.app_structure and solution.app_structure.permissions:
            all_roles.update(solution.app_structure.permissions.keys())
        
        for role_name in all_roles:
            permissions = []
            if solution.app_structure and solution.app_structure.permissions.get(role_name):
                permissions = solution.app_structure.permissions[role_name]
            
            roles.append(RoleDesign(
                role_name=role_name,
                permissions=permissions,
                components_access=[c.name for c in components]
            ))
        
        # Формируем связи между сущностями
        if solution.app_structure and solution.process_design:
            entity_relations.append(EntityRelation(
                from_entity=solution.app_structure.app_name,
                to_entity=solution.process_design.process_name,
                relation_type="workflow",
                description="Процесс работает с данными приложения"
            ))
        
        # Формируем обоснование
        reasoning = solution.reasoning or "Архитектура спроектирована на основе анализа AS-IS процесса и документации ELMA365."
        
        # Собираем ссылки на документацию
        doc_references = []
        for ref in solution.references:
            doc_references.append({
                "doc_id": ref.doc_id,
                "title": ref.extracted_info.get("title", ref.doc_id),
                "url": ref.extracted_info.get("url", ""),
                "relevance": ref.relevance
            })
        
        return ELMAArchitecture(
            components=components,
            roles=roles,
            entity_relations=entity_relations,
            reasoning=reasoning,
            complexity="medium",  # Будет переопределено в _assess_complexity
            confidence=solution.confidence,
            documentation_references=doc_references
        )
    
    def _assess_complexity(self, architecture: ELMAArchitecture) -> str:
        """Оценивает сложность решения."""
        component_count = len(architecture.components)
        role_count = len(architecture.roles)
        relation_count = len(architecture.entity_relations)
        
        # Простая логика оценки
        total_score = component_count + role_count * 0.5 + relation_count * 0.3
        
        if total_score <= 3:
            return "simple"
        elif total_score <= 8:
            return "medium"
        else:
            return "complex"

