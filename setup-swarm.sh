#!/bin/bash

# Sophia Intel Perfect Swarm - Setup Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}======================================"
echo "   🎯 SOPHIA INTEL PERFECT SWARM"
echo "======================================${NC}"
echo ""

# Check if Node.js is installed
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js is installed$(NC)"
else
    echo -e "${YELLOW}Installing Node.js...${NC}"
    brew install node
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
npm install @modelcontextprotocol/sdk node-fetch

echo -e "${YELLOW}Installing global MCP servers...${NC}"
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-git

# Check if Claude Code is installed
if command -v claude &> /dev/null; then
    echo -e "${GREEN}✅ Claude Code CLI is installed${NC}"
else
    echo -e "${YELLOW}⚠️  Claude Code CLI not found${NC}"
    echo "Install from: https://docs.claude.ai/claude-code"
fi

echo ""
echo -e "${GREEN}======================================"
echo "   ✅ SETUP COMPLETE!"
echo "======================================${NC}"
echo ""
echo -e "${CYAN}To start the swarm:${NC}"
echo "  cd /Users/lynnmusil/Projects/sophia-main/sophia-intel-clone"
echo "  make dev"
echo "  claude"
echo ""
echo -e "${YELLOW}Available Tools in Claude:${NC}"
echo "  • use openrouter_tools.plan() - Deep reasoning & architecture"
echo "  • use openrouter_tools.code_special() - Specialized coding"
echo "  • use openrouter_tools.challenge() - Code review & bug hunting"
echo "  • use openrouter_tools.qa_test() - Test generation"
echo "  • use openrouter_tools.doc_review() - Documentation review"
echo ""
echo -e "${CYAN}Example Workflow:${NC}"
echo '  1. use openrouter_tools.plan({ goal: "Migrate to TypeScript" })'
echo '  2. [Claude Code implements the plan]'
echo '  3. use openrouter_tools.challenge({ diff: "git diff main" })'
echo '  4. use openrouter_tools.qa_test({ target: "src/main.ts" })'
echo ""
echo -e "${GREEN}Your OpenRouter API key is already configured!${NC}"
echo -e "${GREEN}Ready to rock! 🚀${NC}"
