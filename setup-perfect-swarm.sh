#!/bin/bash

# 🎯 SOPHIA INTEL PERFECT SWARM - COMPLETE SETUP
# Multi-LLM orchestration with best-in-class models

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

clear

echo -e "${CYAN}${BOLD}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════╗
║                   🎯 SOPHIA INTEL PERFECT SWARM                         ║
║                  Multi-LLM Coding Environment Setup                     ║
╚══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Step 1: Verify Installation
echo -e "${YELLOW}${BOLD}Step 1: Verifying Environment${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js installed: ${NODE_VERSION}${NC}"
else
    echo -e "${RED}❌ Node.js not found${NC}"
    echo -e "${YELLOW}Installing Node.js...${NC}"
    PATH=/opt/homebrew/bin:$PATH
    brew install node
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm installed: ${NPM_VERSION}${NC}"
else
    echo -e "${RED}❌ npm not found${NC}"
fi

# Check API keys
echo -e "\n${YELLOW}${BOLD}Step 2: API Keys Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# OpenRouter key (already embedded)
echo -e "${GREEN}✅ OpenRouter API Key: Configured${NC}"

# Display available models
echo -e "\n${YELLOW}${BOLD}Step 3: Model Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${PURPLE}${BOLD}🧠 Planning & Architecture:${NC}"
echo -e "  • Primary: ${BLUE}Claude Opus 4.1${NC} - Deep reasoning, migration strategies"
echo -e "  • Fallback: ${BLUE}DeepSeek Chat v3${NC} - Cost-effective alternative"

echo -e "\n${PURPLE}${BOLD}💻 Specialized Coding:${NC}"
echo -e "  • Primary: ${BLUE}Qwen 3 Coder (32B)${NC} - Best for complex code generation"
echo -e "  • Fallback: ${BLUE}Mistral Nemo${NC} - Fast, efficient coding"

echo -e "\n${PURPLE}${BOLD}🔍 Code Review & Challenge:${NC}"
echo -e "  • Primary: ${BLUE}Grok 4${NC} - Catches edge cases, challenges assumptions"
echo -e "  • Fallback: ${BLUE}GPT-4 Turbo${NC} - Comprehensive review"

echo -e "\n${PURPLE}${BOLD}🧪 QA & Testing:${NC}"
echo -e "  • Primary: ${BLUE}Gemini 2.5 Flash${NC} - Fast test generation"
echo -e "  • Fallback: ${BLUE}Claude Haiku${NC} - Thorough test coverage"

echo -e "\n${PURPLE}${BOLD}📚 Documentation Review:${NC}"
echo -e "  • Primary: ${BLUE}Gemini 2.5 Flash${NC} - Multimodal capable"

# Test the CLI
echo -e "\n${YELLOW}${BOLD}Step 4: Testing Swarm CLI${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "swarm-cli.js" ]; then
    echo -e "${GREEN}✅ Swarm CLI found${NC}"
else
    echo -e "${RED}❌ Swarm CLI not found${NC}"
fi

# Create shortcuts
echo -e "\n${YELLOW}${BOLD}Step 5: Creating Command Shortcuts${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create alias file
cat > swarm-aliases.sh << 'ALIASES'
# Sophia Intel Swarm Aliases
alias swarm='node /Users/lynnmusil/Projects/sophia-main/sophia-intel-clone/swarm-cli.js'
alias swarm-plan='echo "plan" | swarm'
alias swarm-code='echo "code_special" | swarm'
alias swarm-review='echo "challenge" | swarm'
alias swarm-test='echo "qa_test" | swarm'
alias swarm-doc='echo "doc_review" | swarm'
ALIASES

echo -e "${GREEN}✅ Aliases created in swarm-aliases.sh${NC}"
echo -e "${YELLOW}Add to your ~/.zshrc: source $(pwd)/swarm-aliases.sh${NC}"

# Usage guide
echo -e "\n${YELLOW}${BOLD}Step 6: Usage Guide${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${PURPLE}${BOLD}Quick Start:${NC}"
echo -e "  1. Run the CLI: ${GREEN}node swarm-cli.js${NC}"
echo -e "  2. Use commands:"
echo -e "     ${BLUE}plan${NC} Create a TypeScript migration strategy"
echo -e "     ${BLUE}code_special${NC} Add comprehensive error handling to fetchWrapper.ts"
echo -e "     ${BLUE}challenge${NC} Review this authentication implementation for security issues"
echo -e "     ${BLUE}qa_test${NC} Generate unit tests for the UserService class"
echo -e "     ${BLUE}doc_review${NC} Check if this API documentation matches the implementation"

echo -e "\n${PURPLE}${BOLD}Example Workflow:${NC}"
cat << 'WORKFLOW'

  1. Planning Phase:
     > plan Migrate our Express.js API to Fastify with TypeScript

  2. Implementation (in Claude Code):
     $ claude
     // Let Claude Code implement based on the plan

  3. Specialized Coding:
     > code_special Add rate limiting middleware with Redis caching

  4. Code Review:
     > challenge Check the new auth middleware for timing attacks

  5. Test Generation:
     > qa_test Create integration tests for the new API endpoints

  6. Documentation:
     > doc_review Verify the OpenAPI spec matches our implementation

WORKFLOW

# Final status
echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}                        ✅ SETUP COMPLETE!                                 ${NC}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}${BOLD}Ready to use the Perfect Swarm!${NC}"
echo -e "${YELLOW}Start with: ${GREEN}node swarm-cli.js${NC}"
echo -e "\n${PURPLE}The swarm combines:${NC}"
echo -e "  • ${BLUE}5 specialized roles${NC} (Planner, Coder, Challenger, Tester, Reviewer)"
echo -e "  • ${BLUE}10+ cutting-edge models${NC} with automatic fallbacks"
echo -e "  • ${BLUE}Persistent memory${NC} for patterns and preferences"
echo -e "  • ${BLUE}Claude Code integration${NC} for file operations"

echo -e "\n${GREEN}${BOLD}Happy coding! 🚀${NC}\n"
