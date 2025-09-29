# 🎨 Генератор Образовательных Комиксов

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange)
![Stable Diffusion](https://img.shields.io/badge/Stable%20Diffusion-WebUI-purple)

Превращение сложных документов в увлекательные образовательные комиксы с помощью AI агентов и Stable Diffusion.

## 🌟 Особенности

- **🤖 AI-агенты**: Использует CrewAI для анализа документов и создания сценариев
- **🎨 Генерация изображений**: Интеграция с Stable Diffusion для создания качественных иллюстраций  
- **📚 Поддержка PDF**: Автоматическое извлечение и анализ контента из PDF документов
- **🎭 Персонажи**: Автоматическое создание запоминающихся персонажей
- **📖 HTML вывод**: Красивый адаптивный веб-интерфейс для просмотра комиксов
- **⚙️ Конфигурируемость**: Гибкие настройки через конфигурационные файлы и переменные окружения

## 🏗️ Архитектура

```
comic_generator/
├── models/              # Модели данных
│   └── comic_models.py  # ComicPanel, ComicCharacter, ProcessInfo
├── services/            # Сервисы
│   ├── llm_service.py   # Интеграция с LLM
│   └── document_service.py # Работа с документами
├── generators/          # Генераторы контента
│   ├── content_analyzer.py # Анализ документов
│   ├── scenario_generator.py # Создание сценариев
│   ├── image_generator.py # Генерация изображений
│   └── comic_generator.py # Главный генератор
├── utils/              # Утилиты
│   ├── html_generator.py # Создание HTML
│   └── data_manager.py  # Управление данными
├── config/             # Конфигурация
│   └── settings.py     # Настройки приложения
└── main.py            # Точка входа
```

## 🚀 Быстрый старт

### Предварительные требования

1. **Python 3.8+**
2. **Ollama** с моделью llama3.1:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama3.1
   ollama serve
   ```

3. **Stable Diffusion WebUI** (опционально, для генерации изображений):
   ```bash
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
   cd stable-diffusion-webui
   ./webui.sh --api
   ```

### Установка

1. **Клонирование репозитория:**
   ```bash
   git clone <repository-url>
   cd comic_generator
   ```

2. **Создание виртуального окружения:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\\Scripts\\activate  # Windows
   ```

3. **Установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```

### Базовое использование

```bash
# Генерация комикса из PDF
python comic_generator/main.py document.pdf

# С дополнительными параметрами
python comic_generator/main.py document.pdf \\
    --panels 10 \\
    --audience "студенты" \\
    --style professional \\
    --output my_comic

# Только проверка зависимостей
python comic_generator/main.py --validate-only
```

## 📖 Подробное использование

### Параметры командной строки

- `pdf_file` - Путь к PDF файлу для обработки
- `--panels`, `-p` - Количество панелей (по умолчанию: 8)
- `--audience`, `-a` - Целевая аудитория (по умолчанию: "взрослые")
- `--style`, `-s` - Стиль изображений (educational, professional, friendly, narrative)
- `--output`, `-o` - Базовое имя выходных файлов (по умолчанию: "comic")
- `--validate-only` - Только проверить зависимости
- `--log-level` - Уровень логирования (DEBUG, INFO, WARNING, ERROR)
- `--config` - Путь к файлу конфигурации JSON

### Переменные окружения

```bash
# LLM настройки
export LLM_MODEL_NAME="llama3.1"
export LLM_API_BASE="http://127.0.0.1:11434"
export LLM_TEMPERATURE="0.7"

# Stable Diffusion настройки  
export SD_API_BASE="http://127.0.0.1:7860"
export SD_STEPS="50"
export SD_WIDTH="768"
export SD_HEIGHT="512"

# Общие настройки
export OUTPUT_DIR="outputs"
export LOG_LEVEL="INFO"
```

### Конфигурационный файл

Создайте `config.json`:

```json
{
  "llm": {
    "model_name": "llama3.1",
    "api_base": "http://127.0.0.1:11434",
    "temperature": 0.7,
    "max_tokens": 4000
  },
  "stable_diffusion": {
    "api_base": "http://127.0.0.1:7860",
    "steps": 50,
    "width": 768,
    "height": 512,
    "cfg_scale": 8.0
  },
  "output_dir": "outputs",
  "defaults": {
    "panels_count": 8,
    "target_audience": "взрослые"
  }
}
```

## 🎯 Примеры использования

### Создание комикса для студентов

```bash
python comic_generator/main.py legal_document.pdf \\
    --audience "студенты юридических факультетов" \\
    --panels 12 \\
    --style educational \\
    --output legal_process_comic
```

### Профессиональный стиль для бизнеса

```bash
python comic_generator/main.py business_process.pdf \\
    --audience "сотрудники компании" \\
    --style professional \\
    --panels 6 \\
    --output business_comic
```

### Использование с кастомной конфигурацией

```bash
python comic_generator/main.py document.pdf \\
    --config my_config.json \\
    --log-level DEBUG
```

## 📊 Выходные файлы

После успешной генерации создаются следующие файлы:

```
outputs/
├── comic.html              # Основной HTML файл комикса
├── comic_data.json         # Структурированные данные
├── comic_summary.json      # Сводка проекта
├── comic_config.json       # Использованная конфигурация
└── comic_images/          # Директория с изображениями
    ├── panel_1.png
    ├── panel_2.png
    └── ...
```

## 🛠️ Разработка

### Структура классов

- **ComicGenerator** - Главный класс-оркестратор
- **ContentAnalyzer** - Анализ документов с помощью CrewAI
- **ScenarioGenerator** - Создание персонажей и сценариев
- **ImageGenerator** - Генерация изображений через Stable Diffusion
- **HTMLGenerator** - Создание веб-интерфейса
- **DataManager** - Управление данными и сохранение

### Добавление новых стилей

1. Обновите `StyleType` в `models/comic_models.py`
2. Добавьте стиль в `style_presets` в `ImageGenerator`
3. Обновите документацию

### Создание кастомных агентов

```python
from crewai import Agent
from comic_generator.services.llm_service import CustomOllamaLLM

llm = CustomOllamaLLM()
custom_agent = Agent(
    role="Специализированный аналитик",
    goal="Ваша цель",
    backstory="История агента",
    llm=llm
)
```

## 🔧 Устранение неполадок

### Частые проблемы

1. **LLM недоступен**
   ```bash
   # Проверьте статус Ollama
   ollama list
   ollama serve
   ```

2. **Stable Diffusion недоступен**
   ```bash
   # Убедитесь что WebUI запущен с API
   ./webui.sh --api --listen
   ```

3. **Ошибки памяти**
   ```bash
   # Уменьшите размер изображений
   export SD_WIDTH="512"
   export SD_HEIGHT="384"
   ```

4. **Медленная генерация**
   ```bash
   # Уменьшите количество шагов
   export SD_STEPS="20"
   ```

### Логирование

Включите детальное логирование:

```bash
python comic_generator/main.py document.pdf --log-level DEBUG
```

Лог-файл сохраняется в `comic_generator.log`.

## 📈 Производительность

- **Анализ документа**: ~30-60 секунд
- **Создание сценария**: ~60-120 секунд  
- **Генерация изображений**: ~30-60 секунд на панель
- **Общее время**: 5-15 минут на комикс из 8 панелей

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Сделайте коммит (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Правила кодирования

- Используйте type hints
- Добавляйте docstrings для всех функций
- Покрывайте код тестами
- Следуйте PEP 8

```bash
# Форматирование кода
black comic_generator/

# Линтинг
flake8 comic_generator/

# Проверка типов
mypy comic_generator/

# Тесты
pytest tests/
```

