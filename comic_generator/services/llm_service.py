"""
Сервис для работы с LLM моделями.
"""

from crewai.llm import LLM
import litellm
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CustomOllamaLLM(LLM):
    """Кастомный LLM класс для работы с Ollama через litellm."""
    
    def __init__(self, model_name: str = "llama3.1", api_base: str = "http://127.0.0.1:11434"):
        """
        Инициализация LLM.
        
        Args:
            model_name: Название модели
            api_base: Базовый URL API
        """
        super().__init__(model=model_name)
        self.api_base = api_base
        self.temperature = 0.7
        self.max_tokens = 4000
        
    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Вызов LLM для генерации ответа.
        
        Args:
            messages: Список сообщений для обработки
            **kwargs: Дополнительные параметры
            
        Returns:
            Сгенерированный ответ
        """
        try:
            response = litellm.completion(
                model=f"ollama/{self.model}",
                api_base=self.api_base,
                temperature=self.temperature,
                messages=messages,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка LLM: {e}")
            return "Произошла ошибка при обработке запроса."
    
    def is_available(self) -> bool:
        """
        Проверка доступности LLM сервиса.
        
        Returns:
            True если сервис доступен
        """
        try:
            test_response = self.call([{"role": "user", "content": "test"}])
            return bool(test_response)
        except Exception:
            return False


class LLMServiceManager:
    """Менеджер для управления LLM сервисами."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация менеджера.
        
        Args:
            config: Конфигурация для LLM
        """
        self.config = config or {}
        self._llm_instance = None
    
    def get_llm(self) -> CustomOllamaLLM:
        """
        Получение экземпляра LLM.
        
        Returns:
            Настроенный экземпляр LLM
        """
        if self._llm_instance is None:
            model_name = self.config.get("model_name", "llama3.1")
            api_base = self.config.get("api_base", "http://127.0.0.1:11434")
            self._llm_instance = CustomOllamaLLM(model_name, api_base)
        
        return self._llm_instance
    
    def validate_llm_connection(self) -> bool:
        """
        Валидация подключения к LLM.
        
        Returns:
            True если подключение успешно
        """
        llm = self.get_llm()
        return llm.is_available()