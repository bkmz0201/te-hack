"""
Генератор изображений для комиксов с использованием Stable Diffusion.
"""

import base64
import requests
from PIL import Image
import io
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

from ..models.comic_models import ComicPanel, StyleType

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Генератор изображений с оптимизированными промптами для Stable Diffusion."""
    
    def __init__(self, api_base: str = "http://127.0.0.1:7860"):
        """
        Инициализация генератора изображений.
        
        Args:
            api_base: Базовый URL для Stable Diffusion API
        """
        self.api_base = api_base
        
        # Базовые стили для разных типов панелей
        self.style_presets = {
            StyleType.PROFESSIONAL.value: "clean corporate art style, professional illustration, business setting",
            StyleType.FRIENDLY.value: "warm cartoon style, friendly characters, approachable design",
            StyleType.EDUCATIONAL.value: "clear educational illustration, simple but detailed, instructional diagram style",
            StyleType.NARRATIVE.value: "storytelling illustration, sequential art, comic book style"
        }
        
        # Оптимизированные промпты для читаемых speech bubbles
        self.text_quality_prompts = [
            "clear readable text in speech bubbles",
            "sharp text, high contrast speech bubbles",
            "professional comic book lettering",
            "clean white speech bubbles with black text",
            "well-defined text areas, no blurred letters"
        ]
        
        # Промпты для настроений
        self.mood_prompts = {
            "дружелюбный": "warm lighting, positive atmosphere, welcoming environment",
            "профессиональный": "office environment, business setting, professional atmosphere",
            "объясняющий": "educational setting, clear visual elements, instructional mood",
            "решающий": "decisive moment, clear action, problem-solving atmosphere",
            "озадаченный": "confused expression, questioning look, uncertain atmosphere",
            "нейтральный": "neutral atmosphere, balanced lighting"
        }
    
    def check_server(self) -> bool:
        """
        Проверка доступности сервера Stable Diffusion.
        
        Returns:
            True если сервер доступен
        """
        try:
            response = requests.get(f"{self.api_base}/sdapi/v1/options", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Сервер Stable Diffusion недоступен: {e}")
            return False
    
    def build_optimized_prompt(self, 
                             scene_description: str, 
                             dialogue: str,
                             characters: List[str], 
                             mood: str, 
                             style: str = StyleType.EDUCATIONAL.value) -> Tuple[str, str]:
        """
        Создание оптимизированного промпта для высокого качества.
        
        Args:
            scene_description: Описание сцены
            dialogue: Диалог персонажей
            characters: Список персонажей
            mood: Настроение сцены
            style: Стиль изображения
            
        Returns:
            Кортеж (промпт, negative_prompt)
        """
        # Базовый стиль
        base_style = self.style_presets.get(style, self.style_presets[StyleType.EDUCATIONAL.value])
        
        # Промпт для персонажей
        char_prompt = ""
        if characters:
            char_descriptions = {
                "Алексей": "teenage boy with brown hair, wearing casual modern clothes, friendly expression",
                "Мария": "teenage girl with blonde hair, wearing modern clothes, curious expression", 
                "Специалист": "professional adult in business attire, helpful demeanor",
                "Мария Ивановна": "middle-aged woman in business attire, professional and kind",
                "Чиновник": "middle-aged person in formal wear, official appearance"
            }
            char_list = [char_descriptions.get(char, f"person named {char}") for char in characters]
            char_prompt = f"featuring {', '.join(char_list)}, "
        
        # Промпт для диалога (если есть)
        dialogue_prompt = ""
        if dialogue and dialogue.strip():
            dialogue_prompt = f"with clear white speech bubble containing readable Russian text: '{dialogue[:50]}...', "
        
        # Промпт для настроения
        mood_prompt = self.mood_prompts.get(mood, "neutral atmosphere")
        
        # Собираем финальный промпт
        final_prompt = f"""
{base_style}, {char_prompt}{dialogue_prompt}
{scene_description}, {mood_prompt},
high quality illustration, sharp details, consistent art style,
{', '.join(self.text_quality_prompts[:2])},
masterpiece, professional comic art, 8k resolution
""".strip().replace('\n', ' ')
        
        # Negative prompt для улучшения качества
        negative_prompt = """
