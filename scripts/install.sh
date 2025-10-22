#!/bin/bash
#
# BrowserHDL Installation Script
# Usage: ./install.sh [install|uninstall|verify|update]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

verify_system() {
    print_info "Verifying system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
    print_success "pip3 found"
    
    print_success "System verification complete"
}

install_dependencies() {
    print_info "Installing Python dependencies..."
    
    cd "$PROJECT_DIR"
    pip3 install -r requirements.txt --break-system-packages
    
    print_success "Python dependencies installed"
    
    print_info "Installing Playwright browsers..."
    python3 -m playwright install chromium firefox webkit
    print_success "Playwright browsers installed"
}

install_package() {
    print_info "Installing BrowserHDL..."
    
    cd "$PROJECT_DIR"
    pip3 install -e . --break-system-packages
    
    print_success "BrowserHDL installed"
    print_info "You can now run: browserhdl"
}

uninstall_package() {
    print_info "Uninstalling BrowserHDL..."
    
    pip3 uninstall -y browserhdl
    
    print_success "BrowserHDL uninstalled"
}

update_package() {
    print_info "Updating BrowserHDL..."
    
    cd "$PROJECT_DIR"
    git pull origin main
    pip3 install -e . --upgrade --break-system-packages
    
    print_success "BrowserHDL updated"
}

case "${1:-install}" in
    install)
        verify_system
        install_dependencies
        install_package
        print_success "Installation complete!"
        echo
        print_info "Run 'browserhdl --help' to get started"
        ;;
    
    uninstall)
        uninstall_package
        ;;
    
    verify)
        verify_system
        ;;
    
    update)
        update_package
        ;;
    
    *)
        echo "Usage: $0 [install|uninstall|verify|update]"
        exit 1
        ;;
esac
