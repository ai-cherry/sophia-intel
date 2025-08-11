#!/bin/bash
# 🚀 SOPHIA INTEL - ONE COMMAND DEPLOYMENT
# This script sets up EVERYTHING from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="sophia-intel"
GITHUB_ORG="ai-cherry"
GITHUB_USERNAME="${GITHUB_USERNAME:-scoobyjava}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 SOPHIA INTEL DEPLOYMENT SYSTEM${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 0: Prerequisites Check
echo -e "\n${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists git; then
    print_error "Git not installed"
    exit 1
fi
print_status "Git installed"

if ! command_exists python3; then
    print_error "Python3 not installed"
    exit 1
fi
print_status "Python3 installed"

if ! command_exists gh; then
    print_warning "GitHub CLI not installed. Installing..."
    brew install gh
fi
print_status "GitHub CLI ready"

# Step 1: Authenticate GitHub
echo -e "\n${BLUE}🔐 Setting up GitHub authentication...${NC}"

# Check if already authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "Please authenticate with GitHub:"
    gh auth login
fi
print_status "GitHub authenticated"

# Step 2: Create or Clone Repository
echo -e "\n${BLUE}📦 Setting up repository...${NC}"

REPO_PATH="$HOME/Projects/$PROJECT_NAME"

if [ -d "$REPO_PATH" ]; then
    print_warning "Repository already exists at $REPO_PATH"
    cd "$REPO_PATH"
    git pull origin main 2>/dev/null || true
else
    # Check if repo exists on GitHub
    if gh repo view "$GITHUB_ORG/$PROJECT_NAME" >/dev/null 2>&1; then
        print_status "Repository exists on GitHub, cloning..."
        gh repo clone "$GITHUB_ORG/$PROJECT_NAME" "$REPO_PATH"
    else
        print_status "Creating new repository..."
        mkdir -p "$REPO_PATH"
        cd "$REPO_PATH"
        git init
        gh repo create "$GITHUB_ORG/$PROJECT_NAME" --public --source=. --remote=origin
    fi
    cd "$REPO_PATH"
fi

# Step 3: Create Project Structure
echo -e "\n${BLUE}🏗️ Creating project structure...${NC}"

# Create all directories
directories=(
    ".devcontainer"
    ".github/workflows"
    ".github/environments/development"
    ".github/environments/production"
    "agents"
    "services"
    "mcp_servers"
    "integrations"
    "tools"
    "dashboards/ui/project-dashboard"
    "config"
    "tests/unit"
    "tests/golden"
    "tests/e2e"
    ".prompts/templates"
    "docs/sop"
    "docs/migration"
    "reports"
    "planning"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done
print_status "Directory structure created"

# Step 4: Copy deployment files
echo -e "\n${BLUE}📄 Creating core files...${NC}"

# Create Python requirements
cat > requirements.txt << 'EOF'
# Core
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# AI/ML
openai==1.6.0
anthropic==0.8.0
langchain==0.1.0
sentence-transformers==2.2.2
numpy==1.24.0
pandas==2.1.0

# Vector DB
qdrant-client==1.7.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0

# Integrations
notion-client==2.2.0
PyGithub==2.1.1
slack-sdk==3.23.0
aiohttp==3.9.1

# Tools
python-dotenv==1.0.0
click==8.1.7
rich==13.7.0
httpx==0.25.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Dev tools
black==23.12.0
ruff==0.1.8
mypy==1.7.1
EOF

print_status "Requirements file created"

# Step 5: Set up GitHub Secrets
echo -e "\n${BLUE}🔑 Setting up GitHub Secrets...${NC}"

# Check if secrets exist, if not prompt for them
setup_secret() {
    local $NOTION_API_KEY=$1
    local $NOTION_API_KEY=$2
    local default_value=$3
    
    if ! gh secret list | grep -q "$$NOTION_API_KEY"; then
        if [ -n "$default_value" ]; then
            echo "$default_value" | gh secret set "$$NOTION_API_KEY"
            print_status "$$NOTION_API_KEY set with provided value"
        else
            print_warning "$$NOTION_API_KEY not set. Add it with:"
            echo "  gh secret set $$NOTION_API_KEY"
        fi
    else
        print_status "$$NOTION_API_KEY already exists"
    fi
}

# Set secrets with known values
setup_secret "GITHUB_TOKEN" "GitHub Personal Access Token" ""
setup_secret "NOTION_API_KEY" "Notion API Key" "${NOTION_API_KEY}"
setup_secret "LAMBDA_CLOUD_API_KEY" "Lambda Labs API Key" "$NOTION_API_KEY_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
setup_secret "NOTION_WORKSPACE_ID" "Notion Workspace ID" "${NOTION_WORKSPACE_ID}"

# Step 6: Create GitHub Actions Workflow
echo -e "\n${BLUE}⚙️ Setting up GitHub Actions...${NC}"

cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install ruff black pytest
    
    - name: Run linting
      run: |
        ruff check .
        black --check .
    
    - name: Run tests
      run: pytest tests/
    
    - name: Check duplication
      run: |
        npx jscpd . --reporters json --output reports/
EOF

print_status "GitHub Actions workflow created"

# Step 7: Create Codespaces Configuration
echo -e "\n${BLUE}🌐 Setting up Codespaces...${NC}"

cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Sophia Intel",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:1": {}
  },
  "postCreateCommand": "pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "github.copilot",
        "ms-python.vscode-pylance"
      ]
    }
  },
  "forwardPorts": [8000, 3000, 5432]
}
EOF

print_status "Codespaces configuration created"

# Step 8: Commit and Push
echo -e "\n${BLUE}📤 Pushing to GitHub...${NC}"

git add .
git commit -m "🚀 Initial Sophia Intel setup via automated deployment" || true
git push -u origin main || git push

print_status "Code pushed to GitHub"

# Step 9: Create Codespace
echo -e "\n${BLUE}☁️ Creating Codespace...${NC}"

if gh codespace list | grep -q "$PROJECT_NAME"; then
    print_warning "Codespace already exists"
else
    gh codespace create --repo "$GITHUB_ORG/$PROJECT_NAME" --branch main --machine basicLinux32gb
    print_status "Codespace created"
fi

# Step 10: Final Status
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SOPHIA INTEL DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}📊 Summary:${NC}"
echo "  Repository: https://github.com/$GITHUB_ORG/$PROJECT_NAME"
echo "  Local Path: $REPO_PATH"
echo "  Codespace: Ready to launch"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo "  1. Open Codespace:"
echo "     gh codespace code -R $GITHUB_ORG/$PROJECT_NAME"
echo ""
echo "  2. Or open in browser:"
echo "     gh codespace list"
echo "     gh codespace code [codespace-name]"
echo ""
echo "  3. Set any missing secrets:"
echo "     gh secret set OPENAI_API_KEY"
echo "     gh secret set ANTHROPIC_API_KEY"

echo -e "\n${GREEN}🎉 Your AI development environment is ready!${NC}"
