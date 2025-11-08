#!/bin/bash
#
# Heimdall Full Stack Deployment Script
# Run this ON the simulator machine
#

set -e  # Exit on error

echo "🚁 Heimdall Full Stack Deployment"
echo "=================================="
echo ""

# Configuration
APP_DIR="${HOME}/heimdall-app"
PYTHON_VERSION="python3.10"
NODE_VERSION="18"

echo "📁 Installation directory: ${APP_DIR}"
echo "🐍 Python: ${PYTHON_VERSION}"
echo "📦 Node.js: v${NODE_VERSION}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "⚠️  Running as root. Will create heimdall user if needed."
   TARGET_USER="heimdall"
else
   TARGET_USER="$USER"
fi

# ============================================================================
# STEP 1: Install System Dependencies
# ============================================================================

echo "Step 1/8: Installing system dependencies..."

if [ "$EUID" -eq 0 ]; then
    apt-get update
    apt-get install -y \
        python3.10 \
        python3.10-venv \
        python3-pip \
        build-essential \
        git \
        curl \
        wget \
        libffi-dev \
        libssl-dev \
        ca-certificates \
        gnupg
else
    echo "⚠️  Not root - please run system installation manually if needed:"
    echo "   sudo apt-get update"
    echo "   sudo apt-get install -y python3.10 python3.10-venv python3-pip build-essential nodejs npm"
fi

echo "✅ System dependencies ready"

# ============================================================================
# STEP 2: Install Node.js
# ============================================================================

echo ""
echo "Step 2/8: Installing Node.js..."

# Check if Node.js is already installed
if command -v node &> /dev/null; then
    NODE_CURRENT=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_CURRENT" -ge "$NODE_VERSION" ]; then
        echo "✅ Node.js $(node --version) already installed"
    else
        echo "⚠️  Node.js version too old. Installing v${NODE_VERSION}..."
        if [ "$EUID" -eq 0 ]; then
            curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
            apt-get install -y nodejs
        else
            echo "Please install Node.js ${NODE_VERSION} manually"
        fi
    fi
else
    echo "Installing Node.js v${NODE_VERSION}..."
    if [ "$EUID" -eq 0 ]; then
        curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
        apt-get install -y nodejs
    else
        echo "Please install Node.js ${NODE_VERSION} manually"
    fi
fi

echo "✅ Node.js ready: $(node --version 2>/dev/null || echo 'not installed')"

# ============================================================================
# STEP 3: Setup Application Directory
# ============================================================================

echo ""
echo "Step 3/8: Setting up application directory..."

# Create app directory
mkdir -p ${APP_DIR}
cd ${APP_DIR}

# If files don't exist here, check current directory
if [ ! -d "backend" ]; then
    echo "⚠️  Backend not found in ${APP_DIR}"
    if [ -d "$(dirname $0)/backend" ]; then
        echo "Copying from current directory..."
        cp -r "$(dirname $0)/backend" .
        cp -r "$(dirname $0)/frontend" .
        cp -r "$(dirname $0)/playbooks" . 2>/dev/null || mkdir -p playbooks
    else
        echo "❌ Backend code not found. Please copy backend/ and frontend/ to ${APP_DIR}"
        exit 1
    fi
fi

echo "✅ Application directory ready"

# ============================================================================
# STEP 4: Setup Python Backend
# ============================================================================

echo ""
echo "Step 4/8: Setting up Python backend..."

# Create virtual environment
if [ ! -d "venv" ]; then
    ${PYTHON_VERSION} -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install backend dependencies
echo "Installing Python packages..."
cd backend

if pip install -r requirements.txt; then
    echo "✅ All Python packages installed"
else
    echo "⚠️  Some packages failed. Installing without parrot-olympe..."
    grep -v "^parrot-olympe" requirements.txt > /tmp/req_filtered.txt
    pip install -r /tmp/req_filtered.txt
    echo "✅ Core packages installed (parrot-olympe skipped)"
fi

