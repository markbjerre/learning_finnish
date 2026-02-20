#!/bin/bash

###############################################################################
#
# Development Environment Setup Script
# Sets up all projects for local development
#
# Usage: bash scripts/setup-dev-env.sh
#        bash scripts/setup-dev-env.sh --docker    (use Docker)
#        bash scripts/setup-dev-env.sh --help      (show help)
#
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
USE_DOCKER=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    cat << EOF
Development Environment Setup Script

USAGE:
    bash scripts/setup-dev-env.sh [OPTIONS]

OPTIONS:
    --docker    Use Docker Compose for development
    --help      Show this help message

EXAMPLES:
    bash scripts/setup-dev-env.sh              # Local development setup
    bash scripts/setup-dev-env.sh --docker     # Docker development setup

WHAT THIS SCRIPT DOES:
    1. Checks system dependencies (Node.js, Python, Docker)
    2. Installs project dependencies
    3. Sets up environment variables
    4. Initializes databases (if needed)
    5. Starts development servers

REQUIREMENTS:
    - Node.js 20+ (for frontends)
    - Python 3.11+ (for backends)
    - Docker & Docker Compose (optional, if using --docker)
    - Git

EOF
}

check_dependencies() {
    print_header "Checking System Dependencies"
    
    local missing_deps=false
    
    # Check Node.js
    if command -v node &> /dev/null; then
        local node_version=$(node -v)
        print_success "Node.js $node_version found"
    else
        print_error "Node.js not found. Install from https://nodejs.org"
        missing_deps=true
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        local npm_version=$(npm -v)
        print_success "npm $npm_version found"
    else
        print_error "npm not found"
        missing_deps=true
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 $python_version found"
    else
        print_error "Python 3 not found. Install from https://python.org"
        missing_deps=true
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_success "Git $git_version found"
    else
        print_error "Git not found"
        missing_deps=true
    fi
    
    # Check Docker (only if --docker flag)
    if [ "$USE_DOCKER" = true ]; then
        if command -v docker &> /dev/null; then
            local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
            print_success "Docker $docker_version found"
        else
            print_error "Docker not found. Install from https://docker.com"
            missing_deps=true
        fi
        
        if command -v docker-compose &> /dev/null; then
            local compose_version=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
            print_success "Docker Compose $compose_version found"
        else
            print_error "Docker Compose not found"
            missing_deps=true
        fi
    fi
    
    if [ "$missing_deps" = true ]; then
        print_error "Please install missing dependencies and try again"
        exit 1
    fi
}

setup_frontend() {
    local frontend_name=$1
    local frontend_path=$2
    
    print_header "Setting up $frontend_name Frontend"
    
    if [ ! -d "$frontend_path" ]; then
        print_error "Directory not found: $frontend_path"
        return 1
    fi
    
    cd "$frontend_path"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install --legacy-peer-deps
        print_success "$frontend_name dependencies installed"
    else
        print_info "$frontend_name dependencies already installed"
    fi
    
    cd "$PROJECT_ROOT"
}

setup_backend() {
    local backend_name=$1
    local backend_path=$2
    
    print_header "Setting up $backend_name Backend"
    
    if [ ! -d "$backend_path" ]; then
        print_error "Directory not found: $backend_path"
        return 1
    fi
    
    cd "$backend_path"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_info "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "$backend_name dependencies installed"
    fi
    
    deactivate
    cd "$PROJECT_ROOT"
}

setup_env_files() {
    print_header "Setting up Environment Variables"
    
    # Learning Finnish
    if [ ! -f "learning_finnish/backend/.env" ]; then
        print_info "Creating learning_finnish backend .env"
        cat > learning_finnish/backend/.env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=1
EOF
        print_success "learning_finnish/.env created"
    fi
    
    # Finance Dashboard
    if [ ! -f "Finance dashboard/.env" ]; then
        print_warning "Finance dashboard .env not found"
        print_info "Create 'Finance dashboard/.env' with:"
        echo "FLASK_ENV=development"
        echo "FLASK_DEBUG=1"
        echo "OPENAI_API_KEY=sk_..."
        echo "NEWSAPI_KEY=..."
    fi
    
    print_info "Add API keys to .env files as needed"
}

setup_docker() {
    print_header "Starting Docker Development Environment"
    
    if [ ! -f "docker-compose.dev.yml" ]; then
        print_error "docker-compose.dev.yml not found"
        exit 1
    fi
    
    print_info "Building and starting containers..."
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Docker containers started"
    print_info "Services are starting. Check status with:"
    echo "  docker-compose -f docker-compose.dev.yml ps"
}

setup_local() {
    print_header "Local Development Setup Complete"
    
    print_info "To start development servers:"
    echo ""
    echo "  Learning Finnish Frontend:"
    echo "    cd learning_finnish && npm run dev"
    echo "    (available at http://localhost:5173)"
    echo ""
    echo "  Learning Finnish Backend:"
    echo "    cd learning_finnish/backend && source venv/bin/activate && flask run"
    echo "    (available at http://localhost:8000)"
    echo ""
    echo "  Finance Dashboard:"
    echo "    cd 'Finance dashboard' && source venv/bin/activate && flask run"
    echo "    (available at http://localhost:5002)"
    echo ""
    echo "  Wedding:"
    echo "    cd Wedding/markella-boho-celebration && npm run dev"
    echo "    (available at http://localhost:5173)"
    echo ""
    echo "Run tests:"
    echo "  npx playwright test --ui"
}

show_service_status() {
    print_header "Service Status"
    
    if [ "$USE_DOCKER" = true ]; then
        docker-compose -f docker-compose.dev.yml ps
    fi
}

###############################################################################
# Main Script
###############################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header "Development Environment Setup"
    
    # Check dependencies
    check_dependencies
    
    if [ "$USE_DOCKER" = true ]; then
        print_info "Using Docker Compose for development"
        setup_docker
        show_service_status
    else
        print_info "Setting up local development environment"
        
        # Setup frontends
        setup_frontend "Learning Finnish" "learning_finnish"
        setup_frontend "Wedding" "Wedding/markella-boho-celebration"
        
        # Setup backends
        setup_backend "Learning Finnish" "learning_finnish/backend"
        setup_backend "Finance Dashboard" "Finance dashboard"
        setup_backend "Housing Market" "Danish Housing Market Search"
        setup_backend "Website Front Page" "Website Front Page"
        
        # Setup environment files
        setup_env_files
        
        # Show final instructions
        setup_local
    fi
    
    print_header "Setup Complete!"
    print_success "Development environment is ready"
    print_info "Next: Run development servers and access http://localhost:5173"
}

# Run main function
main "$@"
