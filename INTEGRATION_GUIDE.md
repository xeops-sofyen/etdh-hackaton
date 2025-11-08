# Frontend/Backend Integration Guide

**Team Heimdall - ETDH Hackathon**

## 🎯 Integration Status

✅ **Backend API** - Ready (FastAPI + WebSocket)
✅ **Frontend** - Ready (React + TypeScript)
✅ **API Service** - Created (`frontend/src/services/api.ts`)
✅ **WebSocket Support** - Added to backend
⏳ **Testing** - To be done

---

## 📋 Quick Start

### 1. Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # Si pas déjà activé
python api/main.py
```

Backend démarre sur: `http://localhost:8000`

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
yarn install  # First time only
yarn dev
```

Frontend démarre sur: `http://localhost:5173`

---

## 🔌 Integration Points

### API Endpoints Available

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/status` | GET | Current drone status |
| `/mission/execute` | POST | Execute a mission |
| `/mission/abort` | POST | Emergency abort |
| `/playbooks/list` | GET | List example playbooks |
| `/playbooks/{filename}` | GET | Get specific playbook |
| `/mission/parse-natural-language` | POST | Parse NL command |
| `/ws/mission/{id}` | WebSocket | Real-time updates |

### Data Flow

```
User Input (Frontend)
    ↓
Chat/Manual Builder → Playbook (GeoJSON)
    ↓
api.ts → Convert to Backend Format
    ↓
POST /mission/execute
    ↓
Backend (Olympe Translator)
    ↓
WebSocket Updates ← Drone Telemetry
    ↓
Frontend Map Updates
```

---

## 🔄 How to Replace Mocks with Real API

### Option 1: Quick Toggle (Recommended for Demo)

Create `frontend/src/utils/useRealAPI.ts`:

```typescript
// Toggle between mock and real API
export const USE_REAL_API = true; // Set to false for mock mode
```

### Option 2: Replace in Components

In `frontend/src/components/MainView/MainView.tsx`:

**Before (Mock):**
```typescript
import { MockDroneWebSocket } from '../../services/mockWebSocket';
```

**After (Real):**
```typescript
import { HeimdallWebSocket, heimdallAPI } from '../../services/api';
```

---

## 📊 Type Mapping

### Frontend → Backend

| Frontend (GeoJSON) | Backend (Playbook) |
|--------------------|-------------------|
| `playbook.id` | `mission_id` |
| `playbook.name` | `description` |
| `playbook.route.features` | `waypoints[]` |
| `Point.coordinates` | `{lat, lon, alt}` |

### Conversion is Automatic

The `api.ts` service handles conversion:
- `playbookToBackend()` - Frontend → Backend
- `backendToDroneState()` - Backend → Frontend

---

## 🧪 Testing the Integration

### 1. Test Backend Alone

```bash
# Health check
curl http://localhost:8000/

# Get status
curl http://localhost:8000/status

# List playbooks
curl http://localhost:8000/playbooks/list
```

### 2. Test Frontend with Real API

1. Start backend (`python backend/api/main.py`)
2. Start frontend (`yarn dev`)
3. Open browser: `http://localhost:5173`
4. Create a mission using Chat or Manual Builder
5. Click "Start Mission"
6. Watch real-time updates on the map

### 3. Test WebSocket

Open browser console (F12) and run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/mission/test-123');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
```

---

## 🚀 Deployment

### Development

```bash
# Backend
cd backend && python api/main.py

# Frontend
cd frontend && yarn dev
```

### Production

**Backend:**
```bash
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
yarn build
# Serve dist/ folder with nginx or vercel
```

---

## 🐛 Troubleshooting

### CORS Errors

Backend already has CORS enabled for all origins (`allow_origins=["*"]`).

For production, update `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    ...
)
```

### WebSocket Connection Failed

1. Check backend is running: `curl http://localhost:8000/`
2. Check WebSocket endpoint: `wscat -c ws://localhost:8000/ws/mission/test`
3. Check browser console for errors

### API Calls Failing

1. Check `.env` file exists in `frontend/`
2. Verify `VITE_API_URL=http://localhost:8000`
3. Restart frontend after changing `.env`

---

## 📝 Integration Checklist for Dmytro

- [ ] Pull latest changes (`git pull origin master`)
- [ ] Install frontend deps (`cd frontend && yarn install`)
- [ ] Verify `.env` file exists with correct API URL
- [ ] Start backend on port 8000
- [ ] Start frontend on port 5173
- [ ] Test creating a mission via Chat
- [ ] Test creating a mission via Manual Builder
- [ ] Verify map shows drone movement
- [ ] Test WebSocket real-time updates
- [ ] Test abort mission

---

## 🔗 API Documentation

Full interactive API docs available at:
**http://localhost:8000/docs** (Swagger UI)

---

## 💬 Questions?

**Backend (Sofyen):**
- Playbook schema
- Olympe integration
- API endpoints

**Frontend (Dmytro & Titouan):**
- React components
- Map visualization
- UI/UX

---

## 📦 Files Created for Integration

1. **`frontend/src/services/api.ts`** - Real API service
2. **`frontend/.env`** - API configuration
3. **`backend/api/main.py`** - WebSocket support added
4. **`INTEGRATION_GUIDE.md`** - This file

---

## 🎯 Next Steps

1. **Test locally** - Both frontend + backend running
2. **Demo rehearsal** - Full mission execution flow
3. **Production deploy** (if time permits)
4. **Prepare slides** - Show architecture diagram

Good luck! 🚁🎉
