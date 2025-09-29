#!/usr/bin/env python3
"""
Главный модуль для запуска генератора комиксов.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Добавляем корневую директорию в путь
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from generators.comic_generator import ComicGenerator
from config.settings import Settings, DEFAULT_CONFIG
from models.comic_models import StyleType


def setup_logging(log_level: str = "INFO"):
    """
    Настройка логирования.
    
    Args:
        log_level: Уровень логирования
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=Settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("comic_generator.log", encoding="utf-8")
        ]
    )


def print_banner():
    """Печать баннера приложения."""
    banner = """
🎨 ================================= 🎨
    ГЕНЕРАТОР ОБРАЗОВАТЕЛЬНЫХ КОМИКСОВ
🎨 ================================= 🎨

Превращение документов в увлекательные комиксы
с помощью AI агентов и Stable Diffusion
"""
    print(banner)


def validate_dependencies(generator: ComicGenerator) -> bool:
    """
    Проверка зависимостей системы.
    
    Args:
        generator: Экземпляр генератора
        
    Returns:
        True если все зависимости доступны
    """
    print("🔍 Проверка зависимостей...")
    
    dependencies = generator.validate_dependencies()
    
    for service, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"   {status} {service}: {'Доступен' if available else 'Недоступен'}")
    
    # Проверка конфигурации
    config_validation = Settings.validate_config()
    for config_part, valid in config_validation.items():
        status = "✅" if valid else "❌"
        print(f"   {status} {config_part}: {'OK' if valid else 'Ошибка'}")
    
    all_valid = all(dependencies.values()) and all(config_validation.values())
    
    if not all_valid:
        print("\\n⚠️ Некоторые зависимости недоступны. Генерация может работать с ограничениями.")
        print("   - Убедитесь, что Ollama запущен на порту 11434")
        print("   - Убедитесь, что Stable Diffusion WebUI запущен на порту 7860")
    
    return True  # Продолжаем работу даже если не все доступно


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Генератор образовательных комиксов из PDF документов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py document.pdf
  python main.py document.pdf --panels 10 --audience "студенты"
  python main.py document.pdf --style professional --output my_comic
  python main.py --validate-only
        """
    )
    
    parser.add_argument(
        "pdf_file",
        nargs="?",
        help="Путь к PDF файлу для обработки"
    )
    
    parser.add_argument(
        "--panels", "-p",
        type=int,
        default=DEFAULT_CONFIG["defaults"]["panels_count"],
        help="Количество панелей в комиксе (по умолчанию: 8)"
    )
    
    parser.add_argument(
        "--audience", "-a",
        default=DEFAULT_CONFIG["defaults"]["target_audience"],
        help="Целевая аудитория (по умолчанию: взрослые)"
    )
    
    parser.add_argument(
        "--style", "-s",
        choices=[style.value for style in StyleType],
        default=StyleType.EDUCATIONAL.value,
        help="Стиль изображений (по умолчанию: educational)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="comic",
        help="Базовое имя выходных файлов (по умолчанию: comic)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Только проверить зависимости, не запускать генерацию"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Уровень логирования (по умолчанию: INFO)"
    )
    
    parser.add_argument(
        "--config",
        help="Путь к файлу конфигурации JSON"
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    print_banner()
    
    # Загрузка конфигурации
    config = DEFAULT_CONFIG.copy()
    if args.config and os.path.exists(args.config):
        try:
            import json
            with open(args.config, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            config.update(custom_config)
            print(f"✅ Загружена конфигурация из {args.config}")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
    
    # Создание генератора
    try:
        generator = ComicGenerator(config)
    except Exception as e:
        logger.error(f"Ошибка инициализации генератора: {e}")
        sys.exit(1)
    
    # Проверка зависимостей
    if not validate_dependencies(generator):
        sys.exit(1)
    
    # Если только валидация - выходим
    if args.validate_only:
        print("\\n✅ Проверка зависимостей завершена")
        sys.exit(0)
    
    # Проверка входного файла
    if not args.pdf_file:
        print("❌ Необходимо указать PDF файл для обработки")
        parser.print_help()
        sys.exit(1)
    
    if not os.path.exists(args.pdf_file):
        print(f"❌ Файл не найден: {args.pdf_file}")
        sys.exit(1)
    
    # Запуск генерации
    try:
        print(f"\\n🚀 Начинаем генерацию комикса из {args.pdf_file}")
        print(f"   📊 Панелей: {args.panels}")
        print(f"   👥 Аудитория: {args.audience}")
        print(f"   🎨 Стиль: {args.style}")
        print(f"   📁 Выходное имя: {args.output}")
        print()
        
        result = generator.generate_comic_from_pdf(
            pdf_path=args.pdf_file,
            target_audience=args.audience,
            num_panels=args.panels,
            output_name=args.output,
            style=args.style
        )
        
        if result:
            print(f"\\n🎉 Комикс успешно создан!")
            print(f"📄 HTML файл: {result}")
            
            # Показываем статистику
            stats = generator.get_generation_stats()
            print(f"⏱️ Время генерации: {stats.get('duration_seconds', 0):.1f} сек")
            print(f"🖼️ Изображений создано: {stats.get('images_generated', 0)}")
            print(f"🤖 Вызовов LLM: {stats.get('llm_calls', 0)}")
            
            if stats.get('errors'):
                print(f"⚠️ Предупреждений: {len(stats['errors'])}")
            
        else:
            print("❌ Не удалось создать комикс")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\n⏹️ Генерация прервана пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()