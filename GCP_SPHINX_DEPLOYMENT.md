# GCP Sphinx Simulator Deployment Guide

## 🎯 Overview

Deploy Parrot Sphinx drone simulator on Google Cloud Platform (GCP) with proper GPU support and networking for the Heimdall backend integration.

## 🏗️ Architecture

```
GCP Compute Engine VM
├── Ubuntu 22.04 LTS
├── NVIDIA GPU (T4 or better)
├── Parrot Sphinx Simulator
├── Olympe SDK
├── Heimdall Backend
└── Public IP for API access
```

## 📋 Prerequisites

- GCP account with billing enabled
- GCP project created (e.g., `heimdall-drone` or use existing)
- `gcloud` CLI installed locally
- Sufficient quota for GPU instances

## 🚀 Step 1: GCP Project Setup

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export ZONE="us-central1-a"

# Login to GCP
gcloud auth login

# Set project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
```

## 🖥️ Step 2: Create GPU-Enabled VM

### Option A: Using gcloud CLI (Recommended)

```bash
# Create VM with NVIDIA T4 GPU
gcloud compute instances create sphinx-simulator \
  --zone=$ZONE \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --maintenance-policy=TERMINATE \
  --metadata=install-nvidia-driver=True \
  --tags=sphinx-simulator,http-server,https-server \
  --scopes=cloud-platform

# Note: --maintenance-policy=TERMINATE is required for GPU instances
# GPU instances cannot live-migrate
```

### Option B: Using Console

1. Go to **Compute Engine** > **VM instances**
2. Click **Create Instance**
3. Configure:
   - **Name:** `sphinx-simulator`
   - **Region:** `us-central1` (or closest to your users)
   - **Machine type:** `n1-standard-4` (4 vCPUs, 15 GB memory)
   - **GPU:** Add GPU → NVIDIA Tesla T4 → 1 GPU
   - **Boot disk:** Ubuntu 22.04 LTS, 50 GB SSD
   - **Firewall:** Allow HTTP and HTTPS traffic

## 🔐 Step 3: Configure Firewall Rules

```bash
# Allow backend API access (port 8000)
gcloud compute firewall-rules create allow-backend-api \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8000 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=sphinx-simulator

# Allow monitor server (port 8001)
gcloud compute firewall-rules create allow-monitor \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8001 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=sphinx-simulator

# Allow Sphinx ports (if needed for debugging)
gcloud compute firewall-rules create allow-sphinx \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8383,udp:8383,tcp:9100 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=sphinx-simulator
```

## 📦 Step 4: Install Dependencies on VM

### SSH into the VM

```bash
gcloud compute ssh sphinx-simulator --zone=$ZONE
```

### Install NVIDIA Drivers (if not auto-installed)

```bash
# Check if drivers are installed
nvidia-smi

# If not installed, install manually
sudo apt update
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Install System Dependencies

```bash
# After reboot, SSH back in
gcloud compute ssh sphinx-simulator --zone=$ZONE

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
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
  xvfb

# Install Docker (for Sphinx)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify Docker + GPU
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 🦅 Step 5: Install Parrot Sphinx

```bash
# Add Parrot repository
echo "deb http://plf.parrot.com/sphinx/binary `lsb_release -cs`/" | \
  sudo tee /etc/apt/sources.list.d/sphinx.list > /dev/null

# Add Parrot GPG key
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 508B1AE5

# Install Sphinx
sudo apt update
sudo apt install -y parrot-sphinx

# Verify installation
sphinx --version
```

## 🐍 Step 6: Install Olympe SDK

```bash
# Create project directory
mkdir -p ~/heimdall
cd ~/heimdall

# Clone your repository
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton

# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Olympe SDK
pip install parrot-olympe

# Install backend dependencies
pip install -r requirements.txt  # If you have one
# OR install manually:
pip install fastapi uvicorn pydantic python-multipart
```

## 🚁 Step 7: Start Sphinx Simulator

```bash
# Start Xvfb (virtual display)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Start Sphinx with ANAFI drone model
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi4k.drone &

# Wait a few seconds for Sphinx to start
sleep 10

# Verify Sphinx is running
ps aux | grep sphinx
```

## 🔧 Step 8: Start Heimdall Backend

```bash
# In the backend directory
cd ~/heimdall/etdh-hackaton/backend
source venv/bin/activate

# Start the REAL backend (with Olympe)
PYTHONPATH=~/heimdall/etdh-hackaton python api/main.py > /tmp/backend.log 2>&1 &

# Or use screen to keep it running
screen -S backend
PYTHONPATH=~/heimdall/etdh-hackaton python api/main.py
# Press Ctrl+A then D to detach

# Start monitor server (optional)
screen -S monitor
python monitor_server.py
# Press Ctrl+A then D to detach
```

## 🌐 Step 9: Get Public IP and Test

```bash
# Get your VM's public IP
gcloud compute instances describe sphinx-simulator \
  --zone=$ZONE \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Test from your local machine
export VM_IP="<your-vm-ip>"

# Test backend health
curl http://$VM_IP:8000/

# Test mission execution
curl -X POST http://$VM_IP:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d @/tmp/test_mission.json
```

## 🔄 Step 10: Update Frontend to Use GCP Backend

```bash
# On your local machine
cd /Users/sofyenmarzougui/etdh-hackaton/frontend

# Update .env
cat > .env << EOF
VITE_API_URL=http://$VM_IP:8000
VITE_WS_URL=ws://$VM_IP:8000
VITE_USE_REAL_API=true
EOF

