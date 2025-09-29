# Makefile для генератора комиксов

.PHONY: help install dev-install test lint format clean run validate

# Переменные
PYTHON := python3
PIP := pip3
VENV := venv
SOURCE := comic_generator
TESTS := tests

help:  ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Установить зависимости
	$(PIP) install -r requirements.txt

dev-install:  ## Установить зависимости для разработки
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

venv:  ## Создать виртуальное окружение
	$(PYTHON) -m venv $(VENV)
	@echo "Активируйте окружение: source $(VENV)/bin/activate"

test:  ## Запустить тесты
	pytest $(TESTS) -v --tb=short

test-coverage:  ## Запустить тесты с покрытием
	pytest $(TESTS) -v --cov=$(SOURCE) --cov-report=html --cov-report=term

lint:  ## Проверить код линтером
	flake8 $(SOURCE) $(TESTS)
	mypy $(SOURCE)

format:  ## Отформатировать код
	black $(SOURCE) $(TESTS)
	isort $(SOURCE) $(TESTS)

format-check:  ## Проверить форматирование
	black --check $(SOURCE) $(TESTS)
	isort --check-only $(SOURCE) $(TESTS)

clean:  ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf outputs/
	rm -f comic_generator.log

run:  ## Запустить генератор (требует PDF файл)
	@if [ -z "$(PDF)" ]; then \
		echo "Использование: make run PDF=path/to/file.pdf"; \
		echo "Дополнительные параметры:"; \
		echo "  PANELS=8 (количество панелей)"; \
		echo "  AUDIENCE=взрослые (целевая аудитория)"; \
		echo "  STYLE=educational (стиль изображений)"; \
		echo "  OUTPUT=comic (базовое имя файлов)"; \
	else \
		$(PYTHON) $(SOURCE)/main.py $(PDF) \
			--panels $(or $(PANELS),8) \
			--audience "$(or $(AUDIENCE),взрослые)" \
			--style $(or $(STYLE),educational) \
			--output $(or $(OUTPUT),comic); \
	fi

validate:  ## Проверить зависимости системы
	$(PYTHON) $(SOURCE)/main.py --validate-only

example:  ## Запустить с примером (если есть example.pdf)
	@if [ -f "example.pdf" ]; then \
		$(PYTHON) $(SOURCE)/main.py example.pdf --panels 6 --output example_comic; \
	else \
		echo "Файл example.pdf не найден. Создайте его или используйте make run PDF=your_file.pdf"; \
	fi

build:  ## Собрать пакет для распространения
	$(PYTHON) setup.py sdist bdist_wheel

install-local:  ## Установить локально для разработки
	$(PIP) install -e .

check-deps:  ## Проверить актуальность зависимостей
	$(PIP) list --outdated

security-check:  ## Проверить безопасность зависимостей
	safety check

doc:  ## Генерировать документацию
	@echo "Документация доступна в README.md"
	@echo "Для создания Sphinx документации:"
	@echo "  sphinx-quickstart docs"
	@echo "  sphinx-build -b html docs docs/_build"

all-checks: format-check lint test  ## Выполнить все проверки

ci: install all-checks  ## CI/CD pipeline

# Примеры использования
demo-educational:  ## Демо с образовательным стилем
	@echo "Для демо создайте файл demo.pdf и запустите:"
	@echo "make run PDF=demo.pdf STYLE=educational PANELS=8 OUTPUT=educational_demo"

demo-professional:  ## Демо с профессиональным стилем
	@echo "Для демо создайте файл demo.pdf и запустите:"
	@echo "make run PDF=demo.pdf STYLE=professional PANELS=6 OUTPUT=business_demo"

# Развертывание
deploy-dev:  ## Развернуть в dev окружении
	@echo "Настройка dev окружения..."
	cp .env.example .env
	@echo "Отредактируйте .env файл и запустите make install"

server-check:  ## Проверить доступность серверов
	@echo "Проверяем Ollama..."
	@curl -s http://127.0.0.1:11434/api/tags > /dev/null && echo "✅ Ollama доступен" || echo "❌ Ollama недоступен"
	@echo "Проверяем Stable Diffusion..."
	@curl -s http://127.0.0.1:7860/docs > /dev/null && echo "✅ Stable Diffusion доступен" || echo "❌ Stable Diffusion недоступен"