#!/bin/bash
#
# BrowserHDL Docker Management Script
# Usage: ./docker.sh [build|run|stop|clean]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

IMAGE_NAME="browserhdl"
CONTAINER_NAME="browserhdl-container"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0;33m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

build_image() {
    print_info "Building Docker image..."
    
    cd "$PROJECT_DIR"
    docker build -t "$IMAGE_NAME:latest" .
    
    print_success "Docker image built successfully"
}

run_container() {
    print_info "Starting Docker container..."
    
    # Stop existing container if running
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        print_info "Stopping existing container..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
    fi
    
    # Run container
    docker run -it \
        --name "$CONTAINER_NAME" \
        -v "$PROJECT_DIR/profiles:/app/profiles" \
        -v "$PROJECT_DIR/examples:/app/examples" \
        "$IMAGE_NAME:latest" \
        "${@:2}"
    
    print_success "Container started"
}

stop_container() {
    print_info "Stopping Docker container..."
    
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    print_success "Container stopped"
}

clean_docker() {
    print_info "Cleaning Docker resources..."
    
    stop_container
    docker rmi "$IMAGE_NAME:latest" 2>/dev/null || true
    
    print_success "Docker resources cleaned"
}

case "${1:-build}" in
    build)
        build_image
        ;;
    
    run)
        run_container "$@"
        ;;
    
    stop)
        stop_container
        ;;
    
    clean)
        clean_docker
        ;;
    
    *)
        echo "Usage: $0 [build|run|stop|clean]"
        exit 1
        ;;
esac
