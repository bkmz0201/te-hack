"""
Анализатор контента документов с использованием CrewAI агентов.
"""

from crewai import Agent, Task, Crew, Process
import json
import re
import logging
from typing import Dict, Any, Optional

from ..models.comic_models import ProcessInfo, ProcessStep, ProcessParticipant
from ..services.llm_service import CustomOllamaLLM

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Анализатор контента для извлечения структурированной информации из документов."""
    
    def __init__(self, llm: CustomOllamaLLM):
        """
        Инициализация анализатора.
        
        Args:
            llm: Экземпляр LLM для работы с агентами
        """
        self.llm = llm
        self.agent = Agent(
            role="Специалист по анализу документов",
            goal="Извлекать структурированную информацию из юридических документов",
            backstory="""Ты эксперт по анализу правовых документов. Твоя задача - 
            найти ключевые процессы, этапы, участников и правила. Ты умеешь 
            выделять главное и игнорировать второстепенные детали.""",
            llm=llm,
            verbose=True
        )
    
    def extract_process_info(self, document_text: str) -> ProcessInfo:
        """
        Извлечение информации о процессе из документа.
        
        Args:
            document_text: Текст документа для анализа
            
        Returns:
            Структурированная информация о процессе
        """
        logger.info("Начало анализа документа...")
        
        task = Task(
            description=f"""
Проанализируй документ и извлеки ОСНОВНОЙ ПРОЦЕСС:

ДОКУМЕНТ:
{document_text[:3000]}

НАЙДИ И СТРУКТУРИРУЙ:
1. НАЗВАНИЕ процесса (что именно описывается)
2. УЧАСТНИКИ (кто участвует в процессе)
3. ЭТАПЫ (последовательность действий)
4. ПРАВИЛА (ключевые требования и ограничения)
5. РЕЗУЛЬТАТ (что получается в итоге)

ТРЕБОВАНИЯ:
- Определи ОДИН главный процесс (не список всех упоминаний)
- Для участников используй РОЛИ, а не географические названия
- Этапы должны быть ДЕЙСТВИЯМИ, а не описаниями текста
- Все ответы на РУССКОМ языке

ФОРМАТ ОТВЕТА (JSON):
{{
    "process_name": "Четкое название процесса",
    "participants": [
        {{
            "role": "Роль участника",
            "description": "Что делает этот участник"
        }}
    ],
    "steps": [
        {{
            "step_number": 1,
            "action": "Конкретное действие",
            "description": "Подробное описание этапа",
            "responsible": "Кто выполняет"
        }}
    ],
    "rules": ["список ключевых правил"],
    "outcome": "Что получается в результате"
}}
""",
            expected_output="JSON с структурированным описанием процесса",
            agent=self.agent
        )
        
        try:
            crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
            result = crew.kickoff()
            
            # Парсим JSON из ответа
            process_data = self._parse_json_from_response(str(result))
            if process_data:
                return self._create_process_info_from_data(process_data)
            
        except Exception as e:
            logger.error(f"Ошибка анализа документа: {e}")
        
        # Возвращаем fallback процесс
        return self._get_fallback_process()
    
    def _parse_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Извлечение JSON из ответа LLM.
        
        Args:
            response: Ответ от LLM
            
        Returns:
            Распарсенный JSON или None
        """
        try:
            # Ищем JSON блок в ответе
            json_match = re.search(r'\\{.*\\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Ошибка парсинга JSON из ответа: {e}")
        
        return None
    
    def _create_process_info_from_data(self, data: Dict[str, Any]) -> ProcessInfo:
        """
        Создание ProcessInfo из распарсенных данных.
        
        Args:
            data: Данные процесса из JSON
            
        Returns:
            Объект ProcessInfo
        """
        # Создаем участников
        participants = []
        for p_data in data.get("participants", []):
            participant = ProcessParticipant(
                role=p_data.get("role", ""),
                description=p_data.get("description", "")
            )
            participants.append(participant)
        
        # Создаем этапы
        steps = []
        for s_data in data.get("steps", []):
            step = ProcessStep(
                step_number=s_data.get("step_number", 0),
                action=s_data.get("action", ""),
                description=s_data.get("description", ""),
                responsible=s_data.get("responsible", "")
            )
            steps.append(step)
        
        return ProcessInfo(
            process_name=data.get("process_name", "Неизвестный процесс"),
            participants=participants,
            steps=steps,
            rules=data.get("rules", []),
            outcome=data.get("outcome", "")
        )
    
    def _get_fallback_process(self) -> ProcessInfo:
        """
        Получение процесса по умолчанию в случае ошибки анализа.
        
        Returns:
            Базовый ProcessInfo
        """
        participants = [
            ProcessParticipant(
                role="Гражданин",
                description="Лицо, обращающееся за получением услуги"
            ),
            ProcessParticipant(
                role="Специалист",
                description="Сотрудник, обрабатывающий обращение"
            )
        ]
        
        steps = [
            ProcessStep(
                step_number=1,
                action="Подача заявления",
                description="Гражданин подает письменное заявление с необходимыми документами",
                responsible="Гражданин"
            ),
            ProcessStep(
                step_number=2,
                action="Прием и регистрация",
                description="Специалист принимает и регистрирует заявление в системе",
                responsible="Специалист"
            ),
            ProcessStep(
                step_number=3,
                action="Рассмотрение заявления",
                description="Проверка документов и принятие решения",
                responsible="Специалист"
            ),
            ProcessStep(
                step_number=4,
                action="Выдача результата",
                description="Предоставление результата заявителю",
                responsible="Специалист"
            )
        ]
        
        return ProcessInfo(
            process_name="Процедура рассмотрения обращений граждан",
            participants=participants,
            steps=steps,
            rules=[
                "Заявление должно быть подано в письменной форме",
                "Рассмотрение происходит в течение установленного срока",
                "Необходимо предоставить полный пакет документов"
            ],
            outcome="Получение официального ответа или решения по обращению"
        )
    
    def validate_process_info(self, process_info: ProcessInfo) -> bool:
        """
        Валидация извлеченной информации о процессе.
        
        Args:
            process_info: Информация о процессе для валидации
            
        Returns:
            True если информация валидна
        """
        if not process_info.process_name or len(process_info.process_name.strip()) < 5:
            return False
        
        if len(process_info.participants) < 1:
            return False
        
        if len(process_info.steps) < 2:
            return False
        
        # Проверяем, что у каждого этапа есть основная информация
        for step in process_info.steps:
            if not step.action or not step.responsible:
                return False
        
        return True