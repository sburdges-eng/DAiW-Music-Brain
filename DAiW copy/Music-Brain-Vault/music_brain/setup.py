"""
Music Brain Setup

Install with:
    pip install .

Or for development:
    pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name='music-brain',
    version='1.0.0',
    author='Sean',
    description='Music production analysis toolkit - groove, structure, and audio',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'mido',
    ],
    extras_require={
        'audio': ['librosa', 'numpy', 'soundfile'],
        'full': ['librosa', 'numpy', 'soundfile'],
    },
    entry_points={
        'console_scripts': [
            'music-brain=music_brain.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
