#!/bin/bash
# .devcontainer/setup.sh - GitHub Codespaces Setup Script
# Sophia Intel CLI Development Environment

set -euo pipefail

# Configuration
readonly VERSION="3.0.0"
readonly REPO="ai-cherry/sophia-intel"
readonly WORKSPACE_DIR="/workspaces/sophia-intel"
readonly CONFIG_DIR="/home/codespace/.sophia-cli"

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

# Show setup header
show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║      SOPHIA INTEL CLI - CODESPACES SETUP              ║
║         GitHub Codespaces Development Environment     ║
║                    Version 3.0.0                     ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Update system packages
update_system() {
    info "Updating system packages..."
    
    sudo apt-get update -qq
    sudo apt-get install -y \
        curl \
        wget \
        jq \
        tree \
        htop \
        vim \
        nano \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        unzip \
        zip \
        tar \
        gzip
    
    success "System packages updated"
}

# Install additional CLI tools
install_cli_tools() {
    info "Installing additional CLI tools..."
    
    # Install fzf for fuzzy finding
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
    ~/.fzf/install --all
    
    # Install bat for better cat
    wget -q https://github.com/sharkdp/bat/releases/download/v0.24.0/bat_0.24.0_amd64.deb
    sudo dpkg -i bat_0.24.0_amd64.deb
    rm bat_0.24.0_amd64.deb
    
    # Install exa for better ls
    wget -q https://github.com/ogham/exa/releases/download/v0.10.1/exa-linux-x86_64-v0.10.1.zip
    unzip -q exa-linux-x86_64-v0.10.1.zip
    sudo mv bin/exa /usr/local/bin/
    rm -rf bin exa-linux-x86_64-v0.10.1.zip
    
    # Install ripgrep for better grep
    wget -q https://github.com/BurntSushi/ripgrep/releases/download/13.0.0/ripgrep_13.0.0_amd64.deb
    sudo dpkg -i ripgrep_13.0.0_amd64.deb
    rm ripgrep_13.0.0_amd64.deb
    
    success "Additional CLI tools installed"
}

# Install Python packages for AI integration
install_python_packages() {
    info "Installing Python packages for AI integration..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install AI packages
    pip3 install --user \
        anthropic \
        openai \
        requests \
        python-dotenv \
        rich \
        typer \
        httpx \
        aiohttp \
        asyncio \
        python-telegram-bot \
        fastapi \
        uvicorn \
        pydantic \
        sqlalchemy \
        alembic \
        redis \
        celery \
        pytest \
        black \
        pylint \
        mypy \
        isort
    
    success "Python packages installed"
}

# Install Node.js packages
install_node_packages() {
    info "Installing Node.js packages..."
    
    # Install global packages
    npm install -g \
        @anthropic-ai/sdk \
        openai \
        commander \
        chalk \
        inquirer \
        axios \
        dotenv \
        express \
        socket.io \
        nodemon \
        typescript \
        ts-node \
        @types/node \
        eslint \
        prettier
    
    success "Node.js packages installed"
}

# Setup Sophia CLI
setup_sophia_cli() {
    info "Setting up Sophia Intel CLI..."
    
    # Create config directory
    mkdir -p "$CONFIG_DIR"
    
    # Download and install CLI tools
    curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/cli-tools/install.sh | bash
    
    # Install universal CLI
    curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/sophia-universal-cli -o /usr/local/bin/sophia
    chmod +x /usr/local/bin/sophia
    
    # Create Codespaces-specific configuration
    cat > "$CONFIG_DIR/codespaces-config.json" << 'CONFIG'
{
  "environment": "codespaces",
  "version": "3.0.0",
  "workspace": "/workspaces/sophia-intel",
  "features": {
    "auto_branch_detection": true,
    "ai_integration": true,
    "github_integration": true,
    "port_forwarding": true
  },
  "ports": {
    "frontend": 3000,
    "backend": 5000,
    "cli_server": 8000,
    "telegram_bot": 9000
  },
  "ai_providers": {
    "claude": {
      "enabled": true,
      "env_var": "CLAUDE_API_KEY"
    },
    "gpt": {
      "enabled": true,
      "env_var": "OPENAI_API_KEY"
    },
    "grok": {
      "enabled": true,
      "env_var": "GROK_API_KEY"
    }
  }
}
CONFIG
    
    success "Sophia CLI setup complete"
}

