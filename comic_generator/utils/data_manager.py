"""
Менеджер для сохранения и загрузки данных комиксов.
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models.comic_models import ComicData, ComicCharacter, ComicPanel, ProcessInfo

logger = logging.getLogger(__name__)


class DataManager:
    """Менеджер для работы с данными комиксов."""
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Инициализация менеджера данных.
        
        Args:
            output_dir: Директория для сохранения файлов
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Создание директории для выходных файлов."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Создана директория: {self.output_dir}")
    
    def save_comic_data(self, 
                       comic_data: ComicData, 
                       output_name: str) -> str:
        """
        Сохранение полных данных комикса в JSON.
        
        Args:
            comic_data: Данные комикса
            output_name: Базовое имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        try:
            data_dict = comic_data.to_dict()
            
            # Добавляем метаданные
            data_dict["metadata"]["saved_at"] = datetime.now().isoformat()
            data_dict["metadata"]["version"] = "1.0"
            
            filename = os.path.join(self.output_dir, f"{output_name}_data.json")
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Данные комикса сохранены: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return ""
    
    def load_comic_data(self, filename: str) -> Optional[ComicData]:
        """
        Загрузка данных комикса из JSON.
        
        Args:
            filename: Путь к файлу
            
        Returns:
            Загруженные данные комикса или None
        """
        try:
            if not os.path.exists(filename):
                logger.error(f"Файл не найден: {filename}")
                return None
            
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Восстанавливаем объекты
            process_info = ProcessInfo.from_dict(data["process_info"])
            
            characters = [
                ComicCharacter.from_dict(char_data) 
                for char_data in data["characters"]
            ]
            
            panels = [
                ComicPanel.from_dict(panel_data) 
                for panel_data in data["panels"]
            ]
            
            comic_data = ComicData(
                process_info=process_info,
                characters=characters,
                panels=panels,
                metadata=data.get("metadata", {})
            )
            
            logger.info(f"Данные комикса загружены: {filename}")
            return comic_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return None
    
    def save_config(self, config: Dict[str, Any], output_name: str) -> str:
        """
        Сохранение конфигурации проекта.
        
        Args:
            config: Конфигурация
            output_name: Базовое имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        try:
            filename = os.path.join(self.output_dir, f"{output_name}_config.json")
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Конфигурация сохранена: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            return ""
    
    def create_project_summary(self, 
                              comic_data: ComicData, 
                              output_name: str,
                              generation_stats: Dict[str, Any] = None) -> str:
        """
        Создание сводки по проекту.
        
        Args:
            comic_data: Данные комикса
            output_name: Базовое имя файла
            generation_stats: Статистика генерации
            
        Returns:
            Путь к файлу сводки
        """
        try:
            stats = generation_stats or {}
            
            summary = {
                "project_name": output_name,
                "created_at": datetime.now().isoformat(),
                "process_name": comic_data.process_info.process_name,
                "characters_count": len(comic_data.characters),
                "panels_count": len(comic_data.panels),
                "characters": [char.name for char in comic_data.characters],
                "generation_stats": stats,
                "files_created": [
                    f"{output_name}.html",
                    f"{output_name}_data.json",
                    f"{output_name}_summary.json"
                ]
            }
            
            filename = os.path.join(self.output_dir, f"{output_name}_summary.json")
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Сводка проекта создана: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка создания сводки: {e}")
            return ""
    
    def cleanup_temp_files(self, output_name: str):
        """
        Очистка временных файлов.
        
        Args:
            output_name: Базовое имя файлов для очистки
        """
        try:
            temp_patterns = [
                f"{output_name}_temp_*",
                f"temp_{output_name}_*"
            ]
            
            for pattern in temp_patterns:
                import glob
                for file_path in glob.glob(os.path.join(self.output_dir, pattern)):
                    try:
                        os.remove(file_path)
                        logger.debug(f"Удален временный файл: {file_path}")
                    except Exception as e:
                        logger.warning(f"Не удалось удалить {file_path}: {e}")
                        
        except Exception as e:
            logger.warning(f"Ошибка очистки временных файлов: {e}")
    
    def get_output_files(self, output_name: str) -> List[str]:
        """
        Получение списка созданных файлов.
        
        Args:
            output_name: Базовое имя проекта
            
        Returns:
            Список путей к созданным файлам
        """
        files = []
        base_patterns = [
            f"{output_name}.html",
            f"{output_name}_data.json",
            f"{output_name}_summary.json",
            f"{output_name}_config.json"
        ]
        
        for pattern in base_patterns:
            file_path = os.path.join(self.output_dir, pattern)
            if os.path.exists(file_path):
                files.append(file_path)
        
        # Добавляем изображения если есть
        images_dir = os.path.join(self.output_dir, f"{output_name}_images")
        if os.path.exists(images_dir):
            import glob
            image_files = glob.glob(os.path.join(images_dir, "*.png"))
            files.extend(image_files)
        
        return files