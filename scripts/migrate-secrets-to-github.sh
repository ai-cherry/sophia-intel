#!/bin/bash
# Migrate all secrets from .env to GitHub Secrets
# This script extracts secrets and provides commands to set them

echo "🔐 Sophia AIOS Secret Migration Tool"
echo "====================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed or not in PATH"
    echo "Please install: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Please run: gh auth login"
    exit 1
fi

echo "📋 Extracting secrets from .env..."
echo ""

# Create a secure temp file for commands
COMMANDS_FILE="secret_commands_$(date +%s).sh"
echo "#!/bin/bash" > $COMMANDS_FILE
echo "# GitHub Secrets Upload Commands" >> $COMMANDS_FILE
echo "# Generated: $(date)" >> $COMMANDS_FILE
echo "" >> $COMMANDS_FILE

# Parse .env file and generate commands
if [ -f ".env" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]] && [[ -n "$value" ]]; then
            # Check if it's a secret (contains KEY, TOKEN, SECRET, PASSWORD)
            if [[ "$key" =~ (KEY|TOKEN|SECRET|PASSWORD|PAT|_ID) ]]; then
                # Escape special characters in value
                escaped_value=$(echo "$value" | sed 's/"/\\"/g')
                
                # Generate the gh secret set command
                echo "gh secret set $key --body \"$escaped_value\"" >> $COMMANDS_FILE
                
                # Show progress (without revealing the secret)
                echo "  ✓ Found: $key (${#value} characters)"
            fi
        fi
    done < .env
    
    echo ""
    echo "📊 Summary:"
    echo "-----------"
    SECRET_COUNT=$(grep -c "gh secret set" $COMMANDS_FILE)
    echo "  Total secrets found: $SECRET_COUNT"
    echo ""
    echo "📝 Commands saved to: $COMMANDS_FILE"
    echo ""
    echo "🚀 To upload all secrets to GitHub, run:"
    echo "   chmod +x $COMMANDS_FILE"
    echo "   ./$COMMANDS_FILE"
    echo ""
    echo "⚠️  After uploading, remember to:"
    echo "   1. Remove .env from repository: git rm --cached .env"
    echo "   2. Add .env to .gitignore"
    echo "   3. Delete the commands file: rm $COMMANDS_FILE"
    
else
    echo "❌ No .env file found"
    exit 1
fi

# Create .env.example for documentation
echo ""
echo "📄 Creating .env.example for documentation..."

cat > .env.example << 'EOF'
# Sophia AIOS Environment Variables Template
# Copy this to .env and fill in your values
# NEVER commit the actual .env file!

# Infrastructure
LAMBDA_API_KEY=
LAMBDA_CLOUD_API_KEY=
PULUMI_ACCESS_TOKEN=

# AI/LLM Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=

# Databases
NEON_API_TOKEN=
QDRANT_API_KEY=
REDIS_URL=

# Add other secrets as needed...
EOF

echo "✓ Created .env.example"
echo ""
echo "✅ Migration preparation complete!"
