#!/usr/bin/env python3
"""
Integrated CLI - Direct AI orchestration without the translation bullshit
"""
import os
import sys
import json
import requests
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import openai
from anthropic import Anthropic

# Load environment
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

class IntegratedSwarm:
    """Direct AI orchestration - no middleman bullshit"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.mcp_url = "http://localhost:8001"
        
        # Initialize clients
        openai.api_key = self.openai_key
        self.anthropic = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
    def run_command(self, cmd: str) -> str:
        """Run shell command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def store_context(self, content: str, session_id: str = "main"):
        """Store context in MCP memory"""
        try:
            response = requests.post(
                f"{self.mcp_url}/context/store",
                json={"session_id": session_id, "content": content}
            )
            return response.json() if response.ok else None
        except:
            return None
    
    def query_context(self, query: str, session_id: str = "main"):
        """Query context from MCP memory"""
        try:
            response = requests.post(
                f"{self.mcp_url}/context/query",
                json={"session_id": session_id, "query": query}
            )
            return response.json() if response.ok else None
        except:
            return None
    
    def call_openrouter(self, model: str, prompt: str) -> str:
        """Direct OpenRouter API call"""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4096
                }
            )
            if response.ok:
                return response.json()['choices'][0]['message']['content']
            return f"Error: {response.text}"
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_repository(self):
        """Analyze the repository structure"""
        print("\n🔍 Analyzing Repository Structure...")
        
        # Get branch info
        branches = self.run_command("git branch -a")
        print(f"\n📊 Branches Found:\n{branches}")
        
        # Get file counts per branch
        for branch in branches.split('\n'):
            if branch.strip():
                branch_name = branch.strip().replace('* ', '').replace('remotes/origin/', '')
                file_count = self.run_command(f"git ls-tree -r {branch_name} --name-only 2>/dev/null | wc -l").strip()
                if file_count and file_count != '0':
                    print(f"  {branch_name}: {file_count} files")
        
        # Store analysis in memory
        self.store_context(f"Repository analysis: {branches}", "repo_analysis")
        
        return branches
    
    def plan_with_ai(self, goal: str):
        """Use best AI for planning"""
        print(f"\n🧠 Planning: {goal}")
        
        # Try Claude first, fall back to OpenRouter
        if self.anthropic:
            try:
                response = self.anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": f"Create a detailed plan for: {goal}"}],
                    max_tokens=4096
                )
                plan = response.content[0].text
                print(f"\n📋 Plan (via Claude):\n{plan}")
                self.store_context(f"Plan: {plan}", "planning")
                return plan
            except:
                pass
        
        # Fall back to OpenRouter
        plan = self.call_openrouter("anthropic/claude-3-opus-20240229", f"Create a detailed plan for: {goal}")
        print(f"\n📋 Plan (via OpenRouter):\n{plan}")
        self.store_context(f"Plan: {plan}", "planning")
        return plan
    
    def execute_branch_reorg(self):
        """Execute the branch reorganization directly"""
        print("\n🚀 Executing Branch Reorganization...")
        
        commands = [
            # Delete duplicates
            "git branch -D unified-dev 2>/dev/null",
            "git branch -D backup/pre-swarm-20250812-013122 2>/dev/null",
            
            # Archive old features as tags
            "git tag archive/feat-autonomous-agent feat/autonomous-agent 2>/dev/null",
            "git tag archive/feat-initial-setup feat/initial-setup 2>/dev/null",
            "git tag archive/feat-integration-agno feat/integration-agno 2>/dev/null",
            "git tag archive/feat-esc-bootstrap feat/esc-bootstrap-and-fixes 2>/dev/null",
            "git tag archive/feat-github-security feat/github-security 2>/dev/null",
            
            # Delete archived branches
            "git branch -D feat/autonomous-agent 2>/dev/null",
            "git branch -D feat/initial-setup 2>/dev/null",
            "git branch -D feat/integration-agno 2>/dev/null",
            "git branch -D feat/esc-bootstrap-and-fixes 2>/dev/null",
            "git branch -D feat/github-security 2>/dev/null",
            
            # Show final state
            "echo '\n✅ Final Branch Structure:' && git branch"
        ]
        
        for cmd in commands:
            print(f"  → {cmd}")
            result = self.run_command(cmd)
            if result and "error" not in result.lower():
                print(f"    ✓ {result.strip()}")
        
        # Store result
        final_branches = self.run_command("git branch")
        self.store_context(f"Branch reorganization complete: {final_branches}", "repo_reorg")
        
        return final_branches
    
    def interactive_mode(self):
        """Interactive CLI mode"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          🎯 INTEGRATED AI SWARM - NO BULLSHIT MODE            ║
╚══════════════════════════════════════════════════════════════╝

Commands:
  analyze     - Analyze repository structure
  plan <goal> - AI creates a plan for your goal
  execute     - Execute branch reorganization
  query <q>   - Query stored memory
  git <cmd>   - Run any git command
  ai <prompt> - Direct AI query
  quit        - Exit
        """)
        
        while True:
            try:
                cmd = input("\n🎯 > ").strip()
                
                if cmd == "quit":
                    break
                elif cmd == "analyze":
                    self.analyze_repository()
                elif cmd.startswith("plan "):
                    goal = cmd[5:]
                    self.plan_with_ai(goal)
                elif cmd == "execute":
                    self.execute_branch_reorg()
                elif cmd.startswith("query "):
                    query = cmd[6:]
                    result = self.query_context(query)
                    print(f"Memory: {result}")
                elif cmd.startswith("git "):
                    git_cmd = cmd[4:]
                    result = self.run_command(f"git {git_cmd}")
                    print(result)
                elif cmd.startswith("ai "):
                    prompt = cmd[3:]
                    response = self.call_openrouter("anthropic/claude-3-opus-20240229", prompt)
                    print(f"AI: {response}")
                else:
                    print("Unknown command. Try 'analyze', 'plan', 'execute', 'query', 'git', or 'ai'")
                    
            except KeyboardInterrupt:
                print("\n\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    swarm = IntegratedSwarm()
    
    # If arguments provided, execute directly
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        if command == "analyze":
            swarm.analyze_repository()
        elif command.startswith("plan "):
            swarm.plan_with_ai(command[5:])
        elif command == "execute":
            swarm.execute_branch_reorg()
        else:
            print(f"Unknown command: {command}")
    else:
        # Interactive mode
        swarm.interactive_mode()
