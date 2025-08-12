#!/usr/bin/env python3
"""
Test the Memory Service functionality
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.memory_service import MemoryService
from loguru import logger

async def test_memory_service():
    """Test memory service operations"""
    logger.info("Testing Memory Service...")
    
    # Initialize memory service
    memory = MemoryService()
    
    # Test 1: Store some context
    test_session = f"test_session_{datetime.now().timestamp()}"
    
    contexts = [
        {
            "content": "The user's name is Lynn Musil and they are working on the Sophia Intel project.",
            "metadata": {"type": "user_info", "timestamp": datetime.now().isoformat()}
        },
        {
            "content": "The project involves creating an MCP server with AI routing and memory capabilities.",
            "metadata": {"type": "project_info", "timestamp": datetime.now().isoformat()}
        },
        {
            "content": "The system uses Qdrant for vector storage and OpenRouter for embeddings.",
            "metadata": {"type": "technical_info", "timestamp": datetime.now().isoformat()}
        }
    ]
    
    logger.info(f"Storing {len(contexts)} context items...")
    for i, ctx in enumerate(contexts):
        try:
            result = await memory.store_context(
                session_id=test_session,
                content=ctx["content"],
                metadata=ctx["metadata"]
            )
            logger.success(f"✓ Stored context {i+1}: {ctx['content'][:50]}...")
        except Exception as e:
            logger.error(f"✗ Failed to store context {i+1}: {e}")
    
    # Test 2: Query stored context
    queries = [
        "What is the user's name?",
        "What technology is used for vector storage?",
        "What is Sophia Intel?"
    ]
    
    logger.info("\nQuerying stored context...")
    for query in queries:
        try:
            results = await memory.query_context(
                session_id=test_session,
                query=query,
                top_k=3
            )
            logger.info(f"\nQuery: {query}")
            if results:
                for r in results:
                    logger.info(f"  - Score: {r.get('score', 0):.3f} | {r.get('content', '')[:100]}...")
            else:
                logger.warning("  No results found")
        except Exception as e:
            logger.error(f"✗ Query failed: {e}")
    
    # Test 3: Get session history
    logger.info("\nRetrieving session history...")
    try:
        history = await memory.get_session_history(test_session)
        logger.info(f"Found {len(history)} items in session history")
        for item in history[:3]:  # Show first 3
            logger.info(f"  - {item.get('content', '')[:80]}...")
    except Exception as e:
        logger.error(f"✗ Failed to get history: {e}")
    
    # Test 4: Health check
    logger.info("\nPerforming health check...")
    try:
        health = await memory.health_check()
        logger.success(f"✓ Memory service health: {json.dumps(health, indent=2)}")
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
    
    logger.info("\n" + "="*50)
    logger.success("Memory Service Test Complete!")
    logger.info("The memory service can now store and retrieve contextual information")
    logger.info("for maintaining conversation history and providing relevant context.")

if __name__ == "__main__":
    try:
        asyncio.run(test_memory_service())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)
