# Heimdall Full Stack Deployment on Sphinx Simulator Machine

Complete guide to deploy both frontend and backend on your Sphinx simulator machine.

## 📋 Prerequisites

- Ubuntu 20.04/22.04 (your Vast.ai instance)
- Python 3.10+
- Node.js 18+ and npm
- Sphinx simulator already installed
- At least 4GB free disk space

## 🚀 Quick Deploy (Recommended)

### Option 1: Automated Script Deployment

```bash
# On your local machine, transfer files to simulator
cd /path/to/etdh-hackaton-1
./deploy_full_stack.sh <user>@<simulator-ip>

# Example for Vast.ai:
./deploy_full_stack.sh root@ssh8.vast.ai -p 23570
```

### Option 2: Manual Deployment

Follow the steps below for complete control.

---

## 📦 Manual Deployment Steps

### Step 1: Transfer Project to Simulator

**From your local machine:**

```bash
# Create deployment package
cd /path/to/etdh-hackaton-1
tar czf heimdall-deploy.tar.gz \
  backend/ \
  frontend/ \
  playbooks/ \
  deploy_on_server.sh \
  --exclude=node_modules \
  --exclude=dist \
  --exclude=build \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=venv

# Transfer to simulator (Vast.ai example)
scp -P 23570 heimdall-deploy.tar.gz root@ssh8.vast.ai:/home/heimdall/

# Or use rsync for faster sync
rsync -avz -e "ssh -p 23570" \
  --exclude=node_modules \
  --exclude=dist \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=venv \
  backend/ frontend/ playbooks/ \
  root@ssh8.vast.ai:/home/heimdall/heimdall-app/
```

### Step 2: Run Deployment on Simulator

**SSH into simulator:**

```bash
# For Vast.ai
ssh -p 23570 root@ssh8.vast.ai

# Switch to heimdall user
su - heimdall

# Extract and deploy
cd ~
tar xzf heimdall-deploy.tar.gz
cd heimdall-app
chmod +x deploy_on_server.sh
./deploy_on_server.sh
```

---

## 🐳 Docker Deployment (Alternative)

If you prefer Docker (includes both frontend + backend):

### On Simulator Machine:

```bash
cd /home/heimdall/heimdall-app

# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access the application:**
- Frontend: http://<simulator-ip>:4173
- Backend API: http://<simulator-ip>:8000
- API Docs: http://<simulator-ip>:8000/docs

### Stop services:

```bash
docker-compose down
```

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env` (created during deployment):

```bash
# Drone/Simulator connection
DRONE_IP=10.202.0.1
SIMULATOR_MODE=true

# API Server
HOST=0.0.0.0
PORT=8000

# CORS (for frontend)
FRONTEND_URL=http://localhost:4173
```

### Frontend Configuration

Edit `frontend/.env.production`:

```bash
# Backend API URL (use simulator's IP)
VITE_API_URL=http://<SIMULATOR_IP>:8000
VITE_WS_URL=ws://<SIMULATOR_IP>:8000
VITE_USE_REAL_API=true
```

**Example for Vast.ai:**
```bash
VITE_API_URL=http://50.217.226.47:8000
VITE_WS_URL=ws://50.217.226.47:8000
VITE_USE_REAL_API=true
```

---

## 🚁 Running the Application

### Start Backend

```bash
cd /home/heimdall/heimdall-app
./start_backend.sh
```

Backend will be available at: `http://<simulator-ip>:8000`

### Start Frontend

**In a new terminal:**

```bash
cd /home/heimdall/heimdall-app
./start_frontend.sh
```

Frontend will be available at: `http://<simulator-ip>:4173`

### Start Both (Background)

```bash
cd /home/heimdall/heimdall-app
./start_all.sh
```

### Check Status

```bash
# Check if services are running
ps aux | grep -E "uvicorn|vite"

# Check ports
netstat -tulpn | grep -E "8000|4173"

# Test backend
curl http://localhost:8000/

# Test frontend
curl http://localhost:4173/
```

---

## 🔗 Access from Your Local Machine

### Port Forwarding via SSH

**From your local machine:**

```bash
# Forward both frontend and backend ports
ssh -p 23570 root@ssh8.vast.ai \
  -L 8000:localhost:8000 \
  -L 4173:localhost:4173

# Keep this terminal open
```

**Then open in your browser:**
- Frontend: http://localhost:4173
- Backend API: http://localhost:8000

### Using VNC Desktop

If you have VNC access:
1. Open Firefox/Chrome in VNC
2. Navigate to http://localhost:4173
3. Full desktop experience with visualization

---

## 🧪 Testing the Deployment

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/

# Get status
curl http://localhost:8000/status

