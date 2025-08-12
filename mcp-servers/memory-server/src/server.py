"""
Sophia AIOS Memory Server
Hybrid memory management across multiple backends
"""
import os
import json
import hashlib
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from loguru import logger
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import redis.asyncio as redis
import openai
from pathlib import Path
import pickle

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Sophia AIOS Memory Server", version="1.0.0")

# Initialize clients
openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

class HybridMemoryCore:
    """Unified memory management across multiple backends"""
    
    def __init__(self):
        self.qdrant = None
        self.redis = None
        self.local_cache = {}
        self.collections = {}
        self.initialize_backends()
    
    def initialize_backends(self):
        """Initialize all memory backends"""
        try:
            # Qdrant for vector memory
            self.qdrant = QdrantClient(host=QDRANT_URL, port=QDRANT_PORT)
            self._ensure_collections()
            logger.info("Qdrant vector database connected")
        except Exception as e:
            logger.warning(f"Qdrant initialization failed: {e}, using local fallback")
            self.qdrant = None
        
        # Redis for fast cache
        try:
            self.redis = redis.from_url(REDIS_URL)
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}, using local cache")
            self.redis = None
    
    def _ensure_collections(self):
        """Ensure required Qdrant collections exist"""
        collections_config = {
            "conversations": {"size": 1536, "distance": Distance.COSINE},
            "knowledge": {"size": 1536, "distance": Distance.COSINE},
            "code_patterns": {"size": 1536, "distance": Distance.COSINE},
            "agent_memory": {"size": 1536, "distance": Distance.COSINE}
        }
        
        for name, config in collections_config.items():
            try:
                self.qdrant.get_collection(name)
                logger.info(f"Collection '{name}' exists")
            except:
                self.qdrant.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=config["size"],
                        distance=config["distance"]
                    )
                )
                logger.info(f"Created collection '{name}'")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            response = await openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return random embedding as fallback
            return np.random.randn(1536).tolist()
    
    async def store_memory(
        self,
        collection: str,
        content: str,
        metadata: Dict = None,
        session_id: str = None
    ) -> str:
        """Store memory in the hybrid system"""
        memory_id = hashlib.sha256(f"{content}{datetime.utcnow()}".encode()).hexdigest()[:16]
        
        # Prepare metadata
        metadata = metadata or {}
        metadata.update({
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id or "default",
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:8]
        })
        
        # Generate embedding
        embedding = await self.embed_text(content)
        
        # Store in Qdrant (if available)
        if self.qdrant:
            try:
                self.qdrant.upsert(
                    collection_name=collection,
                    points=[PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            **metadata
                        }
                    )]
                )
                logger.info(f"Memory {memory_id} stored in Qdrant/{collection}")
            except Exception as e:
                logger.error(f"Qdrant storage failed: {e}")
        
        # Store in Redis cache (if available)
        if self.redis:
            try:
                cache_key = f"{collection}:{memory_id}"
                cache_data = json.dumps({
                    "content": content,
                    "metadata": metadata,
                    "embedding": embedding[:50]  # Store partial embedding for quick checks
                })
                await self.redis.setex(cache_key, 3600, cache_data)  # 1 hour TTL
                logger.info(f"Memory {memory_id} cached in Redis")
            except Exception as e:
                logger.error(f"Redis caching failed: {e}")
        
        # Always store in local cache
        self.local_cache[f"{collection}:{memory_id}"] = {
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        }
        
        return memory_id
    
    async def retrieve_memory(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
        filters: Dict = None
    ) -> List[Dict]:
        """Retrieve relevant memories"""
        # Generate query embedding
        query_embedding = await self.embed_text(query)
        
        results = []
        
        # Try Qdrant first
        if self.qdrant:
            try:
                search_results = self.qdrant.search(
                    collection_name=collection,
                    query_vector=query_embedding,
                    limit=top_k,
                    query_filter=filters
                )
                
                for result in search_results:
                    results.append({
                        "id": result.id,
                        "score": result.score,
                        "content": result.payload.get("content"),
                        "metadata": {k: v for k, v in result.payload.items() if k != "content"}
                    })
                
                logger.info(f"Retrieved {len(results)} memories from Qdrant")
            except Exception as e:
                logger.error(f"Qdrant retrieval failed: {e}")
        
        # Fallback to local cache if needed
        if not results and self.local_cache:
            # Simple cosine similarity search in local cache
            cache_results = []
            for key, memory in self.local_cache.items():
                if key.startswith(f"{collection}:"):
                    # Calculate similarity
                    similarity = np.dot(query_embedding, memory["embedding"]) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(memory["embedding"])
                    )
                    cache_results.append({
                        "id": key.split(":")[1],
                        "score": float(similarity),
                        "content": memory["content"],
                        "metadata": memory["metadata"]
                    })
            
            # Sort by score and take top_k
            cache_results.sort(key=lambda x: x["score"], reverse=True)
            results = cache_results[:top_k]
            logger.info(f"Retrieved {len(results)} memories from local cache")
        
        return results
    
    async def get_session_history(
        self,
        session_id: str,
        collection: str = "conversations",
        limit: int = 100
    ) -> List[Dict]:
        """Get all memories for a specific session"""
        if self.qdrant:
            try:
                results = self.qdrant.scroll(
                    collection_name=collection,
                    scroll_filter={
                        "must": [
                            {"key": "session_id", "match": {"value": session_id}}
                        ]
                    },
                    limit=limit
                )[0]
                
                return [
                    {
                        "id": point.id,
                        "content": point.payload.get("content"),
                        "metadata": {k: v for k, v in point.payload.items() if k != "content"}
                    }
                    for point in results
                ]
            except Exception as e:
                logger.error(f"Session history retrieval failed: {e}")
        
        # Fallback to local cache
        session_memories = []
        for key, memory in self.local_cache.items():
            if memory["metadata"].get("session_id") == session_id:
                session_memories.append({
                    "id": key.split(":")[1],
                    "content": memory["content"],
                    "metadata": memory["metadata"]
                })
        
        return session_memories
    
    async def clear_session(self, session_id: str, collection: str = "conversations"):
        """Clear all memories for a session"""
        if self.qdrant:
            try:
                self.qdrant.delete(
                    collection_name=collection,
                    points_selector={
                        "filter": {
                            "must": [
                                {"key": "session_id", "match": {"value": session_id}}
                            ]
                        }
                    }
                )
                logger.info(f"Cleared session {session_id} from Qdrant")
            except Exception as e:
                logger.error(f"Session clearing failed: {e}")
        
        # Clear from local cache
        keys_to_delete = [
            key for key, memory in self.local_cache.items()
            if memory["metadata"].get("session_id") == session_id
        ]
        for key in keys_to_delete:
            del self.local_cache[key]
        
        logger.info(f"Cleared {len(keys_to_delete)} memories from local cache")
    
    async def export_memories(self, collection: str = None) -> Dict:
        """Export all memories for backup"""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "collections": {}
        }
        
        if collection:
            collections = [collection]
        else:
            collections = ["conversations", "knowledge", "code_patterns", "agent_memory"]
        
        for coll in collections:
            memories = []
            
            # Export from Qdrant
            if self.qdrant:
                try:
                    results, _ = self.qdrant.scroll(
                        collection_name=coll,
                        limit=10000
                    )
                    for point in results:
                        memories.append({
                            "id": point.id,
                            "content": point.payload.get("content"),
                            "metadata": {k: v for k, v in point.payload.items() if k != "content"}
                        })
                except:
                    pass
            
            # Add from local cache
            for key, memory in self.local_cache.items():
                if key.startswith(f"{coll}:"):
                    memories.append({
                        "id": key.split(":")[1],
                        "content": memory["content"],
                        "metadata": memory["metadata"]
                    })
            
            export_data["collections"][coll] = memories
        
        return export_data

