#!/bin/bash
# 🚀 QUICK CONSOLIDATION AND PUSH
# This consolidates everything into sophia-intel and pushes

set -e

echo "========================================="
echo "🚀 SOPHIA INTEL - QUICK PUSH TO GITHUB"
echo "========================================="

# Create sophia-intel if it doesn't exist
if [ ! -d ~/Projects/sophia-intel ]; then
    echo "Creating sophia-intel repository..."
    mkdir -p ~/Projects/sophia-intel
    cd ~/Projects/sophia-intel
    git init
    
    # Copy all relevant files
    echo "Copying files from other directories..."
    
    # From sophia-mcp-hybrid
    if [ -d ~/Projects/sophia-mcp-hybrid ]; then
        cp -r ~/Projects/sophia-mcp-hybrid/* .
    fi
    
    # From sophia-intel-deployment
    if [ -d ~/Projects/sophia-intel-deployment ]; then
        mkdir -p deployment
        cp ~/Projects/sophia-intel-deployment/*.sh deployment/
        cp ~/Projects/sophia-intel-deployment/*.py deployment/
        cp ~/Projects/sophia-intel-deployment/*.md deployment/
    fi
    
    # From sophia-intel-mcp-sync
    if [ -d ~/Projects/sophia-intel-mcp-sync ]; then
        mkdir -p services
        cp -r ~/Projects/sophia-intel-mcp-sync/* services/
    fi
    
    # Create README if doesn't exist
    if [ ! -f README.md ]; then
        cat > README.md << 'EOF'
# 🚀 Sophia Intel

AI-powered development ecosystem with intelligent knowledge management.

## Features
- 🧠 30-40% deduplication of content
- ☁️ Cloud-native architecture  
- 🌉 Hybrid MCP bridge system
- 📊 Executive dashboard
- 🤖 AI agents

## Quick Start
```bash
gh codespace create --repo ai-cherry/sophia-intel
```

## Architecture
- Local MCP Bridge (port 8000)
- Cloud Server (port 8080)
- Notion sync
- Lambda Labs GPU compute
EOF
    fi
    
    # Add all files
    git add .
    git commit -m "🚀 Consolidated Sophia Intel system with all components"
    
    # Create on GitHub if doesn't exist
    if ! gh repo view ai-cherry/sophia-intel &>/dev/null; then
        echo "Creating GitHub repository..."
        gh repo create ai-cherry/sophia-intel --public --description "AI-powered development ecosystem" --source=.
    fi
    
    # Set remote if needed
    if ! git remote | grep -q origin; then
        git remote add origin https://github.com/ai-cherry/sophia-intel.git
    fi
    
    # Push to main
    git push -u origin main || git push origin main --force
    
    echo "✅ Pushed to main branch"
    
    # Create feature branch
    git checkout -b feat/ceo-command-center
    git push -u origin feat/ceo-command-center
    
    echo "✅ Created and pushed feature branch"
    
else
    echo "sophia-intel already exists, updating..."
    cd ~/Projects/sophia-intel
    
    # Commit any changes
    if [ -n "$(git status --porcelain)" ]; then
        git add .
        git commit -m "📦 Update: $(date '+%Y-%m-%d %H:%M')"
    fi
    
    # Push current branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    git push origin "$current_branch"
fi

echo ""
echo "========================================="
echo "✅ COMPLETE!"
echo "========================================="
echo ""
echo "Repository: https://github.com/ai-cherry/sophia-intel"
echo "Local: ~/Projects/sophia-intel"
echo ""
echo "Next steps:"
echo "1. Create PR: gh pr create"
echo "2. Open Codespace: gh codespace create --repo ai-cherry/sophia-intel"
echo "3. Open in browser: gh repo view --web"
