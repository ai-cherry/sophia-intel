#!/bin/bash
# lib/file_ops.sh - File operations for Sophia Intel CLI
# Version: 3.0.0

# File viewing operations
view_file() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local lines="${3:-50}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    if dry_run_message "Would view $file_path from branch $branch (first $lines lines)"; then
        return 0
    fi
    
    info "Viewing $file_path from branch: $branch"
    
    local file_url="https://raw.githubusercontent.com/$REPO_NAME/$branch/$file_path"
    
    if curl -s -f "$file_url" | head -n "$lines"; then
        if [ "$lines" -lt 1000 ]; then
            echo
            info "Showing first $lines lines. Use --full to see complete file."
        fi
    else
        error "Failed to retrieve file: $file_path"
        return 1
    fi
}

# File upload operations (requires GitHub token)
upload_file() {
    local local_path="$1"
    local remote_path="$2"
    local commit_message="$3"
    local branch="${4:-$SOPHIA_BRANCH}"
    
    if [ -z "$local_path" ] || [ -z "$remote_path" ]; then
        error "Usage: upload_file <local_path> <remote_path> [commit_message] [branch]"
        return 1
    fi
    
    if [ ! -f "$local_path" ]; then
        error "Local file not found: $local_path"
        return 1
    fi
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -z "$github_token" ]; then
        error "GitHub token required for file upload"
        return 1
    fi
    
    if dry_run_message "Would upload $local_path to $remote_path on branch $branch"; then
        return 0
    fi
    
    info "Uploading $local_path to $remote_path on branch: $branch"
    
    # Encode file content in base64
    local file_content
    file_content=$(base64 -w 0 "$local_path")
    
    # Get current file SHA if it exists (for updates)
    local current_sha
    current_sha=$(curl -s -H "Authorization: token $github_token" \
        "https://api.github.com/repos/$REPO_NAME/contents/$remote_path?ref=$branch" | \
        jq -r '.sha // empty' 2>/dev/null)
    
    # Prepare JSON payload
    local json_payload
    json_payload=$(jq -n \
        --arg message "${commit_message:-Update $remote_path}" \
        --arg content "$file_content" \
        --arg branch "$branch" \
        --arg sha "$current_sha" \
        '{
            message: $message,
            content: $content,
            branch: $branch
        } + (if $sha != "" then {sha: $sha} else {} end)')
    
    # Upload file
    local response
    response=$(curl -s -X PUT \
        -H "Authorization: token $github_token" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        "https://api.github.com/repos/$REPO_NAME/contents/$remote_path")
    
    if echo "$response" | jq -e '.content.sha' >/dev/null 2>&1; then
        success "File uploaded successfully: $remote_path"
        echo "$response" | jq -r '"Commit SHA: " + .commit.sha'
    else
        error "Failed to upload file"
        echo "$response" | jq -r '.message // "Unknown error"'
        return 1
    fi
}

# File deletion operations
delete_file() {
    local file_path="$1"
    local commit_message="$2"
    local branch="${3:-$SOPHIA_BRANCH}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -z "$github_token" ]; then
        error "GitHub token required for file deletion"
        return 1
    fi
    
    if dry_run_message "Would delete $file_path from branch $branch"; then
        return 0
    fi
    
    # Confirm deletion unless in non-interactive mode
    if [ "${SOPHIA_INTERACTIVE:-true}" = "true" ]; then
        echo -e "${YELLOW}⚠ WARNING: This will permanently delete $file_path${NC}"
        read -p "Are you sure? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            info "File deletion cancelled"
            return 0
        fi
    fi
    
    info "Deleting $file_path from branch: $branch"
    
    # Get current file SHA
    local file_sha
    file_sha=$(curl -s -H "Authorization: token $github_token" \
        "https://api.github.com/repos/$REPO_NAME/contents/$file_path?ref=$branch" | \
        jq -r '.sha // empty' 2>/dev/null)
    
    if [ -z "$file_sha" ]; then
        error "File not found or unable to get file SHA: $file_path"
        return 1
    fi
    
    # Prepare JSON payload
    local json_payload
    json_payload=$(jq -n \
        --arg message "${commit_message:-Delete $file_path}" \
        --arg sha "$file_sha" \
        --arg branch "$branch" \
        '{
            message: $message,
            sha: $sha,
            branch: $branch
        }')
    
    # Delete file
    local response
    response=$(curl -s -X DELETE \
        -H "Authorization: token $github_token" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        "https://api.github.com/repos/$REPO_NAME/contents/$file_path")
    
    if echo "$response" | jq -e '.commit.sha' >/dev/null 2>&1; then
        success "File deleted successfully: $file_path"
        echo "$response" | jq -r '"Commit SHA: " + .commit.sha'
    else
        error "Failed to delete file"
        echo "$response" | jq -r '.message // "Unknown error"'
        return 1
    fi
}

