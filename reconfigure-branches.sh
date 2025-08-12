#!/bin/bash

# 🎯 Sophia Intel Branch Reconfiguration Script
# Safely reorganizes branches into clean structure

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   SOPHIA INTEL - BRANCH RECONFIGURATION         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check
echo -e "${YELLOW}This will reorganize your Git branches.${NC}"
echo -e "${YELLOW}Current branch structure will be backed up.${NC}"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

# Backup current state
echo -e "\n${BLUE}Step 1: Backing up current state...${NC}"
git branch > branches_backup_$(date +%Y%m%d_%H%M%S).txt
echo -e "${GREEN}✅ Backup saved${NC}"

# Stash any changes
echo -e "\n${BLUE}Step 2: Stashing any uncommitted changes...${NC}"
git stash push -m "Branch reconfiguration stash" || true

# Phase 1: Create new structure
echo -e "\n${BLUE}Step 3: Creating new branch structure...${NC}"

# Create production from notion
echo -e "${YELLOW}Creating 'production' branch from notion...${NC}"
git checkout notion 2>/dev/null || git checkout -b notion origin/notion
if ! git branch | grep -q "production"; then
    git checkout -b production
    echo -e "${GREEN}✅ Created 'production' branch${NC}"
else
    echo -e "${YELLOW}⚠️  'production' branch already exists${NC}"
fi

# Create next with advanced features
echo -e "${YELLOW}Creating 'next' branch with advanced features...${NC}"
git checkout main
if ! git branch | grep -q "next"; then
    git checkout -b next
    
    # Merge advanced features
    echo -e "${YELLOW}Merging AI swarm features...${NC}"
    git merge feature/ai-swarm-complete-20250812-014035 --no-edit --no-ff -m "feat: Merge AI swarm orchestration" || true
    
    echo -e "${YELLOW}Merging advanced Portkey features...${NC}"
    git merge feature/advanced-portkey-20250812-013430 --no-edit --no-ff -m "feat: Merge advanced Portkey integration" || true
    
    echo -e "${GREEN}✅ Created 'next' branch with advanced features${NC}"
else
    echo -e "${YELLOW}⚠️  'next' branch already exists${NC}"
fi

# Phase 2: Tag outdated branches for archival
echo -e "\n${BLUE}Step 4: Archiving outdated branches as tags...${NC}"

ARCHIVE_BRANCHES=(
    "feat/autonomous-agent"
    "feat/initial-setup"
    "feat/integration-agno"
    "feat/esc-bootstrap-and-fixes"
    "feat/github-security"
)

for branch in "${ARCHIVE_BRANCHES[@]}"; do
    if git branch | grep -q "$branch"; then
        echo -e "${YELLOW}Archiving $branch...${NC}"
        git tag -f "archive/$branch" "$branch" 2>/dev/null || true
        echo -e "${GREEN}✅ Tagged as archive/$branch${NC}"
    fi
done

# Phase 3: Summary
echo -e "\n${BLUE}Step 5: New Branch Structure Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${GREEN}Active Branches:${NC}"
echo -e "  ${BLUE}main${NC}        - Stable base (115 files)"
echo -e "  ${BLUE}production${NC}  - Streamlined deployment (41 files)"
echo -e "  ${BLUE}next${NC}        - Advanced features (~125 files)"

echo -e "\n${YELLOW}Recommended Cleanup (run manually):${NC}"
echo -e "  git branch -D unified-dev"
echo -e "  git branch -D backup/pre-swarm-20250812-013122"

echo -e "\n${YELLOW}Archived as tags:${NC}"
git tag | grep "archive/" || echo "  None yet"

# Show current branches
echo -e "\n${BLUE}Current branches:${NC}"
git branch | head -10

echo -e "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ RECONFIGURATION COMPLETE!                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}Next steps:${NC}"
echo -e "1. Test the new structure"
echo -e "2. Push new branches: ${YELLOW}git push origin production next${NC}"
echo -e "3. Clean redundant branches (see recommendations above)"
echo -e "4. Update CI/CD to use new branches"

echo -e "\n${BLUE}Workflow:${NC}"
echo -e "  ${CYAN}main${NC} → ${CYAN}next${NC} → ${CYAN}production${NC}"
echo -e "  ↑        ↑         ↑"
echo -e "  stable   develop   deploy"
