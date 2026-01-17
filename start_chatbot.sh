#!/bin/bash

# ============================================================================
# Ruang Hijau Backend + Chatbot Startup Script
# ============================================================================
# This script starts all necessary services for the chatbot to work:
# 1. Ollama (LLM service)
# 2. Flask Backend
# 3. Optional: Diagnostic checks
# ============================================================================

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🌿 Ruang Hijau Backend + Chatbot Startup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# ============================================================================
# Function Definitions
# ============================================================================

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 found"
        return 0
    else
        echo -e "${RED}❌${NC} $1 NOT found - Install: $2"
        return 1
    fi
}

check_port() {
    if nc -z localhost "$1" 2>/dev/null; then
        echo -e "${YELLOW}⚠️${NC}  Port $1 is in use"
        return 0
    else
        echo -e "${GREEN}✅${NC} Port $1 is available"
        return 1
    fi
}

# ============================================================================
# Startup Script
# ============================================================================

echo -e "\n${BLUE}1️⃣  Checking Requirements...${NC}"

# Check Python
if ! check_command python3 "python3"; then
    check_command python "python"
fi

# Check Ollama
if ! check_command ollama "brew install ollama (macOS) or download from ollama.ai"; then
    echo -e "${YELLOW}⚠️  Ollama is required for chatbot. Install it first.${NC}"
    exit 1
fi

# Check if Flask app exists
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo -e "${RED}❌${NC} app.py not found in $PROJECT_DIR"
    exit 1
fi

echo -e "\n${BLUE}2️⃣  Checking Port Status...${NC}"

check_port 11434  # Ollama port
check_port 5000   # Flask port

echo -e "\n${BLUE}3️⃣  Installing Dependencies...${NC}"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Running: pip install -r requirements.txt"
    python3 -m pip install -r "$PROJECT_DIR/requirements.txt" --quiet
    echo -e "${GREEN}✅${NC} Dependencies installed"
else
    echo -e "${RED}❌${NC} requirements.txt not found"
    exit 1
fi

echo -e "\n${BLUE}4️⃣  Starting Services...${NC}"

echo -e "\n${YELLOW}📌 NOTE: Keep the following terminals running:${NC}"
echo -e "   Terminal 1: Ollama (LLM service)"
echo -e "   Terminal 2: Flask Backend"
echo ""

# Check if user wants to start services
read -p "Start Ollama and Flask now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Starting services...${NC}"
    
    # Check if we can use tmux or screen for better session management
    if command -v tmux &> /dev/null; then
        echo -e "${GREEN}✅${NC} Using tmux for session management"
        
        # Create tmux session
        tmux new-session -d -s "ruang-hijau"
        
        # Window 1: Ollama
        tmux send-keys -t ruang-hijau:0 "echo 'Starting Ollama...' && ollama serve" Enter
        sleep 3
        
        # Window 2: Flask
        tmux new-window -t ruang-hijau -n flask
        tmux send-keys -t ruang-hijau:flask "cd $PROJECT_DIR && python3 app.py" Enter
        
        echo -e "${GREEN}✅${NC} Services started in tmux session 'ruang-hijau'"
        echo -e "   View logs: ${YELLOW}tmux attach -t ruang-hijau${NC}"
        echo -e "   Exit: ${YELLOW}Ctrl+B, then D${NC}"
        echo ""
        
        # Give services time to start
        sleep 5
        
        # Test if services are running
        echo -e "${BLUE}5️⃣  Testing Services...${NC}"
        
        if nc -z localhost 11434 2>/dev/null; then
            echo -e "${GREEN}✅${NC} Ollama is running on http://localhost:11434"
        else
            echo -e "${YELLOW}⚠️${NC}  Ollama not responding yet, might still be starting..."
        fi
        
        if nc -z localhost 5000 2>/dev/null; then
            echo -e "${GREEN}✅${NC} Flask is running on http://localhost:5000"
        else
            echo -e "${YELLOW}⚠️${NC}  Flask not responding yet, might still be starting..."
        fi
        
    else
        echo -e "${YELLOW}⚠️  tmux not found, starting in foreground${NC}"
        echo -e "${YELLOW}   Open another terminal and run: cd $PROJECT_DIR && python3 app.py${NC}"
        echo ""
        ollama serve
    fi
else
    echo -e "${YELLOW}⚠️  Manual startup needed:${NC}"
    echo ""
    echo -e "Terminal 1 - Ollama:"
    echo -e "  ${YELLOW}ollama serve${NC}"
    echo ""
    echo -e "Terminal 2 - Flask Backend:"
    echo -e "  ${YELLOW}cd $PROJECT_DIR${NC}"
    echo -e "  ${YELLOW}python3 app.py${NC}"
    echo ""
    echo -e "Terminal 3 - Test (optional):"
    echo -e "  ${YELLOW}cd $PROJECT_DIR${NC}"
    echo -e "  ${YELLOW}python3 test_chatbot_simple.py${NC}"
fi

echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Ensure both Ollama and Flask are running"
echo -e "  2. Download the default model: ${YELLOW}ollama pull gemma2:2b${NC}"
echo -e "  3. Test the chatbot: ${YELLOW}curl -X POST http://localhost:5000/api/chatbot/chat${NC}"
echo -e "  4. Use the Flutter app - the chatbot should now work!"
echo ""
echo -e "Troubleshooting: See ${YELLOW}CHATBOT_502_FIX.md${NC} for detailed help"
echo ""
