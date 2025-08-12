"""
Sophia AIOS Tool Server
Unified interface for all external tools and APIs
"""
import os
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from loguru import logger
import openai
from anthropic import Anthropic
from tavily import TavilyClient
import aioredis

# Initialize clients
openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

app = FastAPI(title="Sophia AIOS Tool Server", version="1.0.0")
security = HTTPBearer()

# Tool Registry
class ToolRegistry:
    """Central registry for all available tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        
        # LLM Tools
        self.register("llm.complete", self.llm_complete, {
            "description": "Generate text using various LLM models",
            "parameters": {
                "model": "Model to use (gpt-4, claude-3, etc.)",
                "prompt": "Input prompt",
                "max_tokens": "Maximum tokens to generate"
            }
        })
        
        # Search Tools
        self.register("search.web", self.search_web, {
            "description": "Search the web using Tavily",
            "parameters": {
                "query": "Search query",
                "max_results": "Maximum number of results"
            }
        })
        
        # Research Tools
        self.register("research.analyze", self.research_analyze, {
            "description": "Deep analysis of a topic",
            "parameters": {
                "topic": "Topic to analyze",
                "depth": "Analysis depth (quick, standard, deep)"
            }
        })
        
        # Code Tools
        self.register("code.review", self.code_review, {
            "description": "Review code for quality and security",
            "parameters": {
                "code": "Code to review",
                "language": "Programming language",
                "focus": "Review focus areas"
            }
        })
        
        # Data Tools
        self.register("data.extract", self.data_extract, {
            "description": "Extract structured data from text",
            "parameters": {
                "text": "Input text",
                "schema": "Expected output schema"
            }
        })
        
        # Integration Tools
        self.register("integration.notion", self.notion_operation, {
            "description": "Interact with Notion API",
            "parameters": {
                "operation": "Operation type (create, update, query)",
                "data": "Operation data"
            }
        })
        
        self.register("integration.slack", self.slack_operation, {
            "description": "Send messages to Slack",
            "parameters": {
                "channel": "Slack channel",
                "message": "Message content"
            }
        })
        
        # Monitoring Tools
        self.register("monitor.health", self.check_health, {
            "description": "Check health of external services",
            "parameters": {
                "services": "List of services to check"
            }
        })
    
    def register(self, name: str, handler: callable, metadata: Dict):
        """Register a new tool"""
        self.tools[name] = {
            "handler": handler,
            "metadata": metadata,
            "usage_count": 0,
            "last_used": None
        }
    
    async def execute(self, tool_name: str, params: Dict) -> Any:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        tool["usage_count"] += 1
        tool["last_used"] = datetime.utcnow().isoformat()
        
        try:
            result = await tool["handler"](**params)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise
    
    # Tool Implementations
    
    async def llm_complete(self, model: str, prompt: str, max_tokens: int = 1000) -> Dict:
        """Generate text using LLM"""
        try:
            if model.startswith("gpt"):
                response = await openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return {
                    "text": response.choices[0].message.content,
                    "model": model,
                    "tokens": response.usage.total_tokens
                }
            elif model.startswith("claude"):
                response = anthropic_client.messages.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return {
                    "text": response.content[0].text,
                    "model": model
                }
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            raise
    
    async def search_web(self, query: str, max_results: int = 5) -> Dict:
        """Search the web using Tavily"""
        try:
            results = tavily_client.search(query, max_results=max_results)
            return {
                "query": query,
                "results": results.get("results", []),
                "answer": results.get("answer"),
                "source": "tavily"
            }
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            raise
    
    async def research_analyze(self, topic: str, depth: str = "standard") -> Dict:
        """Perform deep analysis on a topic"""
        # First, search for information
        search_results = await self.search_web(topic, max_results=10)
        
        # Then analyze with LLM
        analysis_prompt = f"""
        Analyze the following topic: {topic}
        
        Based on these search results:
        {json.dumps(search_results['results'], indent=2)}
        
        Provide a {depth} analysis including:
        1. Key findings
        2. Important patterns
        3. Recommendations
        4. Potential risks or concerns
        """
        
        analysis = await self.llm_complete("gpt-4-turbo-preview", analysis_prompt, 2000)
        
        return {
            "topic": topic,
            "depth": depth,
            "sources": search_results['results'],
            "analysis": analysis['text']
        }
    
    async def code_review(self, code: str, language: str, focus: List[str] = None) -> Dict:
        """Review code for quality and security"""
        focus_areas = focus or ["security", "performance", "readability", "best-practices"]
        
        review_prompt = f"""
        Review the following {language} code:
        
        ```{language}
        {code}
        ```
        
        Focus on: {', '.join(focus_areas)}
        
        Provide:
        1. Security issues (if any)
        2. Performance improvements
        3. Code quality suggestions
        4. Best practices violations
        5. Overall score (1-10)
        """
        
        review = await self.llm_complete("gpt-4-turbo-preview", review_prompt, 1500)
        
        return {
            "language": language,
            "focus_areas": focus_areas,
            "review": review['text'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def data_extract(self, text: str, schema: Dict) -> Dict:
        """Extract structured data from text"""
        extraction_prompt = f"""
        Extract data from the following text according to the schema:
        
        Text: {text}
        
        Schema: {json.dumps(schema, indent=2)}
        
        Return the extracted data as valid JSON matching the schema.
        """
        
        result = await self.llm_complete("gpt-4-turbo-preview", extraction_prompt, 1000)
        
        try:
            extracted = json.loads(result['text'])
            return {
                "success": True,
                "data": extracted,
                "schema": schema
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse extracted data",
                "raw": result['text']
            }
    
    async def notion_operation(self, operation: str, data: Dict) -> Dict:
        """Interact with Notion API"""
        # This would integrate with the notion-sync service
        return {
            "operation": operation,
            "status": "queued",
            "data": data,
            "message": "Operation forwarded to notion-sync service"
        }
    
    async def slack_operation(self, channel: str, message: str) -> Dict:
        """Send message to Slack"""
        # Placeholder for Slack integration
        return {
            "channel": channel,
            "message": message,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def check_health(self, services: List[str] = None) -> Dict:
        """Check health of external services"""
        services = services or ["openai", "anthropic", "tavily", "notion"]
        health_status = {}
        
        for service in services:
            try:
                if service == "openai":
                    # Quick API check
                    await openai_client.models.list()
                    health_status[service] = "healthy"
                elif service == "anthropic":
                    # Check Anthropic
                    health_status[service] = "healthy" if anthropic_client else "unknown"
                else:
                    health_status[service] = "not_implemented"
            except Exception as e:
                health_status[service] = f"unhealthy: {str(e)}"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": health_status,
            "overall": "healthy" if all(v == "healthy" for v in health_status.values()) else "degraded"
        }

# Initialize registry
tool_registry = ToolRegistry()

# API Models
class ToolExecutionRequest(BaseModel):
    tool: str = Field(..., description="Tool name to execute")
    parameters: Dict = Field(..., description="Tool parameters")
    context: Optional[Dict] = Field(None, description="Additional context")

class ToolExecutionResponse(BaseModel):
    success: bool
    tool: str
    result: Optional[Any]
    error: Optional[str]
    execution_time: float

# API Endpoints
@app.get("/")
async def root():
    """Health check and service info"""
    return {
        "service": "Sophia AIOS Tool Server",
        "status": "operational",
        "version": "1.0.0",
        "tools_available": len(tool_registry.tools)
    }

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools_info = {}
    for name, tool in tool_registry.tools.items():
        tools_info[name] = {
            "description": tool["metadata"]["description"],
            "parameters": tool["metadata"]["parameters"],
            "usage_count": tool["usage_count"],
            "last_used": tool["last_used"]
        }
    return {"tools": tools_info}

@app.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific tool"""
    import time
    start_time = time.time()
    
    try:
        result = await tool_registry.execute(request.tool, request.parameters)
        execution_time = time.time() - start_time
        
        return ToolExecutionResponse(
            success=True,
            tool=request.tool,
            result=result,
            error=None,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Tool execution failed: {e}")
        
        return ToolExecutionResponse(
            success=False,
            tool=request.tool,
            result=None,
            error=str(e),
            execution_time=execution_time
        )

@app.post("/batch")
async def batch_execute(requests: List[ToolExecutionRequest]):
    """Execute multiple tools in parallel"""
    tasks = []
    for req in requests:
        tasks.append(tool_registry.execute(req.tool, req.parameters))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "total": len(requests),
        "successful": sum(1 for r in results if not isinstance(r, Exception)),
        "failed": sum(1 for r in results if isinstance(r, Exception)),
        "results": results
    }

@app.get("/stats")
async def get_stats():
    """Get usage statistics"""
    total_usage = sum(tool["usage_count"] for tool in tool_registry.tools.values())
    most_used = max(tool_registry.tools.items(), 
                   key=lambda x: x[1]["usage_count"]) if tool_registry.tools else None
    
    return {
        "total_tools": len(tool_registry.tools),
        "total_executions": total_usage,
        "most_used_tool": most_used[0] if most_used else None,
        "tools_stats": {
            name: {
                "usage_count": tool["usage_count"],
                "last_used": tool["last_used"]
            }
            for name, tool in tool_registry.tools.items()
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sophia AIOS Tool Server...")
    logger.info(f"Registered {len(tool_registry.tools)} tools")
    uvicorn.run(app, host="0.0.0.0", port=8101)
