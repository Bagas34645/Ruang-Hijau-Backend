#!/bin/bash
# Quick start script for Ruang Hijau Backend with Chatbot

echo "=================================================="
echo "🚀 Starting Ruang Hijau Backend"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Run diagnostics
echo ""
echo "🤖 Running chatbot diagnostics..."
python test_chatbot_diagnostic.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ All checks passed! Starting backend..."
    echo "=================================================="
    echo ""
    echo "🌐 Flask will run at: http://localhost:5000"
    echo "💬 Chatbot endpoint: /api/chatbot/chat"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python app.py
else
    echo ""
    echo "❌ Diagnostics failed. Please fix the issues above."
    exit 1
fi
