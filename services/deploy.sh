#!/bin/bash
# Complete setup and deployment script for sophia-intel MCP sync

echo "======================================"
echo "🚀 Sophia Intel MCP-Notion Sync Setup"
echo "======================================"

# Step 1: Clone or navigate to sophia-intel
if [ ! -d "sophia-intel" ]; then
    echo "📥 Cloning sophia-intel repository..."
    git clone https://github.com/ai-cherry/sophia-intel.git
fi

cd sophia-intel

# Step 2: Create and checkout branch
echo "🌿 Creating mcp-notion-sync branch..."
git checkout -b mcp-notion-sync 2>/dev/null || git checkout mcp-notion-sync

# Step 3: Create directory structure
echo "📁 Creating directory structure..."
mkdir -p services/mcp-sync
mkdir -p .github/workflows

# Step 4: Copy all files
echo "📄 Copying sync system files..."
cp ../sophia-intel-mcp-sync/sync_manager.py services/mcp-sync/
cp ../sophia-intel-mcp-sync/requirements.txt services/mcp-sync/
cp ../sophia-intel-mcp-sync/README.md services/mcp-sync/
cp ../sophia-intel-mcp-sync/github-workflow.yml .github/workflows/mcp-sync.yml

# Step 5: Create additional required files
echo "✏️ Creating additional files..."

# Create dedup_engine.py
cat > services/mcp-sync/dedup_engine.py << 'EOF'
#!/usr/bin/env python3
"""
Content Deduplication Engine for Sophia Intel
"""

import hashlib
import json
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import numpy as np
from datetime import datetime, timedelta

