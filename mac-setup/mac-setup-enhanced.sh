#!/bin/bash
# Enhanced Mac Setup Script for Sophia Intel CLI with AI Integration
# Version: 3.0.0 - Complete Mac Development Environment

set -euo pipefail

# Configuration
readonly VERSION="3.0.0"
readonly REPO="ai-cherry/sophia-intel"
readonly INSTALL_DIR="/usr/local/bin"
readonly CONFIG_DIR="$HOME/.sophia-cli"

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m'

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Show header
show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║       SOPHIA INTEL CLI - MAC SETUP ENHANCED           ║
║         Complete Development Environment              ║
║                  Version 3.0.0                       ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        error_exit "This script is designed for macOS only. Current OS: $OSTYPE"
    fi
    success "macOS detected"
}

# Check for Xcode Command Line Tools
check_xcode_tools() {
    info "Checking Xcode Command Line Tools..."
    
    if ! xcode-select -p &>/dev/null; then
        info "Installing Xcode Command Line Tools..."
        xcode-select --install
        
        # Wait for installation
        until xcode-select -p &>/dev/null; do
            sleep 5
        done
    fi
    
    success "Xcode Command Line Tools are installed"
}

# Install Homebrew
install_homebrew() {
    info "Checking Homebrew installation..."
    
    if ! command -v brew &>/dev/null; then
        info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        info "Updating Homebrew..."
        brew update
    fi
    
    success "Homebrew is ready"
}

# Install required tools
install_prerequisites() {
    info "Installing prerequisite tools..."
    
    local tools=(
        "git"
        "gh"
        "jq"
        "curl"
        "wget"
        "python3"
        "node"
        "yarn"
        "fzf"
        "bat"
        "exa"
        "ripgrep"
        "fd"
        "tree"
    )
    
    for tool in "${tools[@]}"; do
        if ! brew list "$tool" &>/dev/null; then
            info "Installing $tool..."
            brew install "$tool"
        else
            info "$tool is already installed"
        fi
    done
    
    success "All prerequisite tools installed"
}

# Install AI CLI tools
install_ai_tools() {
    info "Installing AI CLI tools..."
    
    # Install Python packages for AI integration
    local python_packages=(
        "anthropic"
        "openai"
        "requests"
        "python-dotenv"
        "rich"
        "typer"
        "httpx"
    )
    
    for package in "${python_packages[@]}"; do
        info "Installing Python package: $package"
        pip3 install --user "$package" --upgrade
    done
    
    # Install Node.js packages for additional AI tools
    local node_packages=(
        "@anthropic-ai/sdk"
        "openai"
        "commander"
        "chalk"
        "inquirer"
    )
    
    for package in "${node_packages[@]}"; do
        info "Installing Node.js package: $package"
        npm install -g "$package"
    done
    
    success "AI CLI tools installed"
}

# Create enhanced CLI wrapper
create_enhanced_cli() {
    info "Creating enhanced CLI wrapper..."
    
    # Download the universal CLI
    curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/sophia-universal-cli -o "$INSTALL_DIR/sophia"
    chmod +x "$INSTALL_DIR/sophia"
    
    # Create convenience aliases
    cat > "$INSTALL_DIR/sophia-ai" << 'SOPHIA_AI'
#!/bin/bash
# Sophia AI Assistant Wrapper

case "${1:-}" in
    claude)
        shift
        sophia --ai claude "$@"
        ;;
    gpt|openai)
        shift
        sophia --ai gpt "$@"
        ;;
    grok)
        shift
        sophia --ai grok "$@"
        ;;
    *)
        echo "Usage: sophia-ai <provider> [query]"
        echo "Providers: claude, gpt, grok"
        echo ""
        echo "Examples:"
        echo "  sophia-ai claude 'analyze the notion branch'"
        echo "  sophia-ai gpt 'show me recent commits'"
        echo "  sophia-ai grok 'what files changed recently?'"
        ;;
esac
SOPHIA_AI
    
    chmod +x "$INSTALL_DIR/sophia-ai"
    
    # Create branch-specific shortcuts
    local branches=("notion" "main" "development")
    for branch in "${branches[@]}"; do
        cat > "$INSTALL_DIR/sophia-$branch" << BRANCH_CLI
#!/bin/bash
# Sophia CLI for $branch branch
export SOPHIA_BRANCH="$branch"
sophia "\$@"
BRANCH_CLI
        chmod +x "$INSTALL_DIR/sophia-$branch"
    done
    
    success "Enhanced CLI wrapper created"
}

