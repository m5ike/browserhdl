#!/bin/bash
#
# BrowserHDL Run Script
# Usage: ./run.sh [adapter] [url]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
ADAPTER="${1:-playwright-chromium}"
URL="${2:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🌐 BrowserHDL${NC}"
echo "============================================"
echo -e "${YELLOW}Adapter:${NC} $ADAPTER"
if [ -n "$URL" ]; then
    echo -e "${YELLOW}Initial URL:${NC} $URL"
fi
echo "============================================"
echo

# Run the CLI
cd "$PROJECT_DIR"
python3 -m browserhdl.cli.interactive_cli "$ADAPTER" "$URL"