# Create a test playbook
curl -X POST http://localhost:8000/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "geojson": {
      "type": "FeatureCollection",
      "features": [{
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [2.3522, 48.8566]
        }
      }]
    },
    "description": "Test mission"
  }'
```

### 2. Test Frontend

Open http://localhost:4173 and:
1. Click "New Mission"
2. Click on map to add waypoints
3. Save playbook
4. Start mission

### 3. Full Integration Test

**Terminal 1 - Start Sphinx:**
```bash
cd /home/heimdall
./run_sphinx.sh
```

**Terminal 2 - Start Backend:**
```bash
cd /home/heimdall/heimdall-app
./start_backend.sh
```

**Terminal 3 - Start Frontend:**
```bash
cd /home/heimdall/heimdall-app
./start_frontend.sh
```

**Browser:**
- Open http://localhost:4173
- Create mission with waypoints
- Execute mission
- Watch drone in Sphinx simulator!

---

## 🛑 Stopping the Application

### Stop Individual Services

```bash
# Stop backend (Ctrl+C in terminal, or)
pkill -f "uvicorn backend.api.main"

# Stop frontend (Ctrl+C in terminal, or)
pkill -f "vite"
```

### Stop All Services

```bash
cd /home/heimdall/heimdall-app
./stop_all.sh
```

### Docker Services

```bash
docker-compose down
```

---

## 📊 Systemd Services (Optional - Auto-start)

To run as system services that auto-start on boot:

### Install Services

```bash
cd /home/heimdall/heimdall-app
sudo ./install_services.sh
```

### Manage Services

```bash
# Start services
sudo systemctl start heimdall-backend
sudo systemctl start heimdall-frontend

# Stop services
sudo systemctl stop heimdall-backend
sudo systemctl stop heimdall-frontend

# Enable auto-start on boot
sudo systemctl enable heimdall-backend
sudo systemctl enable heimdall-frontend

# Check status
sudo systemctl status heimdall-backend
sudo systemctl status heimdall-frontend

# View logs
sudo journalctl -u heimdall-backend -f
sudo journalctl -u heimdall-frontend -f
```

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python environment
cd /home/heimdall/heimdall-app
source venv/bin/activate
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "fastapi|uvicorn|olympe"

# Check if port is in use
netstat -tulpn | grep 8000

# Run in debug mode
cd /home/heimdall/heimdall-app
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --log-level debug
```

### Frontend won't start

```bash
# Check Node.js
node --version  # Should be 18+
npm --version

# Rebuild frontend
cd /home/heimdall/heimdall-app/frontend
npm install
npm run build

# Run dev server
npm run dev -- --host 0.0.0.0
```

### Can't connect to Sphinx

```bash
# Check Sphinx is running
ps aux | grep sphinx

# Check drone IP
ping 10.202.0.1

# Test Olympe connection
cd /home/heimdall/heimdall-app
source venv/bin/activate
python -c "import olympe; drone = olympe.Drone('10.202.0.1'); print('Olympe OK')"
```

### CORS errors in browser

Update `backend/api/main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📁 Deployment Directory Structure

```
/home/heimdall/heimdall-app/
├── backend/
│   ├── api/
│   ├── drone_controller/
│   ├── olympe_translator/
│   ├── playbook_parser/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── dist/           (built files)
│   ├── package.json
│   └── vite.config.ts
├── playbooks/
├── venv/               (Python virtual environment)
├── logs/               (application logs)
├── start_backend.sh
├── start_frontend.sh
├── start_all.sh
├── stop_all.sh
└── install_services.sh
```

---

## 🌐 Network Configuration

### Firewall (if enabled)

```bash
# Allow frontend port
sudo ufw allow 4173/tcp

# Allow backend port
sudo ufw allow 8000/tcp

# Check status
sudo ufw status
```

### For Remote Access

Configure your simulator machine to allow external access:

1. **Vast.ai**: Ports are already exposed
2. **GCP/AWS**: Add firewall rules for ports 4173 and 8000
3. **Local network**: Configure router port forwarding

---

## 💡 Tips

1. **Development Mode**: Use `npm run dev` for frontend hot-reload during development
2. **Production Mode**: Use `npm run build && npm run preview` for production builds
3. **Logs**: Check `logs/` directory for application logs
4. **Updates**: Use `git pull` and re-run deployment script
5. **Backups**: Backup `playbooks/` directory regularly

---

## 📞 Need Help?

- Check logs in `logs/` directory
- API documentation: http://localhost:8000/docs
- Backend health: http://localhost:8000/
- Frontend: http://localhost:4173

---

**Team Heimdall - ETDH Hackathon 2025**
