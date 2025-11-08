#!/bin/bash

################################################################################
# Heimdall Sphinx Simulator - VM Setup Script
# Run this script ON the GCP VM after creation
################################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚁 Heimdall Sphinx Simulator - VM Setup${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# Wait for NVIDIA drivers
echo -e "${BLUE}[1/8]${NC} Checking NVIDIA GPU drivers..."
MAX_WAIT=300  # 5 minutes
WAITED=0
while ! nvidia-smi &>/dev/null; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ NVIDIA drivers not installed after 5 minutes${NC}"
        echo -e "${YELLOW}Installing manually...${NC}"
        sudo apt update
        sudo apt install -y ubuntu-drivers-common
        sudo ubuntu-drivers autoinstall
        sudo reboot
        exit 0
    fi
    echo -e "${YELLOW}⏳ Waiting for NVIDIA drivers to install... ($WAITED/$MAX_WAIT seconds)${NC}"
    sleep 10
    WAITED=$((WAITED + 10))
done
echo -e "${GREEN}✓${NC} NVIDIA drivers installed"
nvidia-smi

# Update system
echo -e "${BLUE}[2/8]${NC} Updating system packages..."
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✓${NC} System updated"

# Install dependencies
echo -e "${BLUE}[3/8]${NC} Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    x11-xserver-utils \
    xvfb \
    htop \
    tmux
echo -e "${GREEN}✓${NC} Dependencies installed"

# Install Docker
echo -e "${BLUE}[4/8]${NC} Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✓${NC} Docker installed"
else
    echo -e "${YELLOW}↻${NC} Docker already installed"
fi

# Install NVIDIA Container Toolkit
echo -e "${BLUE}[5/8]${NC} Installing NVIDIA Container Toolkit..."
if ! dpkg -l | grep -q nvidia-container-toolkit; then
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt update
    sudo apt install -y nvidia-container-toolkit
    sudo systemctl restart docker
    echo -e "${GREEN}✓${NC} NVIDIA Container Toolkit installed"
else
    echo -e "${YELLOW}↻${NC} NVIDIA Container Toolkit already installed"
fi

# Verify Docker + GPU
echo -e "${BLUE}[6/8]${NC} Verifying Docker GPU support..."
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
echo -e "${GREEN}✓${NC} Docker GPU support verified"

# Install Parrot Sphinx
echo -e "${BLUE}[7/8]${NC} Installing Parrot Sphinx..."
if ! command -v sphinx &>/dev/null; then
    echo "deb http://plf.parrot.com/sphinx/binary $(lsb_release -cs)/" | \
        sudo tee /etc/apt/sources.list.d/sphinx.list > /dev/null

    # Add Parrot GPG key
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 508B1AE5 || true

    sudo apt update
    sudo apt install -y parrot-sphinx
    echo -e "${GREEN}✓${NC} Parrot Sphinx installed"
else
    echo -e "${YELLOW}↻${NC} Parrot Sphinx already installed"
fi

sphinx --version

# Clone repository and setup backend
echo -e "${BLUE}[8/8]${NC} Setting up Heimdall backend..."

# Create project directory
mkdir -p ~/heimdall
cd ~/heimdall

# Clone repository
if [ ! -d "etdh-hackaton" ]; then
    git clone https://github.com/xeops-sofyen/etdh-hackaton.git
    echo -e "${GREEN}✓${NC} Repository cloned"
else
    echo -e "${YELLOW}↻${NC} Repository already cloned, pulling latest..."
    cd etdh-hackaton
    git pull
    cd ~/heimdall
fi

cd etdh-hackaton/backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}↻${NC} Virtual environment already exists"
fi

# Activate and install dependencies
source venv/bin/activate

# Install Olympe SDK
echo -e "${YELLOW}Installing Olympe SDK...${NC}"
pip install --upgrade pip
pip install parrot-olympe

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip install fastapi uvicorn pydantic python-multipart websockets

echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Create systemd service for Sphinx
echo -e "${BLUE}Creating systemd services...${NC}"

sudo tee /etc/systemd/system/sphinx.service > /dev/null <<EOF
[Unit]
Description=Parrot Sphinx Simulator
After=network.target

[Service]
Type=simple
User=$USER
Environment="DISPLAY=:99"
ExecStartPre=/bin/bash -c 'Xvfb :99 -screen 0 1024x768x24 &'
ExecStart=/usr/bin/sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi4k.drone
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for backend
sudo tee /etc/systemd/system/heimdall-backend.service > /dev/null <<EOF
[Unit]
Description=Heimdall Backend API
After=network.target sphinx.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/heimdall/etdh-hackaton/backend
Environment="PYTHONPATH=/home/$USER/heimdall/etdh-hackaton"
ExecStartPre=/bin/sleep 10
ExecStart=/home/$USER/heimdall/etdh-hackaton/backend/venv/bin/python api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for monitor
sudo tee /etc/systemd/system/heimdall-monitor.service > /dev/null <<EOF
[Unit]
Description=Heimdall Monitor Server
After=network.target heimdall-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/heimdall/etdh-hackaton/backend
ExecStart=/home/$USER/heimdall/etdh-hackaton/backend/venv/bin/python monitor_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo -e "${GREEN}✓${NC} Systemd services created"

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo -e "${YELLOW}To start the services:${NC}"
echo -e "  ${GREEN}sudo systemctl start sphinx${NC}"
echo -e "  ${GREEN}sudo systemctl start heimdall-backend${NC}"
echo -e "  ${GREEN}sudo systemctl start heimdall-monitor${NC}"
echo ""
echo -e "${YELLOW}To enable auto-start on boot:${NC}"
echo -e "  ${GREEN}sudo systemctl enable sphinx heimdall-backend heimdall-monitor${NC}"
echo ""
echo -e "${YELLOW}To check status:${NC}"
echo -e "  ${GREEN}sudo systemctl status sphinx${NC}"
echo -e "  ${GREEN}sudo systemctl status heimdall-backend${NC}"
echo -e "  ${GREEN}sudo systemctl status heimdall-monitor${NC}"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo -e "  ${GREEN}sudo journalctl -u sphinx -f${NC}"
echo -e "  ${GREEN}sudo journalctl -u heimdall-backend -f${NC}"
echo -e "  ${GREEN}sudo journalctl -u heimdall-monitor -f${NC}"
echo ""
echo -e "${YELLOW}External IP:${NC}"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo -e "  ${GREEN}http://$EXTERNAL_IP:8000${NC} - Backend API"
echo -e "  ${GREEN}http://$EXTERNAL_IP:8001${NC} - Monitor Dashboard"
echo ""
echo -e "${BLUE}================================================================================================${NC}"