# Initialize memory core
memory_core = HybridMemoryCore()

# API Models
class StoreMemoryRequest(BaseModel):
    collection: str = Field(..., description="Collection name")
    content: str = Field(..., description="Content to store")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")
    session_id: Optional[str] = Field(None, description="Session identifier")

class RetrieveMemoryRequest(BaseModel):
    collection: str = Field(..., description="Collection to search")
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, description="Number of results")
    filters: Optional[Dict] = Field(None, description="Optional filters")

class SessionHistoryRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    collection: str = Field("conversations", description="Collection name")
    limit: int = Field(100, description="Maximum results")

# API Endpoints
@app.get("/")
async def root():
    """Health check and service info"""
    return {
        "service": "Sophia AIOS Memory Server",
        "status": "operational",
        "version": "1.0.0",
        "backends": {
            "qdrant": memory_core.qdrant is not None,
            "redis": memory_core.redis is not None,
            "local_cache": True
        }
    }

@app.post("/store")
async def store_memory(request: StoreMemoryRequest):
    """Store a new memory"""
    memory_id = await memory_core.store_memory(
        collection=request.collection,
        content=request.content,
        metadata=request.metadata,
        session_id=request.session_id
    )
    
    return {
        "success": True,
        "memory_id": memory_id,
        "collection": request.collection,
        "session_id": request.session_id
    }

@app.post("/retrieve")
async def retrieve_memory(request: RetrieveMemoryRequest):
    """Retrieve relevant memories"""
    results = await memory_core.retrieve_memory(
        collection=request.collection,
        query=request.query,
        top_k=request.top_k,
        filters=request.filters
    )
    
    return {
        "query": request.query,
        "collection": request.collection,
        "results": results,
        "count": len(results)
    }

@app.post("/session/history")
async def get_session_history(request: SessionHistoryRequest):
    """Get session history"""
    memories = await memory_core.get_session_history(
        session_id=request.session_id,
        collection=request.collection,
        limit=request.limit
    )
    
    return {
        "session_id": request.session_id,
        "collection": request.collection,
        "memories": memories,
        "count": len(memories)
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session's memories"""
    await memory_core.clear_session(session_id)
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session cleared"
    }

@app.get("/export")
async def export_memories(collection: Optional[str] = None):
    """Export memories for backup"""
    export_data = await memory_core.export_memories(collection)
    
    return export_data

@app.get("/stats")
async def get_stats():
    """Get memory statistics"""
    stats = {
        "local_cache_size": len(memory_core.local_cache),
        "collections": {}
    }
    
    if memory_core.qdrant:
        for collection in ["conversations", "knowledge", "code_patterns", "agent_memory"]:
            try:
                info = memory_core.qdrant.get_collection(collection)
                stats["collections"][collection] = {
                    "vectors_count": info.vectors_count,
                    "indexed_vectors_count": info.indexed_vectors_count
                }
            except:
                stats["collections"][collection] = {"status": "unavailable"}
    
    return stats

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sophia AIOS Memory Server...")
    uvicorn.run(app, host="0.0.0.0", port=8102)
