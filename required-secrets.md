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
