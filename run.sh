#!/bin/bash
# SMdown Launcher Script
# Usage: ./run.sh

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import PySide6" 2>/dev/null || {
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
}

# Run application
echo "Starting SMdown..."
python3 app/main.py "$@"
