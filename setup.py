"""
Установочный скрипт для генератора комиксов.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="comic-generator",
    version="1.0.0",
    author="Илья Ковалев",
    author_email="ilya@example.com",
    description="Генератор образовательных комиксов с помощью AI агентов и Stable Diffusion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/user/comic-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "jinja2>=3.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "comic-generator=comic_generator.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "comic_generator": [
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/user/comic-generator/issues",
        "Source": "https://github.com/user/comic-generator",
        "Documentation": "https://github.com/user/comic-generator/wiki",
    },
)