# 🚀 Sophia Intel CLI - Multi-Platform Edition v3.0.0

**AI-Integrated Repository Management Tool with Enhanced Modular Architecture**

## 🌟 Overview

The Sophia Intel CLI Multi-Platform Edition is a comprehensive, AI-integrated repository management solution that provides seamless access to GitHub repositories with advanced AI assistance from Claude, GPT-4, and Grok.

### ✨ Key Features

- **🖥️ Universal CLI** - Modular architecture with branch-aware operations
- **🤖 AI Integration** - Claude, GPT-4, and Grok support with natural language processing
- **🔧 Interactive Setup** - Guided configuration wizard for easy onboarding
- **🔐 Secure Credentials** - Encrypted API key management with validation
- **📊 Dry Run Mode** - Preview operations before execution
- **🍎 Mac Integration** - Complete macOS development environment setup
- **☁️ GitHub Codespaces** - Pre-configured cloud development environment
- **💬 Telegram Bot** - Mobile repository management with AI assistance
- **🔄 Auto-Updates** - Automatic CLI updates and maintenance

## 🚀 Quick Start

### Universal Installation (Recommended)

```bash
# Auto-detects platform and installs appropriate components
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/install-all.sh | bash

# Follow the interactive setup wizard
sophia setup

# Start using the CLI
sophia
```

### Platform-Specific Installation

#### macOS Complete Setup
```bash
# Full macOS development environment with AI tools
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/mac-setup/mac-setup-enhanced.sh | bash

# Quick access shortcuts
sophia-notion    # Notion branch
sophia-main      # Main branch
sophia-dev       # Development branch
```

#### Linux/WSL
```bash
# Direct CLI installation
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/cli-tools/sophia-universal-cli -o /usr/local/bin/sophia
chmod +x /usr/local/bin/sophia

# Configure API keys
sophia setup
```

