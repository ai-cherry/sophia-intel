#!/usr/bin/env python3
"""
Local MCP Bridge Server - Test Version
Handles local file operations and forwards compute to cloud
"""

import os
import json
import hashlib
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import aiohttp

app = FastAPI(title="Sophia Local MCP Bridge")

# Configuration
CLOUD_MCP_URL = os.getenv('CLOUD_MCP_URL', 'http://localhost:8080')
LOCAL_DIRS = [
    os.path.expanduser('~/Projects'),
    os.path.expanduser('~/Documents')
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple cache for deduplication
content_cache = {}
dedup_stats = {
    'files_read': 0,
    'duplicates_found': 0,
    'unique_content': 0
}

@app.get("/")
async def health():
    """Health check endpoint"""
    return {
        "status": "operational",
        "mode": "hybrid",
        "cloud_server": CLOUD_MCP_URL,
        "local_dirs": LOCAL_DIRS,
        "stats": dedup_stats
    }

@app.post("/mcp/tool/{tool_name}")
async def execute_tool(tool_name: str, request: Request):
    """Execute MCP tool - route to local or cloud"""
    try:
        params = await request.json()
    except:
        params = {}
    
    if tool_name == 'read_file':
        return await handle_read_file(params)
    elif tool_name == 'list_files':
        return await handle_list_files(params)
    elif tool_name == 'check_duplication':
        return await handle_check_duplication(params)
    else:
        return {"error": f"Unknown tool: {tool_name}"}

async def handle_read_file(params: dict):
    """Read a local file and check for duplicates"""
    path_str = params.get('path', '')
    path = Path(os.path.expanduser(path_str))
    
    dedup_stats['files_read'] += 1
    
    if path.exists() and path.is_file():
        try:
            content = path.read_text()
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check if duplicate
            is_duplicate = content_hash in content_cache
            if is_duplicate:
                dedup_stats['duplicates_found'] += 1
            else:
                content_cache[content_hash] = True
                dedup_stats['unique_content'] += 1
            
            return {
                "success": True,
                "content": content[:500],  # Truncate for response
                "path": str(path),
                "hash": content_hash[:16],
                "is_duplicate": is_duplicate,
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    else:
        return {"error": f"File not found: {path_str}"}

async def handle_list_files(params: dict):
    """List files in a directory"""
    directory = params.get('directory', LOCAL_DIRS[0])
    dir_path = Path(os.path.expanduser(directory))
    
    if dir_path.exists() and dir_path.is_dir():
        files = []
        for f in dir_path.iterdir():
            if f.is_file():
                files.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size
                })
            if len(files) >= 20:  # Limit for testing
                break
        
        return {
            "success": True,
            "directory": str(dir_path),
            "count": len(files),
            "files": files
        }
    else:
        return {"error": f"Directory not found: {directory}"}

async def handle_check_duplication(params: dict):
    """Check if content is duplicate"""
    content = params.get('content', '')
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    is_duplicate = content_hash in content_cache
    if not is_duplicate:
        content_cache[content_hash] = True
    
    return {
        "is_duplicate": is_duplicate,
        "hash": content_hash[:16],
        "cache_size": len(content_cache)
    }

@app.get("/stats")
async def get_stats():
    """Get deduplication statistics"""
    return {
        "stats": dedup_stats,
        "cache_size": len(content_cache),
        "dedup_percentage": (
            f"{(dedup_stats['duplicates_found'] / max(dedup_stats['files_read'], 1) * 100):.1f}%"
        )
    }

if __name__ == "__main__":
    print("🌉 Starting Sophia Local MCP Bridge...")
    print(f"📁 Monitoring directories: {LOCAL_DIRS}")
    print(f"☁️  Cloud server: {CLOUD_MCP_URL}")
    uvicorn.run(app, host="localhost", port=8000)
