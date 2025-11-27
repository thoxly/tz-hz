"""
Анализатор бизнес-требований для определения типа решения.
"""
from typing import List, Dict, Set
import re
from app.decision_engine.models import BusinessRequirements


class RequirementAnalyzer:
    """Анализирует бизнес-требования и определяет тип решения."""
    
    # Ключевые слова для определения типа решения
    APP_KEYWORDS = {
        'приложение', 'справочник', 'карточка', 'данные', 'entity', 'сущность',
        'список', 'таблица', 'directory', 'card', 'application'
    }
    
    PROCESS_KEYWORDS = {
        'процесс', 'согласование', 'этап', 'шаг', 'workflow', 'процедура',
        'маршрут', 'approval', 'route', 'бизнес-процесс', 'автоматизация'
    }
    
    WIDGET_KEYWORDS = {
        'форма', 'виджет', 'widget', 'form', 'интерфейс', 'ui', 'элемент',
        'компонент', 'dashboard', 'панель', 'отчет'
    }
    
    MODULE_KEYWORDS = {
        'интеграция', 'модуль', 'api', 'webhook', 'connector', 'интегратор',
        'синхронизация', 'обмен данными', 'external', 'внешняя система'
    }
    
    def __init__(self):
        self.app_score = 0
        self.process_score = 0
        self.widget_score = 0
        self.module_score = 0
    
    def analyze(self, requirements: BusinessRequirements) -> Dict[str, float]:
        """
        Анализирует требования и возвращает оценки для каждого типа решения.
        
        Returns:
            Dict с оценками: {"app": 0.8, "process": 0.2, "widget": 0.1, "module": 0.0}
        """
        text = self._extract_text(requirements)
        text_lower = text.lower()
        
        # Подсчитываем совпадения по ключевым словам
        app_matches = sum(1 for keyword in self.APP_KEYWORDS if keyword in text_lower)
        process_matches = sum(1 for keyword in self.PROCESS_KEYWORDS if keyword in text_lower)
        widget_matches = sum(1 for keyword in self.WIDGET_KEYWORDS if keyword in text_lower)
        module_matches = sum(1 for keyword in self.MODULE_KEYWORDS if keyword in text_lower)
        
        # Анализируем структуру требований
        if requirements.workflow_steps:
            process_matches += len(requirements.workflow_steps) * 2
        
        if requirements.inputs or requirements.outputs:
            app_matches += 2
        
        if requirements.ui_requirements:
            widget_matches += len(requirements.ui_requirements)
        
        if requirements.integration_targets:
            module_matches += len(requirements.integration_targets) * 3
        
        # Нормализуем оценки (0-1)
        total = app_matches + process_matches + widget_matches + module_matches
        if total == 0:
            # Если нет явных признаков, предполагаем приложение
            return {"app": 0.5, "process": 0.3, "widget": 0.1, "module": 0.1}
        
        return {
            "app": min(1.0, app_matches / max(total, 1)),
            "process": min(1.0, process_matches / max(total, 1)),
            "widget": min(1.0, widget_matches / max(total, 1)),
            "module": min(1.0, module_matches / max(total, 1))
        }
    
    def determine_solution_types(self, requirements: BusinessRequirements) -> List[str]:
        """
        Определяет типы решений на основе анализа.
        
        Returns:
            List[str] - список типов решений, отсортированный по релевантности
        """
        scores = self.analyze(requirements)
        
        # Порог для включения типа решения
        threshold = 0.2
        
        # Сортируем по убыванию оценки
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Возвращаем типы с оценкой выше порога
        solution_types = [
            solution_type 
            for solution_type, score in sorted_types 
            if score >= threshold
        ]
        
        # Если ничего не найдено, возвращаем наиболее вероятный тип
        if not solution_types:
            solution_types = [sorted_types[0][0]]
        
        return solution_types
    
    def _extract_text(self, requirements: BusinessRequirements) -> str:
        """Извлекает весь текст из требований."""
        parts = [
            requirements.title,
            requirements.business_requirements,
            ' '.join(requirements.inputs),
            ' '.join(requirements.outputs),
            ' '.join(requirements.user_roles),
            ' '.join(requirements.workflow_steps),
            ' '.join(requirements.integration_targets),
            ' '.join(requirements.ui_requirements),
            ' '.join(requirements.constraints)
        ]
        return ' '.join(parts)



