# Frontend Integration - How to Use

## 🎯 Quick Start

### Step 1: Install Dependencies

```bash
yarn install
```

### Step 2: Choose Mode (Mock vs Real API)

Edit `.env`:

```bash
# For development with mock data
VITE_USE_REAL_API=false

# For integration with real backend
VITE_USE_REAL_API=true
```

### Step 3: Start Development Server

```bash
yarn dev
```

---

## 🔌 Using the Mission Control Hook

The `useMissionControl()` hook automatically switches between Mock and Real API based on `.env` configuration.

### In Your Component

```typescript
import { useMissionControl } from '../hooks/useMissionControl';

function YourComponent() {
  const { startMission, pauseMission, abortMission, isRealAPI } = useMissionControl();

  // Show which mode we're in
  console.log(`Running in ${isRealAPI ? 'REAL' : 'MOCK'} mode`);

  const handleStart = async (playbook: Playbook) => {
    try {
      await startMission(playbook);
      console.log('Mission started!');
    } catch (error) {
      console.error('Failed to start mission:', error);
    }
  };

  // ... rest of your component
}
```

### No Code Changes Needed!

The hook handles everything:
- ✅ WebSocket connections (Mock or Real)
- ✅ Data format conversion
- ✅ Error handling
- ✅ State updates via Zustand

---

## 📁 Files Created for Integration

| File | Purpose |
|------|---------|
| `src/services/api.ts` | Real API client + WebSocket |
| `src/hooks/useMissionControl.ts` | Abstraction layer (Mock/Real toggle) |
| `.env` | Configuration (API URL + Mode) |

---

## 🧪 Testing Modes

### Mode 1: Mock (Default)

```bash
# .env
VITE_USE_REAL_API=false
```

**Use case:** Frontend development without backend
- Instant feedback
- No network calls
- Predictable behavior

### Mode 2: Real API

```bash
# .env
VITE_USE_REAL_API=true
```

**Prerequisites:**
1. Backend running on `http://localhost:8000`
2. Start backend: `cd backend && python api/main.py`

**Use case:** Full integration testing
- Real drone control
- Actual Olympe SDK execution
- WebSocket streaming

---

## 🔄 Migration Path

### Current Code (Using Mocks)

```typescript
// MainView.tsx
import { MockDroneWebSocket } from '../../services/mockWebSocket';

const ws = new MockDroneWebSocket(playbook.id, playbook.route, playbook.missionType);
ws.start();
```

### New Code (Auto-Switch)

```typescript
// MainView.tsx
import { useMissionControl } from '../../hooks/useMissionControl';

const { startMission } = useMissionControl();
await startMission(playbook);
```

That's it! No manual switching needed.

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"

**Solution:**
1. Check backend is running: `curl http://localhost:8000/`
2. Verify `.env` has correct URL
3. Restart frontend after changing `.env`

### Issue: "CORS error"

**Solution:**
Backend already allows all origins. If still getting CORS:
1. Check backend logs for errors
2. Verify `VITE_API_URL` doesn't end with `/`
3. Try `http://127.0.0.1:8000` instead of `localhost`

### Issue: "WebSocket connection failed"

**Solution:**
1. Ensure backend supports WebSocket (`/ws/mission/{id}`)
2. Check browser console for exact error
3. Test with: `wscat -c ws://localhost:8000/ws/mission/test`

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Component (MainView)                                       │
│      │                                                      │
│      ▼                                                      │
│  useMissionControl()  ◄──── .env (VITE_USE_REAL_API)      │
│      │                                                      │
│      ├──► Mock Mode                                        │
│      │     └─► MockDroneWebSocket                          │
│      │         └─► Simulated updates                       │
│      │                                                      │
│      └──► Real Mode                                        │
│            └─► api.ts                                      │
│                ├─► HTTP: POST /mission/execute             │
│                └─► WebSocket: /ws/mission/{id}             │
│                    └─► Real drone telemetry                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  REST API (/mission/execute)                                │
│      ▼                                                      │
│  OlympeTranslator                                           │
│      ▼                                                      │
│  Parrot Olympe SDK                                          │
│      ▼                                                      │
│  Physical Drone / Sphinx Simulator                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Demo Checklist

Before the hackathon demo:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] `.env` set to `VITE_USE_REAL_API=true`
- [ ] Test mission creation via Chat
- [ ] Test mission execution
- [ ] Verify map shows real-time updates
- [ ] Test abort functionality
- [ ] Prepare backup: Set `VITE_USE_REAL_API=false` if backend fails

---

## 📞 Questions?

**Integration issues:** Ask Sofyen
**UI/Frontend issues:** Ask Dmytro or Titouan

Good luck! 🚁
