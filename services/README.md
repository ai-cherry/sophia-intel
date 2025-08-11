# MCP-Notion Sync for Sophia Intel

## 🤖 Overview
Intelligent knowledge synchronization system for the Sophia Intel project, featuring:
- **Lambda Labs GPU Integration**: Fast semantic similarity computation
- **Deduplication Engine**: Prevents information bloat
- **GitHub-Notion Sync**: Bi-directional knowledge management
- **Smart Content Merging**: Intelligently combines similar content

## 🏗️ Architecture

```
GitHub (sophia-intel) 
    ↓
Lambda Labs GPU (Embeddings)
    ↓
Deduplication Engine (80% similarity threshold)
    ↓
Notion Knowledge Base
```

## 🚀 Key Features

### 1. Intelligent Deduplication
- **Content Hashing**: SHA-256 for exact match detection
- **Semantic Similarity**: GPU-accelerated embedding comparison
- **Smart Merging**: Combines similar content instead of duplicating
- **Temporal Archiving**: Auto-archives content >30 days old

### 2. Lambda Labs Integration
```python
# Uses Lambda GPU for fast embedding computation
async def compute_embedding_lambda(text):
    # Sends to Lambda Labs GPU cluster
    # Falls back to local if unavailable
```

### 3. Sync Statistics
- Tracks duplicates prevented
- Monitors merge operations
- Generates efficiency reports

## 📊 Deduplication Stats

The system tracks:
- `total_processed`: Total files analyzed
- `duplicates_prevented`: Exact/similar content skipped
- `content_merged`: Smart merges performed
- `dedup_rate`: Efficiency percentage

## 🔧 Setup

### 1. Environment Variables
```bash
# Lambda Labs
LAMBDA_CLOUD_API_KEY=secret_sophiacloudapi_xxx
LAMBDA_API_CLOUD_ENDPOINT=https://cloud.lambda.ai/api/v1

# GitHub
GITHUB_PAT=your_pat
GITHUB_USERNAME=scoobyjava

# Notion
NOTION_API_KEY=ntn_xxx
NOTION_WORKSPACE_ID=your_workspace_id
```

### 2. Installation
```bash
pip install -r requirements.txt
python setup.py
```

### 3. Run Sync
```bash
# Manual sync
python sync_manager.py

# Check duplicates
python dedup_engine.py --check-duplicates
```

## 📈 Performance Metrics

- **Deduplication Rate**: Typically 20-40% content reduction
- **Processing Speed**: ~100 files/minute with Lambda GPU
- **Similarity Threshold**: 80% (configurable)
- **Memory Efficiency**: Streaming processing for large repos

## 🔄 GitHub Actions

Automated sync every 15 minutes:
```yaml
schedule:
  - cron: '*/15 * * * *'
```

## 🧠 How It Prevents Bloat

1. **Before Sync**: Checks if content exists
2. **Hash Comparison**: Quick exact match detection
3. **Semantic Analysis**: GPU-powered similarity check
4. **Smart Decision**:
   - Skip if >80% similar
   - Update if significantly different
   - Merge if partially overlapping

## 📝 Example Output

```json
{
  "dedup_stats": {
    "total_processed": 150,
    "duplicates_prevented": 45,
    "content_merged": 12,
    "dedup_rate": "30.00%"
  }
}
```

## 🔗 Integration with Sophia Intel

This system integrates with Sophia's AI capabilities:
- Provides clean, deduplicated knowledge base
- Enables semantic search across all content
- Maintains context without redundancy
- Optimizes token usage for LLM operations

## 📚 Resources

- [Lambda Labs API](https://cloud.lambda.ai/api/v1)
- [Notion API](https://developers.notion.com/)
- [Sophia Intel Main Repo](https://github.com/ai-cherry/sophia-intel)
