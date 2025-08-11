#!/bin/bash
# Universal installer for Sophia Intel CLI Multi-Platform v3.0.0
# Enhanced with interactive setup wizard

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
readonly NC='\033[0m'

# Logging functions
success() { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${CYAN}ℹ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}" >&2; }

# Show welcome banner
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║        SOPHIA INTEL CLI INSTALLER v3.0.0              ║
║      AI-Integrated Repository Management Tool         ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Detect platform
detect_platform() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in curl jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Platform-specific checks
    local platform
    platform=$(detect_platform)
    
    case "$platform" in
        macos)
            if ! command -v brew >/dev/null 2>&1; then
                warning "Homebrew not found. Some features may require manual installation."
            fi
            ;;
        linux)
            if ! command -v apt >/dev/null 2>&1 && ! command -v yum >/dev/null 2>&1 && ! command -v pacman >/dev/null 2>&1; then
                warning "No supported package manager found. Manual dependency installation may be required."
            fi
            ;;
    esac
    
    # Install missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        warning "Missing dependencies: ${missing_deps[*]}"
        
        case "$platform" in
            macos)
                if command -v brew >/dev/null 2>&1; then
                    info "Installing dependencies via Homebrew..."
                    for dep in "${missing_deps[@]}"; do
                        brew install "$dep" || warning "Failed to install $dep"
                    done
                fi
                ;;
            linux)
                if command -v apt >/dev/null 2>&1; then
                    info "Installing dependencies via apt..."
                    sudo apt update
                    for dep in "${missing_deps[@]}"; do
                        sudo apt install -y "$dep" || warning "Failed to install $dep"
                    done
                elif command -v yum >/dev/null 2>&1; then
                    info "Installing dependencies via yum..."
                    for dep in "${missing_deps[@]}"; do
                        sudo yum install -y "$dep" || warning "Failed to install $dep"
                    done
                fi
                ;;
        esac
    fi
    
    success "Prerequisites check completed"
}

# Download and install CLI
install_cli() {
    local platform
    platform=$(detect_platform)
    
    info "Installing Sophia Intel CLI for $platform..."
    
    # Create install directory if it doesn't exist
    if [ ! -d "$INSTALL_DIR" ]; then
        sudo mkdir -p "$INSTALL_DIR" || {
            error "Failed to create install directory: $INSTALL_DIR"
            return 1
        }
    fi
    
    # Download the universal CLI
    local cli_url="https://raw.githubusercontent.com/$REPO/notion/cli-tools/sophia-universal-cli"
    local temp_file
    temp_file=$(mktemp)
    
    if curl -fsSL "$cli_url" -o "$temp_file"; then
        # Install the CLI
        if sudo cp "$temp_file" "$INSTALL_DIR/sophia" && sudo chmod +x "$INSTALL_DIR/sophia"; then
            success "CLI installed to $INSTALL_DIR/sophia"
        else
            error "Failed to install CLI"
            rm -f "$temp_file"
            return 1
        fi
    else
        error "Failed to download CLI from $cli_url"
        rm -f "$temp_file"
        return 1
    fi
    
    rm -f "$temp_file"
    
    # Create convenient aliases
    create_aliases "$platform"
}

# Create shell aliases
create_aliases() {
    local platform="$1"
    
    info "Setting up shell integration..."
    
    # Determine shell configuration file
    local shell_config=""
    if [ -n "${BASH_VERSION:-}" ]; then
        shell_config="$HOME/.bashrc"
    elif [ -n "${ZSH_VERSION:-}" ]; then
        shell_config="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        shell_config="$HOME/.profile"
    fi
    
    if [ -n "$shell_config" ]; then
        # Add aliases if they don't exist
        local aliases_block="
# Sophia Intel CLI aliases
alias sophia-notion='sophia --branch notion'
alias sophia-main='sophia --branch main'
alias sophia-dev='sophia --branch development'
alias ask-claude='sophia --ai claude'
alias ask-gpt='sophia --ai gpt'
alias ask-grok='sophia --ai grok'
alias sophia-chat='sophia'
alias sophia-status='sophia status'
alias sophia-config='sophia config'
"
        
        if ! grep -q "Sophia Intel CLI aliases" "$shell_config" 2>/dev/null; then
            echo "$aliases_block" >> "$shell_config"
            success "Shell aliases added to $shell_config"
        else
            info "Shell aliases already exist in $shell_config"
        fi
    fi
    
    # Platform-specific setup
    case "$platform" in
        macos)
            setup_macos_integration
            ;;
        linux)
            setup_linux_integration
            ;;
    esac
}

