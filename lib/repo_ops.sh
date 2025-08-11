#!/bin/bash
# lib/repo_ops.sh - Repository operations for Sophia Intel CLI
# Version: 3.0.0

# Repository configuration
readonly REPO_NAME="ai-cherry/sophia-intel"
readonly REPO_URL="https://github.com/$REPO_NAME"

# Repository information functions
get_repo_info() {
    local branch="${1:-$SOPHIA_BRANCH}"
    
    if dry_run_message "Would fetch repository information for branch: $branch"; then
        return 0
    fi
    
    info "Fetching repository information for branch: $branch"
    
    # Use GitHub API if token is available
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        local api_response
        api_response=$(curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME")
        
        if [ $? -eq 0 ]; then
            echo "$api_response" | jq -r '
                "Repository: " + .full_name + "\n" +
                "Description: " + (.description // "No description") + "\n" +
                "Stars: " + (.stargazers_count | tostring) + "\n" +
                "Forks: " + (.forks_count | tostring) + "\n" +
                "Issues: " + (.open_issues_count | tostring) + "\n" +
                "Last updated: " + .updated_at
            ' 2>/dev/null || echo "Repository information retrieved"
        else
            warning "Failed to fetch repository information via API"
        fi
    else
        info "Repository: $REPO_NAME"
        info "Branch: $branch"
        info "URL: $REPO_URL"
    fi
}

# Branch operations
list_branches() {
    if dry_run_message "Would list all repository branches"; then
        return 0
    fi
    
    info "Fetching repository branches..."
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/branches" | \
            jq -r '.[] | "• " + .name + (if .protected then " (protected)" else "" end)' 2>/dev/null || \
            echo "• notion\n• main\n• development"
    else
        echo "Available branches:"
        echo "• notion"
        echo "• main" 
        echo "• development"
        warning "Set GitHub token for live branch information"
    fi
}

switch_branch() {
    local new_branch="$1"
    
    if [ -z "$new_branch" ]; then
        error "Branch name required"
        return 1
    fi
    
    if dry_run_message "Would switch to branch: $new_branch"; then
        return 0
    fi
    
    # Validate branch name
    case "$new_branch" in
        notion|main|development)
            export SOPHIA_BRANCH="$new_branch"
            save_config
            success "Switched to branch: $new_branch"
            ;;
        *)
            error "Invalid branch: $new_branch"
            echo "Valid branches: notion, main, development"
            return 1
            ;;
    esac
}

# Commit operations
get_recent_commits() {
    local branch="${1:-$SOPHIA_BRANCH}"
    local limit="${2:-10}"
    
    if dry_run_message "Would fetch $limit recent commits from branch: $branch"; then
        return 0
    fi
    
    info "Fetching recent commits from branch: $branch"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/commits?sha=$branch&per_page=$limit" | \
            jq -r '.[] | 
                "• " + (.sha[:7]) + " " + 
                (.commit.message | split("\n")[0] | .[0:60]) + 
                " (" + (.commit.author.name) + ", " + 
                (.commit.author.date | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d")) + ")"
            ' 2>/dev/null || echo "Recent commits information not available"
    else
        warning "Set GitHub token to view recent commits"
        echo "Recent commits: (GitHub token required for live data)"
    fi
}

# File operations
list_files() {
    local branch="${1:-$SOPHIA_BRANCH}"
    local path="${2:-.}"
    
    if dry_run_message "Would list files in $path on branch: $branch"; then
        return 0
    fi
    
    info "Listing files in $path on branch: $branch"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        local encoded_path
        encoded_path=$(echo "$path" | sed 's/ /%20/g')
        
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/contents/$encoded_path?ref=$branch" | \
            jq -r '.[] | 
                (if .type == "dir" then "📁 " else "📄 " end) + 
                .name + 
                (if .type == "file" then " (" + (.size | tostring) + " bytes)" else "" end)
            ' 2>/dev/null || echo "File listing not available"
    else
        warning "Set GitHub token to browse repository files"
        echo "Repository files: (GitHub token required for live data)"
    fi
}

download_file() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local output_path="${3:-$(basename "$file_path")}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    if dry_run_message "Would download $file_path from branch $branch to $output_path"; then
        return 0
    fi
    
    info "Downloading $file_path from branch: $branch"
    
    local download_url="https://raw.githubusercontent.com/$REPO_NAME/$branch/$file_path"
    
    if curl -s -f "$download_url" -o "$output_path"; then
        success "Downloaded: $output_path"
    else
        error "Failed to download: $file_path"
        return 1
    fi
}

