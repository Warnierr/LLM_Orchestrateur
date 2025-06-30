from setuptools import setup, find_packages

setup(
    name="nina_project",
    version="0.2.0",
    description="Assistant IA intelligent et autonome avec orchestration multi-agents",
    author="Nina Project Team",
    author_email="contact@nina-project.ai",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "qdrant-client>=1.7.0",
        "langchain>=0.1.0",
        "openai>=1.3.6",
        "python-dotenv>=0.21.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
        ],
        "crewai": [
            "crewai>=0.1.0",
            "langchain-community>=0.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "nina=nina_project.app.cli:main",
            "nina-web=nina_project.app.interface:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ai assistant agents orchestration llm rag",
    project_urls={
        "Bug Reports": "https://github.com/nina-project/nina/issues",
        "Source": "https://github.com/nina-project/nina",
        "Documentation": "https://nina-project.readthedocs.io/",
    },
) 