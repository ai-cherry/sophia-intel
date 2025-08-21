#!/bin/bash
set -e

echo "🚀 Deploying SOPHIA Dashboard with all fixes..."

# Set environment variables for build
export VITE_RESEARCH_URL=https://sophia-research.fly.dev
export VITE_CONTEXT_URL=https://sophia-context-v42.fly.dev  
export VITE_CODE_URL=https://sophia-code.fly.dev
export VITE_BUILD_ID=$(date -u +%Y%m%dT%H%M%SZ)
export CACHE_BUSTER=$(date +%s)

echo "Build ID: $VITE_BUILD_ID"
echo "Cache Buster: $CACHE_BUSTER"

# Build with environment variables
npm run build

# Deploy to Fly.io
flyctl deploy --config ./fly.toml --dockerfile ./Dockerfile --build-arg VITE_RESEARCH_URL=$VITE_RESEARCH_URL --build-arg VITE_CONTEXT_URL=$VITE_CONTEXT_URL --build-arg VITE_CODE_URL=$VITE_CODE_URL --build-arg VITE_BUILD_ID=$VITE_BUILD_ID --build-arg CACHE_BUSTER=$CACHE_BUSTER --no-cache --yes

echo "✅ Deployment complete!"