#### GitHub Codespaces
1. Go to [GitHub Repository](https://github.com/ai-cherry/sophia-intel)
2. Click "Code" → "Codespaces" → "Create codespace on notion"
3. Wait for automatic setup (includes all dependencies)
4. Run `sophia` in the terminal

#### Telegram Bot
```bash
# Setup Telegram bot for mobile access
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/telegram-bot/telegram-bot-setup.sh | bash

# Follow BotFather setup instructions
# Configure API keys and start service
```

## 🤖 AI Integration

### Supported Providers

| Provider | Model | Strengths | API Key Format |
|----------|-------|-----------|----------------|
| **Claude** | claude-3-opus-20240229 | Advanced reasoning, code analysis | `sk-ant-...` |
| **GPT-4** | gpt-4 | General purpose, broad knowledge | `sk-...` |
| **Grok** | grok-1 | Real-time data, witty responses | `xai-...` |

### Configuration

```bash
# Interactive setup (recommended)
sophia setup

# Manual configuration
sophia config --set-key claude sk-ant-your-key-here
sophia config --set-key openai sk-your-openai-key
sophia config --set-key grok xai-your-grok-key

# Set default AI provider
sophia --ai claude
```

### Usage Examples

```bash
# Universal CLI with AI
sophia --ai claude "analyze the notion branch"
sophia "what files changed recently?"

# Natural language queries
ask-claude "show me security issues in the repository"
ask-gpt "explain the architecture of this project"
ask-grok "what's the latest commit about?"

# Repository analysis
sophia                    # Interactive menu
sophia status            # Current configuration
sophia --branch notion   # Switch to notion branch
```

## 📦 Architecture

### Modular Design

The CLI uses a modular architecture for maintainability and extensibility:

```
sophia-intel-cli/
├── cli-tools/
│   └── sophia-universal-cli     # Main CLI wrapper
├── lib/                         # Core libraries
│   ├── core.sh                 # Shared functions & config
│   ├── repo_ops.sh             # Repository operations
│   ├── file_ops.sh             # File management
│   └── ai_ops.sh               # AI integration
├── mac-setup/                   # macOS integration
├── codespaces/                  # GitHub Codespaces config
├── telegram-bot/               # Telegram bot implementation
└── docs/                       # Documentation
```

### Core Libraries

- **`core.sh`** - Configuration management, logging, security
- **`repo_ops.sh`** - GitHub API integration, branch operations
- **`file_ops.sh`** - File viewing, uploading, downloading
- **`ai_ops.sh`** - AI provider integration and natural language processing

## 🔧 Features

### Repository Operations
- Repository information and statistics
- Branch listing and switching
- Commit history and analysis
- File browsing and management
- Code search and comparison
- Issue and pull request management

### AI-Powered Features
- Repository analysis and insights
- Code review and security analysis
- Documentation generation
- Commit message generation
- Natural language queries
- Context-aware assistance

### Advanced Operations
- Dry run mode for safe testing
- Bulk file operations
- Branch comparison
- File history tracking
- Security scanning
- Performance analysis

### Configuration Management
- Secure API key storage
- Interactive setup wizard
- Environment-based configuration
- Shell integration and aliases
- Auto-update capabilities

## 🔐 Security

### Best Practices
- API keys stored in encrypted configuration files
- No hardcoded credentials in any scripts
- Input validation and sanitization
- Rate limiting and request throttling
- Secure temporary file handling
- Comprehensive audit logging

### Credential Management
```bash
# Set API keys securely
sophia config --set-key claude sk-ant-your-key

# View configured providers (keys are masked)
sophia config --list

# Reset all configuration
sophia config --reset
```

## 🧪 Testing & Validation

### Dry Run Mode
```bash
# Preview operations without executing
sophia --dry-run delete file.txt
sophia --dry-run --ai claude "analyze repository"

# Test configuration
sophia status
sophia config --list
```

### Local Testing
```bash
# Test CLI functionality
sophia --version
sophia --help
sophia status

# Test AI integration
sophia --ai claude "test connection"
```

## 🔄 Updates

### Automatic Updates
```bash
# Check for and install updates
sophia update

# Enable/disable auto-updates
sophia config --set auto-update true
```

### Manual Updates
```bash
# Re-run installation script
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/install-all.sh | bash
```

## 🐛 Troubleshooting

### Common Issues

**Command not found:**
```bash
# Check PATH
echo $PATH | grep /usr/local/bin

# Reinstall
curl -fsSL https://raw.githubusercontent.com/ai-cherry/sophia-intel/notion/install-all.sh | bash
```

**AI provider errors:**
```bash
# Check API keys
sophia config --get-key claude
sophia config --get-key openai

# Test connectivity
sophia --ai claude "test"
```

**Permission errors:**
```bash
# Fix permissions
sudo chmod +x /usr/local/bin/sophia

# Check installation
ls -la /usr/local/bin/sophia
```

**Configuration issues:**
```bash
# Reset configuration
sophia config --reset

# Run setup wizard
sophia setup
```

### Debug Mode
```bash
# Enable verbose logging
export VERBOSE_LOGGING=true
sophia status

# Check log file
cat ~/.sophia-cli/sophia.log
```

## 📚 Documentation

### Command Reference
```bash
sophia --help              # Show help
sophia config --help       # Configuration help
sophia status             # Current status
sophia setup              # Setup wizard
```

### API Documentation
- **Repository**: https://github.com/ai-cherry/sophia-intel
- **Issues**: https://github.com/ai-cherry/sophia-intel/issues
- **Discussions**: https://github.com/ai-cherry/sophia-intel/discussions

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/ai-cherry/sophia-intel.git
cd sophia-intel
git checkout notion

# Install development dependencies
./install-all.sh

# Run tests
./cli-tools/sophia-universal-cli --version
```

### Code Style
- Follow bash best practices
- Use modular architecture
- Include comprehensive error handling
- Add logging for all operations
- Validate all inputs

## 📄 License

This project is licensed under the MIT License - see the repository for details.

## 🔗 Links

- **Repository**: https://github.com/ai-cherry/sophia-intel
- **Documentation**: https://github.com/ai-cherry/sophia-intel/tree/notion/docs
- **Issues**: https://github.com/ai-cherry/sophia-intel/issues
- **Codespaces**: https://github.com/codespaces/new?repo=ai-cherry/sophia-intel&ref=notion

---

**Multi-platform AI-integrated repository management for the modern developer** 🚀

*Built with ❤️ for developers who want AI-powered repository management*

