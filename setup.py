#!/usr/bin/env python3
"""
EvaBot - Simple robotics library for kids
Progressive learning from single motor to autonomous robot
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="evabot",
    version="0.1.0",
    author="EvaBot Project",
    description="Simple robotics library for progressive learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/evabot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Robotics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-can>=4.0.0",
        "pyserial>=3.5",
        "numpy>=1.20.0",
    ],
    extras_require={
        "camera": [
            "opencv-python>=4.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "evabot-setup=evabot.tools.setup:main",
        ],
    },
)
