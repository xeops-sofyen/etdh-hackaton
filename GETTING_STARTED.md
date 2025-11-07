# Getting Started with Heimdall

Quick guide to test the **Playbook → Olympe Translator** in 30 minutes.

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton
```

### 2. Setup Python environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Test that everything works

```bash
pytest tests/test_translator.py -v
```

You should see:
```
✅ test_load_simple_playbook PASSED
✅ test_load_coastal_patrol PASSED
✅ test_valid_playbook PASSED
```

---

## 🚁 Test with Sphinx Simulator

### 1. Launch Sphinx (in a separate terminal)

```bash
# You must have Parrot Sphinx installed
sphinx --help  # Verify it's installed

# Launch the simulator with an ANAFI drone
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

The simulator will start and display the drone's IP (typically `10.202.0.1`).

### 2. Connection test

```bash
# In your Python terminal
python
>>> from backend.olympe_translator.translator import OlympeTranslator
>>> translator = OlympeTranslator("10.202.0.1")
>>> translator.connect()
True  # ✅ If connection successful
>>> translator.disconnect()
```

### 3. Execute a simple mission

```bash
python backend/quickstart.py --playbook playbooks/simple_test.json
```

Expected output:
```
📂 Loading playbook: playbooks/simple_test.json
✅ Playbook loaded: test_flight_001
   Description: Simple test flight for initial validation
   Waypoints: 3

🔍 Validating playbook...
✅ Playbook is valid

🚁 Executing mission...
⚠️  Make sure Sphinx simulator is running!
Press ENTER to continue...

🚀 Executing mission: test_flight_001
📍 Taking off...
✈️  Reached altitude 50m
🗺️  Executing 3 waypoints
   Waypoint 1/3: lat=48.8788, lon=2.3675
   ✅ Reached waypoint
   📸 Taking photo
   ...
🏠 Returning to home
🛬 Landed safely
✅ Mission completed successfully!
```

---

## 🧪 Tests without simulator

If you don't have Sphinx, you can still test the validation:

```bash
# Validation test only
python backend/quickstart.py \
  --playbook playbooks/simple_test.json \
  --validate-only
```

Output:
```
✅ Playbook is valid
✓ Validation complete (--validate-only flag set)
```

---

## 🎯 Your Role: The Translator

The key component you've built:

```python
# backend/olympe_translator/translator.py

class OlympeTranslator:
    def translate_and_execute(self, playbook: MissionPlaybook):
        """
        Takes a JSON playbook and translates it to Olympe commands
        """
        # 1. Setup
        self._setup_flight_parameters(playbook)
        self._configure_camera(playbook.camera_settings)

        # 2. Takeoff
        self._execute_takeoff(playbook.flight_parameters.altitude_m)

        # 3. Execute waypoints
        for waypoint in playbook.waypoints:
            self._execute_waypoint(waypoint)  # ⭐ TRANSLATION HERE

        # 4. Land
        self._execute_landing()
```

The magic happens in `_execute_waypoint()`:

```python
def _execute_waypoint(self, waypoint: Waypoint):
    """Translates waypoint JSON → Olympe command"""

    # JSON playbook:
    # {"lat": 53.5, "lon": 8.1, "alt": 120, "action": "photo"}

    # Becomes Olympe command:
    assert self.drone(moveTo(
        latitude=waypoint.lat,    # ←
        longitude=waypoint.lon,   # ← Translation
        altitude=waypoint.alt,    # ←
        orientation_mode=0
    )).wait().success()

    # Execute the action
    if waypoint.action == "photo":
        assert self.drone(take_photo(cam_id=0)).wait().success()
```

---

## 📋 Create your own playbooks

JSON format:

```json
{
  "mission_id": "my_mission",
  "mission_type": "patrol",
  "description": "My custom mission description",
  "waypoints": [
    {
      "lat": 48.8788,
      "lon": 2.3675,
      "alt": 50,
      "action": "photo"
    }
  ],
  "flight_parameters": {
    "altitude_m": 50,
    "speed_mps": 5,
    "pattern": "direct"
  }
}
```

Save to `playbooks/my_mission.json` and execute:

```bash
python backend/quickstart.py --playbook playbooks/my_mission.json
```

---

## 🌐 Test the REST API

### 1. Start the server

```bash
python backend/api/main.py
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test the endpoints

```bash
# Health check
curl http://localhost:8000/

# List available playbooks
curl http://localhost:8000/playbooks/list

# Get a specific playbook
curl http://localhost:8000/playbooks/simple_test.json

# Execute a mission (simulation mode)
curl -X POST http://localhost:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d '{
    "playbook": {
      "mission_id": "test",
      "mission_type": "patrol",
      "description": "Test mission",
      "waypoints": [
        {"lat": 48.8788, "lon": 2.3675, "alt": 50}
      ]
    },
    "simulate": true
  }'
```

### 3. Open interactive documentation

Visit http://localhost:8000/docs in your browser.

You'll have a Swagger interface to test all endpoints.

---

## 🐛 Troubleshooting

### Error: "Could not connect to drone"

1. Check that Sphinx is running: `ps aux | grep sphinx`
2. Verify drone IP: `10.202.0.1` by default
3. Test ping: `ping 10.202.0.1`

### Error: "Module not found"

```bash
# Make sure you're in the venv
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Error: "Playbook validation failed"

- Check that altitude is between 10 and 150m
- Check that speed is ≤ 15 m/s
- Check that there's at least 1 waypoint

---

## ✅ Pre-Hackathon Checklist

- [ ] Sphinx simulator installed and tested
- [ ] Connection to simulated drone works
- [ ] `pytest` passes all tests
- [ ] `quickstart.py` executes a complete mission
- [ ] API server starts without errors
- [ ] You understand the flow: Playbook JSON → Translator → Olympe

---

## 🚀 Next Steps

Now that the backend works, you can:

1. **Add complex actions** to the translator (e.g., spiral scan, follow target)
2. **Integrate GPT-4** for natural language → playbook
3. **Your teammate will create the dashboard** for mission visualization
4. **Add real-time telemetry** (battery, GPS, altitude)

The most important component (Playbook → Olympe) is ✅ **DONE**.

---

## 📞 Questions?

Check the code in `backend/olympe_translator/translator.py` - everything is commented!
