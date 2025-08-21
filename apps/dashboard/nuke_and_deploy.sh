#!/bin/bash
set -e

echo "🔥 NUKING OLD BUNDLE AND DEPLOYING FRESH..."

# Clean everything
rm -rf dist/ node_modules/.cache/ .vite/

# Fresh install with legacy peer deps
npm install --legacy-peer-deps

# Build with fresh cache
npm run build

# Verify the build has correct paths
echo "🔍 Verifying build..."
if grep -q '/dashboard/assets/' dist/index.html; then
    echo "❌ ERROR: Still has /dashboard/assets/ paths!"
    exit 1
else
    echo "✅ Build verified: Using correct /assets/ paths"
fi

# Show the built files
echo "📦 Built files:"
ls -la dist/
echo "📄 Index.html content:"
cat dist/index.html

echo "✅ Ready for deployment!"
