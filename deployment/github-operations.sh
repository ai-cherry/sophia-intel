#!/bin/bash
# 🚀 SOPHIA INTEL - GitHub Operations Script
# Uses GitHub CLI (which IS properly authenticated on your system)

set -e

GITHUB_ORG="ai-cherry"
PROJECT_NAME="sophia-intel"
BRANCH_NAME="feat/ceo-command-center"

echo "🔧 Using GitHub CLI for all operations (avoiding MCP issues)"

# Function to execute with status
execute_command() {
    local command="$1"
    local description="$2"
    
    echo -n "⏳ $description... "
    if eval "$command" > /tmp/gh_output.txt 2>&1; then
        echo "✅"
        return 0
    else
        echo "❌"
        echo "   Error: $(cat /tmp/gh_output.txt)"
        return 1
    fi
}

# 1. Check if repo exists
echo ""
echo "📦 Repository Management"
echo "------------------------"

if gh repo view "$GITHUB_ORG/$PROJECT_NAME" &>/dev/null; then
    echo "✅ Repository exists: $GITHUB_ORG/$PROJECT_NAME"
    
    # Clone if not local
    if [ ! -d "$HOME/Projects/$PROJECT_NAME" ]; then
        execute_command "gh repo clone $GITHUB_ORG/$PROJECT_NAME $HOME/Projects/$PROJECT_NAME" "Cloning repository"
    fi
else
    echo "📝 Repository doesn't exist. Creating..."
    execute_command "gh repo create $GITHUB_ORG/$PROJECT_NAME --public --description 'AI-powered development ecosystem with intelligent knowledge management'" "Creating repository"
fi

cd "$HOME/Projects/$PROJECT_NAME" 2>/dev/null || {
    mkdir -p "$HOME/Projects/$PROJECT_NAME"
    cd "$HOME/Projects/$PROJECT_NAME"
    git init
    git remote add origin "https://github.com/$GITHUB_ORG/$PROJECT_NAME.git"
}

# 2. Create feature branch
echo ""
echo "🌿 Branch Management"
echo "--------------------"

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    echo "✅ Branch exists: $BRANCH_NAME"
    git checkout "$BRANCH_NAME"
else
    execute_command "git checkout -b $BRANCH_NAME" "Creating feature branch"
fi

# 3. Set GitHub Secrets
echo ""
echo "🔐 GitHub Secrets"
echo "-----------------"

set_secret() {
    local name="$1"
    local value="$2"
    
    if [ -n "$value" ]; then
        echo "$value" | gh secret set "$name" --repo="$GITHUB_ORG/$PROJECT_NAME" 2>/dev/null && \
            echo "✅ $name configured" || \
            echo "⚠️  $name already exists or couldn't be set"
    else
        echo "⏭️  Skipping $name (no value provided)"
    fi
}

# Set all known secrets
set_secret "NOTION_API_KEY" "${NOTION_API_KEY}"
set_secret "NOTION_WORKSPACE_ID" "${NOTION_WORKSPACE_ID}"
set_secret "LAMBDA_CLOUD_API_KEY" "$NOTION_API_KEY_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
set_secret "GITHUB_PAT" "${GITHUB_PAT}"

# 4. Create/Update Codespace
echo ""
echo "☁️  Codespaces"
echo "-------------"

# Check if codespace exists
if gh codespace list --repo "$GITHUB_ORG/$PROJECT_NAME" --json name | grep -q "$PROJECT_NAME"; then
    echo "✅ Codespace exists"
    echo "   To open: gh codespace code --repo $GITHUB_ORG/$PROJECT_NAME"
else
    echo "📝 Ready to create Codespace"
    echo "   Run: gh codespace create --repo $GITHUB_ORG/$PROJECT_NAME"
fi

# 5. Show current status
echo ""
echo "📊 Current Status"
echo "-----------------"
echo "Repository: https://github.com/$GITHUB_ORG/$PROJECT_NAME"
echo "Branch: $BRANCH_NAME"
echo "Local: $HOME/Projects/$PROJECT_NAME"

# 6. Create PR if changes exist
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo "📝 You have uncommitted changes"
    echo "   To commit: git add . && git commit -m 'Your message'"
    echo "   To push: git push -u origin $BRANCH_NAME"
    echo "   To create PR: gh pr create --title 'CEO Command Center' --body 'Phase 1 implementation'"
fi

echo ""
echo "✅ GitHub operations complete!"
echo ""
echo "Next steps:"
echo "1. cd $HOME/Projects/$PROJECT_NAME"
echo "2. Create your files (I'll generate them next)"
echo "3. git add . && git commit -m '🚀 Initial structure'"
echo "4. git push -u origin $BRANCH_NAME"
echo "5. gh pr create"
echo "6. gh codespace create --repo $GITHUB_ORG/$PROJECT_NAME"
