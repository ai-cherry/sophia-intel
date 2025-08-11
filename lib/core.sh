#!/bin/bash
# lib/core.sh - Core shared functions for Sophia Intel CLI
# Version: 3.0.0

# Configuration
readonly SOPHIA_VERSION="3.0.0"
readonly CONFIG_DIR="$HOME/.sophia-cli"
readonly CONFIG_FILE="$CONFIG_DIR/config"
readonly LOG_FILE="$CONFIG_DIR/sophia.log"

# Color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
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

error() {
    echo -e "${RED}✗ $1${NC}" >&2
    log "ERROR: $1"
}

# Configuration management
ensure_config_dir() {
    if [ ! -d "$CONFIG_DIR" ]; then
        mkdir -p "$CONFIG_DIR"
        log "Created config directory: $CONFIG_DIR"
    fi
}

load_config() {
    ensure_config_dir
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    fi
}

save_config() {
    ensure_config_dir
    cat > "$CONFIG_FILE" << EOF
# Sophia Intel CLI Configuration
# Generated on $(date)

# Current settings
SOPHIA_BRANCH="${SOPHIA_BRANCH:-notion}"
AI_PROVIDER="${AI_PROVIDER:-claude}"

# API Keys (encrypted)
CLAUDE_API_KEY="${CLAUDE_API_KEY:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
GROK_API_KEY="${GROK_API_KEY:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# User preferences
PREFERRED_EDITOR="${PREFERRED_EDITOR:-nano}"
AUTO_UPDATE="${AUTO_UPDATE:-true}"
VERBOSE_LOGGING="${VERBOSE_LOGGING:-false}"
EOF
    chmod 600 "$CONFIG_FILE"
    success "Configuration saved to $CONFIG_FILE"
}

# Secure credential management
set_api_key() {
    local provider="$1"
    local key="$2"
    
    if [ -z "$provider" ] || [ -z "$key" ]; then
        error "Usage: set_api_key <provider> <key>"
        return 1
    fi
    
    case "$provider" in
        claude)
            export CLAUDE_API_KEY="$key"
            ;;
        openai|gpt)
            export OPENAI_API_KEY="$key"
            ;;
        grok)
            export GROK_API_KEY="$key"
            ;;
        github)
            export GITHUB_TOKEN="$key"
            ;;
        *)
            error "Unknown provider: $provider"
            return 1
            ;;
    esac
    
    save_config
    success "API key set for $provider"
}

get_api_key() {
    local provider="$1"
    
    case "$provider" in
        claude)
            echo "${CLAUDE_API_KEY:-}"
            ;;
        openai|gpt)
            echo "${OPENAI_API_KEY:-}"
            ;;
        grok)
            echo "${GROK_API_KEY:-}"
            ;;
        github)
            echo "${GITHUB_TOKEN:-}"
            ;;
        *)
            error "Unknown provider: $provider"
            return 1
            ;;
    esac
}

# Interactive setup wizard
interactive_setup() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║           SOPHIA INTEL CLI SETUP WIZARD               ║
║              Welcome to Configuration                 ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    info "Let's configure your Sophia Intel CLI with AI integration."
    echo
    
    # Branch selection
    echo -e "${YELLOW}1. Default Branch Selection${NC}"
    echo "Which branch would you like to use by default?"
    echo "  1) notion (recommended)"
    echo "  2) main"
    echo "  3) development"
    read -p "Enter choice (1-3): " branch_choice
    
    case "$branch_choice" in
        1) export SOPHIA_BRANCH="notion" ;;
        2) export SOPHIA_BRANCH="main" ;;
        3) export SOPHIA_BRANCH="development" ;;
        *) export SOPHIA_BRANCH="notion" ;;
    esac
    
    success "Default branch set to: $SOPHIA_BRANCH"
    echo
    
    # AI Provider selection
    echo -e "${YELLOW}2. AI Provider Configuration${NC}"
    echo "Which AI provider would you like to use by default?"
    echo "  1) Claude (Anthropic) - Advanced reasoning"
    echo "  2) GPT-4 (OpenAI) - General purpose"
    echo "  3) Grok (xAI) - Real-time responses"
    read -p "Enter choice (1-3): " ai_choice
    
    case "$ai_choice" in
        1) export AI_PROVIDER="claude" ;;
        2) export AI_PROVIDER="gpt" ;;
        3) export AI_PROVIDER="grok" ;;
        *) export AI_PROVIDER="claude" ;;
    esac
    
    success "Default AI provider set to: $AI_PROVIDER"
    echo
    
    # API Keys configuration
    echo -e "${YELLOW}3. API Keys Configuration${NC}"
    echo "Let's configure your AI API keys (you can skip any and add them later):"
    echo
    
    if [ "$AI_PROVIDER" = "claude" ] || [ "$ai_choice" = "1" ]; then
        echo "Claude API Key (from console.anthropic.com):"
        read -s -p "Enter Claude API key (or press Enter to skip): " claude_key
        if [ -n "$claude_key" ]; then
            export CLAUDE_API_KEY="$claude_key"
            success "Claude API key configured"
        fi
        echo
    fi
    
    if [ "$AI_PROVIDER" = "gpt" ] || [ "$ai_choice" = "2" ]; then
        echo "OpenAI API Key (from platform.openai.com):"
        read -s -p "Enter OpenAI API key (or press Enter to skip): " openai_key
        if [ -n "$openai_key" ]; then
            export OPENAI_API_KEY="$openai_key"
            success "OpenAI API key configured"
        fi
        echo
    fi
    
    if [ "$AI_PROVIDER" = "grok" ] || [ "$ai_choice" = "3" ]; then
        echo "Grok API Key (from console.x.ai):"
        read -s -p "Enter Grok API key (or press Enter to skip): " grok_key
        if [ -n "$grok_key" ]; then
            export GROK_API_KEY="$grok_key"
            success "Grok API key configured"
        fi
        echo
    fi
    
    # GitHub token (optional)
    echo "GitHub Token (optional, for enhanced repository features):"
    read -s -p "Enter GitHub token (or press Enter to skip): " github_token
    if [ -n "$github_token" ]; then
        export GITHUB_TOKEN="$github_token"
        success "GitHub token configured"
    fi
    echo
    
    # Save configuration
    save_config
    
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                SETUP COMPLETE!                        ║
║         Your Sophia Intel CLI is ready to use        ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo "Quick start commands:"
    echo "  sophia                    # Interactive menu"
    echo "  sophia --branch notion    # Switch to notion branch"
    echo "  sophia --ai claude        # Use Claude AI"
    echo "  sophia config --help      # Manage configuration"
    echo
}

