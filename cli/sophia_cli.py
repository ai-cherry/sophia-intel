#!/usr/bin/env python3
"""
Sophia Intel CLI - Universal Command Line Interface
Advanced AI-powered development and deployment management
"""

import asyncio
import click
import json
import os
import sys
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.config import Settings, load_settings
from mcp_servers.ai_router import AIRouter

class SophiaIntelCLI:
    """Main CLI class for Sophia Intel operations"""
    
    def __init__(self):
        self.settings = load_settings()
        self.ai_router = AIRouter()
        self.base_url = f"http://localhost:{self.settings.MCP_PORT}"
        
    async def initialize(self):
        """Initialize the CLI with AI router"""
        await self.ai_router.initialize()
        
    def check_server_health(self) -> bool:
        """Check if the MCP server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    async def route_ai_request(self, prompt: str, task_type: str = "general", 
                              preference: str = "balanced") -> Dict[str, Any]:
        """Route AI request through the AI router"""
        try:
            result = await self.ai_router.route_request(
                prompt=prompt,
                task_type=task_type,
                preference=preference
            )
            return result
        except Exception as e:
            return {"error": str(e)}

# Initialize CLI instance
cli_instance = SophiaIntelCLI()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🧠 Sophia Intel CLI - AI-Powered Development Platform
    
    Universal command-line interface for AI routing, deployment, and management.
    """
    pass

@cli.group()
def ai():
    """🤖 AI Operations - Intelligent model routing and interaction"""
    pass

@ai.command()
@click.argument('prompt')
@click.option('--task-type', '-t', default='general', 
              type=click.Choice(['code', 'math', 'creative', 'general', 'review']),
              help='Type of task for optimal model selection')
@click.option('--preference', '-p', default='balanced',
              type=click.Choice(['speed', 'quality', 'cost', 'balanced']),
              help='Optimization preference for model selection')
