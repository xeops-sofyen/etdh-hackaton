#!/bin/bash
#
# Deploy Heimdall Full Stack to Remote Simulator Machine
# Run this FROM your local machine
#

set -e

echo "🚁 Heimdall Full Stack Remote Deployment"
echo "========================================"
echo ""

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <user>@<host> [-p port]"
    echo ""
    echo "Examples:"
    echo "  $0 root@ssh8.vast.ai -p 23570"
    echo "  $0 heimdall@192.168.1.100"
    echo ""
    exit 1
fi

REMOTE=$1
shift  # Remove first argument

# Parse additional arguments (like -p for port)
SSH_ARGS="$@"

echo "📡 Target: ${REMOTE}"
echo "🔑 SSH Args: ${SSH_ARGS}"
echo ""

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📁 Project: ${PROJECT_DIR}"
echo ""

# ============================================================================
# STEP 1: Create Deployment Package
# ============================================================================

echo "Step 1/4: Creating deployment package..."

DEPLOY_PACKAGE="${PROJECT_DIR}/heimdall-deploy.tar.gz"

# Clean up old package
rm -f ${DEPLOY_PACKAGE}

# Create tar archive (excluding unnecessary files)
cd ${PROJECT_DIR}
tar czf ${DEPLOY_PACKAGE} \
    backend/ \
    frontend/ \
    playbooks/ \
    deploy_on_server.sh \
    --exclude=node_modules \
    --exclude=dist \
    --exclude=build \
    --exclude=__pycache__ \
    --exclude=*.pyc \
    --exclude=.git \
    --exclude=venv \
    --exclude=.env \
    --exclude=logs

PACKAGE_SIZE=$(du -h ${DEPLOY_PACKAGE} | cut -f1)
echo "✅ Package created: ${PACKAGE_SIZE}"

# ============================================================================
# STEP 2: Transfer Package
# ============================================================================

echo ""
echo "Step 2/4: Transferring to ${REMOTE}..."

# Transfer package
scp ${SSH_ARGS} ${DEPLOY_PACKAGE} ${REMOTE}:~/

echo "✅ Package transferred"

# ============================================================================
# STEP 3: Extract and Run Deployment
# ============================================================================

echo ""
echo "Step 3/4: Running deployment on remote machine..."

ssh ${SSH_ARGS} ${REMOTE} << 'REMOTE_COMMANDS'
set -e

echo "📦 Extracting deployment package..."

# Extract to home directory
cd ~
tar xzf heimdall-deploy.tar.gz

# Make deployment script executable
chmod +x deploy_on_server.sh

echo "✅ Package extracted"
echo ""
echo "🚀 Running deployment script..."
echo ""

# Run deployment
./deploy_on_server.sh

REMOTE_COMMANDS

echo "✅ Deployment completed on remote machine"

# ============================================================================
# STEP 4: Get Connection Info
# ============================================================================

echo ""
echo "Step 4/4: Getting connection information..."

REMOTE_IP=$(ssh ${SSH_ARGS} ${REMOTE} "hostname -I | awk '{print \$1}'")

echo ""
echo "=============================================="
echo "✅ Deployment Successful!"
echo "=============================================="
echo ""
echo "🔗 Access your application:"
echo ""
echo "  Frontend: http://${REMOTE_IP}:4173"
echo "  Backend:  http://${REMOTE_IP}:8000"
echo "  API Docs: http://${REMOTE_IP}:8000/docs"
echo ""
echo "🌐 SSH Port Forwarding (for local access):"
echo ""
echo "  ssh ${SSH_ARGS} ${REMOTE} \\"
echo "    -L 4173:localhost:4173 \\"
echo "    -L 8000:localhost:8000"
echo ""
echo "  Then access locally:"
echo "    Frontend: http://localhost:4173"
echo "    Backend:  http://localhost:8000"
echo ""
echo "🔧 Manage remote services:"
echo ""
echo "  # Start services"
echo "  ssh ${SSH_ARGS} ${REMOTE} 'cd ~/heimdall-app && ./start_all.sh'"
echo ""
echo "  # Stop services"
echo "  ssh ${SSH_ARGS} ${REMOTE} 'cd ~/heimdall-app && ./stop_all.sh'"
echo ""
echo "  # View logs"
echo "  ssh ${SSH_ARGS} ${REMOTE} 'tail -f ~/heimdall-app/logs/*.log'"
echo ""
echo "=============================================="

# Cleanup local package
rm -f ${DEPLOY_PACKAGE}
echo ""
echo "🧹 Cleaned up local deployment package"
echo ""
