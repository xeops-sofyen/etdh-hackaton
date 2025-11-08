# Backend Monitoring Features - Real-Time Integration

## 🎯 Overview

This update adds **real-time backend monitoring** and **live log streaming** capabilities to the Heimdall Mission Control system. You can now monitor backend activity, mission execution, and API requests in real-time through a web-based dashboard.

## ✨ New Features Added

### 1. **Real-Time Log Monitoring Dashboard**
- **File:** `backend/monitor_live.html`
- **Server:** `backend/monitor_server.py`
- **Access:** http://localhost:8001

**What it does:**
- Streams backend logs in real-time using Server-Sent Events (SSE)
- Automatically categorizes and color-codes logs (missions, requests, errors, WebSocket events)
- Displays live metrics (total requests, missions, WebSocket connections, errors)
- Shows backend connection status with visual indicators
- Auto-scrolls to follow new logs

**Key Features:**
- 🟢 **Live Badge:** Shows LIVE/PAUSED status
- 📊 **Metrics Panel:** Real-time counters for requests, missions, WebSocket events, errors
- 🎨 **Color-Coded Logs:**
  - 🟡 Amber: Mission logs (with 🚁 emoji)
  - 🔵 Blue: HTTP requests
  - 🟢 Green: Info logs
  - 🔴 Red: Errors
  - 🟣 Purple: WebSocket events
- ⏸️ **Pause/Resume:** Pause the stream without disconnecting
- 🧹 **Clear Logs:** Clear the display while stream continues
- 📜 **Auto-Scroll Toggle:** Control whether logs auto-scroll

**Keyboard Shortcuts:**
- `c` - Clear logs
- `a` - Toggle auto-scroll
- `p` - Pause/resume stream

