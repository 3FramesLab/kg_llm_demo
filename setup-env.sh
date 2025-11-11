#!/bin/bash
# DQ-POC Environment Setup Script for Linux/Mac
# Quick setup for different environments

echo ""
echo "========================================"
echo "   DQ-POC Environment Setup"
echo "========================================"
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: ./setup-env.sh [development|docker|production|validate]"
    echo ""
    echo "Examples:"
    echo "  ./setup-env.sh development    - Setup for local development"
    echo "  ./setup-env.sh docker         - Setup for Docker deployment"
    echo "  ./setup-env.sh production     - Setup for production deployment"
    echo "  ./setup-env.sh validate       - Validate current configuration"
    echo ""
    exit 1
fi

echo "Setting up $1 environment..."
echo ""

# Run the Python setup script
if [ "$1" = "validate" ]; then
    python3 scripts/setup-environment.py development --validate
else
    python3 scripts/setup-environment.py $1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   Environment Setup Complete!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Review and customize .env file"
    echo "2. Update database credentials"
    echo "3. Set OpenAI API key if needed"
    echo "4. Run: ./setup-env.sh validate"
    echo ""
else
    echo ""
    echo "========================================"
    echo "   Environment Setup Failed!"
    echo "========================================"
    echo ""
    echo "Please check the error messages above."
    echo ""
    exit 1
fi
