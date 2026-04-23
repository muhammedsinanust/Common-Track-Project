#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Main script
print_header "Sneaker Store Microservices - Setup & Testing"

# Check if Docker is running
print_warning "Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_success "Docker is running"

# Build images
print_header "Building Docker Images"
docker-compose build --no-cache
if [ $? -eq 0 ]; then
    print_success "All images built successfully"
else
    print_error "Failed to build images"
    exit 1
fi

# Start services
print_header "Starting Services"
docker-compose up -d
if [ $? -eq 0 ]; then
    print_success "All services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to be healthy
print_warning "Waiting for services to be ready..."
sleep 10

# Check service health
print_header "Checking Service Health"

services=("api-gateway" "auth-service" "product-service" "raffle-service")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "healthy"; then
        print_success "$service is healthy"
    else
        print_warning "$service is starting..."
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    print_warning "Some services are still starting. Check status with: docker-compose ps"
fi

# Display service URLs
print_header "Service URLs"
echo -e "${BLUE}Frontend:${NC}              http://localhost:3000"
echo -e "${BLUE}API Gateway:${NC}           http://localhost:8000"
echo -e "${BLUE}Auth Service:${NC}          http://localhost:8001"
echo -e "${BLUE}Product Service:${NC}       http://localhost:8002"
echo -e "${BLUE}Raffle Service:${NC}        http://localhost:8003"
echo -e "${BLUE}Load Tester UI:${NC}        http://localhost:8089"

# Test API Gateway
print_header "Testing API Gateway"
response=$(curl -s http://localhost:8000/)
if echo "$response" | grep -q "api-gateway"; then
    print_success "API Gateway is responding"
else
    print_warning "API Gateway response unclear"
fi

# Sample registration command
print_header "Quick Start - Register Test User"
echo -e "${YELLOW}Run this to register a test user:${NC}"
echo -e "${GREEN}curl -X POST http://localhost:8000/api/auth/register \\${NC}"
echo -e "${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${GREEN}  -d '{${NC}"
echo -e "${GREEN}    \"email\": \"test@example.com\",${NC}"
echo -e "${GREEN}    \"username\": \"testuser\",${NC}"
echo -e "${GREEN}    \"password\": \"TestPass123\"${NC}"
echo -e "${GREEN}  }'${NC}"

# Display logs suggestion
print_header "Monitoring"
echo -e "${YELLOW}To view logs for a service:${NC}"
echo -e "${GREEN}docker-compose logs -f [service-name]${NC}"
echo ""
echo -e "${YELLOW}To view all logs:${NC}"
echo -e "${GREEN}docker-compose logs -f${NC}"

print_header "Setup Complete!"
echo -e "${GREEN}Visit http://localhost:3000 to start using the application!${NC}"
