"""
LANGGRAPH SWARM ORCHESTRATION SYSTEM
Multi-agent coordination with phidata integration
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.anthropic import Claude
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.python import PythonTools
from phi.tools.shell import ShellTools
from phi.tools.file import FileTools
from phi.storage.agent.postgres import PgAgentStorage
import os

class AgentRole(Enum):
    ARCHITECT = "architect"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DEPLOYER = "deployer"
    MONITOR = "monitor"

@dataclass
class SwarmState:
    messages: List[Dict[str, Any]]
    current_task: str
    completed_tasks: List[str]
    active_agents: List[str]
    artifacts: Dict[str, Any]
    context: Dict[str, Any]

class SophiaSwarmOrchestrator:
    """Advanced swarm orchestration with LangGraph and phidata"""
    
    def __init__(self):
        # Initialize storage
        self.storage = PgAgentStorage(
            table_name="sophia_agents",
            db_url=os.getenv("DATABASE_URL", "postgresql://localhost/sophia")
        )
        
        # Initialize specialized agents
        self.agents = self._initialize_agents()
        
        # Create LangGraph workflow
        self.workflow = self._create_workflow()
    
    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize specialized AI agents"""
        
        # Architect Agent - System design and planning
        architect = Agent(
            name="SophiaArchitect",
            role="Senior Software Architect",
            model=Claude(model="claude-3-5-sonnet"),
            tools=[DuckDuckGo(), FileTools()],
            instructions=[
                "You are a senior software architect specializing in AI systems",
                "Design scalable, maintainable system architectures",
                "Consider performance, security, and best practices",
                "Create detailed technical specifications"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=10
        )
        
        # Coder Agent - Implementation and development
        coder = Agent(
            name="SophiaCoder",
            role="Senior Full-Stack Developer",
            model=OpenAIChat(model="gpt-4o"),
            tools=[PythonTools(), FileTools(), ShellTools()],
            instructions=[
                "You are an expert full-stack developer",
                "Write clean, efficient, well-documented code",
                "Follow best practices and design patterns",
                "Implement comprehensive error handling"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=15
        )
        
        # Reviewer Agent - Code review and quality assurance
        reviewer = Agent(
            name="SophiaReviewer",
            role="Senior Code Reviewer",
            model=Claude(model="claude-3-5-sonnet"),
            tools=[FileTools(), PythonTools()],
            instructions=[
                "You are a senior code reviewer focused on quality",
                "Review code for bugs, security issues, and best practices",
                "Provide constructive feedback and suggestions",
                "Ensure code meets enterprise standards"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=10
        )
        
        # Tester Agent - Testing and validation
        tester = Agent(
            name="SophiaTester",
            role="Senior QA Engineer",
            model=Gemini(model="gemini-2.5-pro"),
            tools=[PythonTools(), ShellTools(), FileTools()],
            instructions=[
                "You are a senior QA engineer specializing in automated testing",
                "Create comprehensive test suites and scenarios",
                "Perform integration and performance testing",
                "Ensure high code coverage and quality"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=10
        )
        
        # Deployer Agent - Deployment and infrastructure
        deployer = Agent(
            name="SophiaDeployer",
            role="Senior DevOps Engineer",
            model=OpenAIChat(model="gpt-4o"),
            tools=[ShellTools(), FileTools()],
            instructions=[
                "You are a senior DevOps engineer",
                "Handle deployment, CI/CD, and infrastructure",
                "Ensure scalable and secure deployments",
                "Monitor and optimize system performance"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=10
        )
        
        # Monitor Agent - Monitoring and analytics
        monitor = Agent(
            name="SophiaMonitor",
            role="Senior Site Reliability Engineer",
            model=Claude(model="claude-3-haiku"),
            tools=[PythonTools(), ShellTools()],
            instructions=[
                "You are a senior SRE focused on system reliability",
                "Monitor system health and performance",
                "Detect and resolve issues proactively",
                "Provide insights and recommendations"
            ],
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=5
        )
        
        return {
            AgentRole.ARCHITECT.value: architect,
            AgentRole.CODER.value: coder,
            AgentRole.REVIEWER.value: reviewer,
            AgentRole.TESTER.value: tester,
            AgentRole.DEPLOYER.value: deployer,
            AgentRole.MONITOR.value: monitor
        }
    
    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for swarm coordination"""
        
        workflow = StateGraph(SwarmState)
        
        # Add nodes for each agent role
        workflow.add_node("architect", self._architect_node)
        workflow.add_node("coder", self._coder_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("tester", self._tester_node)
        workflow.add_node("deployer", self._deployer_node)
        workflow.add_node("monitor", self._monitor_node)
        workflow.add_node("coordinator", self._coordinator_node)
        
        # Define workflow edges
        workflow.set_entry_point("coordinator")
        
        # Coordinator decides next step
        workflow.add_conditional_edges(
            "coordinator",
            self._route_next_agent,
            {
                "architect": "architect",
                "coder": "coder",
                "reviewer": "reviewer",
                "tester": "tester",
                "deployer": "deployer",
                "monitor": "monitor",
                "end": END
            }
        )
        
        # All agents return to coordinator
        for agent in ["architect", "coder", "reviewer", "tester", "deployer", "monitor"]:
            workflow.add_edge(agent, "coordinator")
        
        return workflow.compile()
    
    async def _architect_node(self, state: SwarmState) -> SwarmState:
        """Architect agent node"""
        agent = self.agents[AgentRole.ARCHITECT.value]
        
        response = agent.run(
            f"Task: {state.current_task}\n"
            f"Context: {json.dumps(state.context, indent=2)}\n"
            f"Please provide architectural design and specifications."
        )
        
        state.messages.append({
            "role": "architect",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract artifacts (diagrams, specs, etc.)
        if "architecture" not in state.artifacts:
            state.artifacts["architecture"] = {}
        
        state.artifacts["architecture"]["design"] = response.content
        state.active_agents.append("architect")
        
        return state
    
    async def _coder_node(self, state: SwarmState) -> SwarmState:
        """Coder agent node"""
        agent = self.agents[AgentRole.CODER.value]
        
        # Get architecture context
        arch_context = state.artifacts.get("architecture", {})
        
        response = agent.run(
            f"Task: {state.current_task}\n"
            f"Architecture: {json.dumps(arch_context, indent=2)}\n"
            f"Previous messages: {json.dumps(state.messages[-3:], indent=2)}\n"
            f"Please implement the required functionality."
        )
        
        state.messages.append({
            "role": "coder",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract code artifacts
        if "code" not in state.artifacts:
            state.artifacts["code"] = {}
        
        state.artifacts["code"]["implementation"] = response.content
        state.active_agents.append("coder")
        
        return state
    
    async def _reviewer_node(self, state: SwarmState) -> SwarmState:
        """Reviewer agent node"""
        agent = self.agents[AgentRole.REVIEWER.value]
        
        # Get code context
        code_context = state.artifacts.get("code", {})
        
        response = agent.run(
            f"Task: Review and validate implementation\n"
            f"Code: {json.dumps(code_context, indent=2)}\n"
            f"Please review for quality, security, and best practices."
        )
        
        state.messages.append({
            "role": "reviewer",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract review artifacts
        if "review" not in state.artifacts:
            state.artifacts["review"] = {}
        
        state.artifacts["review"]["feedback"] = response.content
        state.active_agents.append("reviewer")
        
        return state
    
    async def _tester_node(self, state: SwarmState) -> SwarmState:
        """Tester agent node"""
        agent = self.agents[AgentRole.TESTER.value]
        
        # Get implementation context
        code_context = state.artifacts.get("code", {})
        review_context = state.artifacts.get("review", {})
        
        response = agent.run(
            f"Task: Create and execute tests\n"
            f"Code: {json.dumps(code_context, indent=2)}\n"
            f"Review: {json.dumps(review_context, indent=2)}\n"
            f"Please create comprehensive tests and validate functionality."
        )
        
        state.messages.append({
            "role": "tester",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract test artifacts
        if "tests" not in state.artifacts:
            state.artifacts["tests"] = {}
        
        state.artifacts["tests"]["results"] = response.content
        state.active_agents.append("tester")
        
        return state
    
    async def _deployer_node(self, state: SwarmState) -> SwarmState:
        """Deployer agent node"""
        agent = self.agents[AgentRole.DEPLOYER.value]
        
        # Get all context for deployment
        all_artifacts = state.artifacts
        
        response = agent.run(
            f"Task: Deploy and configure system\n"
            f"Artifacts: {json.dumps(all_artifacts, indent=2)}\n"
            f"Please handle deployment and infrastructure setup."
        )
        
        state.messages.append({
            "role": "deployer",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract deployment artifacts
        if "deployment" not in state.artifacts:
            state.artifacts["deployment"] = {}
        
        state.artifacts["deployment"]["status"] = response.content
        state.active_agents.append("deployer")
        
        return state
    
    async def _monitor_node(self, state: SwarmState) -> SwarmState:
        """Monitor agent node"""
        agent = self.agents[AgentRole.MONITOR.value]
        
        # Get deployment context
        deployment_context = state.artifacts.get("deployment", {})
        
        response = agent.run(
            f"Task: Monitor and validate deployment\n"
            f"Deployment: {json.dumps(deployment_context, indent=2)}\n"
            f"Please monitor system health and performance."
        )
        
        state.messages.append({
            "role": "monitor",
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Extract monitoring artifacts
        if "monitoring" not in state.artifacts:
            state.artifacts["monitoring"] = {}
        
        state.artifacts["monitoring"]["status"] = response.content
        state.active_agents.append("monitor")
        
        return state
    
    async def _coordinator_node(self, state: SwarmState) -> SwarmState:
        """Coordinator node for workflow management"""
        
        # Analyze current state and determine next action
        completed_roles = set(state.active_agents)
        
        # Define workflow stages
        workflow_stages = [
            AgentRole.ARCHITECT.value,
            AgentRole.CODER.value,
            AgentRole.REVIEWER.value,
            AgentRole.TESTER.value,
            AgentRole.DEPLOYER.value,
            AgentRole.MONITOR.value
        ]
        
        # Find next stage
        for stage in workflow_stages:
            if stage not in completed_roles:
                state.context["next_agent"] = stage
                return state
        
        # All stages completed
        state.completed_tasks.append(state.current_task)
        state.context["next_agent"] = "end"
        
        return state
    
    def _route_next_agent(self, state: SwarmState) -> str:
        """Route to next agent based on workflow state"""
        return state.context.get("next_agent", "end")
    
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using the swarm"""
        
        initial_state = SwarmState(
            messages=[],
            current_task=task,
            completed_tasks=[],
            active_agents=[],
            artifacts={},
            context=context or {}
        )
        
        # Execute workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "task": task,
            "status": "completed",
            "messages": final_state.messages,
            "artifacts": final_state.artifacts,
            "active_agents": final_state.active_agents,
            "execution_time": datetime.utcnow().isoformat()
        }
    
    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        
        agent_status = {}
        for role, agent in self.agents.items():
            agent_status[role] = {
                "name": agent.name,
                "model": str(agent.model),
                "tools": [tool.__class__.__name__ for tool in agent.tools] if agent.tools else [],
                "active": True
            }
        
        return {
            "swarm_status": "operational",
            "agents": agent_status,
            "workflow_stages": [role.value for role in AgentRole],
            "timestamp": datetime.utcnow().isoformat()
        }

# Global swarm instance
_swarm_orchestrator = None

async def get_swarm_orchestrator() -> SophiaSwarmOrchestrator:
    global _swarm_orchestrator
    if _swarm_orchestrator is None:
        _swarm_orchestrator = SophiaSwarmOrchestrator()
    return _swarm_orchestrator
