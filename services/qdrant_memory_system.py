"""
QDRANT CLOUD MEMORY SYSTEM
Advanced vector memory with embeddings
"""

import asyncio
from typing import Dict, List, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import json
import hashlib
from datetime import datetime
import os

class SophiaMemorySystem:
    """Advanced memory system with Qdrant cloud integration"""
    
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_key = os.getenv("QDRANT_API_KEY")
        
        if not self.qdrant_url or not self.qdrant_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")
        
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_key
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection names
        self.collections = {
            "conversations": "sophia_conversations",
            "code_snippets": "sophia_code",
            "documents": "sophia_documents",
            "agent_memory": "sophia_agents"
        }
        
        # Initialize collections
        asyncio.create_task(self._initialize_collections())
    
    async def _initialize_collections(self):
        """Initialize Qdrant collections"""
        
        vector_config = models.VectorParams(
            size=384,  # all-MiniLM-L6-v2 embedding size
            distance=models.Distance.COSINE
        )
        
        for collection_name in self.collections.values():
            try:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=vector_config
                )
                print(f"✅ Created collection: {collection_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"📝 Collection exists: {collection_name}")
                else:
                    print(f"❌ Error creating {collection_name}: {e}")
    
    async def store_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store conversation with vector embeddings"""
        
        # Create conversation text for embedding
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        # Generate embedding
        embedding = self.embedding_model.encode(conversation_text).tolist()
        
        # Create point ID
        point_id = hashlib.md5(conversation_id.encode()).hexdigest()
        
        # Prepare payload
        payload = {
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collections["conversations"],
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        
        return point_id
    
    async def search_similar_conversations(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar conversations"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collections["conversations"],
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "conversation_id": result.payload["conversation_id"],
                "messages": result.payload["messages"],
                "score": result.score,
                "timestamp": result.payload["timestamp"],
                "metadata": result.payload.get("metadata", {})
            })
        
        return results
    
    async def store_code_snippet(
        self,
        code: str,
        language: str,
        description: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store code snippet with semantic search"""
        
        # Create searchable text
        searchable_text = f"{description}\n{code}"
        
        # Generate embedding
        embedding = self.embedding_model.encode(searchable_text).tolist()
        
        # Create point ID
        point_id = hashlib.md5(f"{code}{description}".encode()).hexdigest()
        
        # Prepare payload
        payload = {
            "code": code,
            "language": language,
            "description": description,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collections["code_snippets"],
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        
        return point_id
    
    async def search_code_snippets(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for relevant code snippets"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Prepare filter
        search_filter = None
        if language:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="language",
                        match=models.MatchValue(value=language)
                    )
                ]
            )
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collections["code_snippets"],
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "code": result.payload["code"],
                "language": result.payload["language"],
                "description": result.payload["description"],
                "tags": result.payload["tags"],
                "score": result.score,
                "timestamp": result.payload["timestamp"]
            })
        
        return results
    
    async def store_agent_memory(
        self,
        agent_id: str,
        memory_type: str,
        content: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Store agent-specific memory"""
        
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        # Create point ID
        point_id = hashlib.md5(f"{agent_id}{memory_type}{content}".encode()).hexdigest()
        
        # Prepare payload
        payload = {
            "agent_id": agent_id,
            "memory_type": memory_type,
            "content": content,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collections["agent_memory"],
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )
        
        return point_id
    
    async def get_agent_memories(
        self,
        agent_id: str,
        memory_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve agent memories"""
        
        # Prepare filter
        filter_conditions = [
            models.FieldCondition(
                key="agent_id",
                match=models.MatchValue(value=agent_id)
            )
        ]
        
        if memory_type:
            filter_conditions.append(
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchValue(value=memory_type)
                )
            )
        
        search_filter = models.Filter(must=filter_conditions)
        
        # Search in Qdrant
        search_results = self.client.scroll(
            collection_name=self.collections["agent_memory"],
            scroll_filter=search_filter,
            limit=limit
        )
        
        # Format results
        results = []
        for result in search_results[0]:  # scroll returns (points, next_page_offset)
            results.append({
                "memory_type": result.payload["memory_type"],
                "content": result.payload["content"],
                "context": result.payload["context"],
                "timestamp": result.payload["timestamp"]
            })
        
        return results
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        
        stats = {}
        
        for collection_type, collection_name in self.collections.items():
            try:
                info = self.client.get_collection(collection_name)
                stats[collection_type] = {
                    "total_points": info.points_count,
                    "vector_size": info.config.params.vectors.size,
                    "distance_metric": info.config.params.vectors.distance.value
                }
            except Exception as e:
                stats[collection_type] = {"error": str(e)}
        
        return {
            "collections": stats,
            "embedding_model": "all-MiniLM-L6-v2",
            "timestamp": datetime.utcnow().isoformat()
        }

# Global memory instance
_memory_system = None

async def get_memory_system() -> SophiaMemorySystem:
    global _memory_system
    if _memory_system is None:
        _memory_system = SophiaMemorySystem()
    return _memory_system
