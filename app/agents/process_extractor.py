"""
Process Extractor - Аналитик, который превращает хаос в структуру.

Берёт грязный поток сознания клиента (транскрибацию встречи) и превращает его 
в понятный, структурированный процесс AS-IS.
"""
from typing import List, Dict, Any, Optional
import logging
import re
from app.agents.models import (
    ProcessExtractRequest,
    ProcessExtractResponse,
    ProcessAsIs,
    ProcessStep,
    BusinessRule
)

logger = logging.getLogger(__name__)


class ProcessExtractor:
    """
    Агент для извлечения структурированного процесса AS-IS из транскрибации.
    
    Задачи:
    - Выделяет роли (кто участвует)
    - Выделяет шаги процесса
    - Ставит шаги в правильный порядок
    - Фиксирует бизнес-правила
    - Отмечает проблемы, боли, дубли, хаос
    - Указывает "неизвестно", если данные отсутствуют
    """
    
    def __init__(self):
        """Инициализация Process Extractor."""
        self.logger = logging.getLogger(__name__)
    
    async def extract(self, request: ProcessExtractRequest) -> ProcessExtractResponse:
        """
        Извлекает структурированный процесс AS-IS из транскрибации.
        
        Args:
            request: Запрос с транскрибацией
            
        Returns:
            ProcessExtractResponse с извлеченным процессом
        """
        self.logger.info("Начинаем извлечение процесса AS-IS из транскрибации")
        
        transcript = request.transcript.strip()
        
        # Извлекаем компоненты процесса
        process_name = self._extract_process_name(transcript)
        roles = self._extract_roles(transcript)
        steps = self._extract_steps(transcript, roles)
        business_rules = self._extract_business_rules(transcript)
        problems = self._extract_problems(transcript)
        unknowns = self._extract_unknowns(transcript)
        
        # Формируем описание процесса
        process_description = self._generate_process_description(transcript, steps)
        
        # Вычисляем уверенность
        confidence = self._calculate_confidence(transcript, steps, roles)
        
        as_is = ProcessAsIs(
            process_name=process_name,
            process_description=process_description,
            roles=roles,
            steps=steps,
            business_rules=business_rules,
            problems=problems,
            unknowns=unknowns,
            confidence=confidence
        )
        
        metadata = {
            "transcript_length": len(transcript),
            "steps_count": len(steps),
            "roles_count": len(roles),
            "rules_count": len(business_rules),
            "problems_count": len(problems)
        }
        
        self.logger.info(f"Извлечен процесс '{process_name}' с {len(steps)} шагами, уверенность: {confidence:.2f}")
        
        return ProcessExtractResponse(
            as_is=as_is,
            extraction_metadata=metadata
        )
    
    def _extract_process_name(self, transcript: str) -> str:
        """Извлекает название процесса из транскрибации."""
        # Ищем паттерны типа "процесс X", "процедура Y", "задача Z"
        patterns = [
            r"процесс[ае]?\s+([А-Яа-яЁё\w\s]+?)(?:\.|,|$|\n)",
            r"процедур[аеы]?\s+([А-Яа-яЁё\w\s]+?)(?:\.|,|$|\n)",
            r"задач[аеи]?\s+([А-Яа-яЁё\w\s]+?)(?:\.|,|$|\n)",
            r"речь идет о ([А-Яа-яЁё\w\s]+?)(?:\.|,|$|\n)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:
                    return name
        
        # Если не нашли, берем первые слова
        words = transcript.split()[:5]
        return " ".join(words) if words else "Неизвестный процесс"
    
    def _extract_roles(self, transcript: str) -> List[str]:
        """Извлекает роли участников процесса."""
        roles = set()
        
        # Паттерны для ролей
        role_patterns = [
            r"([А-Яа-яЁё]+(?:менеджер|директор|бухгалтер|специалист|руководитель|сотрудник|администратор))",
            r"([А-Яа-яЁё]+(?:отдел|департамент|служба))",
            r"роль[и]?\s+([А-Яа-яЁё\w\s]+?)(?:\.|,|$|\n)",
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            roles.update(matches)
        
        # Убираем дубликаты и нормализуем
        normalized_roles = []
        seen = set()
        for role in roles:
            role_lower = role.lower().strip()
            if role_lower not in seen and len(role) > 2:
                normalized_roles.append(role.strip())
                seen.add(role_lower)
        
        return normalized_roles[:10]  # Ограничиваем количество
    
    def _extract_steps(self, transcript: str, roles: List[str]) -> List[ProcessStep]:
        """Извлекает шаги процесса из транскрибации."""
        steps = []
        
        # Паттерны для шагов
        step_patterns = [
            r"(?:шаг|этап|стадия|стадию|шага|этапа)\s+(\d+)[:\.]\s*([^\.]+?)(?:\.|$|\n)",
            r"(\d+)[\.\)]\s*([^\.]+?)(?:\.|$|\n)",
            r"(?:сначала|потом|затем|далее|после этого)[\s,]+([^\.]+?)(?:\.|$|\n)",
            r"(?:делаем|выполняем|осуществляем)[\s,]+([^\.]+?)(?:\.|$|\n)",
        ]
        
        step_texts = []
        for pattern in step_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    step_num = match.group(1) if match.group(1).isdigit() else None
                    step_text = match.group(2).strip()
                else:
                    step_num = None
                    step_text = match.group(1).strip()
                
                if step_text and len(step_text) > 5:
                    step_texts.append((step_num, step_text))
        
        # Если не нашли структурированные шаги, разбиваем по предложениям
        if not step_texts:
            sentences = re.split(r'[\.!?]\s+', transcript)
            for i, sentence in enumerate(sentences[:20], 1):  # Ограничиваем 20 шагами
                sentence = sentence.strip()
                if len(sentence) > 10 and any(keyword in sentence.lower() for keyword in 
                    ['делаем', 'выполняем', 'отправляем', 'получаем', 'создаем', 'проверяем']):
                    step_texts.append((str(i), sentence))
        
        # Формируем ProcessStep объекты
        for i, (step_num, step_text) in enumerate(step_texts[:15], 1):  # Максимум 15 шагов
            # Извлекаем актора
            actor = self._extract_actor_from_step(step_text, roles)
            
            # Извлекаем входы/выходы
            inputs = self._extract_inputs_outputs(step_text, "input")
            outputs = self._extract_inputs_outputs(step_text, "output")
            
            # Извлекаем условия
            conditions = self._extract_conditions(step_text)
            
            # Извлекаем проблемы
            problems = self._extract_problems_from_step(step_text)
            
            steps.append(ProcessStep(
                step_number=i,
                name=step_text[:100] if len(step_text) > 100 else step_text,
                description=step_text if len(step_text) <= 100 else None,
                actor=actor,
                inputs=inputs,
                outputs=outputs,
                conditions=conditions,
                problems=problems,
                is_unknown=False
            ))
        
        return steps
    
    def _extract_actor_from_step(self, step_text: str, roles: List[str]) -> Optional[str]:
        """Извлекает актора (роль) из шага."""
        step_lower = step_text.lower()
        for role in roles:
            if role.lower() in step_lower:
                return role
        return None
    
    def _extract_inputs_outputs(self, text: str, io_type: str) -> List[str]:
        """Извлекает входные или выходные данные."""
        items = []
        
        if io_type == "input":
            patterns = [
                r"получаем\s+([^\.]+?)(?:\.|$|\n)",
                r"вход[ае]?\s+([^\.]+?)(?:\.|$|\n)",
                r"принимаем\s+([^\.]+?)(?:\.|$|\n)",
            ]
        else:
            patterns = [
                r"отправляем\s+([^\.]+?)(?:\.|$|\n)",
                r"выход[ае]?\s+([^\.]+?)(?:\.|$|\n)",
                r"создаем\s+([^\.]+?)(?:\.|$|\n)",
                r"формируем\s+([^\.]+?)(?:\.|$|\n)",
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            items.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return items[:5]  # Ограничиваем
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Извлекает условия из текста."""
        conditions = []
        
        patterns = [
            r"если\s+([^\.]+?)(?:\.|$|\n)",
            r"при условии\s+([^\.]+?)(?:\.|$|\n)",
            r"в случае\s+([^\.]+?)(?:\.|$|\n)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return conditions[:3]
    
    def _extract_problems_from_step(self, text: str) -> List[str]:
        """Извлекает проблемы из шага."""
        problems = []
        
        problem_keywords = ['проблема', 'боль', 'сложно', 'неудобно', 'долго', 'медленно', 'ошибка']
        if any(keyword in text.lower() for keyword in problem_keywords):
            # Берем предложение целиком как проблему
            sentences = re.split(r'[\.!?]\s+', text)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in problem_keywords):
                    problems.append(sentence.strip())
        
        return problems[:2]
    
    def _extract_business_rules(self, transcript: str) -> List[BusinessRule]:
        """Извлекает бизнес-правила из транскрибации."""
        rules = []
        
        rule_patterns = [
            r"(?:правило|требование|условие)[:\.]?\s+([^\.]+?)(?:\.|$|\n)",
            r"должно быть\s+([^\.]+?)(?:\.|$|\n)",
            r"обязательно\s+([^\.]+?)(?:\.|$|\n)",
        ]
        
        for pattern in rule_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE)
            for match in matches:
                rule_text = match.group(1).strip()
                if len(rule_text) > 10:
                    rules.append(BusinessRule(
                        rule_text=rule_text,
                        context=None,
                        step_numbers=[]
                    ))
        
        return rules[:10]
    
    def _extract_problems(self, transcript: str) -> List[str]:
        """Извлекает общие проблемы процесса."""
        problems = []
        
        problem_sections = re.findall(
            r"(?:проблем[аеы]?|боль|сложност[иь]?)[:\.]?\s+([^\.]+?)(?:\.|$|\n)",
            transcript,
            re.IGNORECASE
        )
        
        problems.extend([p.strip() for p in problem_sections if len(p.strip()) > 5])
        
        return problems[:10]
    
    def _extract_unknowns(self, transcript: str) -> List[str]:
        """Извлекает неизвестные/неясные моменты."""
        unknowns = []
        
        unknown_patterns = [
            r"(?:не знаю|неизвестно|неясно|не понятно|не помню)[:\.]?\s*([^\.]+?)(?:\.|$|\n)",
            r"(?:не уверен|сомневаюсь)[:\.]?\s*([^\.]+?)(?:\.|$|\n)",
        ]
        
        for pattern in unknown_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            unknowns.extend([m.strip() for m in matches if len(m.strip()) > 5])
        
        return unknowns[:5]
    
    def _generate_process_description(self, transcript: str, steps: List[ProcessStep]) -> str:
        """Генерирует описание процесса."""
        if steps:
            return f"Процесс состоит из {len(steps)} шагов: " + \
                   ", ".join([f"{s.step_number}. {s.name}" for s in steps[:5]])
        else:
            # Берем первые предложения из транскрибации
            sentences = re.split(r'[\.!?]\s+', transcript)
            return ". ".join(sentences[:3]) + "."
    
    def _calculate_confidence(self, transcript: str, steps: List[ProcessStep], roles: List[str]) -> float:
        """Вычисляет уверенность в извлечении."""
        confidence = 0.3  # Базовая уверенность
        
        # Увеличиваем при наличии структурированных шагов
        if steps:
            confidence += min(0.3, len(steps) * 0.05)
        
        # Увеличиваем при наличии ролей
        if roles:
            confidence += min(0.2, len(roles) * 0.1)
        
        # Увеличиваем при длине транскрибации
        if len(transcript) > 500:
            confidence += 0.1
        elif len(transcript) > 1000:
            confidence += 0.1
        
        return min(1.0, confidence)

