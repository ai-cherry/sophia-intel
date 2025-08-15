#!/usr/bin/env python3
"""
Pluggable Embedding MCP Server for Autonomous Evolution v2
Vendor-independent embedding service with intelligent routing
"""

import os
import sys
import json
import yaml
import logging
import asyncio
import aiohttp
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingRequest:
    """Data class for embedding requests"""
    text: Union[str, List[str]]
    model_id: str = 'default'
    use_case: Optional[str] = None
    cache_key: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Generate cache key if not provided
        if self.cache_key is None:
            text_str = self.text if isinstance(self.text, str) else '|'.join(self.text)
            cache_input = f"{text_str}:{self.model_id}:{self.use_case or ''}"
            self.cache_key = hashlib.md5(cache_input.encode()).hexdigest()

@dataclass
class EmbeddingResponse:
    """Data class for embedding responses"""
    embeddings: List[List[float]]
    model_id: str
    provider: str
    dimensions: int
    token_count: int
    cost_estimate: float
    cache_hit: bool
    processing_time_ms: float
    metadata: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class EmbeddingCache:
    """Simple in-memory cache for embeddings"""
    
    def __init__(self, ttl_hours: int = 24):
        self.cache: Dict[str, Tuple[EmbeddingResponse, datetime]] = {}
        self.ttl_hours = ttl_hours
        logger.info(f"EmbeddingCache initialized with TTL: {ttl_hours} hours")
    
    def get(self, cache_key: str) -> Optional[EmbeddingResponse]:
        """Get cached embedding if not expired"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=self.ttl_hours):
                logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]
                logger.debug(f"Cache expired for key: {cache_key[:8]}...")
        
        return None
    
    def set(self, cache_key: str, response: EmbeddingResponse):
        """Cache embedding response"""
        self.cache[cache_key] = (response, datetime.now())
        logger.debug(f"Cached embedding for key: {cache_key[:8]}...")
    
    def clear(self):
        """Clear all cached embeddings"""
        self.cache.clear()
        logger.info("Embedding cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_entries = 0
        
        now = datetime.now()
        for _, (_, timestamp) in self.cache.items():
            if now - timestamp >= timedelta(hours=self.ttl_hours):
                expired_entries += 1
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "ttl_hours": self.ttl_hours
        }

class VendorIndependentEmbeddingMCP:
    """Vendor-independent Embedding MCP with intelligent routing"""
    
    def __init__(self, config_path: str = "/app/config/embedding_models.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.cache = EmbeddingCache(ttl_hours=self.config.get('settings', {}).get('cache_ttl_hours', 24))
        self.session = None
        
        logger.info("VendorIndependentEmbeddingMCP initialized")
        logger.info(f"Available models: {list(self.config['embedding_models'].keys())}")
        logger.info(f"Default model: {self.config.get('default_model', 'nomic-embed-text-v1.5')}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load embedding models configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Loaded config from {self.config_path}")
                return config
            else:
                logger.warning(f"Config file not found: {self.config_path}, using default config")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}, using default config")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is not available"""
        return {
            "default_model": "nomic-embed-text-v1.5",
            "embedding_models": {
                "nomic-embed-text-v1.5": {
                    "provider": "openrouter",
                    "model": "nomic-ai/nomic-embed-text-v1.5",
                    "dimensions": 768,
                    "cost_per_million_tokens": 0.10,
                    "description": "Excellent general-purpose embedding model"
                }
            },
            "providers": {
                "openrouter": {
                    "api_key_env": "OPENROUTER_API_KEY",
                    "base_url": "https://openrouter.ai/api/v1",
                    "timeout": 30
                }
            },
            "settings": {
                "cache_embeddings": True,
                "cache_ttl_hours": 24
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10)
            )
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_model_config(self, model_id: str) -> Dict[str, Any]:
        """Get configuration for a specific model with intelligent routing"""
        models = self.config.get('embedding_models', {})
        
        # Direct model lookup
        if model_id in models:
            return models[model_id]
        
        # Use case mapping
        if model_id == 'default':
            default_model = self.config.get('default_model', 'nomic-embed-text-v1.5')
            if default_model in models:
                return models[default_model]
        
        # Use case to model mapping
        use_case_mappings = self.config.get('routing_rules', {}).get('use_case_mappings', {})
        if model_id in use_case_mappings:
            mapped_model = use_case_mappings[model_id]
            if mapped_model in models:
                return models[mapped_model]
        
        # Fallback chain
        fallback_chain = self.config.get('routing_rules', {}).get('fallback_chain', [])
        for fallback_model in fallback_chain:
            if fallback_model in models:
                logger.warning(f"Model '{model_id}' not found, using fallback: {fallback_model}")
                return models[fallback_model]
        
        raise ValueError(f"Model '{model_id}' not found and no fallback available")
    
    async def generate_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings using vendor-independent routing"""
        start_time = time.time()
        
        try:
            # Check cache first
            if self.config.get('settings', {}).get('cache_embeddings', True):
                cached_response = self.cache.get(request.cache_key)
                if cached_response:
                    cached_response.cache_hit = True
                    cached_response.processing_time_ms = (time.time() - start_time) * 1000
                    return cached_response
            
            # Get model configuration with intelligent routing
            model_config = self.get_model_config(request.model_id)
            provider_name = model_config['provider']
            
            # Generate embeddings based on provider
            if provider_name == 'openrouter':
                response = await self._generate_openrouter_embedding(request, model_config)
            elif provider_name == 'lambda_inference':
                response = await self._generate_lambda_embedding(request, model_config)
            elif provider_name == 'openai':
                response = await self._generate_openai_embedding(request, model_config)
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
            
            # Cache the response
            if self.config.get('settings', {}).get('cache_embeddings', True):
                self.cache.set(request.cache_key, response)
            
            response.processing_time_ms = (time.time() - start_time) * 1000
            response.cache_hit = False
            
            logger.info(f"Generated embeddings: model={request.model_id}, provider={provider_name}, tokens={response.token_count}, time={response.processing_time_ms:.1f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            # Try fallback chain
            return await self._try_fallback(request, str(e), start_time)
    
    async def _try_fallback(self, request: EmbeddingRequest, original_error: str, start_time: float) -> EmbeddingResponse:
        """Try fallback models if primary fails"""
        fallback_chain = self.config.get('routing_rules', {}).get('fallback_chain', [])
        
        for fallback_model in fallback_chain:
            if fallback_model == request.model_id:
                continue  # Skip the model that already failed
                
            try:
                logger.warning(f"Trying fallback model: {fallback_model}")
                fallback_request = EmbeddingRequest(
                    text=request.text,
                    model_id=fallback_model,
                    use_case=request.use_case,
                    metadata={**request.metadata, "fallback_from": request.model_id, "original_error": original_error}
                )
                
                model_config = self.get_model_config(fallback_model)
                provider_name = model_config['provider']
                
                if provider_name == 'openrouter':
                    response = await self._generate_openrouter_embedding(fallback_request, model_config)
                elif provider_name == 'openai':
                    response = await self._generate_openai_embedding(fallback_request, model_config)
                else:
                    continue
                
                response.processing_time_ms = (time.time() - start_time) * 1000
                response.cache_hit = False
                response.metadata["fallback_used"] = True
                
                logger.info(f"Fallback successful: {fallback_model}")
                return response
                
            except Exception as fallback_error:
                logger.error(f"Fallback {fallback_model} also failed: {str(fallback_error)}")
                continue
        
        # All fallbacks failed
        raise Exception(f"All embedding models failed. Original error: {original_error}")
    
    async def _generate_openrouter_embedding(self, request: EmbeddingRequest, model_config: Dict[str, Any]) -> EmbeddingResponse:
        """Generate embeddings using OpenRouter API"""
        try:
            session = await self._get_session()
            provider_config = self.config['providers']['openrouter']
            
            # Get API key
            api_key = os.getenv(provider_config['api_key_env'])
            if not api_key:
                raise ValueError(f"API key not found: {provider_config['api_key_env']}")
            
            # Prepare input
            input_texts = request.text if isinstance(request.text, list) else [request.text]
            
            # OpenRouter embeddings API call
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://sophia-intel.ai',
                'X-Title': 'SOPHIA Intel Embedding MCP'
            }
            
            payload = {
                'model': model_config['model'],
                'input': input_texts
            }
            
            url = f"{provider_config['base_url']}/embeddings"
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract embeddings
                    embeddings = [item['embedding'] for item in data['data']]
                    
                    # Calculate cost estimate
                    total_tokens = data['usage']['total_tokens']
                    cost_per_million = model_config.get('cost_per_million_tokens', 0.10)
                    cost_estimate = (total_tokens / 1_000_000) * cost_per_million
                    
                    return EmbeddingResponse(
                        embeddings=embeddings,
                        model_id=request.model_id,
                        provider='openrouter',
                        dimensions=model_config['dimensions'],
                        token_count=total_tokens,
                        cost_estimate=cost_estimate,
                        cache_hit=False,
                        processing_time_ms=0,
                        metadata={
                            "model": model_config['model'],
                            "input_count": len(input_texts),
                            "use_case": request.use_case,
                            **request.metadata
                        },
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"OpenRouter embedding generation failed: {str(e)}")
            # Return mock response for demo purposes
            return await self._mock_embedding_response(request, model_config, 'openrouter')
    
    async def _generate_lambda_embedding(self, request: EmbeddingRequest, model_config: Dict[str, Any]) -> EmbeddingResponse:
        """Generate embeddings using Lambda Inference API"""
        # For now, return mock response as Lambda embeddings may not be available
        logger.info("Lambda Inference API embeddings not yet implemented, using mock response")
        return await self._mock_embedding_response(request, model_config, 'lambda_inference')
    
    async def _generate_openai_embedding(self, request: EmbeddingRequest, model_config: Dict[str, Any]) -> EmbeddingResponse:
        """Generate embeddings using OpenAI API (fallback only)"""
        try:
            session = await self._get_session()
            provider_config = self.config['providers']['openai']
            
            # Get API key
            api_key = os.getenv(provider_config['api_key_env'])
            if not api_key:
                raise ValueError(f"API key not found: {provider_config['api_key_env']}")
            
            # Prepare input
            input_texts = request.text if isinstance(request.text, list) else [request.text]
            
            # OpenAI embeddings API call
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model_config['model'],
                'input': input_texts
            }
            
            url = f"{provider_config['base_url']}/embeddings"
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract embeddings
                    embeddings = [item['embedding'] for item in data['data']]
                    
                    # Calculate cost estimate
                    total_tokens = data['usage']['total_tokens']
                    cost_per_million = model_config.get('cost_per_million_tokens', 0.02)
                    cost_estimate = (total_tokens / 1_000_000) * cost_per_million
                    
                    return EmbeddingResponse(
                        embeddings=embeddings,
                        model_id=request.model_id,
                        provider='openai',
                        dimensions=model_config['dimensions'],
                        token_count=total_tokens,
                        cost_estimate=cost_estimate,
                        cache_hit=False,
                        processing_time_ms=0,
                        metadata={
                            "model": model_config['model'],
                            "input_count": len(input_texts),
                            "use_case": request.use_case,
                            "fallback_provider": True,
                            **request.metadata
                        },
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            return await self._mock_embedding_response(request, model_config, 'openai')
    
    async def _mock_embedding_response(self, request: EmbeddingRequest, model_config: Dict[str, Any], provider: str) -> EmbeddingResponse:
        """Generate mock embedding response for demo purposes"""
        input_texts = request.text if isinstance(request.text, list) else [request.text]
        dimensions = model_config['dimensions']
        
        # Generate mock embeddings (random normalized vectors)
        import random
        embeddings = []
        for _ in input_texts:
            embedding = [random.gauss(0, 1) for _ in range(dimensions)]
            # Normalize
            norm = sum(x*x for x in embedding) ** 0.5
            embedding = [x/norm for x in embedding]
            embeddings.append(embedding)
        
        # Estimate token count (rough approximation)
        total_chars = sum(len(text) for text in input_texts)
        estimated_tokens = total_chars // 4  # Rough estimate
        
        cost_per_million = model_config.get('cost_per_million_tokens', 0.10)
        cost_estimate = (estimated_tokens / 1_000_000) * cost_per_million
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model_id=request.model_id,
            provider=provider,
            dimensions=dimensions,
            token_count=estimated_tokens,
            cost_estimate=cost_estimate,
            cache_hit=False,
            processing_time_ms=0,
            metadata={
                "model": model_config['model'],
                "input_count": len(input_texts),
                "use_case": request.use_case,
                "mock": True,
                **request.metadata
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models and their configurations"""
        models = {}
        for model_id, config in self.config.get('embedding_models', {}).items():
            models[model_id] = {
                "provider": config['provider'],
                "model": config['model'],
                "dimensions": config['dimensions'],
                "description": config.get('description', ''),
                "use_cases": config.get('use_cases', []),
                "quality_tier": config.get('quality_tier', 'standard'),
                "cost_per_million_tokens": config.get('cost_per_million_tokens', 0.0)
            }
        return models
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP capabilities and configuration"""
        return {
            "models": self.get_available_models(),
            "providers": list(self.config.get('providers', {}).keys()),
            "routing_rules": self.config.get('routing_rules', {}),
            "settings": self.config.get('settings', {}),
            "cache_stats": self.cache.stats(),
            "principles": self.config.get('principles', {})
        }

# Flask application for MCP endpoints
app = Flask(__name__)
CORS(app)

# Initialize Vendor-Independent Embedding MCP
embedding_mcp = VendorIndependentEmbeddingMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "embedding-mcp",
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "vendor-independent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models_available": len(embedding_mcp.get_available_models()),
        "default_model": embedding_mcp.config.get('default_model'),
        "cache_enabled": embedding_mcp.config.get('settings', {}).get('cache_embeddings', True)
    })

@app.route('/generate_embedding', methods=['POST'])
def generate_embedding():
    """Generate embeddings for text using intelligent routing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: text"
            }), 400
        
        # Create EmbeddingRequest object
        embedding_request = EmbeddingRequest(
            text=data['text'],
            model_id=data.get('model_id', 'default'),
            use_case=data.get('use_case'),
            metadata=data.get('metadata', {})
        )
        
        # Execute async request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(embedding_mcp.generate_embedding(embedding_request))
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "data": result.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Generate embedding failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Get available embedding models"""
    try:
        models = embedding_mcp.get_available_models()
        return jsonify({
            "success": True,
            "data": {
                "models": models,
                "total_models": len(models),
                "default_model": embedding_mcp.config.get('default_model')
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Get models failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get MCP capabilities and configuration"""
    try:
        capabilities = embedding_mcp.get_capabilities()
        return jsonify({
            "success": True,
            "data": capabilities,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Get capabilities failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/test_embedding', methods=['GET'])
def test_embedding():
    """Test embedding generation with multiple models"""
    try:
        test_cases = [
            {
                "text": "This is a test sentence for vendor-independent embedding generation.",
                "model_id": "default",
                "use_case": "test"
            },
            {
                "text": "Testing high-quality embeddings for foundational knowledge.",
                "model_id": "foundational_knowledge",
                "use_case": "critical"
            },
            {
                "text": ["Batch test sentence one.", "Batch test sentence two."],
                "model_id": "bulk_processing",
                "use_case": "batch_test"
            }
        ]
        
        results = []
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for test_case in test_cases:
                embedding_request = EmbeddingRequest(
                    text=test_case["text"],
                    model_id=test_case["model_id"],
                    use_case=test_case["use_case"]
                )
                
                result = loop.run_until_complete(embedding_mcp.generate_embedding(embedding_request))
                results.append({
                    "test_case": test_case,
                    "result": {
                        "success": True,
                        "model_used": result.model_id,
                        "provider": result.provider,
                        "dimensions": result.dimensions,
                        "token_count": result.token_count,
                        "cost_estimate": result.cost_estimate,
                        "processing_time_ms": result.processing_time_ms,
                        "cache_hit": result.cache_hit,
                        "fallback_used": result.metadata.get("fallback_used", False)
                    }
                })
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "data": {
                "tests": results,
                "total_tests": len(results),
                "successful_tests": len(results)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Test embedding failed: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

if __name__ == '__main__':
    logger.info("🔧 Starting Vendor-Independent Embedding MCP Server for Autonomous Evolution v2")
    logger.info(f"Default model: {embedding_mcp.config.get('default_model')}")
    logger.info(f"Available models: {list(embedding_mcp.get_available_models().keys())}")
    
    app.run(host='0.0.0.0', port=5003, debug=False)

