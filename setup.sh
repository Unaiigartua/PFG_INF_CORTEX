#!/bin/bash

# setup_cortex.sh - Script to setup and start Cortex application

set -e

echo "🚀 Starting Cortex Medical Application Setup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

print_success "docker-compose is available"

# Create required directories
print_status "Creating required directories..."
mkdir -p cortex_back/data
mkdir -p cortex_back/omop_testing
mkdir -p cortex_back/rag_index
mkdir -p cortex_back/model_cache
mkdir -p nginx

print_success "Directories created"

# Start the services
print_status "Starting Docker Compose services..."
docker-compose up -d

# Wait for Ollama to be ready
print_status "Waiting for Ollama service to be ready..."
sleep 10

# Function to check if Ollama is ready
check_ollama() {
    docker exec cortex-ollama curl -f http://localhost:11434/api/tags > /dev/null 2>&1
}

# Wait up to 2 minutes for Ollama to be ready
TIMEOUT=120
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if check_ollama; then
        print_success "Ollama is ready"
        break
    fi
    print_status "Waiting for Ollama... ($ELAPSED/$TIMEOUT seconds)"
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    print_error "Ollama failed to start within $TIMEOUT seconds"
    exit 1
fi

# Pull the required model
print_status "Pulling the DeepSeek Coder model (this may take a while)..."
docker exec cortex-ollama ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M

# Verify model is available
print_status "Verifying model availability..."
if docker exec cortex-ollama ollama list | grep -q deepseek-coder-v2; then
    print_success "DeepSeek Coder model is available"
else
    print_error "Failed to pull DeepSeek Coder model"
    exit 1
fi

# Check backend health
print_status "Checking backend health..."
sleep 5

# Function to check backend health
check_backend() {
    curl -f http://localhost:8000/ > /dev/null 2>&1
}

# Wait up to 1 minute for backend to be ready
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if check_backend; then
        print_success "Backend is ready"
        break
    fi
    print_status "Waiting for backend... ($ELAPSED/$TIMEOUT seconds)"
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    print_warning "Backend may not be ready yet, check logs with: docker-compose logs backend"
fi

# Test the connection
print_status "Testing Ollama connection from backend..."
CONNECTION_TEST=$(curl -s http://localhost:8000/sql-generation/test-connection)
if echo "$CONNECTION_TEST" | grep -q '"success": true'; then
    print_success "Backend successfully connected to Ollama"
else
    print_warning "Backend connection test failed. Check the debug endpoint: http://localhost:8000/sql-generation/debug"
fi

# Display service status
echo ""
print_status "Service Status:"
docker-compose ps

echo ""
print_success "🎉 Cortex Medical Application is ready!"
echo ""
echo "📋 Service URLs:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Ollama: http://localhost:11434"
echo ""
echo "🔧 Health Check URLs:"
echo "   • Backend Health: http://localhost:8000/sql-generation/health"
echo "   • Connection Test: http://localhost:8000/sql-generation/test-connection"
echo "   • Debug Info: http://localhost:8000/sql-generation/debug"
echo ""
echo "📊 Useful Commands:"
echo "   • View logs: docker-compose logs -f [service_name]"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Check Ollama models: docker exec cortex-ollama ollama list"
echo ""

# Optionally open browser
if command -v xdg-open > /dev/null 2>&1; then
    read -p "Open frontend in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000
    fi
elif command -v open > /dev/null 2>&1; then
    read -p "Open frontend in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi