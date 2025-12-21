#!/bin/bash

# BrandForge AI - Production Setup Script
# This script sets up the production environment

set -e  # Exit on error

echo "======================================"
echo "BrandForge AI - Production Setup"
echo "======================================"
echo ""

# Check if running with sudo for system packages
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Do not run this script with sudo"
    exit 1
fi

# Check Python version
echo "1. Checking Python version..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION < 3.9" | bc -l) )); then
        echo "❌ Python 3.9+ is required. You have Python $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python found: $($PYTHON_CMD --version)"
echo ""

# Create virtual environment
echo "2. Setting up virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo "✅ Virtual environment recreated"
    fi
else
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "4. Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "5. Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "6. Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Create necessary directories
echo "7. Creating necessary directories..."
mkdir -p exports logs
echo "✅ Directories created"
echo ""

# Run tests
echo "8. Running tests..."
if [ -d "tests" ]; then
    TEST_PASSED=0
    TEST_TOTAL=0
    for test_file in tests/test_phase*.py; do
        if [ -f "$test_file" ]; then
            TEST_TOTAL=$((TEST_TOTAL + 1))
            if python "$test_file" > /dev/null 2>&1; then
                TEST_PASSED=$((TEST_PASSED + 1))
                echo "  ✅ $(basename $test_file)"
            else
                echo "  ❌ $(basename $test_file)"
            fi
        fi
    done
    echo "✅ Tests completed: $TEST_PASSED/$TEST_TOTAL passed"
else
    echo "⚠️  Tests directory not found, skipping tests"
fi
echo ""

# Check API key
echo "9. Checking API key configuration..."
if grep -q "your_google_api_key_here" .env 2>/dev/null || ! grep -q "GOOGLE_API_KEY=AIza" .env 2>/dev/null; then
    echo "⚠️  GOOGLE_API_KEY not configured in .env file"
    echo ""
    echo "To get your API key:"
    echo "1. Visit: https://makersuite.google.com/app/apikey"
    echo "2. Sign in with your Google account"
    echo "3. Create a new API key"
    echo "4. Copy the key and paste it in .env file"
else
    echo "✅ API key configured"
fi
echo ""

# Final instructions
echo "======================================"
echo "✅ Production setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Make sure your GOOGLE_API_KEY is set in .env"
echo "2. Run the application:"
echo "   streamlit run main.py"
echo ""
echo "For Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "For Streamlit Cloud deployment:"
echo "   See docs/DEPLOYMENT.md for instructions"
echo ""