# macOS-specific setup
setup_macos_integration() {
    info "Setting up macOS integration..."
    
    # Create LaunchAgent for auto-updates (optional)
    local launchagent_dir="$HOME/Library/LaunchAgents"
    local launchagent_file="$launchagent_dir/com.sophia-intel.cli.plist"
    
    if [ ! -f "$launchagent_file" ]; then
        mkdir -p "$launchagent_dir"
        cat > "$launchagent_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sophia-intel.cli</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/sophia</string>
        <string>update</string>
    </array>
    <key>StartInterval</key>
    <integer>86400</integer>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF
        success "Auto-update LaunchAgent created"
    fi
}

# Linux-specific setup
setup_linux_integration() {
    info "Setting up Linux integration..."
    
    # Create desktop entry
    local desktop_dir="$HOME/.local/share/applications"
    local desktop_file="$desktop_dir/sophia-intel-cli.desktop"
    
    if [ ! -f "$desktop_file" ]; then
        mkdir -p "$desktop_dir"
        cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Sophia Intel CLI
Comment=AI-Integrated Repository Management Tool
Exec=gnome-terminal -- sophia
Icon=terminal
Type=Application
Categories=Development;
Terminal=true
EOF
        success "Desktop entry created"
    fi
}

# Interactive setup wizard
interactive_setup() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║              INTERACTIVE SETUP WIZARD                 ║
║         Configure your Sophia Intel CLI               ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    # Create config directory
    mkdir -p "$CONFIG_DIR"
    
    # Branch selection
    echo -e "${YELLOW}1. Default Branch Selection${NC}"
    echo "Which branch would you like to use by default?"
    echo "  1) notion (recommended for latest features)"
    echo "  2) main (stable release)"
    echo "  3) development (cutting edge)"
    read -p "Enter choice (1-3) [1]: " branch_choice
    
    local default_branch
    case "${branch_choice:-1}" in
        2) default_branch="main" ;;
        3) default_branch="development" ;;
        *) default_branch="notion" ;;
    esac
    
    success "Default branch set to: $default_branch"
    
    # AI Provider selection
    echo
    echo -e "${YELLOW}2. AI Provider Configuration${NC}"
    echo "Which AI provider would you like to use by default?"
    echo "  1) Claude (Anthropic) - Advanced reasoning and analysis"
    echo "  2) GPT-4 (OpenAI) - General purpose AI assistance"
    echo "  3) Grok (xAI) - Real-time responses and wit"
    read -p "Enter choice (1-3) [1]: " ai_choice
    
    local default_ai
    case "${ai_choice:-1}" in
        2) default_ai="gpt" ;;
        3) default_ai="grok" ;;
        *) default_ai="claude" ;;
    esac
    
    success "Default AI provider set to: $default_ai"
    
    # API Keys configuration
    echo
    echo -e "${YELLOW}3. API Keys Configuration${NC}"
    echo "Let's configure your AI API keys. You can skip any and add them later using 'sophia config'."
    echo
    
    # Claude API Key
    if [ "$default_ai" = "claude" ] || [ "$ai_choice" = "1" ]; then
        echo "Claude API Key (from console.anthropic.com):"
        echo "Format: sk-ant-..."
        read -s -p "Enter Claude API key (or press Enter to skip): " claude_key
        echo
        if [ -n "$claude_key" ]; then
            success "Claude API key configured"
        fi
    fi
    
    # OpenAI API Key
    if [ "$default_ai" = "gpt" ] || [ "$ai_choice" = "2" ]; then
        echo "OpenAI API Key (from platform.openai.com):"
        echo "Format: sk-..."
        read -s -p "Enter OpenAI API key (or press Enter to skip): " openai_key
        echo
        if [ -n "$openai_key" ]; then
            success "OpenAI API key configured"
        fi
    fi
    
    # Grok API Key
    if [ "$default_ai" = "grok" ] || [ "$ai_choice" = "3" ]; then
        echo "Grok API Key (from console.x.ai):"
        echo "Format: xai-..."
        read -s -p "Enter Grok API key (or press Enter to skip): " grok_key
        echo
        if [ -n "$grok_key" ]; then
            success "Grok API key configured"
        fi
    fi
    
    # GitHub Token (optional)
    echo "GitHub Token (optional, for enhanced repository features):"
    echo "Format: ghp_... or github_pat_..."
    read -s -p "Enter GitHub token (or press Enter to skip): " github_token
    echo
    if [ -n "$github_token" ]; then
        success "GitHub token configured"
    fi
    
    # Save configuration
    cat > "$CONFIG_DIR/config" << EOF
