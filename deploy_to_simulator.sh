#!/bin/bash
#
# Deploy Heimdall Backend to Sphinx Simulator Machine
#
# This script sets up and runs the Heimdall backend on the machine
# running the Sphinx simulator (Vast.ai instance or any Linux machine)
#

set -e  # Exit on error

echo "🚁 Heimdall Backend Deployment for Sphinx Simulator"
echo "=================================================="
echo ""

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
   echo "⚠️  Please run as non-root user (e.g., heimdall)"
   echo "   sudo is only needed for system packages"
   exit 1
fi

# Configuration
INSTALL_DIR="${HOME}/heimdall-backend"
PYTHON_VERSION="python3.10"
VENV_DIR="${INSTALL_DIR}/venv"

echo "📁 Installation directory: ${INSTALL_DIR}"
echo "🐍 Python version: ${PYTHON_VERSION}"
echo ""

# Step 1: Check Python version
echo "Step 1/7: Checking Python installation..."
if ! command -v ${PYTHON_VERSION} &> /dev/null; then
    echo "❌ ${PYTHON_VERSION} not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3-pip
else
    echo "✅ ${PYTHON_VERSION} found: $(${PYTHON_VERSION} --version)"
fi

# Step 2: Install system dependencies
echo ""
echo "Step 2/7: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    curl \
    libffi-dev \
    libssl-dev

echo "✅ System dependencies installed"

# Step 3: Create installation directory
echo ""
echo "Step 3/7: Creating installation directory..."
mkdir -p ${INSTALL_DIR}
cd ${INSTALL_DIR}
echo "✅ Working directory: $(pwd)"

# Step 4: Create Python virtual environment
echo ""
echo "Step 4/7: Setting up Python virtual environment..."
if [ ! -d "${VENV_DIR}" ]; then
    ${PYTHON_VERSION} -m venv ${VENV_DIR}
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source ${VENV_DIR}/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Step 5: Install Python dependencies
echo ""
echo "Step 5/7: Installing Python dependencies..."

# Create requirements file if not exists
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt..."
    cat > requirements.txt <<'EOF'
# Core dependencies for Heimdall Backend
parrot-olympe>=7.7.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
python-multipart>=0.0.6
websockets>=11.0.0

# Utilities
python-dotenv>=1.0.0

# Optional (for development)
# pytest>=7.4.0
# pytest-asyncio>=0.21.0
EOF
fi

# Install dependencies
# Note: parrot-olympe should already be installed system-wide via Parrot installer
echo "Installing Python packages..."
pip install -r requirements.txt || {
    echo "⚠️  Some packages failed to install. Trying without parrot-olympe..."
    grep -v "^parrot-olympe" requirements.txt > /tmp/requirements_filtered.txt
    pip install -r /tmp/requirements_filtered.txt
}

echo "✅ Python dependencies installed"

# Step 6: Copy backend code (if not already present)
echo ""
echo "Step 6/7: Setting up backend code..."

if [ ! -d "backend" ]; then
    echo "⚠️  Backend code not found in ${INSTALL_DIR}"
    echo "   Please copy the backend directory here, or run from project directory"
    echo ""
    echo "   Example:"
    echo "   cd /path/to/etdh-hackaton"
    echo "   cp -r backend playbooks ${INSTALL_DIR}/"
    echo ""
    read -p "Press Enter after copying the files, or Ctrl+C to exit..."
fi

# Create playbooks directory if needed
mkdir -p playbooks

echo "✅ Backend code ready"

# Step 7: Create startup script
echo ""
echo "Step 7/7: Creating startup script..."

cat > ${INSTALL_DIR}/start_backend.sh <<'STARTSCRIPT'
#!/bin/bash
#
# Start Heimdall Backend Server
#

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH=${DIR}

# Configuration
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

echo "🚁 Starting Heimdall Backend API Server"
echo "========================================"
echo "Host: ${HOST}"
echo "Port: ${PORT}"
echo "API URL: http://$(hostname -I | awk '{print $1}'):${PORT}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
cd ${DIR}
python3 -m uvicorn backend.api.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --log-level info \
    --reload
STARTSCRIPT

chmod +x ${INSTALL_DIR}/start_backend.sh

echo "✅ Startup script created: ${INSTALL_DIR}/start_backend.sh"

# Create systemd service (optional)
echo ""
echo "Creating systemd service (optional)..."

cat > /tmp/heimdall-backend.service <<SERVICEEOF
[Unit]
Description=Heimdall Backend API Server
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PYTHONPATH=${INSTALL_DIR}"
ExecStart=${VENV_DIR}/bin/python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "To install as systemd service (optional):"
echo "  sudo cp /tmp/heimdall-backend.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable heimdall-backend"
echo "  sudo systemctl start heimdall-backend"
echo ""

# Final instructions
echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "📍 Installation location: ${INSTALL_DIR}"
echo ""
echo "🚀 To start the backend server:"
echo "   cd ${INSTALL_DIR}"
echo "   ./start_backend.sh"
echo ""
echo "🔗 API will be available at:"
echo "   http://$(hostname -I | awk '{print $1}'):8000"
echo "   http://localhost:8000 (local)"
echo ""
echo "📊 Check API status:"
echo "   curl http://localhost:8000/"
echo ""
echo "🛑 To stop the server:"
echo "   Press Ctrl+C in the terminal"
echo ""
echo "📝 Logs location:"
echo "   Server logs will appear in the terminal"
echo ""
echo "=================================================="
