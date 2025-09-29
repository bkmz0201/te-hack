"""
Генератор сценариев комиксов с использованием CrewAI агентов.
"""

from crewai import Agent, Task, Crew, Process
import json
import re
import logging
from typing import List, Dict, Any

from ..models.comic_models import (
    ComicCharacter, ComicPanel, ProcessInfo, 
    MoodType, StyleType
)
from ..services.llm_service import CustomOllamaLLM

logger = logging.getLogger(__name__)


class ScenarioGenerator:
    """Генератор сценариев для образовательных комиксов."""
    
    def __init__(self, llm: CustomOllamaLLM):
        """
        Инициализация генератора сценариев.
        
        Args:
            llm: Экземпляр LLM для работы с агентами
        """
        self.llm = llm
        
        # Агент для создания персонажей
        self.character_creator = Agent(
            role="Создатель персонажей",
            goal="Создавать запоминающихся персонажей для образовательных комиксов",
            backstory="""Ты эксперт по созданию персонажей для образовательного контента. 
            Твои персонажи должны быть релевантными, запоминающимися и подходящими для целевой аудитории.""",
            llm=llm,
            verbose=True
        )
        
        # Агент для создания сюжета
        self.story_creator = Agent(
            role="Сценарист образовательных историй",
            goal="Превращать сложные процессы в увлекательные истории",
            backstory="""Ты мастер сторителлинга в образовательной сфере. Умеешь превращать 
            скучные процедуры в захватывающие истории с четкой структурой и логикой.""",
            llm=llm,
            verbose=True
        )
    
    def create_characters(self, 
                         process_info: ProcessInfo, 
                         target_audience: str) -> List[ComicCharacter]:
        """
        Создание персонажей на основе процесса.
        
        Args:
            process_info: Информация о процессе
            target_audience: Целевая аудитория
            
        Returns:
            Список персонажей комикса
        """
        logger.info("Создание персонажей комикса...")
        
        participants = [p.to_dict() for p in process_info.participants]
        
        task = Task(
            description=f"""
Создай 2-3 персонажа для комикса на основе процесса:

ПРОЦЕСС: {process_info.process_name}
УЧАСТНИКИ ПРОЦЕССА: {participants}
ЦЕЛЕВАЯ АУДИТОРИЯ: {target_audience}

ТРЕБОВАНИЯ К ПЕРСОНАЖАМ:
1. Главный герой - молодой человек (студент/выпускник) 
2. Помощник - опытный специалист/наставник
3. Дополнительный персонаж при необходимости

ДЛЯ КАЖДОГО ПЕРСОНАЖА УКАЖИ:
- Имя (простое, запоминающееся)
- Внешность (для рисования)
- Характер (как говорит и ведет себя)
- Роль в истории

ФОРМАТ ОТВЕТА (JSON):
[
    {{
        "name": "Имя персонажа",
        "description": "Подробная внешность для художника",
        "personality": "Характер и манера речи",
        "role": "Роль в истории",
        "visual_style": "Стиль изображения"
    }}
]
""",
            expected_output="JSON массив с персонажами",
            agent=self.character_creator
        )
        
        try:
            crew = Crew(agents=[self.character_creator], tasks=[task], process=Process.sequential)
            result = crew.kickoff()
            
            characters_data = self._parse_json_array_from_response(str(result))
            if characters_data:
                return [ComicCharacter.from_dict(char) for char in characters_data]
            
        except Exception as e:
            logger.error(f"Ошибка создания персонажей: {e}")
        
        # Возвращаем персонажей по умолчанию
        return self._get_default_characters()
    
    def create_scenario(self, 
                       process_info: ProcessInfo,
                       characters: List[ComicCharacter], 
                       target_audience: str, 
                       num_panels: int = 8) -> List[ComicPanel]:
        """
        Создание сценария комикса.
        
        Args:
            process_info: Информация о процессе
            characters: Персонажи комикса
            target_audience: Целевая аудитория
            num_panels: Количество панелей
            
        Returns:
            Список панелей комикса
        """
        logger.info(f"Создание сценария на {num_panels} панелей...")
        
        char_descriptions = [f"{char.name} ({char.role})" for char in characters]
        steps = [s.to_dict() for s in process_info.steps]
        
        task = Task(
            description=f"""
Создай сценарий комикса на {num_panels} панелей:

ПРОЦЕСС: {process_info.process_name}
ЭТАПЫ: {steps}
ПЕРСОНАЖИ: {char_descriptions}
АУДИТОРИЯ: {target_audience}

СТРУКТУРА ИСТОРИИ:
1. Панель 1: Введение проблемы (герой сталкивается с необходимостью)
2. Панели 2-3: Поиск информации (герой узнает о процессе)
3. Панели 4-6: Выполнение этапов (пошаговое прохождение процесса)
4. Панели 7-8: Результат и выводы (успешное завершение + мораль)

ДЛЯ КАЖДОЙ ПАНЕЛИ СОЗДАЙ:
- Номер панели
- Описание сцены (что происходит)
- Диалог (что говорят персонажи, кратко!)
- Участвующие персонажи
- Настроение/атмосфера

ВАЖНО:
- Диалоги короткие (до 15 слов)
- Сцены понятные и визуальные
- Логическая связь между панелями
- Позитивный тон

ФОРМАТ ОТВЕТА (JSON):
[
    {{
        "panel_id": "panel_1",
        "scene_description": "Подробное описание происходящего",
        "dialogue": "Короткая реплика персонажа",
        "characters": ["список имен"],
        "mood": "настроение сцены",
        "importance": 0.8
    }}
]
""",
            expected_output="JSON массив с панелями комикса",
            agent=self.story_creator
        )
        
        try:
            crew = Crew(agents=[self.story_creator], tasks=[task], process=Process.sequential)
            result = crew.kickoff()
            
            panels_data = self._parse_json_array_from_response(str(result))
            if panels_data:
                panels = []
                for i, panel_data in enumerate(panels_data):
                    panel = ComicPanel(
                        panel_id=panel_data.get('panel_id', f'panel_{i+1}'),
                        scene_description=panel_data.get('scene_description', ''),
                        dialogue=panel_data.get('dialogue', ''),
                        visual_prompt="",  # Будет создан позже
                        characters=panel_data.get('characters', []),
                        mood=panel_data.get('mood', MoodType.NEUTRAL.value),
                        importance=panel_data.get('importance', 0.5)
                    )
                    panels.append(panel)
                return panels
                
        except Exception as e:
            logger.error(f"Ошибка создания сценария: {e}")
        
        # Возвращаем базовый сценарий
        return self._get_default_scenario(characters)
    
    def _parse_json_array_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Извлечение JSON массива из ответа LLM.
        
        Args:
            response: Ответ от LLM
            
        Returns:
            Распарсенный JSON массив или пустой список
        """
        try:
            # Ищем JSON массив в ответе
            json_match = re.search(r'\\[.*\\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Ошибка парсинга JSON массива: {e}")
        
        return []
    
    def _get_default_characters(self) -> List[ComicCharacter]:
        """
        Получение персонажей по умолчанию.
        
        Returns:
            Список базовых персонажей
        """
        return [
            ComicCharacter(
                name="Алексей",
                description="Молодой человек 20 лет, в современной одежде, дружелюбное лицо",
                personality="Любознательный, вежливый, немного неуверенный в официальных процедурах",
                role="Главный герой, который изучает процесс",
                visual_style="современный реалистичный стиль"
            ),
            ComicCharacter(
                name="Мария Ивановна",
                description="Женщина средних лет, в деловом костюме, доброжелательная",
                personality="Опытная, терпеливая, готова помочь и объяснить",
                role="Специалист, который помогает разобраться",
                visual_style="профессиональный стиль"
            )
        ]
    
    def _get_default_scenario(self, characters: List[ComicCharacter]) -> List[ComicPanel]:
        """
        Создание базового сценария.
        
        Args:
            characters: Персонажи для сценария
            
        Returns:
            Список панелей базового сценария
        """
        char_names = [char.name for char in characters]
        main_char = char_names[0] if char_names else "Алексей"
        helper_char = char_names[1] if len(char_names) > 1 else "Мария Ивановна"
        
        return [
            ComicPanel(
                panel_id="panel_1",
                scene_description=f"{main_char} держит документы и выглядит озадаченным",
                dialogue="Как же подать это обращение правильно?",
                visual_prompt="",
                characters=[main_char],
                mood=MoodType.CONFUSED.value,
                importance=0.9
            ),
            ComicPanel(
                panel_id="panel_2",
                scene_description=f"{helper_char} в офисе приветливо встречает {main_char}",
                dialogue="Добро пожаловать! Я помогу вам разобраться.",
                visual_prompt="",
                characters=[main_char, helper_char],
                mood=MoodType.FRIENDLY.value,
                importance=0.8
            ),
            ComicPanel(
                panel_id="panel_3",
                scene_description=f"{helper_char} объясняет процедуру, показывая документы",
                dialogue="Сначала нужно заполнить заявление по форме.",
                visual_prompt="",
                characters=[main_char, helper_char],
                mood=MoodType.EXPLAINING.value,
                importance=0.8
            ),
            ComicPanel(
                panel_id="panel_4",
                scene_description=f"{main_char} заполняет документы за столом",
                dialogue="Теперь понятно! Заполняю все поля.",
                visual_prompt="",
                characters=[main_char],
                mood=MoodType.PROFESSIONAL.value,
                importance=0.7
            ),
            ComicPanel(
                panel_id="panel_5",
                scene_description=f"{main_char} подает документы {helper_char}",
                dialogue="Вот мое заявление и все документы.",
                visual_prompt="",
                characters=[main_char, helper_char],
                mood=MoodType.PROFESSIONAL.value,
                importance=0.8
            ),
            ComicPanel(
                panel_id="panel_6",
                scene_description=f"{helper_char} проверяет документы и ставит печать",
                dialogue="Все правильно! Ставлю отметку о приеме.",
                visual_prompt="",
                characters=[main_char, helper_char],
                mood=MoodType.PROFESSIONAL.value,
                importance=0.8
            ),
            ComicPanel(
                panel_id="panel_7",
                scene_description=f"{helper_char} выдает расписку {main_char}",
                dialogue="Вот расписка. Результат будет готов через 10 дней.",
                visual_prompt="",
                characters=[main_char, helper_char],
                mood=MoodType.FRIENDLY.value,
                importance=0.7
            ),
            ComicPanel(
                panel_id="panel_8",
                scene_description=f"{main_char} довольный уходит из офиса",
                dialogue="Спасибо! Теперь я знаю, как это делать!",
                visual_prompt="",
                characters=[main_char],
                mood=MoodType.FRIENDLY.value,
                importance=0.9
            )
        ]