#!/bin/bash

echo "================================================"
echo "  DQ-POC Web App Starter"
echo "================================================"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

echo "================================================"
echo "  Starting Frontend Development Server..."
echo "================================================"
echo ""
echo "Web App will run on: http://localhost:3000"
echo ""
echo "Browser will open automatically"
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

npm start