# Configure shell environment
configure_shell() {
    info "Configuring shell environment..."
    
    # Configure zsh
    cat >> ~/.zshrc << 'ZSHRC'

# Sophia Intel CLI Configuration for Codespaces
export SOPHIA_CLI_VERSION="3.0.0"
export SOPHIA_BRANCH="${SOPHIA_BRANCH:-notion}"
export AI_PROVIDER="${AI_PROVIDER:-claude}"
export GITHUB_CODESPACES="true"

# Path additions
export PATH="/usr/local/bin:$HOME/.local/bin:$PATH"

# Sophia CLI aliases
alias sophia='sophia'
alias notion='sophia --branch notion'
alias main='sophia --branch main'
alias dev='sophia --branch development'

# AI shortcuts
alias ask-claude='sophia --ai claude'
alias ask-gpt='sophia --ai gpt'
alias ask-grok='sophia --ai grok'

# Development shortcuts
alias ll='exa -la'
alias la='exa -la'
alias ls='exa'
alias cat='bat'
alias grep='rg'
alias find='fd'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# Codespaces specific
alias ports='gh codespace ports'
alias logs='gh codespace logs'
alias ssh-codespace='gh codespace ssh'

# Function for quick branch switching
sophia-switch() {
    local branch="${1:-}"
    if [ -z "$branch" ]; then
        echo "Available branches: notion, main, development"
        echo "Usage: sophia-switch <branch>"
        return 1
    fi
    export SOPHIA_BRANCH="$branch"
    echo "Switched to branch: $branch"
    sophia --branch "$branch"
}

# Function for AI chat
sophia-chat() {
    local query="$*"
    if [ -z "$query" ]; then
        echo "Usage: sophia-chat <your question>"
        return 1
    fi
    sophia --ai claude "$query"
}

# Auto-start message
echo "🚀 Sophia Intel CLI ready in Codespaces!"
echo "Run 'sophia' to get started"

ZSHRC
    
    # Configure bash as fallback
    cat >> ~/.bashrc << 'BASHRC'

# Sophia Intel CLI Configuration for Codespaces
export SOPHIA_CLI_VERSION="3.0.0"
export SOPHIA_BRANCH="${SOPHIA_BRANCH:-notion}"
export AI_PROVIDER="${AI_PROVIDER:-claude}"
export GITHUB_CODESPACES="true"

# Path additions
export PATH="/usr/local/bin:$HOME/.local/bin:$PATH"

# Sophia CLI aliases
alias sophia='sophia'
alias notion='sophia --branch notion'
alias main='sophia --branch main'

# Development shortcuts
alias ll='exa -la'
alias cat='bat'
alias grep='rg'

BASHRC
    
    success "Shell environment configured"
}

# Setup GitHub integration
setup_github_integration() {
    info "Setting up GitHub integration..."
    
    # Configure git
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    git config --global core.editor "code --wait"
    
    # Setup GitHub CLI
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        echo "$GITHUB_TOKEN" | gh auth login --with-token
        success "GitHub CLI authenticated"
    else
        warning "GITHUB_TOKEN not set. Manual authentication required."
    fi
    
    success "GitHub integration setup complete"
}

# Create development shortcuts
create_dev_shortcuts() {
    info "Creating development shortcuts..."
    
    # Create workspace scripts
    mkdir -p /workspaces/sophia-intel/.vscode
    
    # VS Code tasks
    cat > /workspaces/sophia-intel/.vscode/tasks.json << 'TASKS'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Sophia CLI",
            "type": "shell",
            "command": "sophia",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Run Security Scan",
            "type": "shell",
            "command": "sophia --scan",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "AI Analysis",
            "type": "shell",
            "command": "sophia --ai claude 'analyze the current branch'",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ]
}
TASKS
    
    # VS Code launch configuration
    cat > /workspaces/sophia-intel/.vscode/launch.json << 'LAUNCH'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Telegram Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/telegram_bot.py",
            "console": "integratedTerminal",
            "env": {
                "TELEGRAM_BOT_TOKEN": "${env:TELEGRAM_BOT_TOKEN}",
                "CLAUDE_API_KEY": "${env:CLAUDE_API_KEY}",
                "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
            }
        }
    ]
}
LAUNCH
    
    success "Development shortcuts created"
}

