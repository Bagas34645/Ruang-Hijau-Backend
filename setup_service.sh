#!/bin/bash
# Setup script to install/update Flask systemd service with proper timeout configuration

echo "=========================================="
echo "🚀 Flask Service Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    echo "   Usage: sudo bash setup_service.sh"
    exit 1
fi

PROJECT_DIR="/home/ubuntu/Ruang-Hijau-Backend"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

echo "📋 Step 1: Stopping existing Flask service..."
systemctl stop flask 2>/dev/null || echo "   ℹ️  Service not running (this is OK)"

echo "📋 Step 2: Copying service file..."
cp "$PROJECT_DIR/flask.service" /etc/systemd/system/flask.service

# Set proper permissions
chmod 644 /etc/systemd/system/flask.service

echo "📋 Step 3: Creating logs directory..."
mkdir -p "$PROJECT_DIR/logs"
chown ubuntu:ubuntu "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"

echo "📋 Step 4: Reloading systemd daemon..."
systemctl daemon-reload

echo "📋 Step 5: Enabling Flask service (auto-start on boot)..."
systemctl enable flask

echo "📋 Step 6: Starting Flask service..."
systemctl start flask

echo "📋 Step 7: Checking service status..."
sleep 2
systemctl status flask --no-pager

echo ""
echo "=========================================="
echo "✅ Flask service setup complete!"
echo "=========================================="
echo ""
echo "📝 Useful commands:"
echo "   Start:   sudo systemctl start flask"
echo "   Stop:    sudo systemctl stop flask"
echo "   Restart: sudo systemctl restart flask"
echo "   Status:  sudo systemctl status flask"
echo "   Logs:    sudo journalctl -u flask -f"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:8000/api/"
echo ""
echo "🤖 Test the chatbot:"
echo "   curl -X POST http://localhost:8000/api/chatbot/chat \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"Apa itu daur ulang?\"}'"
echo ""
