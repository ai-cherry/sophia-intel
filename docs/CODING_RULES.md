# Coding Rules and AI Guardrails

**Version:** 1.0  
**Last Updated:** 2025-08-21  
**Scope:** Sophia AI Project

## AI Coding Guardrails

### Code Generation Standards
1. **No Hardcoded Secrets**: All credentials must be retrieved from environment variables
2. **Error Handling**: Every API call must include proper error handling and logging
3. **Type Hints**: All Python functions must include type hints
4. **Documentation**: All public functions and classes must have docstrings
5. **Testing**: New code must include corresponding unit tests

### Security Requirements
- **Input Validation**: All user inputs must be validated and sanitized
- **Authentication**: All API endpoints must implement proper authentication
- **HTTPS Only**: All external communications must use HTTPS
- **Secret Rotation**: Support for secret rotation without service restart

## Meta-Tagging System

### Service Tags
```python
# Meta-tags for service classification
SERVICE_TAGS = {
    "service": "research|context|code|dashboard|business",
    "layer": "api|mcp|ui|data|infrastructure", 
    "team": "backend|frontend|devops|ai",
    "risk": "low|medium|high|critical"
}
```

### Usage Examples
```python
# Example service file header
"""
Meta-tags:
- service: research
- layer: mcp
- team: backend
- risk: medium
"""
```

## Microservice Boundaries

### Service Responsibilities
- **Research Service**: External data retrieval and search
- **Context Service**: Code indexing and semantic search
- **Code Service**: Code generation and analysis
- **Dashboard Service**: User interface and orchestration
- **Business Service**: Business intelligence and analytics

### Communication Patterns
- **Synchronous**: HTTP/REST for real-time operations
- **Asynchronous**: Message queues for background processing
- **Event-Driven**: Pub/sub for service coordination

### Data Ownership
- Each service owns its data and database
- Cross-service data access through APIs only
- No direct database access between services

## Architecture Patterns

### Agent Inheritance
```python
class BaseAgent:
    """Base class for all AI agents"""
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
    
    def execute(self, task: Task) -> Result:
        """Execute a task with proper error handling"""
        pass

class PlannerAgent(BaseAgent):
    """Specialized agent for planning tasks"""
    pass
```

### Route Standardization
```python
# Standard route patterns
@app.route('/healthz')  # Health check
@app.route('/api/v1/<service>/<action>')  # API endpoints
@app.route('/mcp/<protocol>/<method>')  # MCP endpoints
```

### Database Access Pattern
```python
class DatabaseManager:
    """Centralized database access with connection pooling"""
    
    def __init__(self, connection_string: str):
        self.pool = create_connection_pool(connection_string)
    
    async def execute_query(self, query: str, params: dict) -> List[dict]:
        """Execute query with proper error handling and logging"""
        pass
```

## Quality Gates

### Pre-commit Checks
- [ ] Lint checks pass (flake8, black, mypy)
- [ ] Unit tests pass with >80% coverage
- [ ] Security scan passes (bandit)
- [ ] Documentation is updated

### CI/CD Requirements
- [ ] All tests pass in CI environment
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks meet thresholds
- [ ] Deployment smoke tests pass

## Enforcement Mechanisms

### Automated Checks
- **GitHub Actions**: Automated lint, test, and security checks
- **Pre-commit Hooks**: Local validation before commits
- **Code Review**: Mandatory peer review for all changes
- **Dependency Scanning**: Automated vulnerability detection

### Manual Reviews
- **Architecture Review**: For significant design changes
- **Security Review**: For authentication and authorization changes
- **Performance Review**: For changes affecting critical paths

## Exception Process

### When to Break Rules
1. **Emergency Fixes**: Critical production issues
2. **Prototype Code**: Clearly marked experimental code
3. **Legacy Integration**: When working with existing systems

### Documentation Requirements
- All exceptions must be documented with justification
- Technical debt tickets must be created for rule violations
- Timeline for remediation must be established

---

*These rules are enforced through automated tooling and peer review processes.*

