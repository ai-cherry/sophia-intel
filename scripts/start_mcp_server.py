#!/usr/bin/env python3
"""
Start the Enhanced MCP Server with Memory
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.enhanced_unified_server import EnhancedUnifiedMCPServer
import uvicorn
from loguru import logger

async def main():
    """Start the enhanced MCP server"""
    logger.info("Starting Enhanced MCP Server with Memory...")
    
    # Create server instance
    server = EnhancedUnifiedMCPServer()
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=server.app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True,
        reload_dirs=["mcp_servers", "services", "agents", "config"]
    )
    
    # Create server and run
    server_instance = uvicorn.Server(config)
    await server_instance.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