# Search operations
search_code() {
    local query="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    
    if [ -z "$query" ]; then
        error "Search query required"
        return 1
    fi
    
    if dry_run_message "Would search for '$query' in branch: $branch"; then
        return 0
    fi
    
    info "Searching for: $query"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        local search_query="$query+repo:$REPO_NAME"
        
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/search/code?q=$search_query" | \
            jq -r '.items[] | 
                "📄 " + .name + " (in " + .path + ")\n" +
                "   " + (.html_url | split("/blob/")[1] // "")
            ' 2>/dev/null || echo "Search results not available"
    else
        warning "Set GitHub token to search repository code"
        echo "Code search: (GitHub token required)"
    fi
}

# Issue operations
list_issues() {
    local state="${1:-open}"
    local limit="${2:-10}"
    
    if dry_run_message "Would list $limit $state issues"; then
        return 0
    fi
    
    info "Fetching $state issues..."
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/issues?state=$state&per_page=$limit" | \
            jq -r '.[] | 
                "• #" + (.number | tostring) + " " + 
                .title + 
                " (" + .user.login + ", " + 
                (.created_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d")) + ")"
            ' 2>/dev/null || echo "Issues information not available"
    else
        warning "Set GitHub token to view repository issues"
        echo "Repository issues: (GitHub token required)"
    fi
}

# Pull request operations
list_pull_requests() {
    local state="${1:-open}"
    local limit="${2:-10}"
    
    if dry_run_message "Would list $limit $state pull requests"; then
        return 0
    fi
    
    info "Fetching $state pull requests..."
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/pulls?state=$state&per_page=$limit" | \
            jq -r '.[] | 
                "• #" + (.number | tostring) + " " + 
                .title + 
                " (" + .user.login + " → " + .base.ref + ", " + 
                (.created_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d")) + ")"
            ' 2>/dev/null || echo "Pull requests information not available"
    else
        warning "Set GitHub token to view pull requests"
        echo "Pull requests: (GitHub token required)"
    fi
}

# Repository statistics
get_repo_stats() {
    local branch="${1:-$SOPHIA_BRANCH}"
    
    if dry_run_message "Would fetch repository statistics for branch: $branch"; then
        return 0
    fi
    
    info "Fetching repository statistics..."
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        # Get repository info
        local repo_info
        repo_info=$(curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME")
        
        # Get contributors
        local contributors
        contributors=$(curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/contributors" | \
            jq -r 'length' 2>/dev/null || echo "0")
        
        # Get languages
        local languages
        languages=$(curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/languages" | \
            jq -r 'keys | join(", ")' 2>/dev/null || echo "Unknown")
        
        echo "Repository Statistics:"
        echo "$repo_info" | jq -r '
            "• Size: " + (.size | tostring) + " KB\n" +
            "• Stars: " + (.stargazers_count | tostring) + "\n" +
            "• Forks: " + (.forks_count | tostring) + "\n" +
            "• Watchers: " + (.watchers_count | tostring) + "\n" +
            "• Open Issues: " + (.open_issues_count | tostring) + "\n" +
            "• Default Branch: " + .default_branch + "\n" +
            "• Created: " + (.created_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d")) + "\n" +
            "• Last Updated: " + (.updated_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d"))
        ' 2>/dev/null
        
        echo "• Contributors: $contributors"
        echo "• Languages: $languages"
    else
        warning "Set GitHub token to view detailed repository statistics"
        echo "Repository statistics: (GitHub token required)"
    fi
}

# Branch comparison
compare_branches() {
    local base_branch="${1:-main}"
    local head_branch="${2:-$SOPHIA_BRANCH}"
    
    if dry_run_message "Would compare $base_branch...$head_branch"; then
        return 0
    fi
    
    info "Comparing $base_branch...$head_branch"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/compare/$base_branch...$head_branch" | \
            jq -r '
                "Comparison: " + .base_commit.sha[:7] + "..." + .head_commit.sha[:7] + "\n" +
                "Status: " + .status + "\n" +
                "Ahead by: " + (.ahead_by | tostring) + " commits\n" +
                "Behind by: " + (.behind_by | tostring) + " commits\n" +
                "Files changed: " + (.files | length | tostring)
            ' 2>/dev/null || echo "Branch comparison not available"
    else
        warning "Set GitHub token to compare branches"
        echo "Branch comparison: (GitHub token required)"
    fi
}

