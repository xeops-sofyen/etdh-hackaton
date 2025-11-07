#!/bin/bash
# Automated Olympe SDK Setup for Vast.ai
# Run this script on your Vast.ai Linux instance

set -e

echo "=================================="
echo "Heimdall Olympe Setup on Vast.ai"
echo "=================================="
echo ""

# Check OS
echo "📋 Checking system requirements..."
if [[ ! -f /etc/lsb-release ]]; then
    echo "❌ Error: This script requires Ubuntu/Debian"
    exit 1
fi

source /etc/lsb-release
echo "✅ OS: $DISTRIB_DESCRIPTION"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
    echo "❌ Error: Python 3.9+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Update system
echo ""
echo "📦 Updating system packages..."
apt-get update -qq
apt-get install -y -qq \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    libgl1 \
    curl \
    wget \
    bc

# Check if repository already exists
if [[ -d ~/etdh-hackaton ]]; then
    echo ""
    echo "📂 Repository already exists. Updating..."
    cd ~/etdh-hackaton
    git pull origin main || echo "⚠️  Could not pull latest changes (continuing anyway)"
else
    # Clone repository
    echo ""
    echo "📥 Cloning Heimdall repository..."
    cd ~
    git clone https://github.com/xeops-sofyen/etdh-hackaton.git
    cd etdh-hackaton
fi

# Create virtual environment if not exists
if [[ ! -d backend/venv ]]; then
    echo ""
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source backend/venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install Olympe SDK
echo ""
echo "🚁 Installing Parrot Olympe SDK..."
pip install parrot-olympe -q

# Install other dependencies
echo ""
echo "📚 Installing project dependencies..."
pip install -q \
    pydantic \
    fastapi \
    uvicorn \
    pytest \
    python-dotenv \
    typing-extensions

# Verify installation
echo ""
echo "✅ Verifying installations..."

# Check Olympe
OLYMPE_VERSION=$(python3 -c "import olympe; print(olympe.__version__)" 2>/dev/null || echo "ERROR")
if [[ "$OLYMPE_VERSION" == "ERROR" ]]; then
    echo "❌ Olympe installation failed"
    exit 1
else
    echo "✅ Olympe SDK: $OLYMPE_VERSION"
fi

# Check Pydantic
PYDANTIC_VERSION=$(python3 -c "import pydantic; print(pydantic.__version__)" 2>/dev/null || echo "ERROR")
if [[ "$PYDANTIC_VERSION" == "ERROR" ]]; then
    echo "❌ Pydantic installation failed"
    exit 1
else
    echo "✅ Pydantic: $PYDANTIC_VERSION"
fi

# Check FastAPI
FASTAPI_VERSION=$(python3 -c "import fastapi; print(fastapi.__version__)" 2>/dev/null || echo "ERROR")
if [[ "$FASTAPI_VERSION" == "ERROR" ]]; then
    echo "❌ FastAPI installation failed"
    exit 1
else
    echo "✅ FastAPI: $FASTAPI_VERSION"
fi

# Check pytest
PYTEST_VERSION=$(pytest --version | head -n1 | cut -d' ' -f2)
echo "✅ pytest: $PYTEST_VERSION"

# Check if GPU is available for Sphinx simulator
echo ""
echo "🎮 Checking GPU availability for Sphinx simulator..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1)
    if [[ -n "$GPU_INFO" ]]; then
        echo "✅ GPU detected: $GPU_INFO"
        INSTALL_SPHINX=true
    else
        echo "⚠️  nvidia-smi found but no GPU detected"
        INSTALL_SPHINX=false
    fi
else
    echo "⚠️  No NVIDIA GPU detected (Sphinx simulator will not be available)"
    INSTALL_SPHINX=false
fi

# Install Sphinx simulator if GPU is available
if [[ "$INSTALL_SPHINX" == "true" ]]; then
    echo ""
    echo "🚁 Installing Parrot Sphinx simulator..."

    # Add Parrot repository
    echo "deb http://plf.parrot.com/sphinx/binary $(lsb_release -cs)/" | tee /etc/apt/sources.list.d/sphinx.list

    # Add Parrot GPG key
    wget -qO - http://plf.parrot.com/sphinx/gpg.asc | apt-key add -

    # Update and install
    apt-get update -qq
    apt-get install -y -qq parrot-sphinx

    # Verify Sphinx installation
    if command -v sphinx &> /dev/null; then
        SPHINX_VERSION=$(sphinx --version 2>&1 | head -n1 || echo "unknown")
        echo "✅ Parrot Sphinx: $SPHINX_VERSION"
    else
        echo "⚠️  Sphinx installation may have issues"
    fi
else
    echo "ℹ️  Skipping Sphinx simulator installation (no GPU)"
    echo "   You can still run all Olympe SDK tests!"
fi

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "📊 Running test suite..."
echo ""

# Run tests
pytest tests/ -v --tb=short

TEST_EXIT_CODE=$?

echo ""
echo "=================================="
if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo "🎉 All tests passed!"
else
    echo "⚠️  Some tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=================================="
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Activate environment:"
echo "   cd ~/etdh-hackaton"
echo "   source backend/venv/bin/activate"
echo ""
echo "2. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "3. Run GeoJSON demo:"
echo "   python demo_geojson_translation.py"
echo ""
echo "4. Start API server:"
echo "   python backend/api/main.py"
echo ""
echo "5. Test with Sphinx simulator (if GPU available):"
if [[ "$INSTALL_SPHINX" == "true" ]]; then
    echo "   # Terminal 1: Start Sphinx"
    echo "   sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone"
    echo ""
    echo "   # Terminal 2: Execute mission"
    echo "   python backend/quickstart.py --playbook playbooks/simple_test.json"
else
    echo "   ⚠️  Sphinx simulator not installed (no GPU)"
    echo "   Tests still pass, but can't simulate drone flight"
fi
echo ""

exit $TEST_EXIT_CODE
