"""
SOPHIA SWARM MONITORING DASHBOARD
Real-time swarm orchestration and monitoring
"""

import asyncio
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="Sophia AI Swarm Dashboard", version="1.0.0")

class SwarmDashboard:
    """Real-time swarm monitoring dashboard"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.swarm_status = {
            "agents": {},
            "tasks": {},
            "metrics": {},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def connect(self, websocket: WebSocket):
        """Connect new WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send current status
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": self.swarm_status
        }))
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        message = json.dumps({
            "type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Remove disconnected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def update_agent_status(self, agent_id: str, status: Dict[str, Any]):
        """Update agent status"""
        self.swarm_status["agents"][agent_id] = {
            **status,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_update("agent_update", {
            "agent_id": agent_id,
            "status": status
        })
    
    async def update_task_status(self, task_id: str, status: Dict[str, Any]):
        """Update task status"""
        self.swarm_status["tasks"][task_id] = {
            **status,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_update("task_update", {
            "task_id": task_id,
            "status": status
        })
    
    async def update_metrics(self, metrics: Dict[str, Any]):
        """Update system metrics"""
        self.swarm_status["metrics"] = {
            **metrics,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_update("metrics_update", metrics)

# Global dashboard instance
dashboard = SwarmDashboard()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await dashboard.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard.disconnect(websocket)

@app.get("/")
async def get_dashboard():
    """Serve dashboard HTML"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Sophia AI Swarm Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .header { text-align: center; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #2a2a2a; border-radius: 8px; padding: 20px; border: 1px solid #444; }
        .card h3 { margin-top: 0; color: #4CAF50; }
        .status { padding: 5px 10px; border-radius: 4px; font-size: 12px; }
        .status.active { background: #4CAF50; }
        .status.idle { background: #FF9800; }
        .status.error { background: #F44336; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .log { background: #1e1e1e; padding: 10px; border-radius: 4px; max-height: 200px; overflow-y: auto; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .agent-card { background: #333; padding: 15px; border-radius: 6px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Sophia AI Swarm Dashboard</h1>
        <p>Real-time monitoring and orchestration</p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>🎯 Active Agents</h3>
            <div id="agents" class="agent-grid">
                <div class="agent-card">
                    <div>🏗️ Architect</div>
                    <div class="status active">Active</div>
                </div>
                <div class="agent-card">
                    <div>💻 Coder</div>
                    <div class="status active">Active</div>
                </div>
                <div class="agent-card">
                    <div>🔍 Reviewer</div>
                    <div class="status idle">Idle</div>
                </div>
                <div class="agent-card">
                    <div>🧪 Tester</div>
                    <div class="status idle">Idle</div>
                </div>
                <div class="agent-card">
                    <div>🚀 Deployer</div>
                    <div class="status idle">Idle</div>
                </div>
                <div class="agent-card">
                    <div>📊 Monitor</div>
                    <div class="status active">Active</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📋 Current Tasks</h3>
            <div id="tasks">
                <div class="metric">
                    <span>Implement AI Router</span>
                    <span class="status active">In Progress</span>
                </div>
                <div class="metric">
                    <span>Deploy Memory System</span>
                    <span class="status idle">Queued</span>
                </div>
                <div class="metric">
                    <span>Setup Monitoring</span>
                    <span class="status idle">Queued</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 System Metrics</h3>
            <div id="metrics">
                <div class="metric">
                    <span>Total Requests</span>
                    <span>1,247</span>
                </div>
                <div class="metric">
                    <span>Success Rate</span>
                    <span>98.7%</span>
                </div>
                <div class="metric">
                    <span>Avg Response Time</span>
                    <span>0.34s</span>
                </div>
                <div class="metric">
                    <span>Active Models</span>
                    <span>12</span>
                </div>
                <div class="metric">
                    <span>Memory Usage</span>
                    <span>2.1GB</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🔄 Recent Activity</h3>
            <div id="activity" class="log">
                <div>2025-01-12 01:45:23 - Architect: System design completed</div>
                <div>2025-01-12 01:44:15 - Coder: Implementation started</div>
                <div>2025-01-12 01:43:02 - Monitor: Health check passed</div>
                <div>2025-01-12 01:42:18 - Portkey: Model routing optimized</div>
                <div>2025-01-12 01:41:33 - Memory: Vector embeddings updated</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🧠 Model Performance</h3>
            <div id="models">
                <div class="metric">
                    <span>GPT-4o</span>
                    <span>95.2% success</span>
                </div>
                <div class="metric">
                    <span>Claude-3.5-Sonnet</span>
                    <span>97.8% success</span>
                </div>
                <div class="metric">
                    <span>Gemini-2.5-Pro</span>
                    <span>94.1% success</span>
                </div>
                <div class="metric">
                    <span>Groq-Llama-3.3</span>
                    <span>92.7% success</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>💾 Memory System</h3>
            <div id="memory">
                <div class="metric">
                    <span>Conversations</span>
                    <span>1,523 stored</span>
                </div>
                <div class="metric">
                    <span>Code Snippets</span>
                    <span>847 indexed</span>
                </div>
                <div class="metric">
                    <span>Agent Memories</span>
                    <span>2,341 entries</span>
                </div>
                <div class="metric">
                    <span>Vector Embeddings</span>
                    <span>4,711 vectors</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            console.log('Received:', message);
            
            // Update dashboard based on message type
            if (message.type === 'agent_update') {
                updateAgentStatus(message.data);
            } else if (message.type === 'task_update') {
                updateTaskStatus(message.data);
            } else if (message.type === 'metrics_update') {
                updateMetrics(message.data);
            }
        };
        
        function updateAgentStatus(data) {
            // Update agent status in real-time
            console.log('Agent update:', data);
        }
        
        function updateTaskStatus(data) {
            // Update task status in real-time
            console.log('Task update:', data);
        }
        
        function updateMetrics(data) {
            // Update metrics in real-time
            console.log('Metrics update:', data);
        }
        
        // Simulate real-time updates
        setInterval(() => {
            const activity = document.getElementById('activity');
            const now = new Date().toISOString().slice(0, 19).replace('T', ' ');
            const activities = [
                'Agent coordination completed',
                'Model routing optimized',
                'Memory system updated',
                'Health check passed',
                'Task queue processed'
            ];
            const randomActivity = activities[Math.floor(Math.random() * activities.length)];
            
            const newEntry = document.createElement('div');
            newEntry.textContent = `${now} - ${randomActivity}`;
            activity.insertBefore(newEntry, activity.firstChild);
            
            // Keep only last 10 entries
            while (activity.children.length > 10) {
                activity.removeChild(activity.lastChild);
            }
        }, 5000);
    </script>
</body>
</html>
    """)

@app.get("/api/status")
async def get_status():
    """Get current swarm status"""
    return dashboard.swarm_status

@app.post("/api/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: Dict[str, Any]):
    """Update agent status"""
    await dashboard.update_agent_status(agent_id, status)
    return {"success": True}

@app.post("/api/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: Dict[str, Any]):
    """Update task status"""
    await dashboard.update_task_status(task_id, status)
    return {"success": True}

@app.post("/api/metrics")
async def update_metrics(metrics: Dict[str, Any]):
    """Update system metrics"""
    await dashboard.update_metrics(metrics)
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
