#!/usr/bin/env python3
"""
Setup script for Short Video Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="short-video-generator",
    version="1.0.0",
    author="Short Video Generator Team",
    author_email="contact@shortvideogenerator.com",
    description="An automated AI-powered system for generating and uploading short videos to multiple social media platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/short-video-generator",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/short-video-generator/issues",
        "Source": "https://github.com/yourusername/short-video-generator",
        "Documentation": "https://github.com/yourusername/short-video-generator#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Content Creators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gpu": [
            "torch>=2.1.0",
            "torchvision>=0.16.0",
            "diffusers>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "short-generator=cli:main",
            "short-video-generator=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)
