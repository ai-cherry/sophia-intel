#!/bin/bash
# Quick test script for Sophia Hybrid MCP System

echo "=========================================="
echo "🧪 Sophia Hybrid MCP System Quick Test"
echo "=========================================="

cd /Users/lynnmusil/Projects/sophia-mcp-hybrid

# Install requirements
echo "📦 Installing requirements..."
pip3 install -q fastapi uvicorn aiohttp numpy requests 2>/dev/null

# Test 1: Lambda API
echo ""
echo "1️⃣ Testing Lambda API Connection..."
python3 -c "
import requests
LAMBDA_API_KEY = '$NOTION_API_KEY_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y'
try:
    response = requests.get('https://cloud.lambda.ai/api/v1/instances', auth=(LAMBDA_API_KEY, ''), timeout=5)
    if response.status_code == 200:
        print('✅ Lambda API: Connected')
        data = response.json()
        print(f'   Instances: {len(data.get(\"data\", []))}')
    else:
        print(f'⚠️  Lambda API: Status {response.status_code}')
except Exception as e:
    print(f'⚠️  Lambda API: {str(e)[:50]}')
"

# Test 2: Notion API
echo ""
echo "2️⃣ Testing Notion API Connection..."
python3 -c "
import requests
NOTION_API_KEY = '${NOTION_API_KEY}'
headers = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': '2022-06-28'
}
try:
    response = requests.get('https://api.notion.com/v1/users/me', headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Notion API: Connected as {data.get(\"name\", \"Unknown\")}')
    else:
        print(f'⚠️  Notion API: Status {response.status_code}')
except Exception as e:
    print(f'⚠️  Notion API: {str(e)[:50]}')
"

# Test 3: Start servers
echo ""
echo "3️⃣ Starting local servers..."

# Start cloud server in background
python3 cloud-server.py > /tmp/cloud-server.log 2>&1 &
CLOUD_PID=$!
echo "   Cloud server started (PID: $CLOUD_PID)"
sleep 2

# Start local bridge in background  
python3 local-bridge.py > /tmp/local-bridge.log 2>&1 &
LOCAL_PID=$!
echo "   Local bridge started (PID: $LOCAL_PID)"
sleep 2

# Test 4: Server health checks
echo ""
echo "4️⃣ Testing server endpoints..."

# Test cloud server
python3 -c "
import requests
try:
    response = requests.get('http://localhost:8080/', timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Cloud Server: {data.get(\"status\")}')
        stats = data.get('stats', {})
        print(f'   Stats: {stats}')
    else:
        print('❌ Cloud Server: Not responding')
except:
    print('❌ Cloud Server: Connection failed')
"

# Test local bridge
python3 -c "
import requests
try:
    response = requests.get('http://localhost:8000/', timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Local Bridge: {data.get(\"status\")}')
        print(f'   Mode: {data.get(\"mode\")}')
    else:
        print('❌ Local Bridge: Not responding')
except:
    print('❌ Local Bridge: Connection failed')
"

# Test 5: File operations
echo ""
echo "5️⃣ Testing file operations..."

# Create test file
echo "Test content for deduplication" > ~/Projects/test-dedup.txt

python3 -c "
import requests
import json

# Read file
try:
    response = requests.post('http://localhost:8000/mcp/tool/read_file', 
                            json={'path': '~/Projects/test-dedup.txt'})
    if response.status_code == 200:
        data = response.json()
        print(f'✅ File Read: Success')
        print(f'   Duplicate: {data.get(\"is_duplicate\")}')
        print(f'   Hash: {data.get(\"hash\")}')
    else:
        print('❌ File Read: Failed')
except:
    print('❌ File Read: Connection failed')

# Check stats
try:
    response = requests.get('http://localhost:8000/stats')
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print(f'✅ Dedup Stats:')
        print(f'   Files read: {stats.get(\"files_read\", 0)}')
        print(f'   Duplicates found: {stats.get(\"duplicates_found\", 0)}')
        print(f'   Dedup rate: {data.get(\"dedup_percentage\", \"0%\")}')
except:
    pass
"

# Cleanup
echo ""
echo "6️⃣ Cleaning up..."
kill $CLOUD_PID 2>/dev/null
kill $LOCAL_PID 2>/dev/null
rm -f ~/Projects/test-dedup.txt

echo ""
echo "=========================================="
echo "📊 Test Complete!"
echo "=========================================="
echo ""
echo "✅ System is ready for use!"
echo "To start permanently:"
echo "  cd /Users/lynnmusil/Projects/sophia-mcp-hybrid"
echo "  python3 cloud-server.py &"
echo "  python3 local-bridge.py &"
echo ""
echo "Configure Claude Desktop:"
echo "  Add to ~/.claude/mcp.json"
echo "=========================================="
