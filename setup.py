from setuptools import setup, find_packages

setup(
    name="latex-debugger",
    version="1.2.0",
    description="AI-powered LaTeX file debugger using Gemini 3.5 Flash",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="LaTeX Debugger",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "google-genai>=1.0.0",
        "click>=8.1.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "latex-debug=latex_debugger.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
)
