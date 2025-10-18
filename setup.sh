#!/bin/bash

echo "🚀 WhatsApp HR Assistant Setup"
echo "================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "📦 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure it:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Add your Google Service Account JSON:"
echo "   Place service-account.json in this directory"
echo ""
echo "3. Run the application:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