# Restart frontend
npm run dev
```

## 🎛️ Management Commands

### Start Services on Boot (Systemd)

Create systemd service files:

```bash
# Backend service
sudo tee /etc/systemd/system/heimdall-backend.service << EOF
[Unit]
Description=Heimdall Backend API
After=network.target sphinx.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/heimdall/etdh-hackaton/backend
Environment="PYTHONPATH=/home/$USER/heimdall/etdh-hackaton"
ExecStartPre=/bin/sleep 5
ExecStart=/home/$USER/heimdall/etdh-hackaton/backend/venv/bin/python api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Sphinx service
sudo tee /etc/systemd/system/sphinx.service << EOF
[Unit]
Description=Parrot Sphinx Simulator
After=network.target

[Service]
Type=simple
User=$USER
Environment="DISPLAY=:99"
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1024x768x24
ExecStart=/usr/bin/sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi4k.drone
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable sphinx heimdall-backend
sudo systemctl start sphinx
sudo systemctl start heimdall-backend

# Check status
sudo systemctl status sphinx
sudo systemctl status heimdall-backend
```

### View Logs

```bash
# Backend logs
sudo journalctl -u heimdall-backend -f

# Sphinx logs
sudo journalctl -u sphinx -f

# Or use log files
tail -f /tmp/backend.log
```

### Stop/Start Services

```bash
# Stop all
sudo systemctl stop heimdall-backend sphinx

# Start all
sudo systemctl start sphinx
sleep 5
sudo systemctl start heimdall-backend

# Restart
sudo systemctl restart heimdall-backend
```

## 💰 Cost Optimization

### Estimated Monthly Costs (us-central1)

- **n1-standard-4:** ~$150/month
- **NVIDIA Tesla T4:** ~$350/month
- **50GB SSD:** ~$10/month
- **Network egress:** ~$5-20/month
- **Total:** ~$515-535/month

### Cost Reduction Strategies

1. **Use Preemptible VMs** (up to 80% cheaper)
   ```bash
   gcloud compute instances create sphinx-simulator \
     --preemptible \
     # ... other flags
   ```

2. **Auto-shutdown when not in use**
   ```bash
   # Create shutdown script
   sudo crontab -e
   # Add: 0 22 * * * /sbin/shutdown -h now
   ```

3. **Use smaller machine type for testing**
   ```bash
   # n1-standard-2 instead of n1-standard-4
   --machine-type=n1-standard-2
   ```

4. **Use Committed Use Discounts** (1 or 3 year commitment)

## 🐛 Troubleshooting

### GPU not detected

```bash
# Check GPU
nvidia-smi

# If not working, reinstall drivers
sudo apt purge nvidia-*
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Sphinx fails to start

```bash
# Check X display
echo $DISPLAY
ps aux | grep Xvfb

# Restart Xvfb
pkill Xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

### Backend can't connect to Sphinx

```bash
# Check Sphinx is running
ps aux | grep sphinx

# Check drone IP (should be 10.202.0.1)
ping 10.202.0.1

# Restart Sphinx
sudo systemctl restart sphinx
```

### Firewall blocking connections

```bash
# Check firewall rules
gcloud compute firewall-rules list

# Test locally first
curl http://localhost:8000/

# Check VM external IP
curl http://$(curl -s ifconfig.me):8000/
```

## 📊 Monitoring

### Basic Monitoring

```bash
# CPU/Memory
htop

# GPU usage
watch -n 1 nvidia-smi

# Network
sudo netstat -tulpn | grep -E '8000|8001'
```

### GCP Monitoring

1. Go to **Monitoring** in GCP Console
2. Create dashboard for:
   - CPU utilization
   - GPU utilization
   - Memory usage
   - Network traffic
   - Disk I/O

## 🔒 Security Best Practices

1. **Use IAP for SSH** (instead of public SSH)
   ```bash
   gcloud compute ssh sphinx-simulator --tunnel-through-iap
   ```

2. **Restrict API access by IP**
   ```bash
   # Only allow your office IP
   gcloud compute firewall-rules update allow-backend-api \
     --source-ranges=YOUR.IP.ADDRESS.HERE/32
   ```

3. **Enable OS Login**
   ```bash
   gcloud compute instances add-metadata sphinx-simulator \
     --metadata enable-oslogin=TRUE
   ```

4. **Regular updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## 🎯 Next Steps

1. **Set up CI/CD** for automatic deployments
2. **Add HTTPS** with Let's Encrypt
3. **Set up monitoring alerts**
4. **Create VM snapshot** for backup
5. **Document API endpoints** for team

## 📚 Useful Commands Cheatsheet

```bash
# SSH into VM
gcloud compute ssh sphinx-simulator --zone=$ZONE

# Copy files to VM
gcloud compute scp local-file.txt sphinx-simulator:~/

# Copy files from VM
gcloud compute scp sphinx-simulator:~/remote-file.txt ./

# Stop VM
gcloud compute instances stop sphinx-simulator --zone=$ZONE

# Start VM
gcloud compute instances start sphinx-simulator --zone=$ZONE

# Delete VM
gcloud compute instances delete sphinx-simulator --zone=$ZONE

# View VM details
gcloud compute instances describe sphinx-simulator --zone=$ZONE
```

---

**Ready to deploy! 🚀**

Need help? Check the docs:
- [Parrot Sphinx](https://developer.parrot.com/docs/sphinx/)
- [Olympe SDK](https://developer.parrot.com/docs/olympe/)
- [GCP Compute Engine](https://cloud.google.com/compute/docs)
