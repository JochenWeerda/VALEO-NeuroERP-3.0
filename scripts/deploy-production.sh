#!/bin/bash

# VALEO NeuroERP 3.0 Production Deployment Script
# This script handles the complete deployment process for production

set -e  # Exit on any error

# Configuration
APP_NAME="valeoneuroerp-3.0"
DOCKER_IMAGE="valeoneuroerp-3.0:latest"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    log_success "All prerequisites are met!"
}

# Create production environment file
create_env_file() {
    log_info "Creating production environment file..."
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# VALEO NeuroERP 3.0 Production Environment
NODE_ENV=production
PORT=3000

# Database Configuration
DB_HOST=valeoneuroerp-db
DB_PORT=5432
DB_NAME=valeoneuroerp
DB_USER=valeoneuroerp
DB_PASSWORD=your_secure_password_here

# Redis Configuration
REDIS_HOST=valeoneuroerp-redis
REDIS_PORT=6379

# Monitoring Configuration
GRAFANA_PASSWORD=your_grafana_password_here
PROMETHEUS_RETENTION=200h

# Security Configuration
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json

# Performance Configuration
MAX_CONNECTIONS=100
REQUEST_TIMEOUT=30000
KEEP_ALIVE_TIMEOUT=5000
EOF
        log_success "Production environment file created: $ENV_FILE"
        log_warning "Please update the passwords and secrets in $ENV_FILE before deployment!"
    else
        log_info "Production environment file already exists: $ENV_FILE"
    fi
}

# Run quality gates
run_quality_gates() {
    log_info "Running quality gates..."
    
    # Install dependencies
    log_info "Installing dependencies..."
    npm ci
    
    # Run type check
    log_info "Running TypeScript type check..."
    npm run type-check
    
    # Run linting
    log_info "Running ESLint..."
    npm run lint
    
    # Run smoke tests
    log_info "Running smoke tests..."
    npm run test:smoke
    
    log_success "All quality gates passed!"
}

# Build production image
build_production_image() {
    log_info "Building production Docker image..."
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << EOF
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose ports
EXPOSE 3000 3001 3002 3003 3004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:3000/health || exit 1

# Start the application
CMD ["npm", "start"]
EOF
        log_success "Dockerfile created"
    fi
    
    # Build the image
    docker build -t "$DOCKER_IMAGE" .
    
    log_success "Production Docker image built: $DOCKER_IMAGE"
}

# Deploy to production
deploy_production() {
    log_info "Deploying to production..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Start services
    log_info "Starting production services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    log_info "Checking service health..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    log_success "Production deployment completed!"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log_info "Running post-deployment tests..."
    
    # Wait for application to be ready
    log_info "Waiting for application to be ready..."
    sleep 60
    
    # Test main application endpoint
    log_info "Testing main application endpoint..."
    if curl -f http://localhost:3000/health; then
        log_success "Main application is responding"
    else
        log_error "Main application is not responding"
        exit 1
    fi
    
    # Test domain endpoints
    log_info "Testing domain endpoints..."
    for port in 3001 3002 3003 3004; do
        if curl -f "http://localhost:$port/health"; then
            log_success "Domain service on port $port is responding"
        else
            log_warning "Domain service on port $port is not responding"
        fi
    done
    
    # Test monitoring endpoints
    log_info "Testing monitoring endpoints..."
    if curl -f http://localhost:9090/-/healthy; then
        log_success "Prometheus is responding"
    else
        log_warning "Prometheus is not responding"
    fi
    
    if curl -f http://localhost:3001/api/health; then
        log_success "Grafana is responding"
    else
        log_warning "Grafana is not responding"
    fi
    
    log_success "Post-deployment tests completed!"
}

# Show deployment status
show_deployment_status() {
    log_info "Deployment Status:"
    echo "=================="
    
    # Show running containers
    log_info "Running containers:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Show service URLs
    log_info "Service URLs:"
    echo "  Main Application: http://localhost:3000"
    echo "  CRM Domain: http://localhost:3001"
    echo "  ERP Domain: http://localhost:3002"
    echo "  Analytics Domain: http://localhost:3003"
    echo "  Integration Domain: http://localhost:3004"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
    
    # Show logs
    log_info "Recent logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
}

# Main deployment function
main() {
    log_info "Starting VALEO NeuroERP 3.0 Production Deployment..."
    echo "=================================================="
    
    check_prerequisites
    create_env_file
    run_quality_gates
    build_production_image
    deploy_production
    run_post_deployment_tests
    show_deployment_status
    
    log_success "🎉 VALEO NeuroERP 3.0 Production Deployment Completed Successfully!"
    log_info "The application is now running in production mode."
    log_info "Check the service URLs above to access the application."
}

# Run main function
main "$@"
