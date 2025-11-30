"""
DAiW - Digital Audio intelligent Workstation
A Python toolkit for music production intelligence.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="idaw",
    version="1.0.0",
    author="Sean Burdges",
    author_email="seanblariat@gmail.com",
    description="iDAW - Intelligent Digital Audio Workstation with Dual Engine architecture, AI-powered music generation, and 7 creative plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DAiW-Music-Brain",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "vault"]),
    package_data={
        "music_brain": ["data/*.json"],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "mido>=1.2.10",
        "numpy>=1.21.0",
    ],
    extras_require={
        "audio": [
            "librosa>=0.9.0",
            "soundfile>=0.10.0",
        ],
        "theory": [
            "music21>=7.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
        "all": [
            "librosa>=0.9.0",
            "soundfile>=0.10.0",
            "music21>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "daiw=music_brain.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="midi music analysis groove chord songwriting daw production",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/DAiW-Music-Brain/issues",
        "Source": "https://github.com/yourusername/DAiW-Music-Brain",
    },
)