# Sophia Intel CLI Configuration
# Generated on $(date)

# Current settings
SOPHIA_BRANCH="$default_branch"
AI_PROVIDER="$default_ai"

# API Keys
CLAUDE_API_KEY="${claude_key:-}"
OPENAI_API_KEY="${openai_key:-}"
GROK_API_KEY="${grok_key:-}"
GITHUB_TOKEN="${github_token:-}"

# User preferences
PREFERRED_EDITOR="nano"
AUTO_UPDATE="true"
VERBOSE_LOGGING="false"
EOF
    
    chmod 600 "$CONFIG_DIR/config"
    success "Configuration saved to $CONFIG_DIR/config"
    
    echo
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                SETUP COMPLETE!                        ║
║         Your Sophia Intel CLI is ready to use        ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║            INSTALLATION SUCCESSFUL!                   ║
║        Sophia Intel CLI v3.0.0 is ready              ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo "Quick start commands:"
    echo "  sophia                    # Interactive menu"
    echo "  sophia --help             # Show help"
    echo "  sophia setup              # Run setup wizard"
    echo "  sophia status             # Show current status"
    echo
    echo "Branch shortcuts:"
    echo "  sophia-notion             # Use notion branch"
    echo "  sophia-main               # Use main branch"
    echo "  sophia-dev                # Use development branch"
    echo
    echo "AI shortcuts:"
    echo "  ask-claude \"question\"      # Ask Claude AI"
    echo "  ask-gpt \"question\"         # Ask GPT-4"
    echo "  ask-grok \"question\"        # Ask Grok AI"
    echo
    echo "Configuration:"
    echo "  sophia config --help      # Configuration help"
    echo "  sophia config --set-key claude sk-ant-...  # Set API key"
    echo
    echo "For more information:"
    echo "  https://github.com/$REPO/tree/notion/docs"
    echo
    
    # Suggest running setup if not already done
    if [ ! -f "$CONFIG_DIR/config" ]; then
        echo -e "${YELLOW}💡 Tip: Run 'sophia setup' to configure API keys and preferences${NC}"
    fi
    
    echo -e "${CYAN}🚀 Start with: sophia${NC}"
}

# Main installation process
main() {
    show_banner
    
    info "Starting Sophia Intel CLI installation..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        warning "Running as root. Installation will proceed but configuration will be for root user."
    fi
    
    # Run installation steps
    check_prerequisites
    install_cli
    
    # Ask if user wants to run setup wizard
    echo
    read -p "Would you like to run the interactive setup wizard now? (Y/n): " run_setup
    
    if [[ ! "$run_setup" =~ ^[Nn]$ ]]; then
        interactive_setup
    else
        info "You can run the setup wizard later with: sophia setup"
    fi
    
    show_completion
}

# Run main function
main "$@"

