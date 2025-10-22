#!/bin/bash

echo "================================================"
echo "  DQ-POC Local Development Starter"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo ""

echo "Installing/Updating dependencies..."
pip install -r requirements.txt --quiet
echo ""

echo "================================================"
echo "  Starting Backend Server..."
echo "================================================"
echo ""
echo "Backend will run on: http://localhost:8000"
echo "API Docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

python -m kg_builder.main
