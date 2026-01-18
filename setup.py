"""
Setup configuration for AiRobo-Trainer
A Stroke Rehabilitation Trainer powered by Brain-Computer Interface (BCI)
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="airobo-trainer",
    version="0.1.0",
    author="AiRobo Team",
    description="A Stroke Rehabilitation Trainer powered by Brain-Computer Interface (BCI) technology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/airobo-trainer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pylint>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "airobo-trainer=main:main",
        ],
    },
)
