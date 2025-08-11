#!/bin/bash
# lib/ai_ops.sh - AI integration operations for Sophia Intel CLI
# Version: 3.0.0

# AI provider configuration
readonly CLAUDE_API_URL="https://api.anthropic.com/v1/messages"
readonly OPENAI_API_URL="https://api.openai.com/v1/chat/completions"
readonly GROK_API_URL="https://api.x.ai/v1/chat/completions"

# AI provider functions
get_ai_provider() {
    echo "${AI_PROVIDER:-claude}"
}

set_ai_provider() {
    local provider="$1"
    
    case "$provider" in
        claude|gpt|openai|grok)
            export AI_PROVIDER="$provider"
            save_config
            success "AI provider set to: $provider"
            ;;
        *)
            error "Invalid AI provider: $provider"
            echo "Valid providers: claude, gpt, openai, grok"
            return 1
            ;;
    esac
}

# Claude AI integration
call_claude() {
    local prompt="$1"
    local system_prompt="${2:-You are a helpful AI assistant for repository management and code analysis.}"
    
    if [ -z "$prompt" ]; then
        error "Prompt required for Claude AI"
        return 1
    fi
    
    local api_key
    api_key=$(get_api_key claude)
    
    if [ -z "$api_key" ]; then
        error "Claude API key not configured. Use: sophia config --set-key claude <key>"
        return 1
    fi
    
    if dry_run_message "Would send prompt to Claude AI: ${prompt:0:50}..."; then
        return 0
    fi
    
    info "Sending request to Claude AI..."
    
    local json_payload
    json_payload=$(jq -n \
        --arg model "claude-3-opus-20240229" \
        --arg system "$system_prompt" \
        --arg prompt "$prompt" \
        '{
            model: $model,
            max_tokens: 1024,
            system: $system,
            messages: [
                {
                    role: "user",
                    content: $prompt
                }
            ]
        }')
    
    local response
    response=$(curl -s -X POST "$CLAUDE_API_URL" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $api_key" \
        -H "anthropic-version: 2023-06-01" \
        -d "$json_payload")
    
    if echo "$response" | jq -e '.content[0].text' >/dev/null 2>&1; then
        echo "$response" | jq -r '.content[0].text'
    else
        error "Claude AI request failed"
        echo "$response" | jq -r '.error.message // "Unknown error"' 2>/dev/null || echo "API request failed"
        return 1
    fi
}

# OpenAI GPT integration
call_openai() {
    local prompt="$1"
    local system_prompt="${2:-You are a helpful AI assistant for repository management and code analysis.}"
    
    if [ -z "$prompt" ]; then
        error "Prompt required for OpenAI"
        return 1
    fi
    
    local api_key
    api_key=$(get_api_key openai)
    
    if [ -z "$api_key" ]; then
        error "OpenAI API key not configured. Use: sophia config --set-key openai <key>"
        return 1
    fi
    
    if dry_run_message "Would send prompt to OpenAI GPT: ${prompt:0:50}..."; then
        return 0
    fi
    
    info "Sending request to OpenAI GPT..."
    
    local json_payload
    json_payload=$(jq -n \
        --arg model "gpt-4" \
        --arg system "$system_prompt" \
        --arg prompt "$prompt" \
        '{
            model: $model,
            max_tokens: 1024,
            messages: [
                {
                    role: "system",
                    content: $system
                },
                {
                    role: "user",
                    content: $prompt
                }
            ]
        }')
    
    local response
    response=$(curl -s -X POST "$OPENAI_API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $api_key" \
        -d "$json_payload")
    
    if echo "$response" | jq -e '.choices[0].message.content' >/dev/null 2>&1; then
        echo "$response" | jq -r '.choices[0].message.content'
    else
        error "OpenAI request failed"
        echo "$response" | jq -r '.error.message // "Unknown error"' 2>/dev/null || echo "API request failed"
        return 1
    fi
}

# Grok AI integration
call_grok() {
    local prompt="$1"
    local system_prompt="${2:-You are a helpful AI assistant for repository management and code analysis.}"
    
    if [ -z "$prompt" ]; then
        error "Prompt required for Grok"
        return 1
    fi
    
    local api_key
    api_key=$(get_api_key grok)
    
    if [ -z "$api_key" ]; then
        error "Grok API key not configured. Use: sophia config --set-key grok <key>"
        return 1
    fi
    
    if dry_run_message "Would send prompt to Grok AI: ${prompt:0:50}..."; then
        return 0
    fi
    
    info "Sending request to Grok AI..."
    
    local json_payload
    json_payload=$(jq -n \
        --arg model "grok-1" \
        --arg system "$system_prompt" \
        --arg prompt "$prompt" \
        '{
            model: $model,
            max_tokens: 1024,
            messages: [
                {
                    role: "system",
                    content: $system
                },
                {
                    role: "user",
                    content: $prompt
                }
            ]
        }')
    
    local response
    response=$(curl -s -X POST "$GROK_API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $api_key" \
        -d "$json_payload")
    
    if echo "$response" | jq -e '.choices[0].message.content' >/dev/null 2>&1; then
        echo "$response" | jq -r '.choices[0].message.content'
    else
        error "Grok request failed"
        echo "$response" | jq -r '.error.message // "Unknown error"' 2>/dev/null || echo "API request failed"
        return 1
    fi
}

# Universal AI call function
call_ai() {
    local prompt="$1"
    local provider="${2:-$(get_ai_provider)}"
    local system_prompt="${3:-You are a helpful AI assistant for repository management and code analysis.}"
    
    if [ -z "$prompt" ]; then
        error "Prompt required for AI call"
        return 1
    fi
    
    case "$provider" in
        claude)
            call_claude "$prompt" "$system_prompt"
            ;;
        gpt|openai)
            call_openai "$prompt" "$system_prompt"
            ;;
        grok)
            call_grok "$prompt" "$system_prompt"
            ;;
        *)
            error "Unknown AI provider: $provider"
            return 1
            ;;
    esac
}