cd ..

# Create .env file for backend
cat > backend/.env <<EOF
# Heimdall Backend Configuration
DRONE_IP=10.202.0.1
SIMULATOR_MODE=true
HOST=0.0.0.0
PORT=8000
PYTHONPATH=${APP_DIR}
EOF

echo "✅ Backend configured"

# ============================================================================
# STEP 5: Setup Frontend
# ============================================================================

echo ""
echo "Step 5/8: Setting up frontend..."

cd ${APP_DIR}/frontend

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Create environment files for both dev and production
cat > .env <<EOF
# Heimdall Frontend Configuration - Development
VITE_API_URL=http://${SERVER_IP}:8000
VITE_WS_URL=ws://${SERVER_IP}:8000
VITE_USE_REAL_API=true
EOF

cat > .env.production <<EOF
# Heimdall Frontend Configuration - Production
VITE_API_URL=http://${SERVER_IP}:8000
VITE_WS_URL=ws://${SERVER_IP}:8000
VITE_USE_REAL_API=true
EOF

echo "Frontend will connect to: http://${SERVER_IP}:8000"
echo "✅ Real API mode enabled (VITE_USE_REAL_API=true)"

# Install npm dependencies
if [ -f "package.json" ]; then
    echo "Installing npm packages..."
    npm install

    # Build frontend for production
    echo "Building frontend for production..."
    npm run build

    echo "✅ Frontend built successfully"
else
    echo "❌ package.json not found in frontend/"
    exit 1
fi

cd ${APP_DIR}

# ============================================================================
# STEP 6: Create Startup Scripts
# ============================================================================

echo ""
echo "Step 6/8: Creating startup scripts..."

# Backend startup script
cat > ${APP_DIR}/start_backend.sh <<'BACKEND_SCRIPT'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}

source venv/bin/activate
export PYTHONPATH=${DIR}

echo "🚁 Starting Heimdall Backend..."
echo "API: http://$(hostname -I | awk '{print $1}'):8000"
echo ""

python3 -m uvicorn backend.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
BACKEND_SCRIPT

# Frontend startup script
cat > ${APP_DIR}/start_frontend.sh <<'FRONTEND_SCRIPT'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/frontend

echo "🌐 Starting Heimdall Frontend..."
echo "URL: http://$(hostname -I | awk '{print $1}'):4173"
echo ""

npm run preview -- --host 0.0.0.0 --port 4173
FRONTEND_SCRIPT

# Start both script
cat > ${APP_DIR}/start_all.sh <<'START_ALL_SCRIPT'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚁 Starting Heimdall Full Stack..."
echo ""

# Start backend in background
${DIR}/start_backend.sh > ${DIR}/logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: ${BACKEND_PID})"

# Wait for backend to start
sleep 3

# Start frontend in background
${DIR}/start_frontend.sh > ${DIR}/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: ${FRONTEND_PID})"

echo ""
echo "📊 Application Status:"
echo "  Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):4173"
echo ""
echo "📝 Logs:"
echo "  Backend:  tail -f ${DIR}/logs/backend.log"
echo "  Frontend: tail -f ${DIR}/logs/frontend.log"
echo ""
echo "🛑 To stop:"
echo "  ${DIR}/stop_all.sh"
echo ""

# Save PIDs
echo ${BACKEND_PID} > ${DIR}/logs/backend.pid
echo ${FRONTEND_PID} > ${DIR}/logs/frontend.pid
START_ALL_SCRIPT

# Stop all script
cat > ${APP_DIR}/stop_all.sh <<'STOP_ALL_SCRIPT'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛑 Stopping Heimdall services..."

# Stop backend
if [ -f "${DIR}/logs/backend.pid" ]; then
    kill $(cat ${DIR}/logs/backend.pid) 2>/dev/null
    rm ${DIR}/logs/backend.pid
    echo "✅ Backend stopped"
fi

