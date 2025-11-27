"""
Модели входных и выходных данных для Decision Engine.
"""
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


class BusinessRequirements(BaseModel):
    """Структурированное бизнес-описание задачи."""
    
    title: str = Field(..., description="Название задачи")
    business_requirements: str = Field(..., description="Описание бизнес-требований")
    inputs: List[str] = Field(default_factory=list, description="Входные данные")
    outputs: List[str] = Field(default_factory=list, description="Выходные данные")
    user_roles: List[str] = Field(default_factory=list, description="Роли пользователей")
    workflow_steps: List[str] = Field(default_factory=list, description="Шаги процесса")
    integration_targets: List[str] = Field(default_factory=list, description="Целевые системы для интеграции")
    ui_requirements: List[str] = Field(default_factory=list, description="Требования к интерфейсу")
    constraints: List[str] = Field(default_factory=list, description="Ограничения и требования")


class ProcessDesign(BaseModel):
    """Дизайн бизнес-процесса."""
    
    process_name: str
    process_type: str = Field(default="workflow", description="Тип процесса: workflow, approval, etc.")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Шаги процесса")
    roles: List[str] = Field(default_factory=list, description="Роли в процессе")
    conditions: List[Dict[str, Any]] = Field(default_factory=list, description="Условия и ветвления")
    timers: List[Dict[str, Any]] = Field(default_factory=list, description="Таймеры и дедлайны")
    notifications: List[Dict[str, Any]] = Field(default_factory=list, description="Уведомления")


class AppStructure(BaseModel):
    """Структура приложения."""
    
    app_name: str
    entity_type: str = Field(default="card", description="Тип сущности: card, directory, etc.")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Поля приложения")
    views: List[Dict[str, Any]] = Field(default_factory=list, description="Представления (списки, карточки)")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="Права доступа по ролям")
    workflows: List[str] = Field(default_factory=list, description="Связанные процессы")


class WidgetDesign(BaseModel):
    """Дизайн виджета."""
    
    widget_name: str
    widget_type: str = Field(..., description="Тип виджета: form, chart, table, etc.")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Поля виджета")
    data_source: Optional[str] = Field(None, description="Источник данных")
    layout: Dict[str, Any] = Field(default_factory=dict, description="Расположение элементов")
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Правила валидации")


class IntegrationPoints(BaseModel):
    """Точки интеграции."""
    
    integration_type: str = Field(..., description="Тип интеграции: api, webhook, connector, etc.")
    target_systems: List[str] = Field(default_factory=list, description="Целевые системы")
    data_mapping: Dict[str, Any] = Field(default_factory=dict, description="Маппинг данных")
    triggers: List[Dict[str, Any]] = Field(default_factory=list, description="Триггеры интеграции")
    authentication: Dict[str, Any] = Field(default_factory=dict, description="Настройки аутентификации")


class DocumentReference(BaseModel):
    """Ссылка на документ документации."""
    
    doc_id: str
    sections: List[str] = Field(default_factory=list, description="Релевантные разделы")
    relevance: str = Field(default="high", description="Релевантность: high, medium, low")
    extracted_info: Dict[str, Any] = Field(default_factory=dict, description="Извлеченная информация")


class ArchitectureSolution(BaseModel):
    """Архитектурное решение."""
    
    solution_type: List[Literal["process", "app", "widget", "module"]] = Field(
        ..., 
        description="Типы решений"
    )
    process_design: Optional[ProcessDesign] = None
    app_structure: Optional[AppStructure] = None
    widget_design: Optional[WidgetDesign] = None
    integration_points: Optional[IntegrationPoints] = None
    references: List[DocumentReference] = Field(
        default_factory=list,
        description="Ссылки на использованную документацию"
    )
    reasoning: str = Field(default="", description="Обоснование решения")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Уверенность в решении (0-1)")



