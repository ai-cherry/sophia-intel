#!/bin/bash
set -e

echo "🔍 SOPHIA Dashboard Deployment Verification"
echo "=========================================="

DASHBOARD_URL="https://sophia-dashboard.fly.dev"
BUILD_ENDPOINT="$DASHBOARD_URL/__build"
HEALTH_ENDPOINT="$DASHBOARD_URL/healthz"

echo "1. Testing Health Endpoint..."
curl -i $HEALTH_ENDPOINT
echo ""

echo "2. Testing Build Fingerprint..."
curl -s $BUILD_ENDPOINT
echo ""

echo "3. Testing Asset Availability..."
# Get the main JS file from the HTML
MAIN_JS=$(curl -s $DASHBOARD_URL | grep -o '/assets/index-[^"]*\.js' | head -1)
if [ ! -z "$MAIN_JS" ]; then
    echo "Found main JS: $MAIN_JS"
    echo "Testing asset availability..."
    curl -I "$DASHBOARD_URL$MAIN_JS"
else
    echo "❌ Could not find main JS asset in HTML"
fi
echo ""

echo "4. Testing Research API Connection..."
curl -s -X POST "$DASHBOARD_URL" -H "Content-Type: application/json" -d '{"query":"test"}' | head -100
echo ""

echo "5. Manual Verification Steps:"
echo "   - Open $DASHBOARD_URL in browser"
echo "   - Disable cache and hard reload"
echo "   - Check Network tab for 200 responses on /assets/*.js"
echo "   - Test research panel with query"
echo "   - Verify no [object Object] in results"
echo ""

echo "✅ Verification script complete!"
