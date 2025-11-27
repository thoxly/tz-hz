"""
Scope Agent - Подрядчик, который пишет короткое ТЗ для согласования.

Берёт AS-IS и архитектуру и составляет краткое ТЗ для согласования с заказчиком.
"""
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.agents.models import (
    ScopeRequest,
    ScopeResponse,
    ScopeSpecification
)
from app.agents.models import ProcessAsIs, ELMAArchitecture

logger = logging.getLogger(__name__)


class ScopeAgent:
    """
    Агент для генерации краткого ТЗ для согласования.
    
    Задачи:
    - Кратко описывает цель проекта
    - Описывает, что сейчас (AS-IS)
    - Перечисляет сущности, которые будут разработаны
    - Формализует функциональные требования
    - Указывает роли и права
    
    НЕ включает:
    - Интерфейсы
    - Поля форм
    - Низкоуровневую логику
    """
    
    def __init__(self):
        """Инициализация Scope Agent."""
        self.logger = logging.getLogger(__name__)
    
    async def generate_scope(self, request: ScopeRequest) -> ScopeResponse:
        """
        Генерирует краткое ТЗ для согласования.
        
        Args:
            request: Запрос с AS-IS и архитектурой
            
        Returns:
            ScopeResponse с кратким ТЗ
        """
        self.logger.info(f"Генерируем Scope ТЗ для проекта '{request.as_is.process_name}'")
        
        # Формируем сущности для разработки
        entities = self._extract_entities(request.architecture)
        
        # Формируем функциональные требования
        functional_reqs = self._extract_functional_requirements(
            request.as_is,
            request.architecture
        )
        
        # Формируем роли и права
        roles_perms = self._extract_roles_permissions(request.architecture)
        
        # Определяем что НЕ входит в scope
        out_of_scope = self._determine_out_of_scope()
        
        # Оцениваем сложность
        complexity = self._estimate_complexity(request.architecture)
        
        scope = ScopeSpecification(
            project_title=request.as_is.process_name,
            project_goal=self._generate_project_goal(request.as_is),
            as_is_summary=self._generate_as_is_summary(request.as_is),
            entities_to_develop=entities,
            functional_requirements=functional_reqs,
            roles_and_permissions=roles_perms,
            out_of_scope=out_of_scope,
            estimated_complexity=complexity
        )
        
        # Генерируем Markdown
        markdown = self._generate_markdown(scope)
        
        metadata = {
            "entities_count": len(entities),
            "requirements_count": len(functional_reqs),
            "roles_count": len(roles_perms),
            "generated_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"Scope ТЗ сгенерировано: {len(entities)} сущностей, {len(functional_reqs)} требований")
        
        return ScopeResponse(
            scope=scope,
            markdown=markdown,
            generation_metadata=metadata
        )
    
    def _extract_entities(self, architecture: ELMAArchitecture) -> List[Dict[str, str]]:
        """Извлекает сущности для разработки из архитектуры."""
        entities = []
        
        for component in architecture.components:
            entity_type_map = {
                "app": "Приложение",
                "process": "Бизнес-процесс",
                "page": "Страница",
                "widget": "Виджет",
                "script": "Скрипт",
                "microservice": "Микросервис",
                "integration": "Интеграция"
            }
            
            entities.append({
                "name": component.name,
                "type": entity_type_map.get(component.component_type, component.component_type),
                "purpose": component.purpose
            })
        
        return entities
    
    def _extract_functional_requirements(
        self,
        as_is: ProcessAsIs,
        architecture: ELMAArchitecture
    ) -> List[str]:
        """Извлекает функциональные требования."""
        requirements = []
        
        # Требования на основе AS-IS
        if as_is.steps:
            requirements.append(
                f"Автоматизировать процесс из {len(as_is.steps)} шагов: {as_is.process_name}"
            )
        
        if as_is.roles:
            requirements.append(
                f"Обеспечить работу ролей: {', '.join(as_is.roles)}"
            )
        
        # Требования на основе архитектуры
        component_types = {}
        for component in architecture.components:
            comp_type = component.component_type
            component_types[comp_type] = component_types.get(comp_type, 0) + 1
        
        if component_types.get("app"):
            requirements.append(
                f"Создать {component_types['app']} приложение(й) для хранения данных"
            )
        
        if component_types.get("process"):
            requirements.append(
                f"Реализовать {component_types['process']} бизнес-процесс(ов) для автоматизации"
            )
        
        if component_types.get("widget"):
            requirements.append(
                f"Разработать {component_types['widget']} виджет(ов) для интерфейса"
            )
        
        if component_types.get("integration"):
            requirements.append(
                f"Настроить {component_types['integration']} интеграцию(ий) с внешними системами"
            )
        
        # Требования на основе бизнес-правил
        if as_is.business_rules:
            requirements.append(
                f"Реализовать {len(as_is.business_rules)} бизнес-правил(а)"
            )
        
        return requirements[:10]  # Ограничиваем количество
    
    def _extract_roles_permissions(
        self,
        architecture: ELMAArchitecture
    ) -> List[Dict[str, Any]]:
        """Извлекает роли и права доступа."""
        roles_perms = []
        
        for role in architecture.roles:
            roles_perms.append({
                "role": role.role_name,
                "permissions": role.permissions,
                "components": role.components_access[:5]  # Ограничиваем
            })
        
        return roles_perms
    
    def _determine_out_of_scope(self) -> List[str]:
        """Определяет что НЕ входит в scope."""
        return [
            "Детальное проектирование интерфейсов",
            "Конкретные поля форм",
            "Низкоуровневая логика обработки данных",
            "Детальная настройка прав доступа",
            "Интеграционное тестирование",
            "Пользовательская документация"
        ]
    
    def _estimate_complexity(self, architecture: ELMAArchitecture) -> str:
        """Оценивает сложность проекта."""
        complexity_map = {
            "simple": "Простая",
            "medium": "Средняя",
            "complex": "Сложная"
        }
        return complexity_map.get(architecture.complexity, "Средняя")
    
    def _generate_project_goal(self, as_is: ProcessAsIs) -> str:
        """Генерирует цель проекта."""
        if as_is.problems:
            return f"Автоматизировать процесс '{as_is.process_name}' и решить проблемы: {', '.join(as_is.problems[:2])}"
        else:
            return f"Автоматизировать процесс '{as_is.process_name}' на платформе ELMA365"
    
    def _generate_as_is_summary(self, as_is: ProcessAsIs) -> str:
        """Генерирует краткое описание AS-IS."""
        summary = f"Текущий процесс '{as_is.process_name}' состоит из {len(as_is.steps)} шагов. "
        
        if as_is.roles:
            summary += f"В процессе участвуют: {', '.join(as_is.roles)}. "
        
        if as_is.problems:
            summary += f"Основные проблемы: {', '.join(as_is.problems[:2])}."
        
        return summary
    
    def _generate_markdown(self, scope: ScopeSpecification) -> str:
        """Генерирует ТЗ в формате Markdown."""
        lines = []
        
        # Заголовок
        lines.append(f"# Техническое задание: {scope.project_title}")
        lines.append("")
        lines.append(f"*Документ для согласования с заказчиком*")
        lines.append(f"*Дата создания: {scope.created_at}*")
        lines.append("")
        
        # Цель проекта
        lines.append("## 1. Цель проекта")
        lines.append("")
        lines.append(scope.project_goal)
        lines.append("")
        
        # Текущее состояние (AS-IS)
        lines.append("## 2. Текущее состояние (AS-IS)")
        lines.append("")
        lines.append(scope.as_is_summary)
        lines.append("")
        
        # Сущности для разработки
        lines.append("## 3. Сущности для разработки")
        lines.append("")
        if scope.entities_to_develop:
            lines.append("| Название | Тип | Назначение |")
            lines.append("|----------|-----|------------|")
            for entity in scope.entities_to_develop:
                lines.append(f"| {entity['name']} | {entity['type']} | {entity['purpose']} |")
        else:
            lines.append("Сущности будут определены в процессе проектирования.")
        lines.append("")
        
        # Функциональные требования
        lines.append("## 4. Функциональные требования")
        lines.append("")
        for i, req in enumerate(scope.functional_requirements, 1):
            lines.append(f"{i}. {req}")
        lines.append("")
        
        # Роли и права
        lines.append("## 5. Роли и права доступа")
        lines.append("")
        if scope.roles_and_permissions:
            for role_perm in scope.roles_and_permissions:
                lines.append(f"### {role_perm['role']}")
                lines.append("")
                if role_perm['permissions']:
                    lines.append(f"**Права:** {', '.join(role_perm['permissions'])}")
                if role_perm['components']:
                    lines.append(f"**Доступ к компонентам:** {', '.join(role_perm['components'])}")
                lines.append("")
        else:
            lines.append("Роли и права будут определены в процессе разработки.")
            lines.append("")
        
        # Что НЕ входит в scope
        lines.append("## 6. Что НЕ входит в scope")
        lines.append("")
        for item in scope.out_of_scope:
            lines.append(f"- {item}")
        lines.append("")
        
        # Оценка сложности
        lines.append("## 7. Оценка сложности")
        lines.append("")
        lines.append(f"**Оценка:** {scope.estimated_complexity}")
        lines.append("")
        
        # Заключение
        lines.append("## 8. Заключение")
        lines.append("")
        lines.append("Данное техническое задание описывает объем работ для автоматизации процесса на платформе ELMA365.")
        lines.append("Детальная техническая спецификация будет разработана после согласования данного документа.")
        lines.append("")
        
        return "\n".join(lines)

