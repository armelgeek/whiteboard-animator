#!/bin/bash

# Whiteboard Animator API Quick Start Script

echo "========================================"
echo "Whiteboard Animator API - Quick Start"
echo "========================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "Error: Python 3.8 or higher is required (found: $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
cd api
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create output directory
mkdir -p output_videos
echo "✓ Output directory created"

# Start the API server
echo ""
echo "========================================"
echo "Starting API Server..."
echo "========================================"
echo ""
echo "API will be available at:"
echo "  - Base URL: http://localhost:8000"
echo "  - Documentation: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