# Stop frontend
if [ -f "${DIR}/logs/frontend.pid" ]; then
    kill $(cat ${DIR}/logs/frontend.pid) 2>/dev/null
    rm ${DIR}/logs/frontend.pid
    echo "✅ Frontend stopped"
fi

# Kill any remaining processes
pkill -f "uvicorn backend.api.main"
pkill -f "vite preview"

echo "✅ All services stopped"
STOP_ALL_SCRIPT

# Make scripts executable
chmod +x ${APP_DIR}/start_backend.sh
chmod +x ${APP_DIR}/start_frontend.sh
chmod +x ${APP_DIR}/start_all.sh
chmod +x ${APP_DIR}/stop_all.sh

echo "✅ Startup scripts created"

# ============================================================================
# STEP 7: Create Logs Directory
# ============================================================================

echo ""
echo "Step 7/8: Creating logs directory..."

mkdir -p ${APP_DIR}/logs
echo "✅ Logs directory: ${APP_DIR}/logs"

# ============================================================================
# STEP 8: Create Systemd Services (Optional)
# ============================================================================

echo ""
echo "Step 8/8: Creating systemd service files..."

cat > /tmp/heimdall-backend.service <<BACKEND_SERVICE
[Unit]
Description=Heimdall Backend API Server
After=network.target

[Service]
Type=simple
User=${TARGET_USER}
WorkingDirectory=${APP_DIR}
Environment="PYTHONPATH=${APP_DIR}"
ExecStart=${APP_DIR}/venv/bin/python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s
StandardOutput=append:${APP_DIR}/logs/backend.log
StandardError=append:${APP_DIR}/logs/backend.log

[Install]
WantedBy=multi-user.target
BACKEND_SERVICE

cat > /tmp/heimdall-frontend.service <<FRONTEND_SERVICE
[Unit]
Description=Heimdall Frontend Web Server
After=network.target heimdall-backend.service

[Service]
Type=simple
User=${TARGET_USER}
WorkingDirectory=${APP_DIR}/frontend
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 4173
Restart=on-failure
RestartSec=5s
StandardOutput=append:${APP_DIR}/logs/frontend.log
StandardError=append:${APP_DIR}/logs/frontend.log

[Install]
WantedBy=multi-user.target
FRONTEND_SERVICE

# Create install script for services
cat > ${APP_DIR}/install_services.sh <<'INSTALL_SERVICES'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
   echo "Please run with sudo"
   exit 1
fi

cp /tmp/heimdall-backend.service /etc/systemd/system/
cp /tmp/heimdall-frontend.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable heimdall-backend
systemctl enable heimdall-frontend

echo "✅ Systemd services installed"
echo ""
echo "Start services:"
echo "  sudo systemctl start heimdall-backend"
echo "  sudo systemctl start heimdall-frontend"
INSTALL_SERVICES

chmod +x ${APP_DIR}/install_services.sh

echo "✅ Systemd service files created"

# ============================================================================
# DONE!
# ============================================================================

echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo "=============================================="
echo ""
echo "📍 Installation: ${APP_DIR}"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "  # Start both frontend and backend:"
echo "  cd ${APP_DIR}"
echo "  ./start_all.sh"
echo ""
echo "  # Or start individually:"
echo "  ./start_backend.sh    # Terminal 1"
echo "  ./start_frontend.sh   # Terminal 2"
echo ""
echo "🔗 Access URLs:"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "  Frontend: http://${SERVER_IP}:4173"
echo "  Backend:  http://${SERVER_IP}:8000"
echo "  API Docs: http://${SERVER_IP}:8000/docs"
echo ""
echo "📝 Logs:"
echo "  tail -f ${APP_DIR}/logs/backend.log"
echo "  tail -f ${APP_DIR}/logs/frontend.log"
echo ""
echo "🛑 Stop services:"
echo "  ${APP_DIR}/stop_all.sh"
echo ""
echo "⚙️  Optional - Install as systemd services:"
echo "  sudo ${APP_DIR}/install_services.sh"
echo ""
echo "=============================================="