# Setup monitoring and logging
setup_monitoring() {
    info "Setting up monitoring and logging..."
    
    # Create log directory
    mkdir -p "$CONFIG_DIR/logs"
    
    # Setup log rotation
    cat > "$CONFIG_DIR/logrotate.conf" << 'LOGROTATE'
/home/codespace/.sophia-cli/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 codespace codespace
}
LOGROTATE
    
    # Create monitoring script
    cat > /usr/local/bin/sophia-monitor << 'MONITOR'
#!/bin/bash
# Sophia CLI Monitoring Script

echo "🔍 Sophia Intel CLI Status"
echo "=========================="
echo "Version: $(sophia --version 2>/dev/null || echo 'Not installed')"
echo "Branch: ${SOPHIA_BRANCH:-none}"
echo "AI Provider: ${AI_PROVIDER:-none}"
echo "Codespace: ${CODESPACE_NAME:-none}"
echo ""
echo "🌐 Port Status:"
netstat -tlnp 2>/dev/null | grep -E ':(3000|5000|8000|9000)' || echo "No services running"
echo ""
echo "📊 Resource Usage:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h /workspaces | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
MONITOR
    
    chmod +x /usr/local/bin/sophia-monitor
    
    success "Monitoring and logging setup complete"
}

# Create welcome message
create_welcome() {
    info "Creating welcome message..."
    
    cat > /workspaces/sophia-intel/CODESPACES_README.md << 'WELCOME'
# 🚀 Sophia Intel CLI - Codespaces Environment

Welcome to your Sophia Intel CLI development environment in GitHub Codespaces!

## Quick Start

```bash
# Start the CLI
sophia

# Switch branches
sophia --branch notion
sophia --branch main

# AI assistance
sophia --ai claude "analyze this repository"
ask-claude "what files changed recently?"

# Monitor status
sophia-monitor
```

## Available Commands

### Core CLI
- `sophia` - Universal CLI interface
- `notion` - Quick access to notion branch
- `main` - Quick access to main branch
- `sophia-monitor` - System status

### AI Integration
- `ask-claude` - Quick Claude queries
- `ask-gpt` - Quick GPT queries
- `sophia-chat` - Natural language interface

### Development
- `ll` - Enhanced file listing (exa)
- `cat` - Enhanced file viewing (bat)
- `grep` - Enhanced search (ripgrep)

## Ports

- **3000** - Frontend development server
- **5000** - Backend Flask server
- **8000** - Sophia CLI server
- **9000** - Telegram bot

## Configuration

Your API keys are automatically loaded from Codespaces secrets:
- `CLAUDE_API_KEY`
- `OPENAI_API_KEY`
- `GROK_API_KEY`
- `TELEGRAM_BOT_TOKEN`

## VS Code Integration

Use Ctrl+Shift+P and search for:
- "Tasks: Run Task" → "Start Sophia CLI"
- "Tasks: Run Task" → "Run Security Scan"
- "Tasks: Run Task" → "AI Analysis"

## Getting Help

- `sophia --help` - CLI help
- `sophia-monitor` - System status
- Check logs: `tail -f ~/.sophia-cli/logs/sophia.log`

Happy coding! 🎉
WELCOME
    
    success "Welcome message created"
}

# Main setup function
main() {
    show_header
    
    info "Starting Codespaces setup for Sophia Intel CLI..."
    
    # Run setup steps
    update_system
    install_cli_tools
    install_python_packages
    install_node_packages
    setup_sophia_cli
    configure_shell
    setup_github_integration
    create_dev_shortcuts
    setup_monitoring
    create_welcome
    
    success "Codespaces setup complete!"
    
    echo
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo "1. Configure your API keys in Codespaces secrets"
    echo "2. Restart the terminal: Ctrl+Shift+\`"
    echo "3. Run: sophia"
    echo
    echo -e "${CYAN}Quick Commands:${NC}"
    echo "• sophia - Start the CLI"
    echo "• sophia-monitor - Check status"
    echo "• ask-claude 'your question' - AI assistance"
    echo
    echo -e "${YELLOW}Documentation: /workspaces/sophia-intel/CODESPACES_README.md${NC}"
}

# Run main function
main "$@"

