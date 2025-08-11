#!/bin/bash
# Setup script for sophia-intel MCP-Notion Sync

echo "🚀 Setting up MCP-Notion Sync for sophia-intel"

# Clone the sophia-intel repository
git clone https://github.com/ai-cherry/sophia-intel.git
cd sophia-intel

# Create and checkout the mcp-notion-sync branch
git checkout -b mcp-notion-sync

# Create the services directory structure
mkdir -p services/mcp-sync
mkdir -p .github/workflows

echo "✅ Repository cloned and branch created"
echo "📁 Now copy all files from sophia-intel-mcp-sync/ to sophia-intel/services/mcp-sync/"
echo "Then commit and push:"
echo "  git add ."
echo "  git commit -m 'Add MCP-Notion sync system with Lambda Labs integration'"
echo "  git push -u origin mcp-notion-sync"
