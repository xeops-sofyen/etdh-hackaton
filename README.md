# Heimdall - AI-Powered Autonomous Drone Mission System

**ETDH Hackathon Paris 2025**
**Team:** Quentin, Dmytro, Titouan, Sofyen

---

## 🎯 Challenge

**UAS-1**: Autonomous Drone Task Execution from Human-Defined Playbooks

Build a system where operators define high-level missions via natural language, and drones autonomously execute them using the Parrot Olympe SDK.

---

## 🏗️ Architecture

```
Human Operator
    ↓ (Natural Language)
┌─────────────────────┐
│  Mission Planner    │  (AI: NL → JSON Playbook)
└──────────┬──────────┘
           ↓ (Structured Playbook)
┌─────────────────────┐
│ Playbook Translator │  ⭐ CORE COMPONENT
│   (JSON → Olympe)   │
└──────────┬──────────┘
           ↓ (Olympe Commands)
┌─────────────────────┐
│  Drone Controller   │  (Execute via Olympe SDK)
└──────────┬──────────┘
           ↓
    Physical Parrot Drone
           ↓
    Real-time Telemetry
           ↓
┌─────────────────────┐
│   Live Dashboard    │  (Mission status + drone state)
└─────────────────────┘
```

---

## 📁 Project Structure

```
etdh-hackaton/
├── backend/
│   ├── playbook_parser/          # Natural language → Playbook JSON
│   │   ├── nl_parser.py          # AI integration
│   │   └── schema.py             # Playbook JSON schema
│   │
│   ├── olympe_translator/        # ⭐ CORE COMPONENT
│   │   ├── translator.py         # Playbook → Olympe commands
│   │   ├── validators.py         # Safety checks
│   │   └── primitives.py         # Olympe command wrappers
│   │
│   ├── drone_controller/
│   │   ├── controller.py         # Olympe SDK executor
│   │   └── telemetry.py          # Real-time state feedback
│   │
│   └── api/
│       ├── main.py               # FastAPI server
│       └── routes.py             # REST endpoints
│
├── frontend/
│   ├── dashboard/                # Next.js mission control UI
│   │   ├── app/
│   │   └── components/
│   └── package.json
│
├── playbooks/                    # Example missions
│   └── simple_test.json          # Basic test flight
│
├── tests/
│   ├── test_translator.py
│   └── test_simulator.py
│
├── requirements.txt
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Option 1: Local Testing (Mac/Windows) - Schema & GeoJSON Only

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install pydantic fastapi uvicorn pytest python-dotenv

# Run tests (15 tests - no Olympe required)
pytest tests/test_schema.py tests/test_geojson_converter.py -v

# Test GeoJSON conversion
python ../demo_geojson_translation.py
```

**Note:** Olympe SDK requires Linux. See [VASTAI_QUICKSTART.md](VASTAI_QUICKSTART.md) for full testing.

### Option 2: Vast.ai Linux Testing (Full Suite with Olympe)

```bash
# 5-minute setup on Vast.ai
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash

# All 20 tests will pass! ✅
```

See [VASTAI_QUICKSTART.md](VASTAI_QUICKSTART.md) for detailed instructions.

### Option 3: Hackathon Machines (Linux with Physical Drones)

```bash
# Clone repository
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton

# Install dependencies
pip install parrot-olympe pydantic fastapi uvicorn pytest

# Test everything
pytest tests/ -v

# Execute mission with physical drone
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 📋 Playbook Schema

Playbooks are JSON definitions of high-level missions:

```json
{
  "mission_id": "patrol_mission_001",
  "mission_type": "patrol",
  "description": "Autonomous patrol mission",
  "flight_parameters": {
    "altitude_m": 50,
    "speed_mps": 5,
    "pattern": "direct"
  },
  "waypoints": [
    {"lat": 48.8788, "lon": 2.3675, "alt": 50, "action": "photo"},
    {"lat": 48.8790, "lon": 2.3680, "alt": 50, "action": "hover", "hover_duration_sec": 5}
  ],
  "contingencies": {
    "low_battery": "return_to_home",
    "gps_loss": "hover_and_alert",
    "obstacle_detected": "reroute"
  }
}
```

---

## 🧠 Core Component: Olympe Translator

Translates high-level playbook commands into Olympe SDK calls.

```python
# Example translation
playbook = {
    "waypoints": [
        {"lat": 48.8788, "lon": 2.3675, "alt": 50, "action": "photo"}
    ]
}

# Translator converts to:
drone(TakeOff()).wait()
drone(moveTo(
    latitude=48.8788,
    longitude=2.3675,
    altitude=50,
    orientation_mode=0
)).wait()
drone(take_photo()).wait()
drone(Landing()).wait()
```

---

## 🎯 Demo Scenario

**Mission:** "Autonomous patrol mission"

1. Operator defines mission via natural language or playbook JSON
2. AI generates/validates structured playbook
3. Translator converts to Olympe commands
4. Drone executes autonomously
5. Dashboard shows live telemetry
6. Mission completes successfully

---

## 🏆 Why This Wins

1. ✅ **Conversational interface** (natural language → missions)
2. ✅ **Autonomous execution** (no waypoint micromanagement)
3. ✅ **Real drone demo** (physical Parrot flight)
4. ✅ **Production-ready code** (clean architecture)
5. ✅ **Safety-first design** (validation layer)

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI
- **Drone SDK:** Parrot Olympe
- **AI:** LLM-based mission planning
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Simulator:** Parrot Sphinx
- **Deployment:** Docker

---

## 📞 Team

Sofyen, Dmytro, Titouan

---

## 📄 License

MIT License - Built for ETDH Hackathon Paris 2025