# Configure shell integration
configure_shell() {
    info "Configuring shell integration..."
    
    local shell_config=""
    case "$SHELL" in
        */bash)
            shell_config="$HOME/.bashrc"
            ;;
        */zsh)
            shell_config="$HOME/.zshrc"
            ;;
        */fish)
            shell_config="$HOME/.config/fish/config.fish"
            ;;
        *)
            warning "Unknown shell: $SHELL. Manual configuration may be required."
            return
            ;;
    esac
    
    if [ -n "$shell_config" ]; then
        # Create backup
        if [ -f "$shell_config" ]; then
            cp "$shell_config" "$shell_config.backup.$(date +%Y%m%d)"
        fi
        
        # Add Sophia CLI configuration
        cat >> "$shell_config" << 'SHELL_CONFIG'

# Sophia Intel CLI Configuration
export SOPHIA_CLI_VERSION="3.0.0"
export SOPHIA_BRANCH="${SOPHIA_BRANCH:-notion}"
export AI_PROVIDER="${AI_PROVIDER:-claude}"

# Sophia CLI aliases
alias sophia='sophia'
alias sophia-ai='sophia-ai'
alias notion='sophia-notion'
alias main='sophia-main'
alias dev='sophia-development'

# AI-powered aliases
alias ask-claude='sophia-ai claude'
alias ask-gpt='sophia-ai gpt'
alias ask-grok='sophia-ai grok'

# Quick operations
alias sophia-scan='sophia --branch notion && sophia'
alias sophia-report='sophia --ai claude "generate a comprehensive report"'
alias sophia-status='sophia --branch notion && sophia'

# Function for natural language queries
sophia-chat() {
    local query="$*"
    if [ -z "$query" ]; then
        echo "Usage: sophia-chat <your question>"
        echo "Example: sophia-chat show me recent commits in notion branch"
        return 1
    fi
    sophia-ai claude "$query"
}

# Function to switch branches quickly
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

# Auto-completion for Sophia CLI
_sophia_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case "${prev}" in
        --branch)
            opts="notion main development"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        --ai)
            opts="claude gpt grok local"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        *)
            opts="--branch --ai --version --help"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
    esac
}

# Register completion
if [ -n "$BASH_VERSION" ]; then
    complete -F _sophia_completion sophia
fi

SHELL_CONFIG
        
        success "Shell configuration added to $shell_config"
        info "Restart your terminal or run: source $shell_config"
    fi
}

# Create AI configuration
create_ai_config() {
    info "Creating AI configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    cat > "$CONFIG_DIR/ai-config.json" << 'AI_CONFIG'
{
  "version": "3.0.0",
  "providers": {
    "claude": {
      "name": "Claude (Anthropic)",
      "endpoint": "https://api.anthropic.com/v1/messages",
      "model": "claude-3-opus-20240229",
      "max_tokens": 1000,
      "env_var": "CLAUDE_API_KEY",
      "description": "Advanced reasoning and analysis"
    },
    "gpt": {
      "name": "GPT-4 (OpenAI)",
      "endpoint": "https://api.openai.com/v1/chat/completions",
      "model": "gpt-4",
      "max_tokens": 1000,
      "env_var": "OPENAI_API_KEY",
      "description": "General purpose AI assistant"
    },
    "grok": {
      "name": "Grok (xAI)",
      "endpoint": "https://api.x.ai/v1/chat/completions",
      "model": "grok-1",
      "max_tokens": 1000,
      "env_var": "GROK_API_KEY",
      "description": "Real-time and witty responses"
    },
    "local": {
      "name": "Local AI",
      "endpoint": "http://localhost:11434/v1/chat/completions",
      "model": "llama2",
      "max_tokens": 1000,
      "env_var": "LOCAL_AI_KEY",
      "description": "Local AI model (Ollama)"
    }
  },
  "default_provider": "claude",
  "features": {
    "auto_branch_detection": true,
    "context_awareness": true,
    "command_suggestions": true,
    "natural_language": true
  }
}
AI_CONFIG
    
    # Create environment template
    cat > "$CONFIG_DIR/.env.template" << 'ENV_TEMPLATE'
# Sophia Intel CLI - AI API Keys
# Copy this file to .env and add your API keys

# Claude (Anthropic) API Key
# Get from: https://console.anthropic.com/
CLAUDE_API_KEY=your_claude_api_key_here

# OpenAI API Key
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Grok (xAI) API Key
# Get from: https://console.x.ai/
GROK_API_KEY=your_grok_api_key_here

# Local AI (Optional)
# For Ollama or other local AI servers
LOCAL_AI_KEY=optional_local_ai_key

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username

# Sophia CLI Configuration
SOPHIA_BRANCH=notion
AI_PROVIDER=claude
LOG_LEVEL=INFO
ENV_TEMPLATE
    
    chmod 600 "$CONFIG_DIR/.env.template"
    
    success "AI configuration created"
    info "Configure your API keys in: $CONFIG_DIR/.env"
}

