#!/bin/bash

# Website Migration Platform - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "Website Migration Platform Setup"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
        return 0
    else
        echo -e "${RED}✗ Docker or Docker Compose not found${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        return 1
    fi
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your API keys:${NC}"
        echo "  - OPENAI_API_KEY (required)"
        echo "  - ANTHROPIC_API_KEY (optional)"
        echo ""
        read -p "Press Enter to continue after editing .env..."
    else
        echo -e "${GREEN}✓ .env file already exists${NC}"
    fi
}

# Build and start Docker containers
start_containers() {
    echo ""
    echo "Building and starting Docker containers..."
    echo "This may take a few minutes on first run..."
    echo ""

    docker-compose up -d --build

    echo ""
    echo -e "${GREEN}✓ Containers started${NC}"
    echo ""
}

# Wait for services to be ready
wait_for_services() {
    echo "Waiting for services to be ready..."
    sleep 10

    # Check if backend is responding
    MAX_TRIES=30
    COUNT=0
    while [ $COUNT -lt $MAX_TRIES ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
            return 0
        fi
        COUNT=$((COUNT + 1))
        echo "Waiting for backend... ($COUNT/$MAX_TRIES)"
        sleep 2
    done

    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check logs with: docker-compose logs backend"
    return 1
}

# Run database migrations
run_migrations() {
    echo ""
    echo "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    echo -e "${GREEN}✓ Database migrations complete${NC}"
}

# Print success message
print_success() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}Setup Complete! 🎉${NC}"
    echo "=================================="
    echo ""
    echo "Access your platform:"
    echo "  - Frontend Dashboard: http://localhost:3000"
    echo "  - Backend API:        http://localhost:8000"
    echo "  - API Docs:           http://localhost:8000/docs"
    echo "  - MinIO Console:      http://localhost:9001"
    echo ""
    echo "Useful commands:"
    echo "  - View logs:          docker-compose logs -f"
    echo "  - Stop services:      docker-compose down"
    echo "  - Restart:            docker-compose restart"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:3000"
    echo "  2. Click 'New Migration'"
    echo "  3. Enter a Wix website URL"
    echo "  4. Start your first migration!"
    echo ""
}

# Print error message
print_error() {
    echo ""
    echo -e "${RED}=================================="
    echo "Setup Failed ❌"
    echo "==================================${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check Docker is running: docker ps"
    echo "  - View logs: docker-compose logs"
    echo "  - Check .env file has API keys"
    echo ""
    echo "For help, see GETTING_STARTED.md"
    echo ""
}

# Main setup flow
main() {
    # Check Docker
    if ! check_docker; then
        exit 1
    fi

    # Setup environment variables
    setup_env

    # Check if user wants to proceed
    echo ""
    read -p "Ready to start setup? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    # Start containers
    if ! start_containers; then
        print_error
        exit 1
    fi

    # Wait for services
    if ! wait_for_services; then
        print_error
        exit 1
    fi

    # Run migrations
    if ! run_migrations; then
        print_error
        exit 1
    fi

    # Success!
    print_success
}

# Run main function
main
