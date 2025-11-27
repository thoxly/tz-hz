"""
Модели данных для всех агентов.
"""
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Process Extractor Models
# ============================================================================

class Actor(BaseModel):
    """Актор процесса."""
    
    name: str = Field(..., description="Имя актора")
    role: str = Field(..., description="Роль актора")


class Entity(BaseModel):
    """Сущность процесса."""
    
    name: str = Field(..., description="Название сущности")
    description: str = Field(..., description="Описание сущности")


class ProcessStep(BaseModel):
    """Шаг процесса AS-IS (новый формат)."""
    
    id: str = Field(..., description="Уникальный ID шага (например, AS1, AS2)")
    actor: str = Field(..., description="Актор шага или 'неизвестно'")
    action: str = Field(..., description="Действие шага")
    input: str = Field(..., description="Входные данные или 'неизвестно'")
    output: str = Field(..., description="Выходные данные или 'неизвестно'")
    business_rules: List[str] = Field(default_factory=list, description="Бизнес-правила шага")
    timeframe: str = Field(..., description="Временные рамки или 'неизвестно'")
    next: Optional[str] = Field(None, description="ID следующего шага или null")
    source_fragment: str = Field(..., description="Фрагмент исходного текста")


class BusinessRule(BaseModel):
    """Бизнес-правило, извлеченное из транскрибации."""
    
    rule_text: str = Field(..., description="Текст правила")
    context: Optional[str] = Field(None, description="Контекст правила")
    step_numbers: List[int] = Field(default_factory=list, description="Связанные шаги")


class ProcessAsIs(BaseModel):
    """Структурированный процесс AS-IS (новый формат)."""
    
    process_name: str = Field(..., description="Название процесса")
    goal: str = Field(..., description="Цель процесса")
    actors: List[Actor] = Field(default_factory=list, description="Акторы процесса")
    entities: List[Entity] = Field(default_factory=list, description="Сущности процесса")
    steps: List[ProcessStep] = Field(default_factory=list, description="Шаги процесса")
    pain_points: List[str] = Field(default_factory=list, description="Точки боли/проблемы")
    
    # Дополнительные поля для обратной совместимости
    process_description: Optional[str] = Field(None, description="Описание процесса (legacy)")
    roles: Optional[List[str]] = Field(None, description="Роли участников (legacy)")
    business_rules: Optional[List[BusinessRule]] = Field(None, description="Бизнес-правила (legacy)")
    problems: Optional[List[str]] = Field(None, description="Проблемы (legacy)")
    unknowns: Optional[List[str]] = Field(None, description="Неизвестные моменты (legacy)")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Уверенность в структуризации")


class ProcessExtractRequest(BaseModel):
    """Запрос на извлечение процесса AS-IS."""
    
    transcript: str = Field(..., description="Транскрибация встречи с клиентом")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Дополнительный контекст (метаданные встречи)"
    )


class ProcessExtractResponse(BaseModel):
    """Ответ с извлеченным процессом AS-IS."""
    
    as_is: ProcessAsIs = Field(..., description="Структурированный процесс AS-IS")
    extraction_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Метаданные извлечения"
    )


# ============================================================================
# Architect Agent Models
# ============================================================================

class ELMAComponent(BaseModel):
    """Компонент ELMA365."""
    
    component_type: Literal["app", "process", "page", "widget", "script", "microservice", "integration"]
    name: str = Field(..., description="Название компонента")
    description: str = Field(..., description="Описание компонента")
    purpose: str = Field(..., description="Назначение компонента")
    related_steps: List[int] = Field(default_factory=list, description="Связанные шаги AS-IS")


class RoleDesign(BaseModel):
    """Дизайн роли в системе."""
    
    role_name: str = Field(..., description="Название роли")
    permissions: List[str] = Field(default_factory=list, description="Права доступа")
    components_access: List[str] = Field(default_factory=list, description="Доступ к компонентам")


class EntityRelation(BaseModel):
    """Связь между сущностями."""
    
    from_entity: str = Field(..., description="Исходная сущность")
    to_entity: str = Field(..., description="Целевая сущность")
    relation_type: str = Field(..., description="Тип связи (reference, workflow, integration)")
    description: Optional[str] = Field(None, description="Описание связи")


class ELMAArchitecture(BaseModel):
    """Архитектурное решение ELMA365."""
    
    components: List[ELMAComponent] = Field(default_factory=list, description="Компоненты решения")
    roles: List[RoleDesign] = Field(default_factory=list, description="Роли и права")
    entity_relations: List[EntityRelation] = Field(default_factory=list, description="Связи сущностей")
    reasoning: str = Field(..., description="Обоснование архитектуры")
    complexity: Literal["simple", "medium", "complex"] = Field(..., description="Сложность решения")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Уверенность в решении")
    documentation_references: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Ссылки на документацию ELMA365"
    )


class ArchitectRequest(BaseModel):
    """Запрос на проектирование архитектуры."""
    
    as_is: ProcessAsIs = Field(..., description="Структурированный процесс AS-IS")


class ArchitectResponse(BaseModel):
    """Ответ с архитектурным решением."""
    
    architecture: ELMAArchitecture = Field(..., description="Архитектурное решение")
    design_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Метаданные проектирования"
    )


# ============================================================================
# Scope Agent Models
# ============================================================================

class ScopeSpecification(BaseModel):
    """Краткое ТЗ для согласования (Scope)."""
    
    project_title: str = Field(..., description="Название проекта")
    project_goal: str = Field(..., description="Цель проекта")
    as_is_summary: str = Field(..., description="Краткое описание текущего состояния (AS-IS)")
    entities_to_develop: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Сущности для разработки (название, тип, назначение)"
    )
    functional_requirements: List[str] = Field(
        default_factory=list,
        description="Функциональные требования"
    )
    roles_and_permissions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Роли и права доступа"
    )
    out_of_scope: List[str] = Field(
        default_factory=list,
        description="Что НЕ входит в scope (будет позже)"
    )
    estimated_complexity: str = Field(..., description="Оценка сложности")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ScopeRequest(BaseModel):
    """Запрос на генерацию Scope ТЗ."""
    
    as_is: ProcessAsIs = Field(..., description="Структурированный процесс AS-IS")
    architecture: ELMAArchitecture = Field(..., description="Архитектурное решение")


class ScopeResponse(BaseModel):
    """Ответ с кратким ТЗ."""
    
    scope: ScopeSpecification = Field(..., description="Краткое ТЗ для согласования")
    markdown: str = Field(..., description="ТЗ в формате Markdown")
    generation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Метаданные генерации"
    )

