#!/bin/bash

# BrandForge AI Setup Script

echo "🎨 BrandForge AI - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Google Gemini API key"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Create .streamlit directory for configuration
mkdir -p .streamlit
if [ ! -f .streamlit/config.toml ]; then
    echo "Creating Streamlit configuration..."
    cat > .streamlit/config.toml << EOL
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"
textColor = "#2C3E50"
font = "sans serif"

[server]
headless = false
port = 8501
EOL
    echo "✓ Streamlit configuration created"
    echo ""
fi

echo "================================"
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Run: streamlit run main.py"
echo "3. Open http://localhost:8501 in your browser"
echo ""
echo "Happy branding! 🚀"