# Dry run mode
is_dry_run() {
    [ "${DRY_RUN:-false}" = "true" ]
}

dry_run_message() {
    if is_dry_run; then
        echo -e "${YELLOW}[DRY RUN] $1${NC}"
        return 0
    fi
    return 1
}

# Utility functions
show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║              SOPHIA INTEL CLI v3.0.0                  ║
║         AI-Integrated Repository Management           ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

show_version() {
    echo "Sophia Intel Universal CLI v$SOPHIA_VERSION"
}

show_help() {
    show_version
    cat << EOF

Usage: sophia [options] [command]

Options:
  --branch <name>     Set current branch (notion/main/development)
  --ai <provider>     Set AI provider (claude/gpt/grok)
  --dry-run          Show what would happen without executing
  --version          Show version information
  --help             Show this help message

Commands:
  config             Manage configuration and API keys
  setup              Run interactive setup wizard
  status             Show current status and configuration
  update             Update CLI to latest version

Configuration Commands:
  config --set-key <provider> <key>    Set API key for provider
  config --get-key <provider>          Get API key for provider
  config --list                        List all configuration
  config --reset                       Reset configuration

Environment Variables:
  SOPHIA_BRANCH      Current branch (default: notion)
  AI_PROVIDER        AI provider (default: claude)
  CLAUDE_API_KEY     Claude API key
  OPENAI_API_KEY     OpenAI API key
  GROK_API_KEY       Grok API key
  GITHUB_TOKEN       GitHub access token

Examples:
  sophia                              # Interactive menu
  sophia --branch notion              # Switch to notion branch
  sophia --ai claude "analyze repo"   # AI analysis
  sophia config --set-key claude sk-ant-...  # Set Claude API key
  sophia --dry-run delete file.txt    # Preview file deletion

For more information, visit:
https://github.com/ai-cherry/sophia-intel/tree/notion/docs

EOF
}

# Validation functions
validate_api_key() {
    local provider="$1"
    local key="$2"
    
    case "$provider" in
        claude)
            if [[ ! "$key" =~ ^sk-ant- ]]; then
                error "Invalid Claude API key format"
                return 1
            fi
            ;;
        openai|gpt)
            if [[ ! "$key" =~ ^sk- ]]; then
                error "Invalid OpenAI API key format"
                return 1
            fi
            ;;
        grok)
            if [[ ! "$key" =~ ^xai- ]]; then
                error "Invalid Grok API key format"
                return 1
            fi
            ;;
        github)
            if [[ ! "$key" =~ ^(ghp_|github_pat_) ]]; then
                error "Invalid GitHub token format"
                return 1
            fi
            ;;
        *)
            error "Unknown provider: $provider"
            return 1
            ;;
    esac
    
    return 0
}

# Initialize core functions
init_core() {
    ensure_config_dir
    load_config
    
    # Set defaults if not configured
    export SOPHIA_BRANCH="${SOPHIA_BRANCH:-notion}"
    export AI_PROVIDER="${AI_PROVIDER:-claude}"
    
    log "Core initialized - Branch: $SOPHIA_BRANCH, AI: $AI_PROVIDER"
}