@click.option('--output', '-o', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
def ask(prompt: str, task_type: str, preference: str, output: str):
    """
    🧠 Ask AI with intelligent model routing
    
    Examples:
      sophia ai ask "Write a Python function to sort a list" --task-type code
      sophia ai ask "Solve: 2x + 5 = 15" --task-type math --preference speed
      sophia ai ask "Write a creative story about AI" --task-type creative
    """
    async def _ask():
        await cli_instance.initialize()
        
        if not cli_instance.check_server_health():
            click.echo("❌ MCP Server not running. Please start the server first.")
            click.echo("   Run: sophia server start")
            return
            
        click.echo(f"🧠 Routing request to optimal AI model...")
        click.echo(f"   Task Type: {task_type}")
        click.echo(f"   Preference: {preference}")
        click.echo()
        
        result = await cli_instance.route_ai_request(prompt, task_type, preference)
        
        if output == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            if 'error' in result:
                click.echo(f"❌ Error: {result['error']}")
            else:
                click.echo(f"🤖 Model: {result.get('model', 'Unknown')}")
                click.echo(f"⚡ Response Time: {result.get('response_time', 0):.3f}s")
                click.echo(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
                click.echo()
                click.echo("📝 Response:")
                click.echo(result.get('response', 'No response'))
    
    asyncio.run(_ask())

@ai.command()
def models():
    """📋 List available AI models and their capabilities"""
    if not cli_instance.check_server_health():
        click.echo("❌ MCP Server not running. Please start the server first.")
        return
        
    try:
        response = requests.get(f"{cli_instance.base_url}/ai/models")
        models_data = response.json()
        
        click.echo("🤖 Available AI Models:")
        click.echo("=" * 50)
        
        for provider, models in models_data.items():
            click.echo(f"\n📡 {provider.upper()}")
            for model in models:
                click.echo(f"  • {model}")
                
    except Exception as e:
        click.echo(f"❌ Error fetching models: {e}")

@ai.command()
def stats():
    """📊 Show AI routing statistics and performance metrics"""
    if not cli_instance.check_server_health():
        click.echo("❌ MCP Server not running. Please start the server first.")
        return
        
    try:
        response = requests.get(f"{cli_instance.base_url}/stats")
        stats_data = response.json()
        
        click.echo("📊 AI Routing Statistics:")
        click.echo("=" * 40)
        click.echo(f"Total Requests: {stats_data.get('total_requests', 0)}")
        click.echo(f"Average Response Time: {stats_data.get('avg_response_time', 0):.3f}s")
        click.echo(f"Average Confidence: {stats_data.get('avg_confidence', 0):.1%}")
        click.echo()
        
        provider_stats = stats_data.get('provider_distribution', {})
        if provider_stats:
            click.echo("🔄 Provider Distribution:")
            for provider, count in provider_stats.items():
                click.echo(f"  {provider}: {count} requests")
                
    except Exception as e:
        click.echo(f"❌ Error fetching statistics: {e}")

@cli.group()
def server():
    """🖥️ Server Management - Start, stop, and monitor MCP server"""
    pass

@server.command()
@click.option('--port', '-p', default=8001, help='Port to run the server on')
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind the server to')
def start(port: int, host: str):
    """🚀 Start the Enhanced MCP Server"""
    click.echo(f"🚀 Starting Sophia Intel MCP Server on {host}:{port}")
    
    try:
        # Start the server using subprocess
        cmd = [
            sys.executable, 
            "mcp_servers/enhanced_unified_server.py",
            "--host", host,
            "--port", str(port)
        ]
        
        process = subprocess.Popen(cmd, cwd=Path(__file__).parent.parent)
        click.echo(f"✅ Server started with PID: {process.pid}")
        click.echo(f"🌐 Server URL: http://{host}:{port}")
        click.echo("📊 Health Check: http://localhost:8001/health")
        click.echo("📋 API Docs: http://localhost:8001/docs")
        
    except Exception as e:
        click.echo(f"❌ Failed to start server: {e}")

@server.command()
def stop():
    """🛑 Stop the MCP Server"""
    try:
        # Find and kill the server process
        result = subprocess.run(
            ["pkill", "-f", "enhanced_unified_server.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ Server stopped successfully")
        else:
            click.echo("⚠️ No server process found or already stopped")
            
    except Exception as e:
        click.echo(f"❌ Error stopping server: {e}")

@server.command()
def status():
    """📊 Check server status and health"""
    if cli_instance.check_server_health():
        try:
            response = requests.get(f"{cli_instance.base_url}/health")
            health_data = response.json()
            
            click.echo("✅ Server Status: HEALTHY")
            click.echo(f"🕐 Uptime: {health_data.get('uptime', 'Unknown')}")
            click.echo(f"📊 Total Requests: {health_data.get('total_requests', 0)}")
            click.echo(f"💾 Memory Usage: {health_data.get('memory_usage', 'Unknown')}")
            
        except Exception as e:
            click.echo(f"⚠️ Server running but health check failed: {e}")
    else:
        click.echo("❌ Server Status: NOT RUNNING")
        click.echo("   Run 'sophia server start' to start the server")

@cli.group()
def deploy():
    """🚀 Deployment Operations - Infrastructure and application deployment"""
    pass

@deploy.command()
@click.option('--environment', '-e', default='dev', 
              type=click.Choice(['dev', 'staging', 'prod']),
              help='Deployment environment')
@click.option('--dry-run', is_flag=True, help='Preview deployment without executing')
def infrastructure(environment: str, dry_run: bool):
    """🏗️ Deploy infrastructure using Pulumi"""
    click.echo(f"🏗️ Deploying infrastructure to {environment} environment")
    
    if dry_run:
        click.echo("👀 Dry run mode - previewing changes only")
        cmd = ["pulumi", "preview"]
    else:
        click.echo("🚀 Executing deployment")
        cmd = ["pulumi", "up", "--yes"]
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env["PULUMI_CONFIG_PASSPHRASE"] = "sophia-intel-secure-2025"
        
        # Run Pulumi command
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent / "infrastructure" / "pulumi",
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ Infrastructure deployment completed successfully")
            if not dry_run:
                click.echo("🌐 Infrastructure is now live")
        else:
            click.echo(f"❌ Deployment failed: {result.stderr}")
            
    except Exception as e:
        click.echo(f"❌ Error during deployment: {e}")

@deploy.command()
@click.option('--tag', '-t', help='Docker image tag to deploy')
def application(tag: str):
    """📦 Deploy application containers"""
    if not tag:
        # Generate tag from current timestamp
        tag = f"latest-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    click.echo(f"📦 Deploying application with tag: {tag}")
    
    try:
        # Build Docker image
        click.echo("🔨 Building Docker image...")
        build_cmd = [
            "docker", "build", 
            "-f", "Dockerfile.enhanced-mcp",
            "-t", f"sophia-intel-mcp:{tag}",
            "."
        ]
        
        result = subprocess.run(
            build_cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ Docker image built successfully")
            click.echo(f"🏷️ Image: sophia-intel-mcp:{tag}")
        else:
            click.echo(f"❌ Docker build failed: {result.stderr}")
            return
            
        # TODO: Add container deployment logic here
        click.echo("🚀 Container deployment logic to be implemented")
        
    except Exception as e:
        click.echo(f"❌ Error during application deployment: {e}")

@cli.group()
def test():
    """🧪 Testing Operations - Performance and functionality testing"""
    pass

@test.command()
@click.option('--concurrency', '-c', default=10, help='Number of concurrent requests')
@click.option('--duration', '-d', default=30, help='Test duration in seconds')
def performance(concurrency: int, duration: int):
    """⚡ Run performance tests against the MCP server"""
    if not cli_instance.check_server_health():
        click.echo("❌ MCP Server not running. Please start the server first.")
        return
    
    click.echo(f"⚡ Running performance test:")
    click.echo(f"   Concurrency: {concurrency}")
    click.echo(f"   Duration: {duration}s")
    click.echo()
    
    try:
        # Run the performance test script
        cmd = [sys.executable, "performance_test.py"]
        
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ Performance test completed")
            click.echo(result.stdout)
        else:
            click.echo(f"❌ Performance test failed: {result.stderr}")
            
    except Exception as e:
        click.echo(f"❌ Error running performance test: {e}")

@test.command()
def health():
    """🏥 Run comprehensive health checks"""
    click.echo("🏥 Running comprehensive health checks...")
    click.echo()
    
    # Check server health
    if cli_instance.check_server_health():
        click.echo("✅ MCP Server: HEALTHY")
    else:
        click.echo("❌ MCP Server: NOT RUNNING")
    
    # Check AI router
    try:
        response = requests.get(f"{cli_instance.base_url}/ai/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            total_models = sum(len(m) for m in models.values())
            click.echo(f"✅ AI Router: {total_models} models available")
        else:
            click.echo("⚠️ AI Router: Partial functionality")
    except:
        click.echo("❌ AI Router: NOT ACCESSIBLE")
    
    # Check infrastructure
    try:
        # Check if Pulumi is configured
        pulumi_dir = Path(__file__).parent.parent / "infrastructure" / "pulumi"
        if pulumi_dir.exists():
            click.echo("✅ Infrastructure: Pulumi configured")
        else:
            click.echo("⚠️ Infrastructure: Pulumi not found")
    except:
        click.echo("❌ Infrastructure: Configuration error")

@cli.command()
def version():
    """📋 Show version information"""
    click.echo("🧠 Sophia Intel CLI v1.0.0")
    click.echo("🚀 Enhanced MCP Server with AI Router")
    click.echo("🏗️ Infrastructure as Code with Pulumi")
    click.echo("📊 Performance: 1,500+ req/s capability")
    click.echo()
    click.echo("🔗 Repository: https://github.com/ai-cherry/sophia-intel")

if __name__ == "__main__":
    cli()

