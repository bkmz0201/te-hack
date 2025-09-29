"""
Модели данных для генератора комиксов.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class MoodType(Enum):
    """Типы настроения для панелей комикса."""
    FRIENDLY = "дружелюбный"
    PROFESSIONAL = "профессиональный"
    EXPLAINING = "объясняющий"
    DECISIVE = "решающий"
    NEUTRAL = "нейтральный"
    CONFUSED = "озадаченный"


class StyleType(Enum):
    """Стили изображений."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EDUCATIONAL = "educational"
    NARRATIVE = "narrative"


@dataclass
class ComicPanel:
    """Структура данных для панели комикса."""
    panel_id: str
    scene_description: str
    dialogue: str
    visual_prompt: str
    characters: List[str]
    mood: str
    importance: float

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации."""
        return {
            "panel_id": self.panel_id,
            "scene_description": self.scene_description,
            "dialogue": self.dialogue,
            "visual_prompt": self.visual_prompt,
            "characters": self.characters,
            "mood": self.mood,
            "importance": self.importance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComicPanel":
        """Создание из словаря."""
        return cls(
            panel_id=data.get("panel_id", ""),
            scene_description=data.get("scene_description", ""),
            dialogue=data.get("dialogue", ""),
            visual_prompt=data.get("visual_prompt", ""),
            characters=data.get("characters", []),
            mood=data.get("mood", MoodType.NEUTRAL.value),
            importance=data.get("importance", 0.5)
        )


@dataclass
class ComicCharacter:
    """Структура данных для персонажа."""
    name: str
    description: str
    personality: str
    role: str
    visual_style: str

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сериализации."""
        return {
            "name": self.name,
            "description": self.description,
            "personality": self.personality,
            "role": self.role,
            "visual_style": self.visual_style
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComicCharacter":
        """Создание из словаря."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            personality=data.get("personality", ""),
            role=data.get("role", ""),
            visual_style=data.get("visual_style", "")
        )


@dataclass
class ProcessStep:
    """Шаг процесса."""
    step_number: int
    action: str
    description: str
    responsible: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "description": self.description,
            "responsible": self.responsible
        }


@dataclass
class ProcessParticipant:
    """Участник процесса."""
    role: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "description": self.description
        }


@dataclass
class ProcessInfo:
    """Информация о процессе из документа."""
    process_name: str
    participants: List[ProcessParticipant]
    steps: List[ProcessStep]
    rules: List[str]
    outcome: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_name": self.process_name,
            "participants": [p.to_dict() for p in self.participants],
            "steps": [s.to_dict() for s in self.steps],
            "rules": self.rules,
            "outcome": self.outcome
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessInfo":
        """Создание из словаря."""
        participants = [
            ProcessParticipant(**p) for p in data.get("participants", [])
        ]
        steps = [
            ProcessStep(**s) for s in data.get("steps", [])
        ]
        
        return cls(
            process_name=data.get("process_name", ""),
            participants=participants,
            steps=steps,
            rules=data.get("rules", []),
            outcome=data.get("outcome", "")
        )


@dataclass
class ComicData:
    """Полные данные комикса."""
    process_info: ProcessInfo
    characters: List[ComicCharacter]
    panels: List[ComicPanel]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_info": self.process_info.to_dict(),
            "characters": [c.to_dict() for c in self.characters],
            "panels": [p.to_dict() for p in self.panels],
            "metadata": self.metadata
        }