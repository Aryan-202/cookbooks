from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import os

requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]


setup(
    name="cook-optimizer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="LLM Inference Optimization Engine - Cook your prompts with optimal settings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aryan-202/cookbooks",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cook=cook.cli.commands:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cook": ["templates/*.html"],
    },
)