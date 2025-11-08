# GCP Sphinx Deployment - Quick Start Guide

**Automated deployment of Heimdall Sphinx Simulator on Google Cloud Platform**

---

## 🚀 One-Command Deployment

### **Prerequisites**
- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Sufficient GPU quota (NVIDIA T4)

### **Step 1: Authenticate with GCP**

```bash
gcloud auth login
```

### **Step 2: Run Deployment Script**

```bash
cd /Users/sofyenmarzougui/etdh-hackaton
./scripts/deploy-sphinx-gcp.sh
```

This script will:
- ✅ Create firewall rules (ports 8000, 8001, 8383, 9100)
- ✅ Deploy GPU-enabled VM (n1-standard-4 + Tesla T4)
- ✅ Install NVIDIA drivers automatically
- ✅ Configure networking and security

**Deployment time:** ~5 minutes

---

## 🖥️ VM Setup (After Deployment)

Once the VM is created, SSH into it:

```bash
gcloud compute ssh heimdall-sphinx-simulator --zone=europe-west1-b
```

### **Option A: Automated Setup (Recommended)**

```bash
# Run the setup script
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup-sphinx-vm.sh | bash
```

This will:
- Install Parrot Sphinx simulator
- Install Olympe SDK
- Clone Heimdall backend
- Create systemd services for auto-start

### **Option B: Manual Setup**

Follow the detailed steps in [GCP_SPHINX_DEPLOYMENT.md](GCP_SPHINX_DEPLOYMENT.md) starting from Step 4.

---

## ▶️ Starting Services

Once setup is complete, start the services:

```bash
# Start Sphinx simulator
sudo systemctl start sphinx

# Start Heimdall backend
sudo systemctl start heimdall-backend

# Start monitor server
sudo systemctl start heimdall-monitor

# Enable auto-start on boot
sudo systemctl enable sphinx heimdall-backend heimdall-monitor
```

---

## 🌐 Access Your Deployment

Get your VM's public IP:

```bash
gcloud compute instances describe heimdall-sphinx-simulator \
  --zone=europe-west1-b \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Then access:
- **Backend API:** `http://<EXTERNAL_IP>:8000`
- **Monitor Dashboard:** `http://<EXTERNAL_IP>:8001`
- **Health Check:** `http://<EXTERNAL_IP>:8000/`

---

## 🔍 Monitoring & Logs

### **Check Service Status**

```bash
sudo systemctl status sphinx
sudo systemctl status heimdall-backend
sudo systemctl status heimdall-monitor
```

### **View Live Logs**

```bash
# Sphinx logs
sudo journalctl -u sphinx -f

# Backend logs
sudo journalctl -u heimdall-backend -f

# Monitor logs
sudo journalctl -u heimdall-monitor -f
```

### **Web-Based Monitor**

Open `http://<EXTERNAL_IP>:8001` in your browser for a real-time dashboard.

---

## 🧪 Testing the Deployment

### **1. Test Backend Health**

```bash
export VM_IP="<your-vm-ip>"
curl http://$VM_IP:8000/
```

Expected response:
```json
{
  "service": "Heimdall Backend API",
  "version": "1.0.0",
  "mode": "Production - Olympe/Sphinx"
}
```

### **2. Test Mission Execution**

Create a test mission file:

```bash
cat > /tmp/test_mission.json << 'EOF'
{
  "playbook": {
    "mission_id": "gcp-test-001",
    "mission_type": "patrol",
    "description": "GCP deployment test mission",
    "waypoints": [
      {"lat": 48.8566, "lon": 2.3522, "alt": 120}
    ],
    "flight_parameters": {
      "altitude_m": 120,
      "speed_mps": 10
    },
    "camera_settings": {
      "mode": "photo",
      "resolution": "4K"
    },
    "auto_execute": true
  },
  "simulate": false
}
EOF
```

Send the mission:

```bash
curl -X POST http://$VM_IP:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d @/tmp/test_mission.json
```

### **3. Monitor in Real-Time**

Open `http://$VM_IP:8001` and watch the mission appear live!

---

## 🔧 Update Frontend to Use GCP Backend

On your **local machine**, update the frontend to connect to the GCP backend:

```bash
cd /Users/sofyenmarzougui/etdh-hackaton/frontend

# Update .env
cat > .env << EOF
VITE_API_URL=http://<VM_IP>:8000
VITE_WS_URL=ws://<VM_IP>:8000
VITE_USE_REAL_API=true
EOF

# Restart frontend
npm run dev
```

