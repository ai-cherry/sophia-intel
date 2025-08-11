#!/bin/bash
# setup-telegram-bot.sh - Sophia Intel Telegram Bot Setup
# Version: 3.0.0

set -euo pipefail

# Configuration
readonly VERSION="3.0.0"
readonly BOT_DIR="$HOME/sophia-telegram-bot"
readonly SERVICE_NAME="sophia-telegram-bot"

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

info() {
    echo -e "${CYAN}ℹ $1${NC}"
    log "INFO: $1"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log "WARNING: $1"
}

error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Show header
show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║      SOPHIA INTEL TELEGRAM BOT SETUP                  ║
║         AI-Integrated Repository Management           ║
║                    Version 3.0.0                     ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Show BotFather instructions
show_botfather_instructions() {
    echo -e "${CYAN}📱 Creating Telegram Bot with BotFather${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Follow these steps to create your bot:"
    echo
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot to BotFather"
    echo "3. Choose a name: Sophia Intel CLI Bot"
    echo "4. Choose a username: sophia_intel_cli_bot (or similar)"
    echo "5. Copy the bot token that BotFather provides"
    echo
    echo "Optional: Configure bot settings with BotFather:"
    echo "• /setdescription - Set bot description"
    echo "• /setabouttext - Set about text"
    echo "• /setuserpic - Upload bot profile picture"
    echo "• /setcommands - Set bot commands menu"
    echo
    read -p "Press Enter when you have your bot token..."
}

# Get bot token from user
get_bot_token() {
    echo
    echo -e "${YELLOW}🔑 Bot Token Configuration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    while true; do
        read -p "Enter your Telegram bot token: " BOT_TOKEN
        
        if [[ $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
            success "Valid bot token format"
            break
        else
            warning "Invalid token format. Please try again."
        fi
    done
}

# Get API keys
get_api_keys() {
    echo
    echo -e "${YELLOW}🤖 AI API Keys Configuration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Configure your AI API keys (optional but recommended):"
    echo
    
    # Claude API Key
    read -p "Claude API Key (from console.anthropic.com): " CLAUDE_API_KEY
    if [ -n "$CLAUDE_API_KEY" ]; then
        success "Claude API key configured"
    fi
    
    # OpenAI API Key
    read -p "OpenAI API Key (from platform.openai.com): " OPENAI_API_KEY
    if [ -n "$OPENAI_API_KEY" ]; then
        success "OpenAI API key configured"
    fi
    
    # Grok API Key
    read -p "Grok API Key (from console.x.ai): " GROK_API_KEY
    if [ -n "$GROK_API_KEY" ]; then
        success "Grok API key configured"
    fi
    
    # GitHub Token
    read -p "GitHub Token (optional, for enhanced features): " GITHUB_TOKEN
    if [ -n "$GITHUB_TOKEN" ]; then
        success "GitHub token configured"
    fi
}

# Install dependencies
install_dependencies() {
    info "Installing Python dependencies..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        error_exit "Python 3 is required but not installed"
    fi
    
    # Install pip if not available
    if ! command -v pip3 &> /dev/null; then
        info "Installing pip..."
        curl https://bootstrap.pypa.io/get-pip.py | python3
    fi
    
    # Install required packages
    pip3 install --user \
        python-telegram-bot \
        anthropic \
        openai \
        aiohttp \
        aiofiles \
        python-dotenv \
        requests
    
    success "Dependencies installed"
}

# Create bot directory and files
create_bot_files() {
    info "Creating bot directory and files..."
    
    # Create directory
    mkdir -p "$BOT_DIR"
    cd "$BOT_DIR"
    
    # Download bot script
    curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/telegram_bot.py -o telegram_bot.py
    chmod +x telegram_bot.py
    
    # Create environment file
    cat > .env << ENV_FILE
# Sophia Intel Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
CLAUDE_API_KEY=$CLAUDE_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
GROK_API_KEY=$GROK_API_KEY
GITHUB_TOKEN=$GITHUB_TOKEN

# Bot Configuration
BOT_VERSION=3.0.0
REPO=ai-cherry/sophia-intel
DEFAULT_BRANCH=notion
MAX_MESSAGE_LENGTH=4096
CACHE_TTL=300
RATE_LIMIT=30
ENV_FILE
    
    chmod 600 .env
    
    # Create requirements.txt
    cat > requirements.txt << 'REQUIREMENTS'
python-telegram-bot>=20.0
anthropic>=0.3.0
openai>=1.0.0
aiohttp>=3.8.0
aiofiles>=23.0.0
python-dotenv>=1.0.0
requests>=2.28.0
REQUIREMENTS
    
    # Create startup script
    cat > start_bot.sh << 'STARTUP'
#!/bin/bash
# Sophia Intel Telegram Bot Startup Script

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if bot token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

echo "🚀 Starting Sophia Intel Telegram Bot..."
echo "Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "Repository: $REPO"

# Start the bot
python3 telegram_bot.py
STARTUP
    
    chmod +x start_bot.sh
    
    success "Bot files created in $BOT_DIR"
}

# Create systemd service (Linux only)
create_systemd_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "Creating systemd service..."
        
        sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << SERVICE_FILE
[Unit]
Description=Sophia Intel Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/start_bot.sh
Restart=always
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin
EnvironmentFile=$BOT_DIR/.env

[Install]
WantedBy=multi-user.target
SERVICE_FILE
        
        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        
        success "Systemd service created and enabled"
        info "Use 'sudo systemctl start $SERVICE_NAME' to start the bot"
        info "Use 'sudo systemctl status $SERVICE_NAME' to check status"
    else
        info "Systemd service creation skipped (not on Linux)"
    fi
}

# Create launchd service (macOS only)
create_launchd_service() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        info "Creating launchd service for macOS..."
        
        local plist_file="$HOME/Library/LaunchAgents/com.sophia.telegram-bot.plist"
        
        cat > "$plist_file" << PLIST_FILE
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sophia.telegram-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>$BOT_DIR/start_bot.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$BOT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$BOT_DIR/bot.log</string>
    <key>StandardErrorPath</key>
    <string>$BOT_DIR/bot.error.log</string>
</dict>
</plist>
PLIST_FILE
        
        # Load the service
        launchctl load "$plist_file"
        
        success "Launchd service created and loaded"
        info "Use 'launchctl start com.sophia.telegram-bot' to start the bot"
        info "Use 'launchctl list | grep sophia' to check status"
    else
        info "Launchd service creation skipped (not on macOS)"
    fi
}