class DeduplicationEngine:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.content_index = {}
        self.metadata_index = {}
        
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        normalized = self.normalize_content(content)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def normalize_content(self, content: str) -> str:
        """Normalize content for comparison"""
        content = re.sub(r'\s+', ' ', content)
        content = content.lower().strip()
        content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)
        content = re.sub(r'\d{2}:\d{2}:\d{2}', '', content)
        return content
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        norm1 = self.normalize_content(text1)
        norm2 = self.normalize_content(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_duplicates(self, new_content: str, existing_contents: List[Dict]) -> List[Tuple[str, float]]:
        """Find potential duplicates of new content"""
        duplicates = []
        new_hash = self.generate_content_hash(new_content)
        
        for existing in existing_contents:
            existing_hash = existing.get('hash', self.generate_content_hash(existing['content']))
            
            if new_hash == existing_hash:
                duplicates.append((existing['id'], 1.0))
                continue
            
            similarity = self.calculate_text_similarity(new_content, existing['content'])
            
            if similarity >= self.similarity_threshold:
                duplicates.append((existing['id'], similarity))
        
        return sorted(duplicates, key=lambda x: x[1], reverse=True)
    
    def generate_dedup_report(self, contents: List[Dict]) -> Dict:
        """Generate a deduplication report"""
        total_content = len(contents)
        unique_hashes = set()
        duplicates_found = []
        
        for i, content in enumerate(contents):
            content_hash = self.generate_content_hash(content.get('content', ''))
            
            if content_hash in unique_hashes:
                duplicates_found.append({
                    'index': i,
                    'id': content.get('id'),
                    'hash': content_hash
                })
            else:
                unique_hashes.add(content_hash)
        
        duplicate_count = len(duplicates_found)
        dedup_ratio = (duplicate_count / total_content * 100) if total_content > 0 else 0
        
        return {
            'total_items': total_content,
            'unique_items': len(unique_hashes),
            'duplicates': duplicate_count,
            'deduplication_ratio': f'{dedup_ratio:.2f}%',
            'duplicate_details': duplicates_found[:10],
            'recommendation': self.generate_recommendation(dedup_ratio)
        }
    
    def generate_recommendation(self, dedup_ratio: float) -> str:
        """Generate recommendation based on deduplication ratio"""
        if dedup_ratio < 5:
            return "Content is well-managed with minimal duplicates."
        elif dedup_ratio < 15:
            return "Some duplicates found. Consider running periodic deduplication."
        elif dedup_ratio < 30:
            return "Significant duplicates detected. Deduplication recommended."
        else:
            return "High duplicate ratio. Immediate deduplication strongly recommended."

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Deduplication Engine')
    parser.add_argument('--check-duplicates', action='store_true')
    parser.add_argument('--threshold', type=float, default=0.8)
    parser.add_argument('--input-file', type=str, default='sync_state.json')
    
    args = parser.parse_args()
    
    engine = DeduplicationEngine(similarity_threshold=args.threshold)
    
    if args.check_duplicates and args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                data = json.load(f)
                contents = [{'content': v, 'id': k} for k, v in data.get('content_hashes', {}).items()]
            
            report = engine.generate_dedup_report(contents)
            print(json.dumps(report, indent=2))
        except Exception as e:
            print(f"Error: {e}")
EOF

# Create .env.example
cat > services/mcp-sync/.env.example << 'EOF'
# Lambda Labs Configuration
LAMBDA_CLOUD_API_KEY=${NOTION_API_KEY}
LAMBDA_API_CLOUD_ENDPOINT=https://cloud.lambda.ai/api/v1

# GitHub Configuration
GITHUB_PAT=${GITHUB_PAT}
GITHUB_USERNAME=scoobyjava
GITHUB_REPO=ai-cherry/sophia-intel
GITHUB_BRANCH=mcp-notion-sync

# Notion Configuration
NOTION_API_KEY=${NOTION_API_KEY}
NOTION_WORKSPACE_ID=xxx

# Sync Configuration
SYNC_INTERVAL_MINUTES=5
DEDUP_THRESHOLD=0.8
ARCHIVE_DAYS_THRESHOLD=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=sync.log
EOF

# Create setup.py
cat > services/mcp-sync/setup.py << 'EOF'
#!/usr/bin/env python3
"""Setup script for MCP-Notion Sync Service"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    print("🚀 Setting up MCP-Notion Sync Service for Sophia Intel")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    dirs_to_create = ['logs', 'data', 'cache', 'backups']
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file. Please update with your API keys.")
    
    sync_state_file = 'sync_state.json'
    if not os.path.exists(sync_state_file):
        initial_state = {
            'version': '1.0.0',
            'last_sync': None,
            'content_hashes': {},
            'notion_mappings': {},
            'github_mappings': {},
            'dedup_stats': {
                'total_processed': 0,
                'duplicates_prevented': 0,
                'content_merged': 0
            }
        }
        with open(sync_state_file, 'w') as f:
            json.dump(initial_state, f, indent=2)
        print(f"✅ Initialized sync state")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env with your API keys")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python sync_manager.py")

if __name__ == '__main__':
    setup_environment()
EOF

# Step 6: Stage all changes
echo "📦 Staging all changes..."
git add .

# Step 7: Create commit
echo "💾 Creating commit..."
git commit -m "Add MCP-Notion sync system with Lambda Labs integration and intelligent deduplication

- Implemented intelligent content deduplication engine
- Added Lambda Labs GPU integration for semantic similarity
- Created GitHub-Notion bi-directional sync
- Prevents information bloat with 80% similarity threshold
- Automated sync via GitHub Actions every 15 minutes
- Includes comprehensive deduplication reporting"

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Push to GitHub:"
echo "   git push -u origin mcp-notion-sync"
echo ""
echo "2. Add GitHub Secrets at:"
echo "   https://github.com/ai-cherry/sophia-intel/settings/secrets/actions"
echo ""
echo "   Required secrets:"
echo "   - LAMBDA_CLOUD_API_KEY"
echo "   - LAMBDA_API_CLOUD_ENDPOINT"
echo "   - GITHUB_PAT (generate new one)"
echo "   - GITHUB_USERNAME"
echo "   - NOTION_API_KEY"
echo "   - NOTION_WORKSPACE_ID"
echo ""
echo "3. Test locally:"
echo "   cd services/mcp-sync"
echo "   pip install -r requirements.txt"
echo "   python setup.py"
echo "   python sync_manager.py"
echo ""
echo "======================================"
