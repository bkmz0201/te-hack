"""
Основной класс генератора комиксов.
"""

import logging
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.comic_models import ComicData, StyleType
from ..services.llm_service import LLMServiceManager
from ..services.document_service import DocumentService
from ..generators.content_analyzer import ContentAnalyzer
from ..generators.scenario_generator import ScenarioGenerator
from ..generators.image_generator import ImageGenerator
from ..utils.html_generator import HTMLGenerator
from ..utils.data_manager import DataManager

logger = logging.getLogger(__name__)


class ComicGenerator:
    """Главный класс генератора образовательных комиксов."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация генератора комиксов.
        
        Args:
            config: Конфигурация генератора
        """
        self.config = config or {}
        
        # Инициализация сервисов
        self.llm_manager = LLMServiceManager(self.config.get("llm", {}))
        self.document_service = DocumentService()
        
        # Инициализация генераторов
        llm = self.llm_manager.get_llm()
        self.content_analyzer = ContentAnalyzer(llm)
        self.scenario_generator = ScenarioGenerator(llm)
        self.image_generator = ImageGenerator(
            self.config.get("stable_diffusion", {}).get("api_base", "http://127.0.0.1:7860")
        )
        
        # Инициализация утилит
        self.html_generator = HTMLGenerator()
        self.data_manager = DataManager(
            self.config.get("output_dir", "outputs")
        )
        
        # Статистика генерации
        self.generation_stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "images_generated": 0,
            "images_failed": 0,
            "llm_calls": 0,
            "errors": []
        }
    
    def generate_comic_from_pdf(self, 
                               pdf_path: str,
                               target_audience: str = "взрослые",
                               num_panels: int = 8,
                               output_name: str = "comic",
                               style: str = StyleType.EDUCATIONAL.value) -> Optional[str]:
        """
        Основная функция создания комикса из PDF документа.
        
        Args:
            pdf_path: Путь к PDF файлу
            target_audience: Целевая аудитория
            num_panels: Количество панелей
            output_name: Базовое имя выходных файлов
            style: Стиль изображений
            
        Returns:
            Путь к созданному HTML файлу или None при ошибке
        """
        self.generation_stats["start_time"] = datetime.now()
        
        try:
            logger.info("="*60)
            logger.info("🚀 ЗАПУСК ГЕНЕРАТОРА КОМИКСОВ")
            logger.info("="*60)
            
            # 1. Загрузка и валидация документа
            document_text = self._load_and_validate_document(pdf_path)
            if not document_text:
                return None
            
            # 2. Анализ содержимого
            process_info = self._analyze_document_content(document_text)
            
            # 3. Создание персонажей
            characters = self._create_characters(process_info, target_audience)
            
            # 4. Генерация сценария
            panels = self._create_scenario(process_info, characters, target_audience, num_panels)
            
            # 5. Генерация изображений
            image_files = self._generate_images(panels, style, output_name)
            
            # 6. Создание HTML
            html_file = self._create_html_output(panels, characters, image_files, output_name)
            
            # 7. Сохранение данных
            self._save_project_data(process_info, characters, panels, output_name)
            
            # Завершение
            self.generation_stats["end_time"] = datetime.now()
            self.generation_stats["duration_seconds"] = (
                self.generation_stats["end_time"] - self.generation_stats["start_time"]
            ).total_seconds()
            
            logger.info("\\n" + "="*60)
            logger.info("🎉 КОМИКС УСПЕШНО СОЗДАН!")
            logger.info(f"📁 HTML файл: {html_file}")
            logger.info(f"⏱️ Время генерации: {self.generation_stats['duration_seconds']:.1f} сек")
            logger.info(f"🖼️ Изображений создано: {self.generation_stats['images_generated']}")
            logger.info("="*60)
            
            return html_file
            
        except Exception as e:
            logger.error(f"Критическая ошибка генерации комикса: {e}")
            self.generation_stats["errors"].append(str(e))
            return None
    
    def _load_and_validate_document(self, pdf_path: str) -> Optional[str]:
        """Загрузка и валидация документа."""
        logger.info("📄 Загрузка документа...")
        
        document_text = self.document_service.load_pdf(pdf_path)
        if not document_text:
            logger.error("Не удалось загрузить PDF документ")
            return None
        
        if not self.document_service.validate_document(document_text):
            logger.error("Документ не прошел валидацию")
            return None
        
        logger.info(f"✅ Документ загружен, символов: {len(document_text)}")
        return document_text
    
    def _analyze_document_content(self, document_text: str):
        """Анализ содержимого документа."""
        logger.info("🔍 Анализ содержимого документа...")
        
        self.generation_stats["llm_calls"] += 1
        process_info = self.content_analyzer.extract_process_info(document_text)
        
        if not self.content_analyzer.validate_process_info(process_info):
            logger.warning("Процесс не прошел валидацию, используется fallback")
        
        logger.info(f"✅ Процесс найден: {process_info.process_name}")
        return process_info
    
    def _create_characters(self, process_info, target_audience):
        """Создание персонажей."""
        logger.info("👥 Создание персонажей...")
        
        self.generation_stats["llm_calls"] += 1
        characters = self.scenario_generator.create_characters(process_info, target_audience)
        
        logger.info(f"✅ Создано персонажей: {len(characters)}")
        for char in characters:
            logger.info(f"   - {char.name}: {char.role}")
        
        return characters
    
    def _create_scenario(self, process_info, characters, target_audience, num_panels):
        """Создание сценария."""
        logger.info(f"📝 Генерация сценария на {num_panels} панелей...")
        
        self.generation_stats["llm_calls"] += 1
        panels = self.scenario_generator.create_scenario(
            process_info, characters, target_audience, num_panels
        )
        
        logger.info(f"✅ Создано панелей: {len(panels)}")
        return panels
    
    def _generate_images(self, panels, style, output_name):
        """Генерация изображений."""
        logger.info("🎨 Генерация изображений...")
        
        image_files = []
        
        if not self.image_generator.check_server():
            logger.warning("⚠️ Сервер Stable Diffusion недоступен, создается версия без изображений")
            return image_files
        
        # Создаем директорию для изображений
        images_dir = f"{output_name}_images"
        os.makedirs(images_dir, exist_ok=True)
        
        for i, panel in enumerate(panels):
            try:
                logger.info(f"   Панель {i+1}/{len(panels)}: {panel.panel_id}")
                
                image_data = self.image_generator.generate_panel_image(panel, style)
                
                if image_data:
                    filename = os.path.join(images_dir, f"panel_{i+1}.png")
                    if self.image_generator.save_image(image_data, filename):
                        image_files.append(filename)
                        self.generation_stats["images_generated"] += 1
                    else:
                        self.generation_stats["images_failed"] += 1
                else:
                    self.generation_stats["images_failed"] += 1
                
                # Пауза между генерациями
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка генерации изображения для панели {i+1}: {e}")
                self.generation_stats["images_failed"] += 1
                self.generation_stats["errors"].append(f"Image generation panel {i+1}: {e}")
        
        logger.info(f"✅ Изображений сгенерировано: {len(image_files)}")
        return image_files
    
    def _create_html_output(self, panels, characters, image_files, output_name):
        """Создание HTML выходного файла."""
        logger.info("📖 Создание HTML...")
        
        html_file = self.html_generator.create_comic_html(
            panels=panels,
            characters=characters,
            image_files=image_files,
            output_name=output_name,
            title="Образовательный комикс"
        )
        
        logger.info(f"✅ HTML создан: {html_file}")
        return html_file
    
    def _save_project_data(self, process_info, characters, panels, output_name):
        """Сохранение данных проекта."""
        logger.info("💾 Сохранение данных проекта...")
        
        # Создаем объект ComicData
        comic_data = ComicData(
            process_info=process_info,
            characters=characters,
            panels=panels,
            metadata={
                "created_at": datetime.now().isoformat(),
                "generator_version": "1.0",
                "config": self.config
            }
        )
        
        # Сохраняем данные
        self.data_manager.save_comic_data(comic_data, output_name)
        
        # Сохраняем конфигурацию
        self.data_manager.save_config(self.config, output_name)
        
        # Создаем сводку
        self.data_manager.create_project_summary(
            comic_data, output_name, self.generation_stats
        )
        
        # Очищаем временные файлы
        self.data_manager.cleanup_temp_files(output_name)
        
        logger.info("✅ Данные проекта сохранены")
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Получение статистики генерации.
        
        Returns:
            Словарь со статистикой
        """
        return self.generation_stats.copy()
    
    def validate_dependencies(self) -> Dict[str, bool]:
        """
        Валидация зависимостей системы.
        
        Returns:
            Словарь с результатами проверки
        """
        results = {
            "llm_service": False,
            "stable_diffusion": False,
            "output_directory": False
        }
        
        try:
            # Проверка LLM
            results["llm_service"] = self.llm_manager.validate_llm_connection()
            
            # Проверка Stable Diffusion
            results["stable_diffusion"] = self.image_generator.check_server()
            
            # Проверка директории
            results["output_directory"] = os.path.exists(self.data_manager.output_dir)
            
        except Exception as e:
            logger.error(f"Ошибка валидации зависимостей: {e}")
        
        return results