Now your frontend dashboard will control the real drone simulator in the cloud! 🚁

---

## 💰 Cost Management

### **Estimated Monthly Costs (europe-west1)**

| Component | Cost/Month |
|-----------|-----------|
| n1-standard-4 VM | ~€130 |
| NVIDIA Tesla T4 GPU | ~€300 |
| 50GB SSD Boot Disk | ~€8 |
| Network Egress | ~€5-20 |
| **Total** | **~€443-458/month** |

### **Stop VM to Save Costs**

```bash
# Stop the VM (you still pay for disk storage)
gcloud compute instances stop heimdall-sphinx-simulator --zone=europe-west1-b

# Start it again when needed
gcloud compute instances start heimdall-sphinx-simulator --zone=europe-west1-b
```

### **Use Preemptible VMs (80% cheaper)**

Edit `scripts/deploy-sphinx-gcp.sh` and add `--preemptible` flag to the instance creation command. Note that preemptible VMs can be terminated at any time.

---

## 🛠️ Management Commands

### **SSH into VM**

```bash
gcloud compute ssh heimdall-sphinx-simulator --zone=europe-west1-b
```

### **Copy Files to VM**

```bash
gcloud compute scp local-file.txt heimdall-sphinx-simulator:~/
```

### **Copy Files from VM**

```bash
gcloud compute scp heimdall-sphinx-simulator:~/remote-file.txt ./
```

### **Delete VM (when done)**

```bash
gcloud compute instances delete heimdall-sphinx-simulator --zone=europe-west1-b
```

---

## 🐛 Troubleshooting

### **GPU Not Detected**

```bash
# SSH into VM
gcloud compute ssh heimdall-sphinx-simulator --zone=europe-west1-b

# Check GPU
nvidia-smi

# If not working, reinstall drivers
sudo apt purge nvidia-*
sudo ubuntu-drivers autoinstall
sudo reboot
```

### **Sphinx Fails to Start**

```bash
# Check Xvfb is running
ps aux | grep Xvfb

# Restart Xvfb
pkill Xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Restart Sphinx
sudo systemctl restart sphinx
```

### **Backend Can't Connect to Sphinx**

```bash
# Check Sphinx is running
ps aux | grep sphinx

# Check drone IP (should be 10.202.0.1)
ping 10.202.0.1

# Restart services
sudo systemctl restart sphinx
sudo systemctl restart heimdall-backend
```

### **Firewall Blocking Connections**

```bash
# Check firewall rules
gcloud compute firewall-rules list

# Test locally first
curl http://localhost:8000/

# Check external access
curl http://$(curl -s ifconfig.me):8000/
```

---

## 📁 Project Structure

```
etdh-hackaton/
├── scripts/
│   ├── deploy-sphinx-gcp.sh        # GCP VM deployment script
│   └── setup-sphinx-vm.sh          # VM setup script (Sphinx + backend)
├── backend/
│   ├── api/main.py                 # Real backend (Olympe)
│   ├── api/main_demo.py            # Demo backend (no Olympe)
│   ├── monitor_server.py           # Real-time monitoring server
│   └── monitor_live.html           # Monitor dashboard
├── GCP_SPHINX_DEPLOYMENT.md        # Detailed deployment guide
├── GCP_QUICKSTART.md               # This file
└── BACKEND_MONITORING_FEATURES.md  # Monitoring documentation
```

---

## 🎯 Next Steps

1. ✅ Deploy VM with `deploy-sphinx-gcp.sh`
2. ✅ Run setup script on VM
3. ✅ Start services
4. ✅ Test with curl
5. ✅ Update frontend to use GCP backend
6. ✅ Control real drone from your dashboard!

---

## 📚 Additional Resources

- **Detailed Guide:** [GCP_SPHINX_DEPLOYMENT.md](GCP_SPHINX_DEPLOYMENT.md)
- **Monitoring Features:** [BACKEND_MONITORING_FEATURES.md](BACKEND_MONITORING_FEATURES.md)
- **Parrot Sphinx Docs:** https://developer.parrot.com/docs/sphinx/
- **Olympe SDK Docs:** https://developer.parrot.com/docs/olympe/
- **GCP Compute Engine:** https://cloud.google.com/compute/docs

---

**Ready to deploy! 🚀**

Questions? Check the troubleshooting section or review the detailed deployment guide.
