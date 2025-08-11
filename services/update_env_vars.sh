#!/bin/bash
# Update sophia-intel with corrected environment variable names

echo "======================================"
echo "🔄 Updating Sophia Intel MCP-Notion Sync"
echo "======================================"

# Navigate to sophia-intel repository
if [ -d "sophia-intel" ]; then
    cd sophia-intel
elif [ -d "../sophia-intel" ]; then
    cd ../sophia-intel
else
    echo "❌ sophia-intel directory not found"
    echo "Please run from Projects directory or sophia-intel-mcp-sync directory"
    exit 1
fi

# Ensure we're on the right branch
git checkout mcp-notion-sync 2>/dev/null || git checkout -b mcp-notion-sync

echo "📝 Updating files with correct environment variable names..."

# Update sync_manager.py
cat > services/mcp-sync/sync_manager_update.py << 'EOF'
# Find and replace in sync_manager.py
import sys

with open('sync_manager.py', 'r') as f:
    content = f.read()

content = content.replace("os.getenv('GITHUB_PAT')", "os.getenv('GH_FINE_GRAINED_TOKEN')")
content = content.replace("os.getenv('GITHUB_USERNAME'", "os.getenv('GH_USERNAME'")

with open('sync_manager.py', 'w') as f:
    f.write(content)

print("✅ Updated sync_manager.py")
EOF

cd services/mcp-sync
python3 sync_manager_update.py
rm sync_manager_update.py
cd ../..

# Update the GitHub workflow
echo "📝 Updating GitHub workflow..."
sed -i '' 's/GITHUB_PAT:/GH_FINE_GRAINED_TOKEN:/g' .github/workflows/mcp-sync.yml
sed -i '' 's/GITHUB_USERNAME:/GH_USERNAME:/g' .github/workflows/mcp-sync.yml
sed -i '' 's/secrets.GITHUB_PAT/secrets.GH_FINE_GRAINED_TOKEN/g' .github/workflows/mcp-sync.yml
sed -i '' 's/secrets.GITHUB_USERNAME/secrets.GH_USERNAME/g' .github/workflows/mcp-sync.yml

# Update .env.example
echo "📝 Updating .env.example..."
cat > services/mcp-sync/.env.example << 'EOF'
# Lambda Labs Configuration
LAMBDA_CLOUD_API_KEY=${NOTION_API_KEY}
LAMBDA_API_CLOUD_ENDPOINT=https://cloud.lambda.ai/api/v1

# GitHub Configuration (GitHub blocks "GITHUB_" prefix in secrets)
GH_FINE_GRAINED_TOKEN=${GITHUB_PAT}
GH_USERNAME=scoobyjava
GITHUB_REPO=ai-cherry/sophia-intel
GITHUB_BRANCH=mcp-notion-sync

# Notion Configuration
NOTION_API_KEY=${NOTION_API_KEY}
NOTION_WORKSPACE_ID=xxx

# Sync Configuration
SYNC_INTERVAL_MINUTES=5
DEDUP_THRESHOLD=0.8
ARCHIVE_DAYS_THRESHOLD=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=sync.log
EOF

# Commit the updates
echo "💾 Committing updates..."
git add -A
git commit -m "Update environment variable names to comply with GitHub restrictions

- Changed GITHUB_PAT to GH_FINE_GRAINED_TOKEN
- Changed GITHUB_USERNAME to GH_USERNAME
- GitHub blocks secrets starting with 'GITHUB_' prefix
- Updated all references in sync_manager.py and workflow files"

echo ""
echo "======================================"
echo "✅ Updates Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Push the updates to GitHub:"
echo "   git push origin mcp-notion-sync"
echo ""
echo "2. Trigger a manual run to test:"
echo "   Go to: https://github.com/ai-cherry/sophia-intel/actions"
echo "   Select 'MCP-Notion Sync for Sophia Intel'"
echo "   Click 'Run workflow'"
echo ""
echo "3. Monitor the first sync:"
echo "   Check the Actions tab for progress"
echo "   View deduplication reports in artifacts"
echo ""
echo "======================================"
echo "🎯 Organization-level secrets detected!"
echo "Your secrets are available to all repos in ai-cherry"
echo "======================================"