# Repository analysis functions
analyze_repository() {
    local branch="${1:-$SOPHIA_BRANCH}"
    local provider="${2:-$(get_ai_provider)}"
    
    if dry_run_message "Would analyze repository branch $branch using $provider"; then
        return 0
    fi
    
    info "Analyzing repository branch: $branch"
    
    # Get repository information
    local repo_info
    repo_info=$(get_repo_info "$branch" 2>/dev/null)
    
    # Get recent commits
    local recent_commits
    recent_commits=$(get_recent_commits "$branch" 5 2>/dev/null)
    
    # Get file structure
    local file_structure
    file_structure=$(list_files "$branch" "." 2>/dev/null)
    
    # Prepare analysis prompt
    local analysis_prompt
    analysis_prompt="Please analyze this repository based on the following information:

Repository Information:
$repo_info

Recent Commits:
$recent_commits

File Structure:
$file_structure

Please provide:
1. A summary of what this repository does
2. Recent activity analysis
3. Code organization assessment
4. Recommendations for improvement
5. Potential issues or concerns

Focus on actionable insights and be concise but thorough."
    
    call_ai "$analysis_prompt" "$provider" "You are an expert software architect and code reviewer. Analyze repositories and provide actionable insights."
}

# Code review functions
review_file() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local provider="${3:-$(get_ai_provider)}"
    
    if [ -z "$file_path" ]; then
        error "File path required for code review"
        return 1
    fi
    
    if dry_run_message "Would review $file_path from branch $branch using $provider"; then
        return 0
    fi
    
    info "Reviewing file: $file_path"
    
    # Get file content
    local file_content
    file_content=$(view_file "$file_path" "$branch" 1000 2>/dev/null)
    
    if [ -z "$file_content" ]; then
        error "Could not retrieve file content for review"
        return 1
    fi
    
    # Prepare review prompt
    local review_prompt
    review_prompt="Please review this code file and provide feedback:

File: $file_path
Branch: $branch

