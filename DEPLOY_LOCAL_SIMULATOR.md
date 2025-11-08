# Deploy Heimdall to Local Onsite Simulator

Quick guide for deploying to your local machine running the Sphinx simulator.

## 📋 Prerequisites

**On the simulator machine:**
- Ubuntu 20.04/22.04 (or similar Linux)
- Python 3.10+
- Sphinx simulator already installed
- Network access from your development machine

**You need to know:**
- Simulator machine's IP address (e.g., `192.168.1.100`)
- SSH access (username/password or SSH key)
- OR physical access to the machine

---

## 🚀 Deployment Methods

### Method 1: SSH Deployment (Recommended)

**From your Mac/development machine:**

```bash
cd /path/to/etdh-hackaton-1

# Deploy to local simulator
# Replace with your simulator's IP and username
./deploy_full_stack.sh user@192.168.1.100

# If using a non-standard SSH port:
./deploy_full_stack.sh user@192.168.1.100 -p 2222
```

**Example outputs:**
```bash
# Common local network scenarios:

# Office network
./deploy_full_stack.sh admin@192.168.1.50

# Lab network
./deploy_full_stack.sh student@10.0.0.25

# Direct ethernet connection
./deploy_full_stack.sh user@169.254.1.1
```

---

### Method 2: USB/Physical Transfer

If SSH is not available or you have physical access:

#### Step 1: Create Package on Your Mac

```bash
cd /path/to/etdh-hackaton-1

# Create deployment package
tar czf heimdall-deploy.tar.gz \
  backend/ \
  frontend/ \
  playbooks/ \
  deploy_on_server.sh \
  --exclude=node_modules \
  --exclude=dist \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=venv

# Package is ready: heimdall-deploy.tar.gz
```

#### Step 2: Transfer Package

**Choose one:**

**Option A - USB Drive:**
```bash
# Copy to USB drive
cp heimdall-deploy.tar.gz /Volumes/USB_DRIVE/

# Then physically move USB to simulator machine
```

**Option B - Network Share:**
```bash
# If you have a shared network folder
cp heimdall-deploy.tar.gz /path/to/shared/folder/
```

**Option C - SCP (if available):**
```bash
scp heimdall-deploy.tar.gz user@192.168.1.100:~/
```

#### Step 3: Deploy on Simulator Machine

**On the simulator machine (via keyboard/monitor or SSH):**

```bash
# Extract package
cd ~
tar xzf heimdall-deploy.tar.gz

# Make deployment script executable
chmod +x deploy_on_server.sh

# Run deployment
./deploy_on_server.sh
```

---

### Method 3: Git Clone (If Simulator Has Internet)

**On the simulator machine:**

```bash
cd ~

# Clone repository
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton

# Run deployment
chmod +x deploy_on_server.sh
./deploy_on_server.sh
```

---

## 🔧 Network Configuration

### Finding Your Simulator's IP Address

**On the simulator machine, run:**

```bash
# Show all IP addresses
hostname -I

# Or more detailed
ip addr show

# Or using ifconfig
ifconfig
```

**Common network interfaces:**
- `eth0` or `enp*` - Wired ethernet
- `wlan0` or `wlp*` - WiFi
- Look for IP like `192.168.x.x` or `10.x.x.x`

### Setting a Static IP (Optional)

If your simulator's IP keeps changing:

```bash
# Edit network configuration
sudo nano /etc/netplan/01-netcfg.yaml
```

Add:
```yaml
network:
  version: 2
  ethernets:
    eth0:  # or your interface name
      dhcp4: no
      addresses:
        - 192.168.1.100/24  # Your desired IP
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply:
```bash
sudo netplan apply
```

---

## 🚀 Starting the Application

### After Deployment Completes:

```bash
# On simulator machine
cd ~/heimdall-app

# Start both frontend and backend
./start_all.sh
```

**You'll see:**
```
🚁 Starting Heimdall Full Stack...

✅ Backend started (PID: 12345)
✅ Frontend started (PID: 12346)

📊 Application Status:
  Backend:  http://192.168.1.100:8000
  Frontend: http://192.168.1.100:4173

📝 Logs:
  Backend:  tail -f ~/heimdall-app/logs/backend.log
  Frontend: tail -f ~/heimdall-app/logs/frontend.log

🛑 To stop:
  ~/heimdall-app/stop_all.sh
```

---

## 🌐 Accessing from Your Development Machine

### Option 1: Direct Browser Access

If your Mac and simulator are on the same network:

**Open in browser on your Mac:**
```
http://192.168.1.100:4173  (Frontend)
http://192.168.1.100:8000  (Backend API)
```

Replace `192.168.1.100` with your simulator's actual IP.

### Option 2: SSH Port Forwarding

For more secure access or if firewall blocks direct access:

**From your Mac:**
```bash
# Forward ports through SSH
ssh user@192.168.1.100 \
  -L 4173:localhost:4173 \
  -L 8000:localhost:8000

# Keep this terminal open
```

**Then access locally:**
```
http://localhost:4173  (Frontend)
http://localhost:8000  (Backend API)
```

---

## 🧪 Quick Test

### 1. Test Backend API

**From simulator machine:**
```bash
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "service": "Heimdall Mission Control",
  "status": "operational",
  "version": "1.0.0"
}
```

### 2. Test Frontend

**From your Mac's browser:**
```
http://192.168.1.100:4173
```

You should see the Heimdall mission control interface with a map.

### 3. Test Complete Flow

**Terminal 1 (on simulator) - Start Sphinx:**
```bash
# Your existing Sphinx startup command
sphinx-start
# OR
./run_sphinx.sh
# OR however you normally start Sphinx
```

**Terminal 2 (on simulator) - Services running:**
```bash
# Already started by ./start_all.sh
# Check status:
ps aux | grep -E "uvicorn|vite"
```

**Browser (on your Mac):**
```
http://192.168.1.100:4173
```

1. Click "New Mission"
2. Click on map to add waypoints
3. Save playbook
4. Click "Start Mission"
5. Watch Sphinx! 🚁

---

## 🛠️ Management Commands

### On Simulator Machine:

```bash
# Start services
cd ~/heimdall-app
./start_all.sh