blurry text, unreadable text, messy speech bubbles, 
inconsistent character design, bad anatomy, low quality,
pixelated, artifacts, watermark, signature,
dark lighting, confusing layout, cluttered composition
""".strip()
        
        return final_prompt, negative_prompt
    
    def generate_with_enhanced_settings(self, 
                                      prompt: str, 
                                      negative_prompt: str,
                                      steps: int = 50, 
                                      width: int = 768, 
                                      height: int = 512) -> Optional[bytes]:
        """
        Генерация изображения с улучшенными настройками.
        
        Args:
            prompt: Промпт для генерации
            negative_prompt: Негативный промпт
            steps: Количество шагов
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            Данные изображения в байтах или None при ошибке
        """
        try:
            if not self.check_server():
                logger.error("Сервер Stable Diffusion недоступен")
                return None
            
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": steps,
                "width": width,
                "height": height,
                "cfg_scale": 8.0,  # Увеличено для лучшего следования промпту
                "sampler_name": "DPM++ 2M Karras",  # Лучший сэмплер для качества
                "seed": -1,
                "restore_faces": True,  # Улучшение лиц
                "enable_hr": True,      # Upscaling для лучшего качества
                "hr_scale": 1.5,
                "hr_upscaler": "R-ESRGAN 4x+",
                "denoising_strength": 0.7
            }
            
            response = requests.post(
                f"{self.api_base}/sdapi/v1/txt2img",
                json=payload,
                timeout=600  # Увеличен таймаут для upscaling
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = result['images'][0]
                return base64.b64decode(image_data)
            else:
                logger.error(f"Ошибка генерации: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при генерации изображения: {e}")
            return None
    
    def generate_panel_image(self, 
                           panel: ComicPanel, 
                           style: str = StyleType.EDUCATIONAL.value) -> Optional[bytes]:
        """
        Генерация изображения для панели комикса.
        
        Args:
            panel: Панель комикса
            style: Стиль изображения
            
        Returns:
            Данные изображения в байтах или None при ошибке
        """
        logger.info(f"Генерация изображения для панели: {panel.panel_id}")
        
        prompt, negative_prompt = self.build_optimized_prompt(
            panel.scene_description, 
            panel.dialogue, 
            panel.characters, 
            panel.mood, 
            style
        )
        
        logger.debug(f"Промпт: {prompt[:100]}...")
        
        image_data = self.generate_with_enhanced_settings(prompt, negative_prompt)
        
        if image_data:
            logger.info(f"Изображение успешно сгенерировано для {panel.panel_id}")
        else:
            logger.error(f"Ошибка генерации изображения для {panel.panel_id}")
            
        return image_data
    
    def save_image(self, image_data: bytes, filename: str) -> bool:
        """
        Сохранение изображения в файл.
        
        Args:
            image_data: Данные изображения
            filename: Имя файла для сохранения
            
        Returns:
            True если сохранение успешно
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.save(filename)
            logger.info(f"Изображение сохранено: {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения изображения {filename}: {e}")
            return False
    
    def create_placeholder_image(self, 
                                panel_id: str, 
                                width: int = 600, 
                                height: int = 400) -> bytes:
        """
        Создание изображения-заглушки.
        
        Args:
            panel_id: ID панели
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            Данные изображения в байтах
        """
        try:
            # Создаем простое изображение-заглушку
            image = Image.new('RGB', (width, height), color='#4CAF50')
            
            # Добавляем текст (требует pillow с поддержкой шрифтов)
            # Здесь можно добавить рисование текста, если нужно
            
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка создания заглушки: {e}")
            # Возвращаем минимальное изображение
            return b''