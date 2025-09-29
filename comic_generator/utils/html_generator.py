"""
Генератор HTML для комиксов.
"""

import base64
import os
import logging
from typing import List, Dict, Any, Optional

from ..models.comic_models import ComicPanel, ComicCharacter

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Генератор HTML страниц для комиксов."""
    
    def __init__(self):
        """Инициализация генератора HTML."""
        pass
    
    def create_comic_html(self, 
                         panels: List[ComicPanel], 
                         characters: List[ComicCharacter],
                         image_files: List[str], 
                         output_name: str,
                         title: str = "Образовательный комикс") -> str:
        """
        Создание HTML страницы комикса.
        
        Args:
            panels: Список панелей комикса
            characters: Список персонажей
            image_files: Список путей к файлам изображений
            output_name: Базовое имя для выходного файла
            title: Заголовок комикса
            
        Returns:
            Путь к созданному HTML файлу
        """
        logger.info(f"Создание HTML для комикса: {title}")
        
        # Создаем HTML для персонажей
        characters_html = self._create_characters_section(characters)
        
        # Создаем HTML для панелей
        panels_html = self._create_panels_section(panels, image_files)
        
        # Создаем полный HTML
        html_content = self._create_full_html(
            title=title,
            characters_html=characters_html,
            panels_html=panels_html
        )
        
        # Сохраняем файл
        filename = f"{output_name}.html"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"HTML файл создан: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Ошибка создания HTML файла: {e}")
            return ""
    
    def _create_characters_section(self, characters: List[ComicCharacter]) -> str:
        """
        Создание HTML секции с персонажами.
        
        Args:
            characters: Список персонажей
            
        Returns:
            HTML код секции персонажей
        """
        characters_html = ""
        for char in characters:
            characters_html += f"""
            <div class="character-card">
                <h4>{char.name}</h4>
                <p><strong>Роль:</strong> {char.role}</p>
                <p><strong>Характер:</strong> {char.personality}</p>
            </div>
            """
        
        return characters_html
    
    def _create_panels_section(self, 
                              panels: List[ComicPanel], 
                              image_files: List[str]) -> str:
        """
        Создание HTML секции с панелями.
        
        Args:
            panels: Список панелей
            image_files: Список файлов изображений
            
        Returns:
            HTML код секции панелей
        """
        panels_html = ""
        
        for i, panel in enumerate(panels):
            # Определяем источник изображения
            img_src = self._get_image_source(i, image_files, panel.panel_id)
            
            # Создаем HTML для панели
            panels_html += f"""
            <div class="comic-panel enhanced">
                <div class="panel-header">
                    <span class="panel-number">Панель {i+1}</span>
                    <span class="panel-mood">{panel.mood}</span>
                </div>
                <img class="panel-image" src="{img_src}" alt="Панель {i+1}">
                <div class="panel-content">
                    <div class="scene-description">{panel.scene_description}</div>
                    {f'<div class="dialogue">💬 "{panel.dialogue}"</div>' if panel.dialogue else ''}
                    <div class="characters-present">
                        👥 Персонажи: {', '.join(panel.characters)}
                    </div>
                </div>
            </div>
            """
        
        return panels_html
    
    def _get_image_source(self, 
                         panel_index: int, 
                         image_files: List[str], 
                         panel_id: str) -> str:
        """
        Получение источника изображения для панели.
        
        Args:
            panel_index: Индекс панели
            image_files: Список файлов изображений
            panel_id: ID панели
            
        Returns:
            Источник изображения (base64 или placeholder)
        """
        # Если есть файл изображения
        if panel_index < len(image_files) and os.path.exists(image_files[panel_index]):
            try:
                with open(image_files[panel_index], "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{img_data}"
            except Exception as e:
                logger.warning(f"Ошибка загрузки изображения {image_files[panel_index]}: {e}")
        
        # Возвращаем placeholder
        return f"https://via.placeholder.com/600x400/4CAF50/white?text=Панель+{panel_index+1}"
    
    def _create_full_html(self, 
                         title: str, 
                         characters_html: str, 
                         panels_html: str) -> str:
        """
        Создание полного HTML документа.
        
        Args:
            title: Заголовок страницы
            characters_html: HTML секции персонажей
            panels_html: HTML секции панелей
            
        Returns:
            Полный HTML код
        """
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="comic-container">
        <div class="header">
            <h1>📚 {title}</h1>
            <p>Увлекательная история о важных процедурах</p>
        </div>
        
        <div class="characters-section">
            <h2 style="color: #333; margin-bottom: 10px;">👥 Персонажи истории</h2>
            <div class="characters-grid">
                {characters_html}
            </div>
        </div>
        
        <div class="comic-grid">
            {panels_html}
        </div>
        
        <div class="footer">
            <p>🎨 Создано с помощью генератора комиксов</p>
            <p>Качественные изображения • Продуманный сценарий • Образовательный контент</p>
        </div>
    </div>
</body>
</html>"""
    
    def _get_css_styles(self) -> str:
        """
        Получение CSS стилей для HTML.
        
        Returns:
            CSS код
        """
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .comic-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .characters-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 3px solid #e9ecef;
        }
        .characters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .character-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #4CAF50;
        }
        .character-card h4 {
            color: #4CAF50;
            font-size: 1.3em;
            margin-bottom: 10px;
        }
        .comic-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            padding: 30px;
        }
        .comic-panel.enhanced {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .comic-panel.enhanced:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        .panel-header {
            background: linear-gradient(135deg, #333 0%, #555 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .panel-number {
            font-weight: bold;
            font-size: 1.1em;
        }
        .panel-mood {
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }
        .panel-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
            display: block;
        }
        .panel-content {
            padding: 20px;
        }
        .scene-description {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #2196F3;
            font-size: 1em;
            line-height: 1.5;
        }
        .dialogue {
            background: #fff3e0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #ff9800;
            font-style: italic;
            font-weight: 500;
            font-size: 1.1em;
        }
        .characters-present {
            background: #f3e5f5;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 3px solid #9c27b0;
            font-size: 0.95em;
            color: #666;
        }
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-style: italic;
        }
        @media (max-width: 768px) {
            .comic-grid {
                grid-template-columns: 1fr;
                padding: 15px;
                gap: 20px;
            }
            .panel-image {
                height: 250px;
            }
        }
        """