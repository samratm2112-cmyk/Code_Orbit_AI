#!/bin/bash

# CodeOrbit AI - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 CodeOrbit AI - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python -m venv venv
        echo "✅ Virtual environment recreated"
    fi
else
    python -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=your_key_here"
fi
echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/repositories data/vector_stores data/cache logs
echo "✅ Directories created"
echo ""

# Create __init__.py files
echo "📝 Creating Python package files..."
touch frontend/__init__.py
touch frontend/pages/__init__.py
touch frontend/components/__init__.py
touch frontend/utils/__init__.py
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/core/__init__.py
touch backend/services/__init__.py
touch backend/models/__init__.py
touch backend/utils/__init__.py
touch tests/__init__.py
echo "✅ Package files created"
echo ""

# Run tests (if available)
if [ -f "tests/test_api.py" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
    echo ""
fi

# Summary
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start backend: cd backend && uvicorn main:app --reload"
echo "4. Start frontend: cd frontend && streamlit run app.py"
echo ""
echo "📖 Documentation:"
echo "   - Architecture: ARCHITECTURE.md"
echo "   - Implementation: IMPLEMENTATION_ROADMAP.md"
echo "   - API Docs: docs/API.md"
echo "   - Demo Script: docs/DEMO.md"
echo ""
echo "Happy coding! 🚀"

# Made with Bob
