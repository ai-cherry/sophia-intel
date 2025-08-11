#!/bin/bash
# 📊 REPOSITORY STATUS CHECK & PUSH SCRIPT
# This script checks all sophia-related repos and pushes changes

set -e

echo "============================================"
echo "📊 SOPHIA REPOSITORIES STATUS CHECK"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check repo status
check_repo() {
    local repo_path=$1
    local repo_name=$(basename "$repo_path")
    
    echo -e "${BLUE}📁 Repository: $repo_name${NC}"
    echo "   Path: $repo_path"
    
    if [ -d "$repo_path/.git" ]; then
        cd "$repo_path"
        
        # Get current branch
        current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        echo "   Branch: $current_branch"
        
        # Check for uncommitted changes
        if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
            echo -e "   ${YELLOW}⚠️  Has uncommitted changes${NC}"
            git status --short
            
            # Offer to commit and push
            read -p "   Commit and push changes? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git add .
                git commit -m "📦 Auto-commit: $(date '+%Y-%m-%d %H:%M:%S')"
                
                # Check if remote exists
                if git remote -v | grep -q origin; then
                    git push origin "$current_branch" 2>/dev/null || {
                        echo -e "   ${YELLOW}Creating upstream branch...${NC}"
                        git push -u origin "$current_branch"
                    }
                    echo -e "   ${GREEN}✅ Pushed to GitHub${NC}"
                else
                    echo -e "   ${RED}❌ No remote configured${NC}"
                fi
            fi
        else
            echo -e "   ${GREEN}✅ Clean (no changes)${NC}"
            
            # Check if up to date with remote
            if git remote -v | grep -q origin; then
                git fetch origin 2>/dev/null
                LOCAL=$(git rev-parse HEAD)
                REMOTE=$(git rev-parse origin/"$current_branch" 2>/dev/null || echo "none")
                
                if [ "$LOCAL" = "$REMOTE" ]; then
                    echo -e "   ${GREEN}✅ Up to date with GitHub${NC}"
                elif [ "$REMOTE" = "none" ]; then
                    echo -e "   ${YELLOW}⚠️  Branch not on GitHub yet${NC}"
                    read -p "   Push to GitHub? (y/n): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        git push -u origin "$current_branch"
                        echo -e "   ${GREEN}✅ Pushed to GitHub${NC}"
                    fi
                else
                    echo -e "   ${YELLOW}⚠️  Needs sync with GitHub${NC}"
                fi
            fi
        fi
        
        # Count files
        file_count=$(find . -type f -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" 2>/dev/null | wc -l)
        echo "   Files: $file_count relevant files"
        
    else
        echo -e "   ${RED}❌ Not a git repository${NC}"
        
        # Check if it has content worth tracking
        if [ -d "$repo_path" ]; then
            file_count=$(find "$repo_path" -type f 2>/dev/null | wc -l)
            if [ "$file_count" -gt 0 ]; then
                echo "   Contains $file_count files"
                read -p "   Initialize as git repo? (y/n): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    cd "$repo_path"
                    git init
                    git add .
                    git commit -m "🎉 Initial commit"
                    echo -e "   ${GREEN}✅ Git initialized${NC}"
                fi
            fi
        fi
    fi
    echo ""
}

# Check each sophia-related directory
for dir in /Users/lynnmusil/Projects/sophia*; do
    if [ -d "$dir" ]; then
        check_repo "$dir"
    fi
done

# Special check for mcp-context-server
if [ -d "/Users/lynnmusil/Projects/mcp-context-server" ]; then
    echo -e "${BLUE}📁 Related: mcp-context-server${NC}"
    cd /Users/lynnmusil/Projects/mcp-context-server
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        echo -e "   ${YELLOW}Has changes${NC}"
    else
        echo -e "   ${GREEN}Clean${NC}"
    fi
    echo ""
fi

echo "============================================"
echo "📊 SUMMARY"
echo "============================================"
