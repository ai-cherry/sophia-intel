#!/bin/bash
# Sophia AIOS Architecture Scaffolding Script

echo "🏗️ Creating Sophia AIOS Directory Structure..."

# Core Infrastructure
mkdir -p infra/pulumi/{lambda-labs,k3s,databases,networking,security}
mkdir -p infra/terraform-archive  # For any legacy Terraform we find

# Dashboard & Frontend
mkdir -p dashboard/{src,components,pages,api,public,styles}
mkdir -p dashboard/src/{hooks,utils,services,types}

# Shared Packages (Monorepo structure)
mkdir -p packages/cli/{src,bin,tests}
mkdir -p packages/shared-utils/{src,types,tests}
mkdir -p packages/notion-sync/{src,api,webhooks,tests}
mkdir -p packages/telegram-bot/{src,handlers,commands,tests}

# MCP Microservices
mkdir -p mcp-servers/secrets-server/{src,api,config,tests}
mkdir -p mcp-servers/tool-server/{src,skills,registry,tests}
mkdir -p mcp-servers/memory-server/{src,stores,indexes,tests}
mkdir -p mcp-servers/agent-server/{src,swarms,orchestrator,tests}
mkdir -p mcp-servers/gateway/{src,routing,middleware,tests}

# Scripts & Automation
mkdir -p scripts/audit/{security,performance,quality}
mkdir -p scripts/deployment/{k8s,lambda,monitoring}
mkdir -p scripts/migration

# Comprehensive Testing
mkdir -p tests/unit/{services,agents,utils}
mkdir -p tests/integration/{api,mcp,database}
mkdir -p tests/e2e/{workflows,user-journeys}
mkdir -p tests/fixtures

# Documentation
mkdir -p docs/{architecture,api,guides,decisions}
mkdir -p docs/decisions  # For ADRs

# CI/CD & Security
mkdir -p .github/workflows
mkdir -p .github/actions
mkdir -p .gitleaks
mkdir -p .security

# Development Tools
mkdir -p .devcontainer
mkdir -p .vscode

# Data & Analytics
mkdir -p data/schemas
mkdir -p data/migrations

# Monitoring & Observability
mkdir -p monitoring/{dashboards,alerts,slo}

echo "✅ Directory structure created!"

# Create placeholder files for critical components
echo "📝 Creating core configuration files..."

# Pulumi Project File
cat > infra/pulumi/Pulumi.yaml << 'EOF'
name: sophia-aios
runtime: nodejs
description: Sophia AI Operating System Infrastructure
config:
  aws:region: us-west-2
  pulumi:template: kubernetes-typescript
EOF

# Package.json for monorepo
cat > package.json << 'EOF'
{
  "name": "@sophia-aios/monorepo",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*",
    "dashboard",
    "mcp-servers/*",
    "infra/pulumi"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "deploy": "turbo run deploy",
    "audit:security": "node scripts/audit/security/scan.js",
    "audit:secrets": "gitleaks detect --source . --verbose"
  },
  "devDependencies": {
    "turbo": "latest",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
EOF

# Security: Required Secrets Documentation
cat > required-secrets.md << 'EOF'
# Required Secrets for Sophia AIOS

## Critical Infrastructure Secrets
- LAMBDA_API_KEY
- LAMBDA_CLOUD_API_KEY
- PULUMI_ACCESS_TOKEN
- DNSIMPLE_API_KEY
- GITHUB_PAT

## AI/LLM Provider Keys
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- OPENROUTER_API_KEY
- PORTKEY_API_KEY
- DEEPSEEK_API_KEY
- GROQ_API_KEY
- MISTRAL_API_KEY

## Database & Storage
- NEON_API_TOKEN
- QDRANT_API_KEY
- QDRANT_URL
- NEO4J_CLIENT_ID
- NEO4J_CLIENT_SECRET
- REDIS_URL

## Memory & Agent Systems
- MEM0_API_KEY
- PHIDATA_API_KEY (Agno)
- LANGCHAIN_API_KEY

## Monitoring & Analytics
- SENTRY_API_TOKEN
- ARIZE_API_KEY

## Integration Services
- NOTION_API_KEY
- LINEAR_API_KEY
- SLACK_APP_TOKEN
- TELEGRAM_API_KEY
- GONG_ACCESS_KEY

## Search & Research
- TAVILY_API_KEY
- EXA_API_KEY
- SERPER_API_KEY
- BRAVE_API_KEY

## Workflow Automation
- N8N_API_KEY
- ESTUARY_ACCESS_TOKEN
- APIFY_API_TOKEN

Note: All secrets must be stored in GitHub Organization Secrets
and accessed via Pulumi ESC. NEVER commit secrets to the repository.
EOF

# GitLeaks Configuration
cat > .gitleaks/config.toml << 'EOF'
title = "Sophia AIOS Gitleaks Configuration"

[[rules]]
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{48}'''
tags = ["key", "openai"]

[[rules]]
description = "Anthropic API Key"
regex = '''sk-ant-[a-zA-Z0-9-_]{90,}'''
tags = ["key", "anthropic"]

[[rules]]
description = "Generic API Key"
regex = '''(?i)(api[_\-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})'''
tags = ["key", "generic"]

[allowlist]
paths = [
  "required-secrets.md",
  ".env.example"
]
EOF

echo "🎯 Sophia AIOS architecture scaffold complete!"
echo ""
echo "Next steps:"
echo "1. Move secrets from .env to GitHub Secrets"
echo "2. Initialize Pulumi stack: cd infra/pulumi && pulumi stack init"
echo "3. Deploy base infrastructure: pulumi up"
echo "4. Start building MCP services"