### 2. **Static Monitoring Page** (Alternative)
- **File:** `backend/monitor.html`
- **Access:** Open directly in browser (file://)

**What it does:**
- Static HTML page with polling-based monitoring
- Polls `/status` endpoint every 2 seconds
- Shows backend health and status
- Works without additional server

**Note:** This is less powerful than the live monitor but doesn't require running `monitor_server.py`.

### 3. **Frontend Real API Integration**
- **File:** `frontend/.env`
- **Configuration:** `VITE_USE_REAL_API=true`

**What changed:**
- Frontend now connects to the backend API instead of using mocks
- Missions created in the dashboard are sent to `http://localhost:8000/mission/execute`
- Real-time WebSocket connection for mission updates
- Toggle between mock and real API modes via environment variable

**Benefits:**
- Test complete integration flow: Frontend → Backend → Translator
- See actual mission data flowing through the system
- Debug API issues in real-time

## 🚀 How to Use

### **Quick Start**

```bash
# Terminal 1: Start Backend
cd /Users/sofyenmarzougui/etdh-hackaton
python3 backend/api/main_demo.py

# Terminal 2: Start Monitor Server
python3 backend/monitor_server.py

# Terminal 3: Start Frontend (Real API mode)
cd frontend
npm run dev
```

Then open:
- **Frontend:** http://localhost:5173
- **Live Monitor:** http://localhost:8001
- **Backend API:** http://localhost:8000

### **Creating a Mission**

1. Open frontend at http://localhost:5173
2. Open monitor at http://localhost:8001 (in another tab/window)
3. Create a mission using Chat or Manual Builder
4. Watch it appear **instantly** in the monitor with:
   - 🚁 Mission received log (amber color)
   - Mission ID and description
   - Updated metrics counter

### **Switching Between Mock and Real API**

```bash
# Frontend Mock Mode (no backend needed)
# In frontend/.env
VITE_USE_REAL_API=false

# Frontend Real API Mode (connects to backend)
# In frontend/.env
VITE_USE_REAL_API=true

# Remember to restart frontend after changing .env!
cd frontend
# Ctrl+C to stop
npm run dev
```

## 🔧 Technical Details

### **Monitor Server Architecture**

```
monitor_server.py (Port 8001)
    ├── FastAPI server
    ├── SSE endpoint: /logs/stream
    ├── Watches: /tmp/backend_test.log
    ├── Parses log lines
    ├── Categorizes by type
    └── Streams to browser

monitor_live.html (Browser)
    ├── EventSource connection to /logs/stream
    ├── Receives JSON log data
    ├── Renders with color coding
    ├── Updates metrics
    └── Auto-scrolls
```

### **Log Categorization Logic**

The monitor automatically detects log types:
- **Mission:** Contains "🚁", "Received mission", or "mission" keyword
- **WebSocket:** Contains "WebSocket", "ws/"
- **Request:** Contains "POST", "GET" (HTTP requests)
- **Error:** Contains "ERROR", "error", "❌"
- **Info:** Everything else

### **Data Flow**

```
Frontend Dashboard
    ↓ (HTTP POST)
Backend API /mission/execute
    ↓ (Logs to file)
/tmp/backend_test.log
    ↓ (Watched by)
monitor_server.py
    ↓ (SSE Stream)
monitor_live.html
    ↓ (Display)
User sees live logs
```

## 📊 What You Can Monitor

### **Mission Execution Flow**
1. Frontend sends mission → See POST request (blue)
2. Backend receives → See 🚁 mission log (amber)
3. Backend processes → See detailed logs
4. WebSocket connects → See WS log (purple)
5. Mission completes → See completion log

### **Metrics Tracked**
- **Total Requests:** All HTTP requests to backend
- **Missions Received:** Number of missions sent from frontend
- **WebSocket Events:** WebSocket connections/messages
- **Errors:** Any error logs detected

### **Connection Status**
- Backend API: Online/Offline (green/red dot)
- Frontend URL: Link to http://localhost:5173
- Monitor uptime counter
- Total logs received counter

## 🎨 UI Theme

The monitor uses the **same dark theme** as the frontend:
- Background: `#0a0e14`
- Text: `#e5e7eb`
- Primary Green: `#10b981`
- Borders: `#1f2937`
- Font: System font stack (San Francisco, Segoe UI, Roboto)
- Monospace: SF Mono, Monaco, Cascadia Code

## 🐛 Troubleshooting

### **Monitor shows "Disconnected"**
- Check `monitor_server.py` is running on port 8001
- Refresh the browser page

### **No mission logs appearing**
- Verify `VITE_USE_REAL_API=true` in `frontend/.env`
- **Restart frontend** after changing `.env`
- Check browser console for `🔧 Mission Control Mode: REAL API`

### **Only seeing health check logs**
- Normal! Backend polls `/` and `/status` every few seconds
- Create a mission in the frontend to see mission logs

### **Backend not receiving missions**
- Frontend might still be in mock mode
- Restart frontend: `Ctrl+C` then `npm run dev`
- Check `.env` has `VITE_USE_REAL_API=true`

## 📁 Files Added/Modified

### **New Files**
- `backend/monitor_server.py` - Live log streaming server
- `backend/monitor_live.html` - Real-time monitoring dashboard
- `backend/monitor.html` - Static monitoring page
- `BACKEND_MONITORING_FEATURES.md` - This documentation

### **Modified Files**
- `frontend/.env` - Added `VITE_USE_REAL_API=true`
- `frontend/yarn.lock` - Updated dependencies
- `frontend/package-lock.json` - NPM lock file

### **Existing Integration Files** (Already present)
- `frontend/src/services/api.ts` - Backend API client
- `frontend/src/hooks/useMissionControl.ts` - Mission control hook
- `backend/api/main_demo.py` - Demo backend (no Olympe)

## 🎯 Next Steps

1. **Test with real Olympe:** Once Sphinx is set up, switch to `backend/api/main.py`
2. **Add more metrics:** Extend monitoring to show telemetry data
3. **Mission history:** Store and display past missions
4. **Error alerts:** Add notifications for critical errors
5. **Performance metrics:** Add response time tracking

## 💡 Tips

- **Keep monitor open during development** to debug API issues
- **Use keyboard shortcuts** (`c`, `a`, `p`) for quick control
- **Check browser console** for frontend API mode confirmation
- **Monitor shows last 50 logs on connect** - you won't miss earlier activity
- **Logs auto-rotate** - keeps last 500 entries to prevent memory issues

---

**Built for ETDH Hackathon - Heimdall Mission Control**
Real-time monitoring, real-time excellence! 🚀
