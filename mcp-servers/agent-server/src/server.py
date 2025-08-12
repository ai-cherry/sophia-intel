"""
Sophia AIOS Agent Server - Continued
"""
                    
                    Provide your expert perspective as {agent_type}.
                    """
                    
                    response = agent.run(prompt, stream=False)
                    
                    round_log["contributions"][agent_type] = {
                        "response": response.content,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Update context with this contribution
                    context += f"\n\n{agent_type}: {response.content}"
                    
                except Exception as e:
                    logger.error(f"Agent {agent_type} collaboration failed: {e}")
                    round_log["contributions"][agent_type] = {"error": str(e)}
            
            collaboration_log.append(round_log)
        
        return collaboration_log
    
    def get_swarm_status(self, swarm_id: str) -> Dict:
        """Get status of a swarm"""
        if swarm_id not in self.swarms:
            return {"error": f"Swarm {swarm_id} not found"}
        
        swarm = self.swarms[swarm_id]
        return {
            "id": swarm["id"],
            "objective": swarm["objective"],
            "status": swarm["status"],
            "agents": list(swarm["agents"].keys()),
            "created_at": swarm["created_at"],
            "message_count": len(swarm["messages"])
        }
    
    def list_swarms(self) -> List[Dict]:
        """List all active swarms"""
        return [
            self.get_swarm_status(swarm_id)
            for swarm_id in self.swarms.keys()
        ]

# Initialize swarm manager
swarm_manager = AgentSwarm()

# API Models
class CreateSwarmRequest(BaseModel):
    swarm_id: str = Field(..., description="Unique swarm identifier")
    agent_types: List[str] = Field(..., description="Types of agents to include")
    objective: str = Field(..., description="Swarm objective")

class ExecuteTaskRequest(BaseModel):
    swarm_id: str = Field(..., description="Swarm to use")
    task: str = Field(..., description="Task to execute")
    agent_sequence: Optional[List[str]] = Field(None, description="Custom agent sequence")

class CollaborateRequest(BaseModel):
    swarm_id: str = Field(..., description="Swarm to use")
    topic: str = Field(..., description="Collaboration topic")
    rounds: int = Field(3, description="Number of collaboration rounds")

class AgentQueryRequest(BaseModel):
    agent_type: str = Field(..., description="Agent type")
    query: str = Field(..., description="Query for the agent")
    context: Optional[Dict] = Field(None, description="Additional context")

# API Endpoints
@app.get("/")
async def root():
    """Health check and service info"""
    return {
        "service": "Sophia AIOS Agent Server",
        "status": "operational",
        "version": "1.0.0",
        "agents_available": len(swarm_manager.agents),
        "active_swarms": len(swarm_manager.swarms)
    }

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    agents_info = {}
    for name, agent in swarm_manager.agents.items():
        agents_info[name] = {
            "name": agent.name,
            "role": agent.role,
            "model": agent.model.name if hasattr(agent.model, 'name') else str(agent.model),
            "has_tools": bool(agent.tools) if hasattr(agent, 'tools') else False,
            "storage_enabled": bool(agent.storage) if hasattr(agent, 'storage') else False
        }
    return {"agents": agents_info}

@app.post("/swarm/create")
async def create_swarm(request: CreateSwarmRequest):
    """Create a new agent swarm"""
    swarm = swarm_manager.create_swarm(
        swarm_id=request.swarm_id,
        agent_types=request.agent_types,
        objective=request.objective
    )
    
    return {
        "success": True,
        "swarm_id": swarm["id"],
        "agents": list(swarm["agents"].keys()),
        "objective": swarm["objective"]
    }

@app.post("/swarm/execute")
async def execute_task(request: ExecuteTaskRequest):
    """Execute a task using a swarm"""
    try:
        results = await swarm_manager.execute_task(
            swarm_id=request.swarm_id,
            task=request.task,
            agent_sequence=request.agent_sequence
        )
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/swarm/collaborate")
async def collaborate(request: CollaborateRequest):
    """Agents collaborate on a topic"""
    try:
        collaboration_log = await swarm_manager.collaborate(
            swarm_id=request.swarm_id,
            topic=request.topic,
            rounds=request.rounds
        )
        
        return {
            "success": True,
            "swarm_id": request.swarm_id,
            "topic": request.topic,
            "rounds": request.rounds,
            "collaboration": collaboration_log
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/swarm/{swarm_id}")
async def get_swarm_status(swarm_id: str):
    """Get status of a specific swarm"""
    status = swarm_manager.get_swarm_status(swarm_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status

@app.get("/swarms")
async def list_swarms():
    """List all active swarms"""
    return {
        "swarms": swarm_manager.list_swarms(),
        "total": len(swarm_manager.swarms)
    }

@app.post("/agent/query")
async def query_agent(request: AgentQueryRequest):
    """Query a specific agent directly"""
    if request.agent_type not in swarm_manager.agents:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_type} not found")
    
    agent = swarm_manager.agents[request.agent_type]
    
    try:
        response = agent.run(request.query, stream=False)
        
        return {
            "success": True,
            "agent": request.agent_type,
            "query": request.query,
            "response": response.content,
            "model": response.model,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/swarm/{swarm_id}")
async def websocket_swarm(websocket: WebSocket, swarm_id: str):
    """WebSocket for real-time swarm communication"""
    await websocket.accept()
    
    if swarm_id not in swarm_manager.swarms:
        await websocket.send_json({"error": f"Swarm {swarm_id} not found"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive task from client
            data = await websocket.receive_json()
            
            if data.get("type") == "execute":
                # Execute task and stream results
                task = data.get("task")
                
                await websocket.send_json({
                    "type": "status",
                    "message": f"Starting task: {task}"
                })
                
                # Execute with the swarm
                results = await swarm_manager.execute_task(
                    swarm_id=swarm_id,
                    task=task
                )
                
                # Send results back
                await websocket.send_json({
                    "type": "results",
                    "data": results
                })
            
            elif data.get("type") == "status":
                # Send swarm status
                status = swarm_manager.get_swarm_status(swarm_id)
                await websocket.send_json({
                    "type": "status",
                    "data": status
                })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for swarm {swarm_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()

@app.get("/stats")
async def get_stats():
    """Get agent server statistics"""
    total_executions = sum(
        len(swarm["messages"]) 
        for swarm in swarm_manager.swarms.values()
    )
    
    return {
        "total_agents": len(swarm_manager.agents),
        "active_swarms": len(swarm_manager.swarms),
        "total_executions": total_executions,
        "agents": list(swarm_manager.agents.keys()),
        "uptime": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Sophia AIOS Agent Server...")
    logger.info(f"Initialized with {len(swarm_manager.agents)} agents")
    uvicorn.run(app, host="0.0.0.0", port=8103)
