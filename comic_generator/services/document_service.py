"""
Сервис для работы с документами (PDF и другими форматами).
"""

from langchain_community.document_loaders import PyPDFLoader
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class DocumentService:
    """Сервис для загрузки и обработки документов."""
    
    @staticmethod
    def load_pdf(file_path: str) -> Optional[str]:
        """
        Загрузка текста из PDF файла.
        
        Args:
            file_path: Путь к PDF файлу
            
        Returns:
            Извлеченный текст или None в случае ошибки
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Файл не найден: {file_path}")
                return None
                
            if not file_path.lower().endswith('.pdf'):
                logger.error(f"Файл должен быть в формате PDF: {file_path}")
                return None
            
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            if not pages:
                logger.warning(f"PDF файл пустой: {file_path}")
                return None
            
            text = "\n".join([page.page_content for page in pages])
            
            logger.info(f"Успешно загружен PDF: {file_path}, символов: {len(text)}")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка загрузки PDF {file_path}: {e}")
            return None
    
    @staticmethod
    def load_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Загрузка текстового файла.
        
        Args:
            file_path: Путь к текстовому файлу
            encoding: Кодировка файла
            
        Returns:
            Содержимое файла или None в случае ошибки
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Файл не найден: {file_path}")
                return None
            
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            
            logger.info(f"Успешно загружен текстовый файл: {file_path}, символов: {len(content)}")
            return content
            
        except Exception as e:
            logger.error(f"Ошибка загрузки текстового файла {file_path}: {e}")
            return None
    
    @staticmethod
    def validate_document(content: str, min_length: int = 100) -> bool:
        """
        Валидация загруженного документа.
        
        Args:
            content: Содержимое документа
            min_length: Минимальная длина документа
            
        Returns:
            True если документ валиден
        """
        if not content or not isinstance(content, str):
            return False
            
        if len(content.strip()) < min_length:
            logger.warning(f"Документ слишком короткий: {len(content)} символов")
            return False
        
        return True
    
    @staticmethod
    def get_document_summary(content: str, max_length: int = 500) -> str:
        """
        Получение краткого содержания документа.
        
        Args:
            content: Полное содержимое документа
            max_length: Максимальная длина резюме
            
        Returns:
            Краткое содержание
        """
        if not content:
            return ""
        
        # Берем начало документа для краткого содержания
        summary = content[:max_length]
        
        # Обрезаем по последнему предложению если превышена длина
        if len(content) > max_length:
            last_period = summary.rfind('.')
            if last_period > max_length // 2:  # Если есть точка в разумном месте
                summary = summary[:last_period + 1]
            summary += "..."
        
        return summary.strip()