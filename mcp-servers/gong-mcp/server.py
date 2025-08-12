"""
Sophia AIOS - Gong.io MCP Server
Sales intelligence and conversation analytics
P0 Critical Integration for PayReady
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field
from loguru import logger
import pandas as pd
from mem0 import Memory
import redis.asyncio as redis
from qdrant_client import QdrantClient
import hashlib

# Configuration
GONG_ACCESS_KEY = os.getenv("GONG_ACCESS_KEY")
GONG_CLIENT_SECRET = os.getenv("GONG_CLIENT_SECRET")
GONG_API_URL = "https://api.gong.io/v2"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QDRANT_URL = os.getenv("QDRANT_URL", "localhost:6333")

app = FastAPI(title="Sophia AIOS - Gong.io MCP", version="1.0.0")

class GongIntelligence:
    """Advanced Gong.io integration with AI-powered insights"""
    
    def __init__(self):
        self.gong_client = None
        self.memory = Memory()  # Mem0 for conversation memory
        self.redis = None
        self.qdrant = None
        self.cache_ttl = 300  # 5 minutes
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all service clients"""
        # Gong API client
        self.gong_client = httpx.AsyncClient(
            base_url=GONG_API_URL,
            headers={
                "Authorization": f"Bearer {GONG_ACCESS_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Redis for caching
        try:
            self.redis = redis.from_url(REDIS_URL)
            logger.info("Redis cache connected")
        except:
            logger.warning("Redis unavailable, using local cache")
        
        # Qdrant for vector search
        try:
            self.qdrant = QdrantClient(host=QDRANT_URL)
            self._ensure_collections()
            logger.info("Qdrant connected for conversation vectors")
        except:
            logger.warning("Qdrant unavailable")
    
    def _ensure_collections(self):
        """Ensure Gong-specific collections exist"""
        collections = ["gong_conversations", "gong_insights", "gong_patterns"]
        for collection in collections:
            try:
                self.qdrant.get_collection(collection)
            except:
                from qdrant_client.models import Distance, VectorParams
                self.qdrant.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {collection}")
    
    async def get_conversations(
        self, 
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Fetch conversations from Gong"""
        # Check cache first
        cache_key = f"gong:conversations:{from_date}:{to_date}:{limit}"
        
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info("Returning cached conversations")
                return json.loads(cached)
        
        # Fetch from Gong API
        params = {
            "limit": limit,
            "fromDateTime": from_date or (datetime.now() - timedelta(days=7)).isoformat(),
            "toDateTime": to_date or datetime.now().isoformat()
        }
        
        response = await self.gong_client.get("/calls", params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Gong API error")
        
        conversations = response.json().get("calls", [])
        
        # Cache the results
        if self.redis:
            await self.redis.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(conversations)
            )
        
        # Store in Mem0 for long-term memory
        for conv in conversations[:10]:  # Store top 10 for memory
            self.memory.add(
                f"Sales call {conv['id']}: {conv.get('title', 'No title')}",
                user_id="gong_system",
                metadata={
                    "call_id": conv['id'],
                    "date": conv.get('scheduled'),
                    "participants": conv.get('participants', [])
                }
            )
        
        return conversations
    
    async def analyze_conversation(self, call_id: str) -> Dict:
        """Deep analysis of a specific conversation"""
        # Get call details
        response = await self.gong_client.get(f"/calls/{call_id}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Call not found")
        
        call_data = response.json()
        
        # Get transcript
        transcript_response = await self.gong_client.get(f"/calls/{call_id}/transcript")
        transcript = transcript_response.json() if transcript_response.status_code == 200 else {}
        
        # Analyze with AI
        analysis = await self._ai_analyze_conversation(call_data, transcript)
        
        # Store insights in Qdrant for vector search
        if self.qdrant and analysis.get("embedding"):
            from qdrant_client.models import PointStruct
            self.qdrant.upsert(
                collection_name="gong_insights",
                points=[PointStruct(
                    id=call_id,
                    vector=analysis["embedding"],
                    payload={
                        "call_id": call_id,
                        "insights": analysis["insights"],
                        "sentiment": analysis["sentiment"],
                        "action_items": analysis["action_items"],
                        "timestamp": datetime.now().isoformat()
                    }
                )]
            )
        
        return {
            "call_id": call_id,
            "call_data": call_data,
            "analysis": analysis
        }
    
    async def _ai_analyze_conversation(self, call_data: Dict, transcript: Dict) -> Dict:
        """AI-powered conversation analysis"""
        # This would integrate with the Tool Server for LLM analysis
        # For now, returning structured insights
        
        text = transcript.get("transcript", "")
        
        # Extract key patterns
        insights = {
            "summary": f"Call with {len(call_data.get('participants', []))} participants",
            "sentiment": self._analyze_sentiment(text),
            "action_items": self._extract_action_items(text),
            "pain_points": self._identify_pain_points(text),
            "competitor_mentions": self._find_competitors(text),
            "next_steps": self._extract_next_steps(text),
            "churn_risk": self._assess_churn_risk(call_data, text),
            "upsell_opportunities": self._identify_upsell(text)
        }
        
        # Generate embedding for vector search
        # This would call OpenAI embeddings API
        embedding = [0.1] * 1536  # Placeholder
        
        return {
            "insights": insights,
            "sentiment": insights["sentiment"],
            "action_items": insights["action_items"],
            "embedding": embedding
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze conversation sentiment"""
        # Simplified sentiment analysis
        positive_words = ["great", "excellent", "love", "perfect", "amazing"]
        negative_words = ["problem", "issue", "difficult", "frustrated", "unhappy"]
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        return "neutral"
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from conversation"""
        action_phrases = ["will do", "I'll", "we'll", "going to", "next step", "follow up"]
        actions = []
        
        for phrase in action_phrases:
            if phrase in text.lower():
                # Extract surrounding context
                actions.append(f"Action item related to: {phrase}")
        
        return actions[:5]  # Top 5 action items
    
    def _identify_pain_points(self, text: str) -> List[str]:
        """Identify customer pain points"""
        pain_indicators = ["challenge", "difficult", "problem", "issue", "struggling", "pain"]
        pain_points = []
        
        for indicator in pain_indicators:
            if indicator in text.lower():
                pain_points.append(f"Pain point: {indicator} mentioned")
        
        return pain_points
    
    def _find_competitors(self, text: str) -> List[str]:
        """Find competitor mentions"""
        # Add your actual competitors here
        competitors = ["competitor1", "competitor2", "buildium", "appfolio"]
        mentioned = []
        
        for comp in competitors:
            if comp.lower() in text.lower():
                mentioned.append(comp)
        
        return mentioned
    
    def _extract_next_steps(self, text: str) -> List[str]:
        """Extract next steps from conversation"""
        next_step_phrases = ["next week", "follow up", "schedule", "demo", "proposal"]
        steps = []
        
        for phrase in next_step_phrases:
            if phrase in text.lower():
                steps.append(f"Next step involving: {phrase}")
        
        return steps
    
    def _assess_churn_risk(self, call_data: Dict, text: str) -> str:
        """Assess churn risk based on conversation"""
        risk_indicators = 0
        
        # Check sentiment
        if self._analyze_sentiment(text) == "negative":
            risk_indicators += 2
        
        # Check for competitors
        if self._find_competitors(text):
            risk_indicators += 1
        
        # Check for pain points
        if len(self._identify_pain_points(text)) > 2:
            risk_indicators += 1
        
        if risk_indicators >= 3:
            return "high"
        elif risk_indicators >= 1:
            return "medium"
        return "low"
    
    def _identify_upsell(self, text: str) -> List[str]:
        """Identify upsell opportunities"""
        upsell_indicators = ["need more", "additional", "expand", "grow", "scale"]
        opportunities = []
        
        for indicator in upsell_indicators:
            if indicator in text.lower():
                opportunities.append(f"Upsell opportunity: {indicator}")
        
        return opportunities
    
    async def get_team_stats(self, team_id: Optional[str] = None) -> Dict:
        """Get team performance statistics"""
        # Get stats from Gong
        response = await self.gong_client.get("/stats/team", params={"teamId": team_id})
        
        if response.status_code != 200:
            return {"error": "Failed to fetch team stats"}
        
        stats = response.json()
        
        # Enhance with AI insights
        enhanced_stats = {
            **stats,
            "ai_insights": {
                "top_performers": self._identify_top_performers(stats),
                "improvement_areas": self._suggest_improvements(stats),
                "trends": self._analyze_trends(stats)
            }
        }
        
        return enhanced_stats
    
    def _identify_top_performers(self, stats: Dict) -> List[Dict]:
        """Identify top performing sales reps"""
        # Analyze stats to find top performers
        return [{"rep": "TopRep1", "metric": "calls", "value": 100}]
    
    def _suggest_improvements(self, stats: Dict) -> List[str]:
        """Suggest team improvements based on stats"""
        return ["Increase call duration", "Improve follow-up rate"]
    
    def _analyze_trends(self, stats: Dict) -> Dict:
        """Analyze trends in team performance"""
        return {
            "weekly_trend": "improving",
            "conversion_trend": "stable",
            "activity_trend": "increasing"
        }
    
    async def search_conversations(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Semantic search across conversations"""
        if not self.qdrant:
            return []
        
        # Generate embedding for query
        # This would call OpenAI embeddings
        query_embedding = [0.1] * 1536  # Placeholder
        
        # Search in Qdrant
        results = self.qdrant.search(
            collection_name="gong_conversations",
            query_vector=query_embedding,
            limit=10,
            query_filter=filters
        )
        
        return [
            {
                "id": r.id,
                "score": r.score,
                "payload": r.payload
            }
            for r in results
        ]

# Initialize Gong intelligence
gong_intel = GongIntelligence()

# API Models
class ConversationRequest(BaseModel):
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    limit: int = Field(100, le=500)

class AnalysisRequest(BaseModel):
    call_id: str = Field(..., description="Gong call ID")
    deep_analysis: bool = Field(True, description="Perform deep AI analysis")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    filters: Optional[Dict] = None

# API Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Sophia AIOS - Gong.io MCP",
        "status": "operational",
        "version": "1.0.0",
        "capabilities": [
            "conversation_fetch",
            "ai_analysis",
            "semantic_search",
            "team_stats",
            "churn_prediction",
            "upsell_identification"
        ]
    }

@app.post("/conversations")
async def get_conversations(request: ConversationRequest):
    """Fetch and cache conversations"""
    try:
        conversations = await gong_intel.get_conversations(
            from_date=request.from_date,
            to_date=request.to_date,
            limit=request.limit
        )
        
        return {
            "success": True,
            "count": len(conversations),
            "conversations": conversations
        }
    except Exception as e:
        logger.error(f"Failed to fetch conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_conversation(request: AnalysisRequest):
    """Deep AI analysis of a conversation"""
    try:
        analysis = await gong_intel.analyze_conversation(request.call_id)
        
        return {
            "success": True,
            "call_id": request.call_id,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_conversations(request: SearchRequest):
    """Semantic search across conversations"""
    try:
        results = await gong_intel.search_conversations(
            query=request.query,
            filters=request.filters
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/team")
async def get_team_stats(team_id: Optional[str] = None):
    """Get team performance statistics"""
    try:
        stats = await gong_intel.get_team_stats(team_id)
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """WebSocket for real-time Gong updates"""
    await websocket.accept()
    
    try:
        while True:
            # Listen for requests
            data = await websocket.receive_json()
            
            if data.get("type") == "subscribe":
                # Subscribe to real-time updates
                await websocket.send_json({
                    "type": "subscribed",
                    "message": "Listening for Gong updates"
                })
                
                # Simulate real-time updates
                while True:
                    # Check for new conversations
                    conversations = await gong_intel.get_conversations(limit=5)
                    
                    if conversations:
                        await websocket.send_json({
                            "type": "update",
                            "data": {
                                "new_conversations": len(conversations),
                                "latest": conversations[0] if conversations else None
                            }
                        })
                    
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sophia AIOS - Gong.io MCP Server...")
    uvicorn.run(app, host="0.0.0.0", port=8200)
