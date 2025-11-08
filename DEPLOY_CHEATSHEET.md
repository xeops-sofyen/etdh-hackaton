# 🚀 Deployment Cheat Sheet

Quick commands for deploying to your local onsite simulator.

---

## 📡 Find Simulator IP Address

**On simulator machine:**
```bash
hostname -I
# Example output: 192.168.1.100
```

---

## ⚡ One-Command Deployment

**From your Mac:**
```bash
cd /path/to/etdh-hackaton-1

# Replace with your simulator's IP and username
./deploy_full_stack.sh user@192.168.1.100
```

**That's it!** Wait 5-10 minutes for installation.

---

## 🎮 Start Application

**On simulator machine:**
```bash
cd ~/heimdall-app
./start_all.sh
```

**Output will show:**
```
Backend:  http://192.168.1.100:8000
Frontend: http://192.168.1.100:4173
```

---

## 🌐 Access from Your Mac

**Open in browser:**
```
http://192.168.1.100:4173
```
*(Replace with your simulator's IP)*

---

## 🛑 Stop Application

**On simulator:**
```bash
cd ~/heimdall-app
./stop_all.sh
```

---

## 🔄 Update/Redeploy

**From your Mac:**
```bash
cd /path/to/etdh-hackaton-1
git pull  # Get latest changes
./deploy_full_stack.sh user@192.168.1.100
```

---

## 📋 Status Checks

**On simulator:**
```bash
# Check if running
ps aux | grep -E "uvicorn|vite"

# Check ports
netstat -tulpn | grep -E "8000|4173"

# View logs
tail -f ~/heimdall-app/logs/backend.log
tail -f ~/heimdall-app/logs/frontend.log
```

---

## 🧪 Quick Test

**Test backend:**
```bash
curl http://localhost:8000/
# Should return: {"service":"Heimdall Mission Control","status":"operational"}
```

**Test frontend:**
Open in browser: `http://192.168.1.100:4173`

---

## 🚁 Run Complete Mission

1. **Start Sphinx** (on simulator):
   ```bash
   # Your Sphinx startup command
   sphinx-start  # or ./run_sphinx.sh
   ```

2. **Start Heimdall** (on simulator):
   ```bash
   cd ~/heimdall-app
   ./start_all.sh
   ```

3. **Open Frontend** (on your Mac):
   ```
   http://192.168.1.100:4173
   ```

4. **Create Mission**:
   - Click "New Mission"
   - Click map to add waypoints
   - Save playbook
   - Click "Start Mission"
   - Watch drone fly! 🚁

---

## 🔥 Troubleshooting One-Liners

```bash
# Can't access from Mac? Allow firewall:
sudo ufw allow 8000/tcp && sudo ufw allow 4173/tcp

# Backend won't start? Check Python:
cd ~/heimdall-app && source venv/bin/activate && python --version

# Frontend won't build? Check Node:
node --version  # Should be 18+

# Restart everything:
cd ~/heimdall-app && ./stop_all.sh && ./start_all.sh

# View all logs:
tail -f ~/heimdall-app/logs/*.log
```

---

## 📞 Common IP Examples

```bash
# Office network
./deploy_full_stack.sh admin@192.168.1.50

# Lab network
./deploy_full_stack.sh student@10.0.0.25

# Direct ethernet
./deploy_full_stack.sh user@169.254.1.1
```

---

## 💾 Alternative: USB Deploy (No SSH)

**On your Mac:**
```bash
cd /path/to/etdh-hackaton-1
tar czf heimdall-deploy.tar.gz backend frontend playbooks deploy_on_server.sh \
  --exclude=node_modules --exclude=.git --exclude=venv
# Copy heimdall-deploy.tar.gz to USB drive
```

**On simulator (from USB):**
```bash
cd ~
tar xzf /path/to/usb/heimdall-deploy.tar.gz
chmod +x deploy_on_server.sh
./deploy_on_server.sh
```

---

## 🎯 Directory Locations

```
Simulator machine:
  Application: ~/heimdall-app/
  Logs:        ~/heimdall-app/logs/
  Scripts:     ~/heimdall-app/*.sh
  Frontend:    ~/heimdall-app/frontend/
  Backend:     ~/heimdall-app/backend/
```

---

## 📱 Quick Access URLs

After deployment, bookmark these:

```
Frontend:  http://YOUR_SIMULATOR_IP:4173
Backend:   http://YOUR_SIMULATOR_IP:8000
API Docs:  http://YOUR_SIMULATOR_IP:8000/docs
```

---

## ⚙️ Auto-Start on Boot

**On simulator:**
```bash
cd ~/heimdall-app
sudo ./install_services.sh
sudo systemctl enable heimdall-backend
sudo systemctl enable heimdall-frontend
```

Now services start automatically when simulator boots!

---

## 🆘 Emergency Commands

```bash
# Kill everything
pkill -f "uvicorn backend.api.main"
pkill -f "vite preview"

# Restart from scratch
cd ~/heimdall-app
./stop_all.sh
rm -rf venv frontend/node_modules frontend/dist
./deploy_on_server.sh
./start_all.sh

# Check if ports are taken
netstat -tulpn | grep -E "8000|4173"
```

---

## 📚 Full Documentation

- **Local Deployment:** [DEPLOY_LOCAL_SIMULATOR.md](DEPLOY_LOCAL_SIMULATOR.md)
- **Quick Start:** [QUICKSTART_DEPLOY.md](QUICKSTART_DEPLOY.md)
- **Complete Guide:** [DEPLOY_SIMULATOR.md](DEPLOY_SIMULATOR.md)

---

**Print this page for quick reference!** 🚁
