@echo off
REM FDIC Branch Analyzer Installation Script for Windows
REM This script sets up the AI-powered FDIC bank branch analysis tool

echo 🚀 Installing FDIC Branch Analyzer...
echo ======================================

REM Check if Python 3.9+ is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python version: %python_version%

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pip is not installed. Please install pip first.
    pause
    exit /b 1
)

echo ✅ pip found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Install the package in development mode
echo 🔧 Installing package...
pip install -e .

echo.
echo ✅ Installation completed successfully!
echo.
echo 📋 Next steps:
echo 1. Create a .env file with your credentials:
echo    copy .env.example .env
echo    REM Edit .env with your BigQuery and AI API credentials
echo.
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the analyzer:
echo    fdic-analyzer
echo    REM or
echo    python main.py
echo.
echo 📖 For more information, see README.md
echo.
pause 