Code:
\`\`\`
$file_content
\`\`\`

Please provide:
1. Code quality assessment
2. Potential bugs or issues
3. Security considerations
4. Performance improvements
5. Best practices recommendations
6. Documentation suggestions

Be specific and actionable in your feedback."
    
    call_ai "$review_prompt" "$provider" "You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization."
}

# Commit message generation
generate_commit_message() {
    local changes_description="$1"
    local provider="${2:-$(get_ai_provider)}"
    
    if [ -z "$changes_description" ]; then
        error "Changes description required for commit message generation"
        return 1
    fi
    
    if dry_run_message "Would generate commit message for: ${changes_description:0:50}..."; then
        return 0
    fi
    
    info "Generating commit message..."
    
    local commit_prompt
    commit_prompt="Generate a professional Git commit message for the following changes:

Changes: $changes_description

Requirements:
1. Follow conventional commit format
2. Use present tense, imperative mood
3. Be concise but descriptive
4. Include scope if applicable
5. Maximum 72 characters for the subject line

Provide only the commit message, no additional text."
    
    call_ai "$commit_prompt" "$provider" "You are an expert in Git workflows and commit message conventions. Generate clear, professional commit messages."
}

# Documentation generation
generate_documentation() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local provider="${3:-$(get_ai_provider)}"
    
    if [ -z "$file_path" ]; then
        error "File path required for documentation generation"
        return 1
    fi
    
    if dry_run_message "Would generate documentation for $file_path from branch $branch"; then
        return 0
    fi
    
    info "Generating documentation for: $file_path"
    
    # Get file content
    local file_content
    file_content=$(view_file "$file_path" "$branch" 1000 2>/dev/null)
    
    if [ -z "$file_content" ]; then
        error "Could not retrieve file content for documentation"
        return 1
    fi
    
    # Prepare documentation prompt
    local doc_prompt
    doc_prompt="Generate comprehensive documentation for this code file:

File: $file_path

Code:
\`\`\`
$file_content
\`\`\`

Please provide:
1. Overview and purpose
2. Function/class descriptions
3. Parameter documentation
4. Return value descriptions
5. Usage examples
6. Dependencies and requirements

Format the output in Markdown."
    
    call_ai "$doc_prompt" "$provider" "You are a technical writer specializing in software documentation. Create clear, comprehensive documentation."
}

# Security analysis
analyze_security() {
    local file_path="$1"
    local branch="${2:-$SOPHIA_BRANCH}"
    local provider="${3:-$(get_ai_provider)}"
    
    if [ -z "$file_path" ]; then
        error "File path required for security analysis"
        return 1
    fi
    
    if dry_run_message "Would analyze security for $file_path from branch $branch"; then
        return 0
    fi
    
    info "Analyzing security for: $file_path"
    
    # Get file content
    local file_content
    file_content=$(view_file "$file_path" "$branch" 1000 2>/dev/null)
    
    if [ -z "$file_content" ]; then
        error "Could not retrieve file content for security analysis"
        return 1
    fi
    
    # Prepare security analysis prompt
    local security_prompt
    security_prompt="Perform a security analysis of this code:

File: $file_path

Code:
\`\`\`
$file_content
\`\`\`

Please identify:
1. Potential security vulnerabilities
2. Input validation issues
3. Authentication/authorization problems
4. Data exposure risks
5. Injection attack vectors
6. Cryptographic issues
7. Recommended security improvements

Prioritize findings by severity level."
    
    call_ai "$security_prompt" "$provider" "You are a cybersecurity expert specializing in code security analysis. Identify vulnerabilities and provide actionable security recommendations."
}

# Natural language query processing
process_query() {
    local query="$1"
    local context="${2:-repository}"
    local provider="${3:-$(get_ai_provider)}"
    
    if [ -z "$query" ]; then
        error "Query required"
        return 1
    fi
    
    if dry_run_message "Would process query: ${query:0:50}..."; then
        return 0
    fi
    
    info "Processing natural language query..."
    
    # Get context information based on query
    local context_info=""
    
    if [[ "$query" =~ (file|code|script) ]]; then
        context_info="Repository files: $(list_files "$SOPHIA_BRANCH" "." 2>/dev/null | head -20)"
    elif [[ "$query" =~ (commit|change|history) ]]; then
        context_info="Recent commits: $(get_recent_commits "$SOPHIA_BRANCH" 10 2>/dev/null)"
    elif [[ "$query" =~ (issue|bug|problem) ]]; then
        context_info="Open issues: $(list_issues "open" 10 2>/dev/null)"
    else
        context_info="Repository info: $(get_repo_info "$SOPHIA_BRANCH" 2>/dev/null)"
    fi
    
    # Prepare query prompt
    local query_prompt
    query_prompt="Answer this question about the repository:

Question: $query

Context: $context_info

Repository: $REPO_NAME
Branch: $SOPHIA_BRANCH

Please provide a helpful and accurate answer based on the available information."
    
    call_ai "$query_prompt" "$provider" "You are a helpful assistant with expertise in software development and repository management. Answer questions accurately and concisely."
}

