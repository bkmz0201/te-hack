"""
Настройки и конфигурация для генератора комиксов.
"""

import os
from typing import Dict, Any


class Settings:
    """Класс для управления настройками приложения."""
    
    # Настройки LLM
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3.1")
    LLM_API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:11434")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    
    # Настройки Stable Diffusion
    SD_API_BASE = os.getenv("SD_API_BASE", "http://127.0.0.1:7860")
    SD_STEPS = int(os.getenv("SD_STEPS", "50"))
    SD_WIDTH = int(os.getenv("SD_WIDTH", "768"))
    SD_HEIGHT = int(os.getenv("SD_HEIGHT", "512"))
    SD_CFG_SCALE = float(os.getenv("SD_CFG_SCALE", "8.0"))
    
    # Настройки вывода
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
    DEFAULT_PANELS_COUNT = int(os.getenv("DEFAULT_PANELS_COUNT", "8"))
    DEFAULT_TARGET_AUDIENCE = os.getenv("DEFAULT_TARGET_AUDIENCE", "взрослые")
    
    # Настройки логирования
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Получение полной конфигурации.
        
        Returns:
            Словарь с настройками
        """
        return {
            "llm": {
                "model_name": cls.LLM_MODEL_NAME,
                "api_base": cls.LLM_API_BASE,
                "temperature": cls.LLM_TEMPERATURE,
                "max_tokens": cls.LLM_MAX_TOKENS
            },
            "stable_diffusion": {
                "api_base": cls.SD_API_BASE,
                "steps": cls.SD_STEPS,
                "width": cls.SD_WIDTH,
                "height": cls.SD_HEIGHT,
                "cfg_scale": cls.SD_CFG_SCALE
            },
            "output_dir": cls.OUTPUT_DIR,
            "defaults": {
                "panels_count": cls.DEFAULT_PANELS_COUNT,
                "target_audience": cls.DEFAULT_TARGET_AUDIENCE
            },
            "logging": {
                "level": cls.LOG_LEVEL,
                "format": cls.LOG_FORMAT
            }
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Валидация конфигурации.
        
        Returns:
            Словарь с результатами валидации
        """
        results = {
            "llm_config": True,
            "sd_config": True,
            "output_config": True
        }
        
        try:
            # Проверка LLM настроек
            if not cls.LLM_API_BASE.startswith("http"):
                results["llm_config"] = False
            
            # Проверка SD настроек
            if not cls.SD_API_BASE.startswith("http"):
                results["sd_config"] = False
            
            if cls.SD_STEPS < 1 or cls.SD_STEPS > 150:
                results["sd_config"] = False
            
            # Проверка выходной директории
            try:
                os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
            except Exception:
                results["output_config"] = False
                
        except Exception:
            results = {k: False for k in results}
        
        return results


# Глобальная конфигурация
DEFAULT_CONFIG = Settings.get_config()