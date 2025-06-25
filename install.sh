#!/bin/bash

# FDIC Branch Analyzer Installation Script
# This script sets up the AI-powered FDIC bank branch analysis tool

set -e  # Exit on any error

echo "🚀 Installing FDIC Branch Analyzer..."
echo "======================================"

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "🔧 Installing package..."
pip install -e .

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create a .env file with your credentials:"
echo "   cp .env.example .env"
echo "   # Edit .env with your BigQuery and AI API credentials"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the analyzer:"
echo "   fdic-analyzer"
echo "   # or"
echo "   python main.py"
echo ""
echo "📖 For more information, see README.md"
echo "" 