# File search operations
search_files() {
    local pattern="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local file_type="${3:-}"
    
    if [ -z "$pattern" ]; then
        error "Search pattern required"
        return 1
    fi
    
    if dry_run_message "Would search for files matching '$pattern' in branch $branch"; then
        return 0
    fi
    
    info "Searching for files matching: $pattern"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        local search_query="filename:$pattern+repo:$REPO_NAME"
        
        if [ -n "$file_type" ]; then
            search_query="$search_query+extension:$file_type"
        fi
        
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/search/code?q=$search_query" | \
            jq -r '.items[] | 
                "📄 " + .name + "\n" +
                "   Path: " + .path + "\n" +
                "   URL: " + .html_url + "\n"
            ' 2>/dev/null || echo "File search results not available"
    else
        warning "Set GitHub token to search repository files"
        echo "File search: (GitHub token required)"
    fi
}

# File comparison operations
compare_file() {
    local file_path="$1"
    local base_branch="${2:-main}"
    local head_branch="${3:-$SOPHIA_BRANCH}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    if dry_run_message "Would compare $file_path between $base_branch and $head_branch"; then
        return 0
    fi
    
    info "Comparing $file_path between $base_branch and $head_branch"
    
    # Download both versions
    local base_content head_content
    base_content=$(curl -s -f "https://raw.githubusercontent.com/$REPO_NAME/$base_branch/$file_path")
    head_content=$(curl -s -f "https://raw.githubusercontent.com/$REPO_NAME/$head_branch/$file_path")
    
    if [ $? -ne 0 ]; then
        error "Failed to retrieve file from one or both branches"
        return 1
    fi
    
    # Create temporary files for comparison
    local temp_base temp_head
    temp_base=$(mktemp)
    temp_head=$(mktemp)
    
    echo "$base_content" > "$temp_base"
    echo "$head_content" > "$temp_head"
    
    # Show diff
    echo "Differences in $file_path ($base_branch vs $head_branch):"
    echo "=================================================="
    
    if command -v diff >/dev/null 2>&1; then
        diff -u "$temp_base" "$temp_head" | head -50
    else
        echo "diff command not available"
        echo "Base branch ($base_branch) has $(wc -l < "$temp_base") lines"
        echo "Head branch ($head_branch) has $(wc -l < "$temp_head") lines"
    fi
    
    # Cleanup
    rm -f "$temp_base" "$temp_head"
}

# File history operations
get_file_history() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local limit="${3:-10}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    if dry_run_message "Would get history for $file_path in branch $branch"; then
        return 0
    fi
    
    info "Getting history for $file_path in branch: $branch"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/commits?path=$file_path&sha=$branch&per_page=$limit" | \
            jq -r '.[] | 
                "• " + (.sha[:7]) + " " + 
                (.commit.message | split("\n")[0] | .[0:60]) + "\n" +
                "  " + .commit.author.name + " on " + 
                (.commit.author.date | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d %H:%M")) + "\n"
            ' 2>/dev/null || echo "File history not available"
    else
        warning "Set GitHub token to view file history"
        echo "File history: (GitHub token required)"
    fi
}

# Bulk file operations
bulk_download() {
    local pattern="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local output_dir="${3:-.}"
    
    if [ -z "$pattern" ]; then
        error "File pattern required"
        return 1
    fi
    
    if dry_run_message "Would download files matching '$pattern' from branch $branch to $output_dir"; then
        return 0
    fi
    
    info "Downloading files matching: $pattern"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        # Search for files matching pattern
        local search_query="filename:$pattern+repo:$REPO_NAME"
        local files
        files=$(curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/search/code?q=$search_query" | \
            jq -r '.items[].path' 2>/dev/null)
        
        if [ -n "$files" ]; then
            local count=0
            while IFS= read -r file_path; do
                if [ -n "$file_path" ]; then
                    local output_file="$output_dir/$(basename "$file_path")"
                    if download_file "$file_path" "$branch" "$output_file"; then
                        ((count++))
                    fi
                fi
            done <<< "$files"
            
            success "Downloaded $count files to $output_dir"
        else
            warning "No files found matching pattern: $pattern"
        fi
    else
        warning "Set GitHub token for bulk file operations"
    fi
}

# File validation
validate_file_path() {
    local file_path="$1"
    
    # Check for dangerous paths
    if [[ "$file_path" =~ \.\./|^/|^\~ ]]; then
        error "Invalid file path: $file_path"
        return 1
    fi
    
    return 0
}

# File size and type detection
get_file_info() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    
    if [ -z "$file_path" ]; then
        error "File path required"
        return 1
    fi
    
    if dry_run_message "Would get information for $file_path in branch $branch"; then
        return 0
    fi
    
    info "Getting file information: $file_path"
    
    local github_token
    github_token=$(get_api_key github)
    
    if [ -n "$github_token" ]; then
        curl -s -H "Authorization: token $github_token" \
            "https://api.github.com/repos/$REPO_NAME/contents/$file_path?ref=$branch" | \
            jq -r '
                "File: " + .name + "\n" +
                "Path: " + .path + "\n" +
                "Size: " + (.size | tostring) + " bytes\n" +
                "Type: " + .type + "\n" +
                "SHA: " + .sha + "\n" +
                "Download URL: " + .download_url
            ' 2>/dev/null || echo "File information not available"
    else
        warning "Set GitHub token to view file information"
        echo "File information: (GitHub token required)"
    fi
}

