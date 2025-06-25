#!/usr/bin/env python3
"""
Setup script for AI-Assisted FDIC Bank Branch Analysis System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fdic-branch-analyzer",
    version="1.0.0",
    author="Jad Edlebi, Jason Richardson",
    author_email="jedlebi@ncrc.org, jrichardson@ncrc.org",
    description="AI-powered FDIC bank branch data analysis and reporting tool. Developed at National Community Reinvestment Coalition (NCRC), 740 15th Street NW, Washington, DC 20005.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fdic-branch-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "fdic-analyzer=src.core.main:main",
            "branch-analyzer=src.core.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.sql"],
    },
    keywords="fdic, banking, analysis, bigquery, ai, claude, gpt",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fdic-branch-analyzer/issues",
        "Source": "https://github.com/yourusername/fdic-branch-analyzer",
        "Documentation": "https://github.com/yourusername/fdic-branch-analyzer/blob/main/README.md",
    },
) 