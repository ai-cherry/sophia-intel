#!/bin/bash

# Sophia AIOS Deployment Script
# Deploys the complete AIOS infrastructure

set -e  # Exit on error

echo "🚀 Sophia AIOS Deployment Starting..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV="${1:-dev}"
PULUMI_STACK="sophia-aios-${DEPLOYMENT_ENV}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check for required tools
    REQUIRED_TOOLS=("docker" "kubectl" "pulumi" "node" "python3" "gh")
    
    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed"
            exit 1
        fi
    done
    
    log_success "All requirements met"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        log_success "Environment variables loaded"
    else
        log_warning ".env file not found - using defaults"
    fi
    
    # Verify critical secrets
    if [ -z "$LAMBDA_API_KEY" ]; then
        log_error "LAMBDA_API_KEY not set"
        exit 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        log_error "OPENAI_API_KEY not set"
        exit 1
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure with Pulumi..."
    
    cd infra/pulumi
    
    # Initialize stack if it doesn't exist
    if ! pulumi stack ls | grep -q $PULUMI_STACK; then
        log_info "Creating Pulumi stack: $PULUMI_STACK"
        pulumi stack init $PULUMI_STACK
    else
        log_info "Using existing stack: $PULUMI_STACK"
        pulumi stack select $PULUMI_STACK
    fi
    
    # Set configuration
    pulumi config set lambdaApiKey $LAMBDA_API_KEY --secret
    pulumi config set lambdaCloudApiKey $LAMBDA_CLOUD_API_KEY --secret
    
    # Deploy infrastructure
    log_info "Running Pulumi deployment..."
    pulumi up --yes
    
    # Export outputs
    pulumi stack output --json > ../../deployment-outputs.json
    
    cd ../..
    log_success "Infrastructure deployed"
}

build_docker_images() {
    log_info "Building Docker images..."
    
    # Build each MCP service
    SERVICES=("secrets-server" "tool-server" "memory-server" "agent-server")
    
    for service in "${SERVICES[@]}"; do
        log_info "Building $service..."
        
        # Copy shared requirements
        cp mcp-servers/requirements.txt mcp-servers/$service/
        
        # Build image
        docker build -t sophia-aios/$service:latest mcp-servers/$service/
        
        log_success "$service image built"
    done
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Get kubeconfig from Pulumi
    KUBECONFIG_PATH=$(pulumi stack output kubeconfig_path 2>/dev/null || echo "")
    
    if [ -z "$KUBECONFIG_PATH" ]; then
        log_warning "No kubeconfig found, using local Docker instead"
        return
    fi
    
    export KUBECONFIG=$KUBECONFIG_PATH
    
    # Create namespaces
    kubectl create namespace mcp --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace databases --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy services
    kubectl apply -f k8s/
    
    log_success "Kubernetes deployment complete"
}

deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Start all services
    docker-compose -f docker-compose.mcp.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    SERVICES=("secrets-server:8100" "tool-server:8101" "memory-server:8102" "agent-server:8103")
    
    for service in "${SERVICES[@]}"; do
        SERVICE_NAME=$(echo $service | cut -d: -f1)
        PORT=$(echo $service | cut -d: -f2)
        
        if curl -f http://localhost:$PORT/health &>/dev/null; then
            log_success "$SERVICE_NAME is healthy"
        else
            log_warning "$SERVICE_NAME health check failed"
        fi
    done
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create Prometheus configuration
    mkdir -p config/prometheus
    cat > config/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'secrets-server:8100'
        - 'tool-server:8101'
        - 'memory-server:8102'
        - 'agent-server:8103'
EOF
    
    # Create Grafana dashboards
    mkdir -p config/grafana/dashboards
    
    log_success "Monitoring configured"
}

run_tests() {
    log_info "Running integration tests..."
    
    # Test each service
    python3 tests/test_integration.py
    
    log_success "All tests passed"
}

create_dashboard_config() {
    log_info "Creating dashboard configuration..."
    
    # Get service URLs from deployment
    SERVICES_CONFIG=$(cat <<EOF
{
    "api": {
        "secrets": "http://localhost:8100",
        "tools": "http://localhost:8101",
        "memory": "http://localhost:8102",
        "agents": "http://localhost:8103",
        "gateway": "http://localhost:8787"
    },
    "databases": {
        "qdrant": "http://localhost:6333",
        "redis": "redis://localhost:6379",
        "neo4j": "bolt://localhost:7687"
    },
    "monitoring": {
        "prometheus": "http://localhost:9090",
        "grafana": "http://localhost:3000"
    }
}
EOF
)
    
    echo "$SERVICES_CONFIG" > dashboard/config.json
    log_success "Dashboard configuration created"
}

main() {
    echo ""
    echo "🎯 Sophia AIOS Deployment"
    echo "========================="
    echo "Environment: $DEPLOYMENT_ENV"
    echo ""
    
    # Run deployment steps
    check_requirements
    setup_environment
    
    # Choose deployment method
    if [ "$DEPLOYMENT_ENV" == "production" ]; then
        deploy_infrastructure
        build_docker_images
        deploy_kubernetes
    else
        build_docker_images
        deploy_docker_compose
    fi
    
    setup_monitoring
    create_dashboard_config
    
    # Run tests if not in production
    if [ "$DEPLOYMENT_ENV" != "production" ]; then
        run_tests
    fi
    
    echo ""
    log_success "🎉 Sophia AIOS Deployment Complete!"
    echo ""
    echo "Access Points:"
    echo "  API Gateway:  http://localhost:8787"
    echo "  Grafana:      http://localhost:3000 (admin/sophiaaios)"
    echo "  Qdrant:       http://localhost:6333/dashboard"
    echo ""
    echo "Next Steps:"
    echo "  1. Check service health: curl http://localhost:8100/health"
    echo "  2. View logs: docker-compose -f docker-compose.mcp.yml logs -f"
    echo "  3. Access dashboard: http://localhost:3000"
    echo ""
}

# Run main function
main "$@"