# 🚀 Quick Deployment Guide

Deploy Heimdall (Frontend + Backend) to your Sphinx simulator machine in 3 steps.

## Method 1: One-Command Deployment (Easiest)

### From Your Local Machine:

```bash
cd /path/to/etdh-hackaton-1

# Deploy to Vast.ai instance
./deploy_full_stack.sh root@ssh8.vast.ai -p 23570

# Or deploy to any Linux server
./deploy_full_stack.sh user@your-server.com
```

**That's it!** The script will:
1. ✅ Package your code
2. ✅ Transfer to simulator
3. ✅ Install dependencies
4. ✅ Build frontend
5. ✅ Configure services
6. ✅ Start everything

**Time:** ~5-10 minutes

---

## Method 2: Manual Deployment

### Step 1: Transfer Files

```bash
# From your local machine
cd /path/to/etdh-hackaton-1

# Create package
tar czf heimdall.tar.gz backend frontend playbooks deploy_on_server.sh \
  --exclude=node_modules --exclude=.git --exclude=venv

# Transfer to simulator
scp -P 23570 heimdall.tar.gz root@ssh8.vast.ai:~/
```

### Step 2: Deploy on Simulator

```bash
# SSH to simulator
ssh -p 23570 root@ssh8.vast.ai

# Extract and deploy
cd ~
tar xzf heimdall.tar.gz
chmod +x deploy_on_server.sh
./deploy_on_server.sh
```

### Step 3: Start Services

```bash
cd ~/heimdall-app
./start_all.sh
```

**Time:** ~10-15 minutes

---

## Method 3: Docker Deployment

### On Simulator Machine:

```bash
cd /home/heimdall/etdh-hackaton-1

# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access:**
- Frontend: http://your-server-ip:4173
- Backend: http://your-server-ip:8000

**Time:** ~15 minutes (first build)

---

## Accessing the Application

### Option A: Direct Access (if server has public IP)

**Open in browser:**
- Frontend: `http://YOUR_SERVER_IP:4173`
- Backend API: `http://YOUR_SERVER_IP:8000`

### Option B: SSH Port Forwarding (for local access)

```bash
# From your local machine
ssh -p 23570 root@ssh8.vast.ai \
  -L 4173:localhost:4173 \
  -L 8000:localhost:8000
```

**Then open locally:**
- Frontend: http://localhost:4173
- Backend: http://localhost:8000

---

## Quick Commands

### Start Services

```bash
cd ~/heimdall-app
./start_all.sh
```

### Stop Services

```bash
cd ~/heimdall-app
./stop_all.sh
```

### View Logs

```bash
# Backend logs
tail -f ~/heimdall-app/logs/backend.log

# Frontend logs
tail -f ~/heimdall-app/logs/frontend.log

# Both
tail -f ~/heimdall-app/logs/*.log
```

### Check Status

```bash
# Check if running
ps aux | grep -E "uvicorn|vite"

# Check ports
netstat -tulpn | grep -E "8000|4173"

# Test backend
curl http://localhost:8000/

# Test frontend
curl http://localhost:4173/
```

### Restart Services

```bash
cd ~/heimdall-app
./stop_all.sh
./start_all.sh
```

---

## Testing the Full Stack

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/

# Expected: {"service":"Heimdall Mission Control","status":"operational"}
```

### 2. Test Frontend

Open http://localhost:4173 in browser
- Should see mission control interface
- Map should load
- Can create waypoints

### 3. Test Full Integration

**Terminal 1 - Sphinx:**
```bash
cd ~
./run_sphinx.sh
```

**Terminal 2 - Already Running:**
```bash
# Services started by ./start_all.sh
```

**Browser:**
```
http://localhost:4173
```

1. Click "New Mission"
2. Click map to add 2-3 waypoints
3. Name your mission
4. Click "Create Playbook"
5. Click "Start Mission"
6. Watch Sphinx simulator! 🚁

---

## For Vast.ai Specifically

### Full Command Sequence:

```bash
# From your Mac/local machine:

# 1. Deploy
cd /path/to/etdh-hackaton-1
./deploy_full_stack.sh root@ssh8.vast.ai -p 23570

# 2. SSH with port forwarding
ssh -p 23570 root@ssh8.vast.ai \
  -L 4173:localhost:4173 \
  -L 8000:localhost:8000 \
  -L 6080:localhost:6080

# 3. On remote machine, start everything:
cd ~/heimdall-app
./start_all.sh

# 4. In another SSH terminal, start Sphinx:
su - heimdall
cd ~
./run_sphinx.sh
```

**Access in browser:**
- Frontend: http://localhost:4173
- VNC (Sphinx): http://localhost:6080/vnc.html

---

## Troubleshooting

### Backend won't start

```bash
cd ~/heimdall-app
source venv/bin/activate
python --version  # Should be 3.10+
pip list | grep fastapi
```

### Frontend won't build

```bash
cd ~/heimdall-app/frontend
node --version  # Should be 18+
npm install
npm run build
```

### Can't connect to backend from frontend

Check `frontend/.env.production`:
```bash
cat ~/heimdall-app/frontend/.env.production
```

Should contain your server's IP:
```
VITE_API_URL=http://YOUR_SERVER_IP:8000
VITE_WS_URL=ws://YOUR_SERVER_IP:8000
VITE_USE_REAL_API=true
```

### Ports already in use

```bash
# Kill existing processes
pkill -f "uvicorn backend.api.main"
pkill -f "vite preview"

# Or change ports in scripts
```

---

## What Gets Installed

```
~/heimdall-app/
├── backend/          # FastAPI backend
├── frontend/         # React + Vite frontend
├── playbooks/        # Mission files
├── venv/             # Python environment
├── logs/             # Application logs
├── start_all.sh      # Start both services
├── stop_all.sh       # Stop both services
├── start_backend.sh  # Start backend only
└── start_frontend.sh # Start frontend only
```

---

## Next Steps

1. ✅ Deploy using method above
2. ✅ Start services
3. ✅ Open frontend in browser
4. ✅ Create a test mission
5. ✅ Start Sphinx simulator
6. ✅ Execute mission
7. 🎉 Watch your drone fly!

---

## Need Help?

See detailed documentation:
- **Full deployment guide:** [DEPLOY_SIMULATOR.md](DEPLOY_SIMULATOR.md)
- **Docker setup:** [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md)
- **API documentation:** http://localhost:8000/docs

---

**Team Heimdall - ETDH Hackathon 2025** 🚁