# Test bot
test_bot() {
    info "Testing bot configuration..."
    
    cd "$BOT_DIR"
    
    # Test import
    if python3 -c "import telegram_bot; print('✓ Bot script imports successfully')" 2>/dev/null; then
        success "Bot script validation passed"
    else
        warning "Bot script validation failed - check dependencies"
    fi
    
    # Test token format
    if [[ $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        success "Bot token format is valid"
    else
        warning "Bot token format may be invalid"
    fi
    
    info "Manual test: Run './start_bot.sh' to test the bot"
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}🎉 Telegram Bot Setup Complete!${NC}"
    echo
    echo -e "${CYAN}📁 Bot Location:${NC} $BOT_DIR"
    echo -e "${CYAN}🚀 Start Command:${NC} $BOT_DIR/start_bot.sh"
    echo
    echo -e "${CYAN}Service Management:${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  sudo systemctl start $SERVICE_NAME"
        echo "  sudo systemctl stop $SERVICE_NAME"
        echo "  sudo systemctl status $SERVICE_NAME"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  launchctl start com.sophia.telegram-bot"
        echo "  launchctl stop com.sophia.telegram-bot"
        echo "  launchctl list | grep sophia"
    fi
    echo
    echo -e "${CYAN}Configuration:${NC}"
    echo "  Edit: $BOT_DIR/.env"
    echo "  Logs: $BOT_DIR/bot.log"
    echo
    echo -e "${CYAN}Bot Commands:${NC}"
    echo "  /start - Start the bot"
    echo "  /help - Show help"
    echo "  /status - Bot status"
    echo "  /branches - List branches"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Test the bot: $BOT_DIR/start_bot.sh"
    echo "2. Send /start to your bot in Telegram"
    echo "3. Configure additional API keys if needed"
    echo "4. Set up automatic startup (service already configured)"
}

# Main setup function
main() {
    show_header
    
    # Handle command line arguments
    case "${1:-}" in
        --help|-h)
            echo "Sophia Intel Telegram Bot Setup v$VERSION"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --help        Show this help message"
            echo "  --token TOKEN Set bot token directly"
            echo
            echo "This script will:"
            echo "1. Guide you through creating a Telegram bot"
            echo "2. Configure API keys for AI integration"
            echo "3. Install dependencies and create bot files"
            echo "4. Set up automatic startup service"
            exit 0
            ;;
        --token)
            BOT_TOKEN="${2:-}"
            if [ -z "$BOT_TOKEN" ]; then
                error_exit "Bot token is required with --token option"
            fi
            ;;
        "")
            # Interactive setup
            show_botfather_instructions
            get_bot_token
            ;;
        *)
            error_exit "Unknown option: $1. Use --help for usage information."
            ;;
    esac
    
    # Run setup steps
    get_api_keys
    install_dependencies
    create_bot_files
    create_systemd_service
    create_launchd_service
    test_bot
    show_completion
}

# Run main function
main "$@"

