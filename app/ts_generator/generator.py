"""
Technical Specification Generator - Генератор ТЗ.
Превращает ArchitectureSolution в формализованное техническое задание.
"""
from typing import Literal, Optional
from datetime import datetime
from app.decision_engine.models import ArchitectureSolution
import logging

logger = logging.getLogger(__name__)


class TechnicalDesigner:
    """Генератор технических заданий на основе архитектурных решений."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_ts(
        self, 
        architecture: ArchitectureSolution,
        mode: Literal["deterministic", "verbose"] = "deterministic"
    ) -> str:
        """
        Генерирует техническое задание на основе архитектурного решения.
        
        Args:
            architecture: Архитектурное решение от Decision Engine
            mode: Режим генерации (deterministic - строгий, verbose - более человеческий)
        
        Returns:
            str - Техническое задание в формате Markdown
        """
        if mode == "deterministic":
            return self._generate_deterministic(architecture)
        else:
            return self._generate_verbose(architecture)
    
    def _generate_deterministic(self, architecture: ArchitectureSolution) -> str:
        """Генерирует строго формализованное ТЗ в Markdown."""
        lines = []
        
        # Заголовок
        lines.append("# Техническое задание")
        lines.append("")
        lines.append(f"**Дата создания:** {self.timestamp}")
        lines.append(f"**Уверенность решения:** {architecture.confidence:.1%}")
        lines.append("")
        
        # 1. Описание задачи
        lines.append("## 1. Описание задачи")
        lines.append("")
        if architecture.reasoning:
            lines.append(architecture.reasoning)
        else:
            lines.append("Задача требует реализации решения на платформе ELMA365.")
        lines.append("")
        
        # 2. Типы решений
        lines.append("## 2. Типы решений")
        lines.append("")
        for solution_type in architecture.solution_type:
            type_names = {
                "process": "Бизнес-процесс",
                "app": "Приложение",
                "widget": "Виджет",
                "module": "Модуль интеграции"
            }
            lines.append(f"- **{type_names.get(solution_type, solution_type)}**")
        lines.append("")
        
        # 3. Архитектура решения
        lines.append("## 3. Архитектура решения")
        lines.append("")
        
        # 3.1. Бизнес-процесс
        if architecture.process_design:
            lines.append("### 3.1. Бизнес-процесс")
            lines.append("")
            lines.append(f"**Название процесса:** {architecture.process_design.process_name}")
            lines.append(f"**Тип процесса:** {architecture.process_design.process_type}")
            lines.append("")
            
            # Добавляем информацию из документации, если есть
            process_refs = [r for r in architecture.references if "process" in r.extracted_info.get("title", "").lower() or r.relevance == "high"]
            if process_refs:
                lines.append("**Основано на документации:**")
                for ref in process_refs[:3]:
                    if ref.extracted_info.get("title"):
                        lines.append(f"- [{ref.extracted_info['title']}]({ref.extracted_info.get('url', '#')})")
                lines.append("")
            
            lines.append("**Шаги процесса:**")
            lines.append("")
            for step in architecture.process_design.steps:
                step_num = step.get("step_number", "?")
                step_name = step.get("name", "Не указано")
                step_type = step.get("type", "task")
                assignee = step.get("assignee_role", "")
                source = step.get("source", "")
                lines.append(f"{step_num}. **{step_name}**")
                lines.append(f"   - Тип: {step_type}")
                if assignee:
                    lines.append(f"   - Исполнитель: {assignee}")
                if source == "documentation":
                    lines.append(f"   - Источник: документация ELMA365")
                lines.append("")
            
            if architecture.process_design.roles:
                lines.append("**Роли в процессе:**")
                lines.append("")
                for role in architecture.process_design.roles:
                    lines.append(f"- {role}")
                lines.append("")
            
            if architecture.process_design.conditions:
                lines.append("**Условия и ветвления:**")
                lines.append("")
                for condition in architecture.process_design.conditions:
                    lines.append(f"- {condition}")
                lines.append("")
            
            if architecture.process_design.timers:
                lines.append("**Таймеры и дедлайны:**")
                lines.append("")
                for timer in architecture.process_design.timers:
                    lines.append(f"- {timer}")
                lines.append("")
        
        # 3.2. Приложение
        if architecture.app_structure:
            lines.append("### 3.2. Приложение")
            lines.append("")
            lines.append(f"**Название приложения:** {architecture.app_structure.app_name}")
            lines.append(f"**Тип сущности:** {architecture.app_structure.entity_type}")
            lines.append("")
            
            lines.append("**Поля приложения:**")
            lines.append("")
            lines.append("| Название | Метка | Тип | Обязательное |")
            lines.append("|----------|-------|-----|--------------|")
            for field in architecture.app_structure.fields:
                name = field.get("name", "")
                label = field.get("label", "")
                field_type = field.get("type", "string")
                required = "Да" if field.get("required", False) else "Нет"
                lines.append(f"| {name} | {label} | {field_type} | {required} |")
            lines.append("")
            
            if architecture.app_structure.views:
                lines.append("**Представления:**")
                lines.append("")
                for view in architecture.app_structure.views:
                    view_name = view.get("name", "")
                    view_type = view.get("type", "")
                    fields = ", ".join(view.get("fields", []))
                    lines.append(f"- **{view_name}** ({view_type}): {fields}")
                lines.append("")
            
            if architecture.app_structure.permissions:
                lines.append("**Права доступа:**")
                lines.append("")
                for role, perms in architecture.app_structure.permissions.items():
                    perms_str = ", ".join(perms)
                    lines.append(f"- **{role}**: {perms_str}")
                lines.append("")
        
        # 3.3. Виджет
        if architecture.widget_design:
            lines.append("### 3.3. Виджет")
            lines.append("")
            lines.append(f"**Название виджета:** {architecture.widget_design.widget_name}")
            lines.append(f"**Тип виджета:** {architecture.widget_design.widget_type}")
            lines.append("")
            
            if architecture.widget_design.fields:
                lines.append("**Поля виджета:**")
                lines.append("")
                for field in architecture.widget_design.fields:
                    name = field.get("name", "")
                    label = field.get("label", "")
                    field_type = field.get("type", "")
                    lines.append(f"- **{name}** ({label}): {field_type}")
                lines.append("")
            
            if architecture.widget_design.data_source:
                lines.append(f"**Источник данных:** {architecture.widget_design.data_source}")
                lines.append("")
        
        # 3.4. Интеграция
        if architecture.integration_points:
            lines.append("### 3.4. Интеграция")
            lines.append("")
            lines.append(f"**Тип интеграции:** {architecture.integration_points.integration_type}")
            lines.append("")
            
            if architecture.integration_points.target_systems:
                lines.append("**Целевые системы:**")
                lines.append("")
                for system in architecture.integration_points.target_systems:
                    lines.append(f"- {system}")
                lines.append("")
            
            if architecture.integration_points.data_mapping:
                lines.append("**Маппинг данных:**")
                lines.append("")
                for source, target_info in architecture.integration_points.data_mapping.items():
                    if isinstance(target_info, dict):
                        target = target_info.get("target", "")
                        lines.append(f"- {source} → {target}")
                    else:
                        lines.append(f"- {source} → {target_info}")
                lines.append("")
        
        # 4. Функциональные требования
        lines.append("## 4. Функциональные требования")
        lines.append("")
        
        if architecture.process_design:
            lines.append("### 4.1. Требования к процессу")
            lines.append("")
            lines.append(f"1. Процесс должен содержать {len(architecture.process_design.steps)} шагов")
            if architecture.process_design.roles:
                lines.append(f"2. В процессе должны быть задействованы роли: {', '.join(architecture.process_design.roles)}")
            lines.append("")
        
        if architecture.app_structure:
            lines.append("### 4.2. Требования к приложению")
            lines.append("")
            lines.append(f"1. Приложение должно содержать {len(architecture.app_structure.fields)} полей")
            lines.append(f"2. Должны быть реализованы представления: {', '.join([v.get('name', '') for v in architecture.app_structure.views])}")
            lines.append("")
        
        if architecture.widget_design:
            lines.append("### 4.3. Требования к виджету")
            lines.append("")
            lines.append(f"1. Виджет должен быть типа {architecture.widget_design.widget_type}")
            lines.append(f"2. Виджет должен содержать {len(architecture.widget_design.fields)} полей")
            lines.append("")
        
        if architecture.integration_points:
            lines.append("### 4.4. Требования к интеграции")
            lines.append("")
            lines.append(f"1. Интеграция должна быть типа {architecture.integration_points.integration_type}")
            lines.append(f"2. Интеграция должна работать с системами: {', '.join(architecture.integration_points.target_systems)}")
            lines.append("")
        
        # 5. Нефункциональные требования
        lines.append("## 5. Нефункциональные требования")
        lines.append("")
        lines.append("- Решение должно соответствовать документации ELMA365")
        lines.append("- Все компоненты должны быть протестированы")
        lines.append("- Решение должно быть масштабируемым")
        lines.append("")
        
        # 6. Роли и права
        lines.append("## 6. Роли и права")
        lines.append("")
        
        all_roles = set()
        if architecture.process_design and architecture.process_design.roles:
            all_roles.update(architecture.process_design.roles)
        if architecture.app_structure and architecture.app_structure.permissions:
            all_roles.update(architecture.app_structure.permissions.keys())
        
        if all_roles:
            for role in sorted(all_roles):
                lines.append(f"### {role}")
                lines.append("")
                if architecture.app_structure and architecture.app_structure.permissions.get(role):
                    perms = architecture.app_structure.permissions[role]
                    lines.append(f"**Права доступа:** {', '.join(perms)}")
                else:
                    lines.append("**Права доступа:** определяются в процессе настройки")
                lines.append("")
        else:
            lines.append("Роли определяются в процессе настройки решения.")
            lines.append("")
        
        # 7. Использованная документация ELMA365
        lines.append("## 7. Использованная документация ELMA365")
        lines.append("")
        
        if architecture.references:
            for i, ref in enumerate(architecture.references, 1):
                title = ref.extracted_info.get("title", ref.doc_id)
                url = ref.extracted_info.get("url", "#")
                lines.append(f"{i}. **[{title}]({url})**")
                lines.append(f"   - Релевантность: {ref.relevance}")
                
                # Показываем извлеченную информацию
                if ref.extracted_info.get("headers"):
                    headers_count = len(ref.extracted_info["headers"])
                    lines.append(f"   - Найдено заголовков: {headers_count}")
                
                if ref.extracted_info.get("lists"):
                    lists_count = len(ref.extracted_info["lists"])
                    lines.append(f"   - Найдено списков: {lists_count}")
                
                if ref.extracted_info.get("code_examples"):
                    code_count = len(ref.extracted_info["code_examples"])
                    lines.append(f"   - Найдено примеров кода: {code_count}")
                
                if ref.extracted_info.get("special_blocks"):
                    special_count = len(ref.extracted_info["special_blocks"])
                    lines.append(f"   - Найдено специальных блоков: {special_count}")
                
                # Показываем ключевые заголовки
                if ref.extracted_info.get("headers"):
                    key_headers = ref.extracted_info["headers"][:3]
                    lines.append(f"   - Ключевые разделы:")
                    for header in key_headers:
                        lines.append(f"     * {header.get('text', '')}")
                
                lines.append("")
        else:
            lines.append("Документация будет уточнена в процессе разработки.")
            lines.append("")
        
        # 8. Заключение
        lines.append("## 8. Заключение")
        lines.append("")
        lines.append("Данное техническое задание описывает архитектурное решение, сгенерированное на основе бизнес-требований и документации ELMA365.")
        lines.append("")
        lines.append(f"Уверенность в решении: **{architecture.confidence:.1%}**")
        lines.append("")
        
        # 9. Приложения
        lines.append("## 9. Приложения")
        lines.append("")
        lines.append("### Приложение А. Структура данных")
        lines.append("")
        lines.append("Детальная структура данных будет определена в процессе разработки.")
        lines.append("")
        lines.append("### Приложение Б. Схемы процессов")
        lines.append("")
        if architecture.process_design:
            lines.append("Схема процесса будет создана на основе шагов, описанных в разделе 3.1.")
        else:
            lines.append("Схемы процессов не требуются.")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_verbose(self, architecture: ArchitectureSolution) -> str:
        """Генерирует более человеческий текст ТЗ."""
        lines = []
        
        # Заголовок
        lines.append("# Техническое задание")
        lines.append("")
        lines.append(f"*Создано: {self.timestamp}*")
        lines.append("")
        
        # Введение
        lines.append("## Введение")
        lines.append("")
        lines.append("Настоящее техническое задание описывает решение, разработанное на основе анализа бизнес-требований и документации платформы ELMA365.")
        lines.append("")
        if architecture.reasoning:
            lines.append(architecture.reasoning)
        lines.append("")
        lines.append(f"Уровень уверенности в предложенном решении составляет {architecture.confidence:.1%}.")
        lines.append("")
        
        # Описание решения
        lines.append("## Описание решения")
        lines.append("")
        
        solution_descriptions = {
            "process": "бизнес-процесс",
            "app": "приложение",
            "widget": "виджет",
            "module": "модуль интеграции"
        }
        
        solution_names = [solution_descriptions.get(st, st) for st in architecture.solution_type]
        if len(solution_names) == 1:
            lines.append(f"Решение представляет собой {solution_names[0]}.")
        else:
            lines.append(f"Решение включает в себя: {', '.join(solution_names[:-1])} и {solution_names[-1]}.")
        lines.append("")
        
        # Детальное описание компонентов
        if architecture.process_design:
            lines.append("### Бизнес-процесс")
            lines.append("")
            lines.append(f"Процесс **{architecture.process_design.process_name}** предназначен для автоматизации рабочих процедур.")
            lines.append("")
            lines.append("Процесс состоит из следующих этапов:")
            lines.append("")
            for step in architecture.process_design.steps:
                step_num = step.get("step_number", "?")
                step_name = step.get("name", "Не указано")
                assignee = step.get("assignee_role", "")
                if assignee:
                    lines.append(f"{step_num}. {step_name} (исполнитель: {assignee})")
                else:
                    lines.append(f"{step_num}. {step_name}")
            lines.append("")
            
            if architecture.process_design.roles:
                lines.append(f"В процессе участвуют следующие роли: {', '.join(architecture.process_design.roles)}.")
                lines.append("")
        
        if architecture.app_structure:
            lines.append("### Приложение")
            lines.append("")
            lines.append(f"Приложение **{architecture.app_structure.app_name}** предназначено для работы с данными типа {architecture.app_structure.entity_type}.")
            lines.append("")
            lines.append(f"Приложение содержит {len(architecture.app_structure.fields)} полей для хранения и обработки информации.")
            lines.append("")
            
            if architecture.app_structure.views:
                lines.append("Для работы с данными предусмотрены следующие представления:")
                lines.append("")
                for view in architecture.app_structure.views:
                    view_name = view.get("name", "")
                    view_type = view.get("type", "")
                    lines.append(f"- **{view_name}**: представление типа {view_type}")
                lines.append("")
        
        if architecture.widget_design:
            lines.append("### Виджет")
            lines.append("")
            lines.append(f"Виджет **{architecture.widget_design.widget_name}** представляет собой компонент интерфейса типа {architecture.widget_design.widget_type}.")
            lines.append("")
            if architecture.widget_design.fields:
                lines.append(f"Виджет содержит {len(architecture.widget_design.fields)} полей для взаимодействия с пользователем.")
                lines.append("")
        
        if architecture.integration_points:
            lines.append("### Интеграция")
            lines.append("")
            lines.append(f"Интеграция реализована через механизм {architecture.integration_points.integration_type}.")
            lines.append("")
            if architecture.integration_points.target_systems:
                lines.append(f"Интеграция обеспечивает взаимодействие со следующими системами: {', '.join(architecture.integration_points.target_systems)}.")
                lines.append("")
        
        # Требования
        lines.append("## Требования")
        lines.append("")
        lines.append("### Функциональные требования")
        lines.append("")
        lines.append("Решение должно обеспечивать выполнение всех описанных выше функций.")
        lines.append("")
        lines.append("### Нефункциональные требования")
        lines.append("")
        lines.append("- Решение должно соответствовать стандартам платформы ELMA365")
        lines.append("- Все компоненты должны быть протестированы и документированы")
        lines.append("- Решение должно обеспечивать необходимый уровень производительности")
        lines.append("")
        
        # Документация
        if architecture.references:
            lines.append("## Использованная документация")
            lines.append("")
            lines.append("При разработке решения использовались следующие документы из официальной документации ELMA365:")
            lines.append("")
            for i, ref in enumerate(architecture.references, 1):
                title = ref.extracted_info.get("title", ref.doc_id)
                lines.append(f"{i}. {title}")
                if ref.relevance == "high":
                    lines.append("   *(высокая релевантность)*")
                lines.append("")
        
        # Заключение
        lines.append("## Заключение")
        lines.append("")
        lines.append("Данное техническое задание описывает архитектурное решение, разработанное на основе анализа бизнес-требований и документации ELMA365.")
        lines.append("")
        lines.append("Решение готово к реализации и может быть использовано для дальнейшей разработки.")
        lines.append("")
        
        return "\n".join(lines)

