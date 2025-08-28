#!/bin/bash
# MCP Development Environment Setup Script
# Automates the setup of Python 3.10+ and MCP SDK 1.2.0+

set -e  # Exit on any error

echo "🚀 Setting up MCP Development Environment..."
echo "================================================"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed or not in PATH"
    echo "Please install Anaconda/Miniconda first: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Found conda: $(conda --version)"

# Check if environment already exists
if conda env list | grep -q "mcp-env"; then
    echo "⚠️  Environment 'mcp-env' already exists"
    read -p "Do you want to remove and recreate it? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n mcp-env -y
    else
        echo "ℹ️  Using existing environment"
        conda activate mcp-env
        echo "✅ Environment activated"
        exit 0
    fi
fi

# Create new conda environment
echo "📦 Creating conda environment with Python 3.11..."
conda create -n mcp-env python=3.11 -y

# Activate environment
echo "🔧 Activating environment..."
eval "$(conda shell.bash hook)"
conda activate mcp-env

# Remove any Python aliases that might interfere
echo "🔨 Removing potential Python aliases..."
unalias python 2>/dev/null || true

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "✅ Python version: $PYTHON_VERSION"

# Check if Python version meets requirement (3.10+)
if python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✅ Python version meets requirement (3.10+)"
else
    echo "❌ Python version does not meet requirement (3.10+)"
    exit 1
fi

# Install MCP SDK
echo "📥 Installing MCP SDK..."
pip install "mcp>=1.2.0"

# Verify MCP installation
echo "🧪 Verifying MCP installation..."
MCP_VERSION=$(pip show mcp | grep Version | cut -d' ' -f2)
echo "✅ MCP SDK version: $MCP_VERSION"

# Test MCP imports
if python -c "import mcp.client; import mcp.server" 2>/dev/null; then
    echo "✅ MCP modules import successfully"
else
    echo "❌ Error: MCP modules failed to import"
    exit 1
fi

# Display success message
echo ""
echo "🎉 MCP Development Environment Setup Complete!"
echo "================================================"
echo "Environment: mcp-env"
echo "Python: $PYTHON_VERSION"
echo "MCP SDK: $MCP_VERSION"
echo ""
echo "To use this environment:"
echo "  conda activate mcp-env"
echo ""
echo "To test the setup:"
echo "  python -c \"import mcp.client; import mcp.server; print('MCP ready!')\""
echo ""
echo "To deactivate:"
echo "  conda deactivate"
echo ""
echo "✅ Ready for MCP development!"
