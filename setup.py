"""Setup configuration for Project Shri Sudarshan."""

from pathlib import Path

from setuptools import find_packages, setup


# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="shri-sudarshan",
    version="0.1.0",
    description="A Hybrid Multi-Agent LLM Architecture for Stock and Derivatives Trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Project Shri Sudarshan Team",
    url="https://github.com/s-p-c-git/ShriSudarshan",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shri-sudarshan=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="trading llm multi-agent langchain langgraph stocks options derivatives",
    project_urls={
        "Documentation": "https://github.com/s-p-c-git/ShriSudarshan/blob/main/docs/",
        "Source": "https://github.com/s-p-c-git/ShriSudarshan",
        "Tracker": "https://github.com/s-p-c-git/ShriSudarshan/issues",
    },
)
