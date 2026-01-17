#!/bin/bash
# Ruang Hijau Backend - Production Startup Script
# This script starts the Flask backend with proper gunicorn configuration

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "🚀 Ruang Hijau Backend - Production Start"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt || {
    echo "❌ Failed to install dependencies"
    exit 1
}

# Stop any existing processes
echo "🛑 Stopping any existing processes..."
pkill -f "gunicorn app:app" 2>/dev/null || true
sleep 1

# Run diagnostics
echo ""
echo "🤖 Running quick diagnostics..."
python test_chatbot_diagnostic.py > /dev/null 2>&1 || {
    echo "❌ Diagnostics failed. Please check your configuration."
    exit 1
}

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "📊 Backend will start with:"
echo "   - Address: 0.0.0.0:8000"
echo "   - Workers: 2"
echo "   - Timeout: 120 seconds (for chatbot)"
echo "   - Mode: Production"
echo ""
echo "📝 Logs:"
echo "   - Access: logs/access.log"
echo "   - Errors: logs/error.log"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Start gunicorn with custom config
gunicorn app:app \
    --config gunicorn_config.py \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info