# Stop services
./stop_all.sh

# Restart services
./stop_all.sh && ./start_all.sh

# View logs in real-time
tail -f logs/backend.log
tail -f logs/frontend.log

# Check if running
ps aux | grep -E "uvicorn|vite"

# Check ports
netstat -tulpn | grep -E "8000|4173"
```

### Install as System Service (Auto-start):

```bash
cd ~/heimdall-app
sudo ./install_services.sh

# Services will now start automatically on boot
sudo systemctl status heimdall-backend
sudo systemctl status heimdall-frontend
```

---

## 🔥 Firewall Configuration

If you can't access from your Mac, check firewall:

### Ubuntu/Debian:

```bash
# Check firewall status
sudo ufw status

# Allow ports
sudo ufw allow 8000/tcp
sudo ufw allow 4173/tcp

# Reload
sudo ufw reload
```

### CentOS/RHEL:

```bash
# Allow ports
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=4173/tcp
sudo firewall-cmd --reload
```

---

## 📊 Typical Network Setup

```
Your Development Mac              Simulator Machine
(192.168.1.50)                    (192.168.1.100)
       |                                 |
       |         Local Network           |
       |         (192.168.1.0/24)        |
       └─────────────┬──────────────────┘
                     |
              Network Switch/Router
              (192.168.1.1)
```

**Browser on Mac → http://192.168.1.100:4173**
```
Mac Browser
    ↓
Frontend (Simulator:4173)
    ↓ API calls
Backend (Simulator:8000)
    ↓ Olympe commands
Sphinx (Simulator:10.202.0.1)
```

---

## 🐛 Troubleshooting

### Can't SSH to Simulator

```bash
# From your Mac, test connection
ping 192.168.1.100

# Test SSH
ssh user@192.168.1.100

# If SSH not installed on simulator:
# On simulator machine:
sudo apt-get update
sudo apt-get install openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
```

### Can't Access Frontend from Mac

**On simulator, check if running:**
```bash
netstat -tulpn | grep 4173
# Should show vite listening on 0.0.0.0:4173
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 4173/tcp
```

**Check frontend is bound to all interfaces:**
```bash
# In start_frontend.sh, ensure it has:
npm run preview -- --host 0.0.0.0 --port 4173
```

### Backend Can't Connect to Sphinx

```bash
# On simulator, check Sphinx is running
ps aux | grep sphinx

# Check drone IP is accessible
ping 10.202.0.1

# Test Olympe connection
cd ~/heimdall-app
source venv/bin/activate
python -c "import olympe; print('Olympe imported successfully')"
```

---

## 📁 Directory Structure on Simulator

```
/home/user/heimdall-app/
├── backend/
│   ├── api/
│   │   └── main.py          # FastAPI server
│   ├── drone_controller/
│   ├── olympe_translator/
│   └── requirements.txt
├── frontend/
│   ├── dist/                 # Built frontend files
│   ├── src/
│   └── package.json
├── playbooks/                # Mission files
├── venv/                     # Python virtual env
├── logs/
│   ├── backend.log
│   └── frontend.log
└── *.sh                      # Management scripts
```

---

## 🔄 Updating the Application

### Pull Latest Changes:

**If deployed via Git:**
```bash
cd ~/heimdall-app
git pull
./stop_all.sh
./deploy_on_server.sh  # Re-run deployment
./start_all.sh
```

**If deployed via package:**
```bash
# Transfer new package
# Then on simulator:
cd ~
./stop_all.sh
tar xzf heimdall-deploy-new.tar.gz
./deploy_on_server.sh
./start_all.sh
```

---

## ✅ Quick Reference Card

```bash
# === ON SIMULATOR MACHINE ===

# Deploy (first time)
~/deploy_on_server.sh

# Start everything
cd ~/heimdall-app && ./start_all.sh

# Stop everything
cd ~/heimdall-app && ./stop_all.sh

# View logs
tail -f ~/heimdall-app/logs/*.log

# Check status
ps aux | grep -E "uvicorn|vite"

# === FROM YOUR MAC ===

# Access frontend
http://192.168.1.100:4173

# Access backend
http://192.168.1.100:8000

# Deploy updates
./deploy_full_stack.sh user@192.168.1.100
```

---

## 💡 Tips for Onsite Setup

1. **Use Static IP** - Set a static IP on simulator to avoid IP changes
2. **Bookmarks** - Save frontend URL in browser bookmarks
3. **Auto-start** - Install systemd services for automatic startup
4. **Shared Screen** - Use VNC or SSH for remote management
5. **Local DNS** - Add entry to `/etc/hosts` for easier access:
   ```bash
   # On your Mac
   echo "192.168.1.100 heimdall-sim" | sudo tee -a /etc/hosts

   # Then access via:
   http://heimdall-sim:4173
   ```

---

**Ready to deploy to your local simulator!** 🚁

Need help? Check the main documentation:
- [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md)
- [DEPLOY_SIMULATOR.md](DEPLOY_SIMULATOR.md)
