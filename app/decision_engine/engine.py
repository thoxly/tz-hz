"""
Decision Engine - Агент-Архитектор для генерации архитектурных решений.
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.decision_engine.models import (
    BusinessRequirements,
    ArchitectureSolution,
    ProcessDesign,
    AppStructure,
    WidgetDesign,
    IntegrationPoints,
    DocumentReference
)
from app.decision_engine.analyzer import RequirementAnalyzer
from app.decision_engine.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Агент-Архитектор для генерации архитектурных решений на основе документации."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analyzer = RequirementAnalyzer()
        self.mcp_client = MCPClient(session)
    
    async def design_solution(self, requirements: BusinessRequirements) -> ArchitectureSolution:
        """
        Генерирует архитектурное решение на основе бизнес-требований.
        
        Args:
            requirements: Структурированные бизнес-требования
            
        Returns:
            ArchitectureSolution с архитектурным решением
        """
        logger.info(f"Начинаем проектирование решения для: {requirements.title}")
        
        # Шаг 1: Определяем тип решения
        solution_types = self.analyzer.determine_solution_types(requirements)
        logger.info(f"Определены типы решений: {solution_types}")
        
        # Шаг 2: Ищем релевантную документацию через MCP
        references = await self._gather_references(requirements, solution_types)
        logger.info(f"Найдено {len(references)} релевантных документов")
        
        # Шаг 3: Генерируем архитектурное решение
        solution = ArchitectureSolution(
            solution_type=solution_types,
            references=references,
            confidence=self._calculate_confidence(requirements, references)
        )
        
        # Шаг 4: Заполняем детали для каждого типа решения
        if "process" in solution_types:
            solution.process_design = await self._design_process(requirements, references)
        
        if "app" in solution_types:
            solution.app_structure = await self._design_app(requirements, references)
        
        if "widget" in solution_types:
            solution.widget_design = await self._design_widget(requirements, references)
        
        if "module" in solution_types:
            solution.integration_points = await self._design_integration(requirements, references)
        
        # Шаг 5: Формируем обоснование
        solution.reasoning = self._generate_reasoning(requirements, solution, references)
        
        logger.info(f"Решение сгенерировано с уверенностью: {solution.confidence:.2f}")
        return solution
    
    async def _gather_references(
        self, 
        requirements: BusinessRequirements, 
        solution_types: List[str]
    ) -> List[DocumentReference]:
        """Собирает релевантные документы через MCP и извлекает конкретную информацию."""
        references = []
        seen_doc_ids = set()
        
        # Ищем документы по типу решения
        if "process" in solution_types:
            docs = await self.mcp_client.find_process_docs()
            for doc in docs[:5]:
                doc_id = doc.get("doc_id")
                if doc_id and doc_id not in seen_doc_ids:
                    # Извлекаем конкретную информацию из документа
                    extracted = await self._extract_doc_info(doc_id, "process")
                    references.append(DocumentReference(
                        doc_id=doc_id,
                        relevance="high",
                        extracted_info={
                            "title": doc.get("title"),
                            "context": doc.get("context", ""),
                            **extracted
                        }
                    ))
                    seen_doc_ids.add(doc_id)
        
        if "app" in solution_types:
            docs = await self.mcp_client.find_app_docs()
            for doc in docs[:5]:
                doc_id = doc.get("doc_id") or doc.get("title", "").lower().replace(" ", "-")
                if doc_id and doc_id not in seen_doc_ids:
                    # Извлекаем конкретную информацию из документа
                    extracted = await self._extract_doc_info(doc_id, "app")
                    references.append(DocumentReference(
                        doc_id=doc_id,
                        relevance="high",
                        extracted_info={
                            "title": doc.get("title"),
                            "context": doc.get("context", ""),
                            **extracted
                        }
                    ))
                    seen_doc_ids.add(doc_id)
        
        if "module" in solution_types:
            docs = await self.mcp_client.find_integration_docs()
            for doc in docs[:5]:
                doc_id = doc.get("doc_id") or doc.get("title", "").lower().replace(" ", "-")
                if doc_id and doc_id not in seen_doc_ids:
                    extracted = await self._extract_doc_info(doc_id, "integration")
                    references.append(DocumentReference(
                        doc_id=doc_id,
                        relevance="high",
                        extracted_info={
                            "title": doc.get("title"),
                            "context": doc.get("context", ""),
                            **extracted
                        }
                    ))
                    seen_doc_ids.add(doc_id)
        
        if "widget" in solution_types:
            docs = await self.mcp_client.find_widget_docs()
            for doc in docs[:5]:
                doc_id = doc.get("doc_id") or doc.get("title", "").lower().replace(" ", "-")
                if doc_id and doc_id not in seen_doc_ids:
                    extracted = await self._extract_doc_info(doc_id, "widget")
                    references.append(DocumentReference(
                        doc_id=doc_id,
                        relevance="high",
                        extracted_info={
                            "title": doc.get("title"),
                            "context": doc.get("context", ""),
                            **extracted
                        }
                    ))
                    seen_doc_ids.add(doc_id)
        
        # Ищем по ключевым словам из требований
        keywords = self._extract_keywords(requirements)
        if keywords:
            relevant_docs = await self.mcp_client.find_relevant_docs(' '.join(keywords[:3]), limit=5)
            for doc in relevant_docs:
                doc_id = doc.get("doc_id") or doc.get("title", "").lower().replace(" ", "-")
                if doc_id and doc_id not in seen_doc_ids:
                    extracted = await self._extract_doc_info(doc_id, "general")
                    references.append(DocumentReference(
                        doc_id=doc_id,
                        relevance="medium",
                        extracted_info={
                            "title": doc.get("title"),
                            "context": doc.get("context", ""),
                            **extracted
                        }
                    ))
                    seen_doc_ids.add(doc_id)
        
        return references
    
    async def _extract_doc_info(self, doc_id: str, doc_type: str) -> Dict[str, Any]:
        """Извлекает конкретную информацию из документа через MCP."""
        extracted = {
            "headers": [],
            "lists": [],
            "code_examples": [],
            "special_blocks": [],
            "url": ""
        }
        
        try:
            # Получаем структуру документа
            doc_structure = await self.mcp_client.get_doc_structure(doc_id)
            if doc_structure:
                extracted["url"] = doc_structure.get("url", "")
                
                # Извлекаем заголовки уровня 2-3
                headers = await self.mcp_client.search_headers(
                    keywords=[doc_type, "настройка", "создание", "использование"],
                    level=2
                )
                # Фильтруем по doc_id
                doc_headers = [h for h in headers if h.get("doc_id") == doc_id][:10]
                extracted["headers"] = [
                    {
                        "text": h.get("text", ""),
                        "level": h.get("level", 2),
                        "url": h.get("url", "")
                    }
                    for h in doc_headers
                ]
                
                # Извлекаем списки (часто содержат шаги настройки)
                list_entities = await self.mcp_client.tools.search_entities("list", {"limit": 20})
                doc_lists = [l for l in list_entities if l.get("doc_id") == doc_id][:5]
                extracted["lists"] = [
                    {
                        "items": l.get("items", [])[:10],  # Первые 10 элементов
                        "ordered": l.get("ordered", False),
                        "text": l.get("text", "")[:200]  # Первые 200 символов
                    }
                    for l in doc_lists
                ]
                
                # Извлекаем примеры кода
                code_entities = await self.mcp_client.tools.search_entities("code_block", {"limit": 10})
                doc_code = [c for c in code_entities if c.get("doc_id") == doc_id][:3]
                extracted["code_examples"] = [
                    {
                        "language": c.get("language", ""),
                        "code": c.get("code", "")[:500],  # Первые 500 символов
                        "text": c.get("text", "")[:200]
                    }
                    for c in doc_code
                ]
                
                # Извлекаем специальные блоки (Важно, Пример, В этой статье)
                special_entities = await self.mcp_client.tools.search_entities("special_block", {"limit": 15})
                doc_special = [s for s in special_entities if s.get("doc_id") == doc_id][:5]
                extracted["special_blocks"] = [
                    {
                        "kind": s.get("kind", ""),
                        "heading": s.get("heading", ""),
                        "content": s.get("content", [])[:5],  # Первые 5 элементов
                        "text": s.get("text", "")[:300]
                    }
                    for s in doc_special
                ]
        except Exception as e:
            logger.warning(f"Ошибка при извлечении информации из документа {doc_id}: {e}")
        
        return extracted
    
    async def _design_process(
        self, 
        requirements: BusinessRequirements, 
        references: List[DocumentReference]
    ) -> ProcessDesign:
        """Проектирует бизнес-процесс на основе документации."""
        # Ищем примеры процессов в документации
        process_headers = await self.mcp_client.search_headers(["процесс", "workflow", "шаг"], level=2)
        
        # Извлекаем шаги из документации (из списков в релевантных документах)
        doc_steps = []
        for ref in references:
            if ref.relevance == "high" and "lists" in ref.extracted_info:
                for list_item in ref.extracted_info.get("lists", []):
                    items = list_item.get("items", [])
                    # Ищем списки, которые похожи на шаги процесса
                    if len(items) >= 2 and any(keyword in ' '.join(items).lower() for keyword in ["шаг", "этап", "step", "действие"]):
                        doc_steps.extend(items[:10])  # Берем первые 10 элементов
        
        # Извлекаем информацию о шагах из требований
        steps = []
        if requirements.workflow_steps:
            # Используем шаги из требований
            for i, step_desc in enumerate(requirements.workflow_steps, 1):
                steps.append({
                    "step_number": i,
                    "name": step_desc,
                    "type": "task",
                    "assignee_role": requirements.user_roles[0] if requirements.user_roles else None,
                    "source": "requirements"
                })
        elif doc_steps:
            # Используем шаги из документации
            for i, step_text in enumerate(doc_steps[:10], 1):
                steps.append({
                    "step_number": i,
                    "name": step_text[:100],  # Ограничиваем длину
                    "type": "task",
                    "assignee_role": requirements.user_roles[0] if requirements.user_roles else None,
                    "source": "documentation"
                })
        
        # Если шаги не указаны, создаем базовую структуру
        if not steps:
            steps = [{
                "step_number": 1,
                "name": "Начало процесса",
                "type": "start"
            }, {
                "step_number": 2,
                "name": "Основной этап",
                "type": "task",
                "assignee_role": requirements.user_roles[0] if requirements.user_roles else None
            }, {
                "step_number": 3,
                "name": "Завершение процесса",
                "type": "end"
            }]
        
        return ProcessDesign(
            process_name=requirements.title,
            process_type="workflow",
            steps=steps,
            roles=requirements.user_roles,
            conditions=[],
            timers=[],
            notifications=[]
        )
    
    async def _design_app(
        self, 
        requirements: BusinessRequirements, 
        references: List[DocumentReference]
    ) -> AppStructure:
        """Проектирует структуру приложения."""
        # Ищем информацию о полях приложений
        app_headers = await self.mcp_client.search_headers(["приложение", "справочник", "карточка"], level=2)
        
        # Создаем поля на основе входных/выходных данных
        fields = []
        for input_data in requirements.inputs:
            fields.append({
                "name": input_data.lower().replace(' ', '_'),
                "label": input_data,
                "type": "string",  # string, number, date, boolean, etc.
                "required": True
            })
        
        for output_data in requirements.outputs:
            fields.append({
                "name": output_data.lower().replace(' ', '_'),
                "label": output_data,
                "type": "string",
                "required": False
            })
        
        # Если полей нет, создаем базовую структуру
        if not fields:
            fields = [{
                "name": "title",
                "label": "Название",
                "type": "string",
                "required": True
            }]
        
        # Создаем представления
        views = [
            {
                "name": "list",
                "type": "table",
                "fields": [f["name"] for f in fields[:5]]
            },
            {
                "name": "card",
                "type": "form",
                "fields": [f["name"] for f in fields]
            }
        ]
        
        # Права доступа
        permissions = {}
        for role in requirements.user_roles:
            permissions[role] = ["read", "create", "update"]
        
        return AppStructure(
            app_name=requirements.title,
            entity_type="card",
            fields=fields,
            views=views,
            permissions=permissions,
            workflows=[]
        )
    
    async def _design_widget(
        self, 
        requirements: BusinessRequirements, 
        references: List[DocumentReference]
    ) -> WidgetDesign:
        """Проектирует виджет."""
        widget_type = "form"  # form, chart, table, dashboard
        
        # Определяем тип виджета по требованиям к UI
        if any("форма" in req.lower() or "form" in req.lower() for req in requirements.ui_requirements):
            widget_type = "form"
        elif any("график" in req.lower() or "chart" in req.lower() for req in requirements.ui_requirements):
            widget_type = "chart"
        elif any("таблица" in req.lower() or "table" in req.lower() for req in requirements.ui_requirements):
            widget_type = "table"
        
        # Создаем поля виджета
        fields = []
        for input_data in requirements.inputs:
            fields.append({
                "name": input_data.lower().replace(' ', '_'),
                "label": input_data,
                "type": "text"
            })
        
        return WidgetDesign(
            widget_name=requirements.title,
            widget_type=widget_type,
            fields=fields,
            data_source=None,
            layout={},
            validation_rules=[]
        )
    
    async def _design_integration(
        self, 
        requirements: BusinessRequirements, 
        references: List[DocumentReference]
    ) -> IntegrationPoints:
        """Проектирует точки интеграции."""
        integration_type = "api"  # api, webhook, connector
        
        # Определяем тип интеграции
        if any("webhook" in target.lower() for target in requirements.integration_targets):
            integration_type = "webhook"
        elif any("connector" in target.lower() for target in requirements.integration_targets):
            integration_type = "connector"
        
        # Маппинг данных
        data_mapping = {}
        for i, input_data in enumerate(requirements.inputs):
            data_mapping[input_data] = {
                "source": input_data.lower().replace(' ', '_'),
                "target": requirements.outputs[i].lower().replace(' ', '_') if i < len(requirements.outputs) else input_data.lower().replace(' ', '_')
            }
        
        return IntegrationPoints(
            integration_type=integration_type,
            target_systems=requirements.integration_targets,
            data_mapping=data_mapping,
            triggers=[],
            authentication={}
        )
    
    def _extract_keywords(self, requirements: BusinessRequirements) -> List[str]:
        """Извлекает ключевые слова из требований."""
        text = f"{requirements.title} {requirements.business_requirements}"
        # Простое извлечение: берем слова длиннее 4 символов
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]
        return list(set(keywords))[:10]
    
    def _calculate_confidence(
        self, 
        requirements: BusinessRequirements, 
        references: List[DocumentReference]
    ) -> float:
        """Вычисляет уверенность в решении (0-1)."""
        confidence = 0.5  # Базовая уверенность
        
        # Увеличиваем уверенность при наличии релевантных документов
        if references:
            high_relevance = sum(1 for r in references if r.relevance == "high")
            confidence += min(0.3, high_relevance * 0.1)
        
        # Увеличиваем уверенность при детальных требованиях
        if requirements.workflow_steps:
            confidence += 0.1
        if requirements.inputs or requirements.outputs:
            confidence += 0.1
        if requirements.user_roles:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _generate_reasoning(
        self, 
        requirements: BusinessRequirements,
        solution: ArchitectureSolution,
        references: List[DocumentReference]
    ) -> str:
        """Генерирует обоснование решения."""
        reasoning_parts = [
            f"На основе анализа бизнес-требований '{requirements.title}' определены следующие типы решений: {', '.join(solution.solution_type)}."
        ]
        
        if solution.process_design:
            reasoning_parts.append(
                f"Спроектирован бизнес-процесс '{solution.process_design.process_name}' "
                f"с {len(solution.process_design.steps)} шагами."
            )
        
        if solution.app_structure:
            reasoning_parts.append(
                f"Спроектировано приложение '{solution.app_structure.app_name}' "
                f"с {len(solution.app_structure.fields)} полями."
            )
        
        if solution.widget_design:
            reasoning_parts.append(
                f"Спроектирован виджет '{solution.widget_design.widget_name}' "
                f"типа '{solution.widget_design.widget_type}'."
            )
        
        if solution.integration_points:
            reasoning_parts.append(
                f"Определены точки интеграции типа '{solution.integration_points.integration_type}' "
                f"с системами: {', '.join(solution.integration_points.target_systems)}."
            )
        
        if references:
            reasoning_parts.append(
                f"Использовано {len(references)} релевантных документов из документации ELMA365."
            )
        
        return " ".join(reasoning_parts)

