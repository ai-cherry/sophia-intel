#!/bin/bash

# Sophia Intel Deployment Script

echo "======================================"
echo "🚀 SOPHIA INTEL DEPLOYMENT OPTIONS"
echo "======================================"
echo ""
echo "Choose deployment target:"
echo "  1) Local Docker"
echo "  2) AWS Lambda"
echo "  3) Google Cloud Run"
echo "  4) Heroku"
echo "  5) Railway.app"
echo "  6) Render.com"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo "📦 Building Docker container..."
        cat > Dockerfile.mcp << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["python", "simple_mcp_server.py"]
EOF
        
        docker build -f Dockerfile.mcp -t sophia-mcp .
        docker run -d -p 8001:8001 --env-file .env sophia-mcp
        echo "✅ Running on http://localhost:8001"
        ;;
        
    2)
        echo "☁️ Deploying to AWS Lambda..."
        echo "Creating Lambda deployment package..."
        
        # Create Lambda handler
        cat > lambda_handler.py << 'EOF'
from mangum import Mangum
from simple_mcp_server import app

handler = Mangum(app)
EOF
        
        # Package for Lambda
        pip install mangum -t lambda_package/
        cp -r *.py mcp_servers services config lambda_package/
        cp .env lambda_package/
        cd lambda_package && zip -r ../lambda_deployment.zip . && cd ..
        
        echo "✅ Lambda package ready: lambda_deployment.zip"
        echo "Upload to AWS Lambda with Python 3.9 runtime"
        ;;
        
    3)
        echo "☁️ Deploying to Google Cloud Run..."
        
        # Create app.yaml for Cloud Run
        cat > app.yaml << 'EOF'
runtime: python39

env_variables:
  MCP_PORT: "8001"

handlers:
- url: /.*
  script: auto
EOF
        
        echo "Run: gcloud run deploy sophia-mcp --source . --region us-central1"
        ;;
        
    4)
        echo "☁️ Deploying to Heroku..."
        
        # Create Procfile
        echo "web: python simple_mcp_server.py" > Procfile
        
        # Create runtime.txt
        echo "python-3.9.18" > runtime.txt
        
        echo "Commands to run:"
        echo "  heroku create sophia-mcp"
        echo "  heroku config:set $(cat .env | xargs)"
        echo "  git push heroku main"
        ;;
        
    5)
        echo "☁️ Deploying to Railway..."
        
        # Create railway.json
        cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python simple_mcp_server.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
        
        echo "Run: railway up"
        ;;
        
    6)
        echo "☁️ Deploying to Render..."
        
        # Create render.yaml
        cat > render.yaml << 'EOF'
services:
  - type: web
    name: sophia-mcp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python simple_mcp_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
EOF
        
        echo "Connect your GitHub repo to Render.com"
        ;;
esac

echo ""
echo "======================================"
echo "📚 NEXT STEPS:"
echo "======================================"
echo "1. Test locally: curl http://localhost:8001/health"
echo "2. Use the API: http://localhost:8001/docs"
echo "3. Check memory: http://localhost:8001/sessions"