# Install additional Mac-specific tools
install_mac_tools() {
    info "Installing Mac-specific productivity tools..."
    
    # Install useful Mac applications via Homebrew Cask
    local cask_apps=(
        "visual-studio-code"
        "iterm2"
        "github-desktop"
        "postman"
        "docker"
    )
    
    for app in "${cask_apps[@]}"; do
        if ! brew list --cask "$app" &>/dev/null; then
            info "Installing $app..."
            brew install --cask "$app" || warning "Failed to install $app"
        else
            info "$app is already installed"
        fi
    done
    
    # Install VS Code extensions
    if command -v code &>/dev/null; then
        info "Installing VS Code extensions..."
        local extensions=(
            "ms-vscode.vscode-json"
            "ms-python.python"
            "ms-vscode.cpptools"
            "github.copilot"
            "github.copilot-chat"
            "ms-vscode.github-issues-prs"
        )
        
        for ext in "${extensions[@]}"; do
            code --install-extension "$ext" --force
        done
    fi
    
    success "Mac-specific tools installed"
}

# Create productivity shortcuts
create_productivity_shortcuts() {
    info "Creating productivity shortcuts..."
    
    # Create Alfred workflow (if Alfred is installed)
    local alfred_dir="$HOME/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows"
    if [ -d "$alfred_dir" ]; then
        info "Creating Alfred workflow for Sophia CLI..."
        # Alfred workflow creation would go here
    fi
    
    # Create Raycast extensions (if Raycast is installed)
    local raycast_dir="$HOME/.config/raycast"
    if [ -d "$raycast_dir" ]; then
        info "Creating Raycast extensions for Sophia CLI..."
        # Raycast extension creation would go here
    fi
    
    # Create macOS Services
    local services_dir="$HOME/Library/Services"
    mkdir -p "$services_dir"
    
    # Quick Actions for Finder
    cat > "$services_dir/Sophia CLI Here.workflow/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Open Sophia CLI Here</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
PLIST
    
    success "Productivity shortcuts created"
}

# Verify installation
verify_installation() {
    info "Verifying installation..."
    
    local checks=(
        "brew --version"
        "git --version"
        "gh --version"
        "python3 --version"
        "node --version"
        "sophia --version"
    )
    
    local failed=0
    for check in "${checks[@]}"; do
        if eval "$check" &>/dev/null; then
            success "$check"
        else
            warning "Failed: $check"
            ((failed++))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        success "All verification checks passed!"
    else
        warning "$failed verification checks failed"
    fi
    
    # Test Sophia CLI
    if sophia --version &>/dev/null; then
        success "Sophia CLI is working correctly"
    else
        error_exit "Sophia CLI installation failed"
    fi
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}🎉 Mac Setup Complete!${NC}"
    echo
    echo -e "${CYAN}Available Commands:${NC}"
    echo "  sophia              - Universal CLI"
    echo "  sophia-ai           - AI assistant"
    echo "  sophia-notion       - Notion branch CLI"
    echo "  sophia-main         - Main branch CLI"
    echo "  ask-claude          - Quick Claude queries"
    echo "  ask-gpt             - Quick GPT queries"
    echo "  sophia-chat         - Natural language interface"
    echo
    echo -e "${CYAN}Quick Start:${NC}"
    echo "  1. Configure API keys: edit $CONFIG_DIR/.env"
    echo "  2. Restart terminal or: source ~/.zshrc"
    echo "  3. Run: sophia"
    echo
    echo -e "${CYAN}AI Integration:${NC}"
    echo "  sophia-ai claude 'analyze the notion branch'"
    echo "  ask-gpt 'show me recent commits'"
    echo "  sophia-chat what files changed recently?"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  • Configure your AI API keys in $CONFIG_DIR/.env"
    echo "  • Authenticate with GitHub: gh auth login"
    echo "  • Explore the CLI: sophia --help"
    echo
}

# Main installation function
main() {
    show_header
    
    # Handle command line arguments
    case "${1:-}" in
        --minimal)
            info "Running minimal installation..."
            check_macos
            install_homebrew
            install_prerequisites
            create_enhanced_cli
            configure_shell
            verify_installation
            ;;
        --full)
            info "Running full installation..."
            check_macos
            check_xcode_tools
            install_homebrew
            install_prerequisites
            install_ai_tools
            create_enhanced_cli
            configure_shell
            create_ai_config
            install_mac_tools
            create_productivity_shortcuts
            verify_installation
            ;;
        --help|-h)
            echo "Sophia Intel CLI - Mac Setup v$VERSION"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --minimal     Install only essential components"
            echo "  --full        Install everything including AI tools and Mac apps"
            echo "  --help        Show this help message"
            echo
            echo "Default: Full installation"
            exit 0
            ;;
        "")
            # Default: full installation
            info "Running full installation..."
            check_macos
            check_xcode_tools
            install_homebrew
            install_prerequisites
            install_ai_tools
            create_enhanced_cli
            configure_shell
            create_ai_config
            install_mac_tools
            create_productivity_shortcuts
            verify_installation
            ;;
        *)
            error_exit "Unknown option: $1. Use --help for usage information."
            ;;
    esac
    
    show_completion
}

# Run main function
main "$@"

