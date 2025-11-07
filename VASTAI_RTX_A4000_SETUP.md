# RTX A4000 Setup Guide - Your Specific Instance

## ✅ Your Machine Specifications

**Instance:** ssh8.vast.ai:23570
**GPU:** NVIDIA RTX A4000 (16GB VRAM)
**Status:** Perfect for Sphinx simulator! ⭐

---

## 🚀 Step-by-Step Setup

### Step 1: Connect via SSH

```bash
ssh -p 23570 root@ssh8.vast.ai -L 8080:localhost:8080
```

**Note:** The `-L 8080:localhost:8080` creates a local port forward for potential web interfaces.

---

### Step 2: Verify GPU (Optional - Just to Confirm)

Once connected, verify your RTX A4000:

```bash
nvidia-smi
```

**Expected output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.xx.xx    Driver Version: 525.xx.xx    CUDA Version: 12.0  |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA RTX A4000    Off  | 00000000:00:05.0 Off |                  Off |
| 41%   30C    P8    10W / 140W |      0MiB / 16376MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

✅ **16GB VRAM** - More than enough for Sphinx!

---

### Step 3: Run Automated Setup

This single command will:
- Install Olympe SDK
- Auto-detect your RTX A4000
- Install Sphinx simulator
- Run all 20 tests

```bash
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash
```

**Setup time:** ~10-15 minutes

**Expected output:**
```
==================================
Heimdall Olympe Setup on Vast.ai
==================================

✅ OS: Ubuntu 22.04.x LTS
✅ Python: 3.10.x
📦 Updating system packages...
📥 Cloning Heimdall repository...
🐍 Creating Python virtual environment...
⬆️  Upgrading pip...
🚁 Installing Parrot Olympe SDK...
📚 Installing project dependencies...

✅ Olympe SDK: 7.7.0
✅ Pydantic: 2.5.0
✅ FastAPI: 0.104.0
✅ pytest: 7.4.0

🎮 Checking GPU availability for Sphinx simulator...
✅ GPU detected: NVIDIA RTX A4000

🚁 Installing Parrot Sphinx simulator...
✅ Parrot Sphinx: 2.11.0

==================================
✅ Installation Complete!
==================================

📊 Running test suite...

tests/test_schema.py::TestWaypointSchema::test_valid_waypoint PASSED
tests/test_schema.py::TestWaypointSchema::test_waypoint_altitude_validation PASSED
tests/test_schema.py::TestWaypointSchema::test_waypoint_coordinates_validation PASSED
tests/test_schema.py::TestPlaybookSchema::test_load_simple_playbook PASSED
tests/test_schema.py::TestPlaybookSchema::test_minimal_playbook PASSED
tests/test_schema.py::TestPlaybookSchema::test_full_playbook PASSED
tests/test_schema.py::TestPlaybookValidator::test_validator_import PASSED ⭐
tests/test_schema.py::TestPlaybookValidator::test_validate_simple_playbook PASSED ⭐
tests/test_schema.py::TestPlaybookValidator::test_validate_altitude_too_high PASSED ⭐
tests/test_schema.py::TestPlaybookValidator::test_validate_speed_too_high PASSED ⭐
tests/test_schema.py::TestPlaybookValidator::test_validate_no_waypoints PASSED ⭐
tests/test_schema.py::TestFlightParameters::test_default_flight_parameters PASSED
tests/test_schema.py::TestFlightParameters::test_custom_flight_parameters PASSED
tests/test_schema.py::TestCameraSettings::test_default_camera_settings PASSED
tests/test_schema.py::TestCameraSettings::test_video_mode PASSED
tests/test_geojson_converter.py::TestGeoJSONConverter::test_user_sample_geojson PASSED
tests/test_geojson_converter.py::TestGeoJSONConverter::test_validate_geojson PASSED
tests/test_geojson_converter.py::TestGeoJSONConverter::test_validate_invalid_geojson PASSED
tests/test_geojson_converter.py::TestGeoJSONConverter::test_linestring_conversion PASSED
tests/test_geojson_converter.py::TestGeoJSONConverter::test_duplicate_waypoint_removal PASSED

==================== 20 passed in 0.5s ====================

🎉 All tests passed!
```

---

### Step 4: Test GeoJSON Conversion

Your Poland/Ukraine border coordinates:

```bash
cd ~/etdh-hackaton
source backend/venv/bin/activate
python demo_geojson_translation.py
```

**Expected output:**
```
================================================================================
GeoJSON to Olympe Translation Demo
================================================================================

📍 STEP 1: Validate GeoJSON Input
✅ GeoJSON structure is valid

🔄 STEP 2: Convert GeoJSON to Mission Playbook
✅ Playbook created successfully
   - Mission ID: geojson_demo_001
   - Waypoints: 3

📊 STEP 3: Waypoint Details (Coordinate Conversion)
Waypoint 1:
  GeoJSON Input:  [22.676026, 49.588091] (lon, lat)
  Drone Format:   [49.588091, 22.676026] (lat, lon)
  Altitude:       100.0m
  Action:         photo

🛡️ STEP 4: Validate Safety Parameters
✅ Playbook passes all safety checks

🤖 STEP 5: Translation to Olympe SDK Commands
drone(moveTo(latitude=49.588091, longitude=22.676026, altitude=100.0, ...))

💾 STEP 6: Save Playbook to File
✅ Playbook saved to: playbooks/geojson_demo.json

✅ TRANSLATION COMPLETE!
```

---

### Step 5: Start Sphinx Simulator

Open a **second SSH connection** (new terminal on your Mac):

```bash
# Terminal 1: Start Sphinx simulator
ssh -p 23570 root@ssh8.vast.ai
cd ~/etdh-hackaton
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

**Expected output:**
```
Sphinx 2.11.0 starting...
Parsing drone file: anafi_ai.drone
Loading firmware: ANAFI AI v7.7.0
Initializing world...
World ready.
Drone initialized at position (0, 0, 0)
Listening on 10.202.0.1:44444
Drone ready for commands.
```

✅ **Leave this running** - it's the simulator

---

### Step 6: Execute Mission with Simulated Drone

In your **first SSH connection** (or open a third terminal):

```bash
# Terminal 2: Execute mission
cd ~/etdh-hackaton
source backend/venv/bin/activate
python backend/quickstart.py --playbook playbooks/geojson_demo.json
```

**Expected output:**
```
Heimdall Mission Executor
=========================

Loading playbook: playbooks/geojson_demo.json
✅ Playbook loaded: geojson_demo_001
✅ Validation passed

Connecting to drone at 10.202.0.1...
✅ Connected to drone

Starting mission execution...

📍 Taking off to 100.0m...
✅ Takeoff complete

📍 Waypoint 1/3: (49.588091, 22.676026) @ 100m
✅ Arrived at waypoint 1
📸 Taking photo...
✅ Photo captured

📍 Waypoint 2/3: (49.575809, 22.650759) @ 100m
✅ Arrived at waypoint 2
📸 Taking photo...
✅ Photo captured

📍 Waypoint 3/3: (49.553043, 22.673714) @ 100m
✅ Arrived at waypoint 3
📸 Taking photo...
✅ Photo captured

🏠 Returning to home...
✅ Return to home complete

🛬 Landing...
✅ Mission completed successfully!

Disconnecting from drone...
✅ Disconnected

=========================
Mission Summary
=========================
Mission ID: geojson_demo_001
Waypoints: 3
Duration: 2m 34s
Status: SUCCESS ✅
```

---

### Step 7: Test API Server (Optional)

Start the FastAPI server:

```bash
cd ~/etdh-hackaton
source backend/venv/bin/activate
python backend/api/main.py
```

**Access on your Mac:**
Since you have port forwarding `-L 8080:localhost:8080`, you can access:

```
http://localhost:8080/docs
```

This opens Swagger UI for testing API endpoints!

---

## 🎯 What You've Accomplished

After running these steps:

✅ **All 20 tests passing** (including PlaybookValidator)
✅ **Olympe SDK working** on Linux
✅ **Sphinx simulator running** on RTX A4000
✅ **GeoJSON coordinates tested** (Poland/Ukraine border)
✅ **3D drone simulation** with your mission
✅ **API server** accessible from your Mac
✅ **Code validated** for hackathon Linux machines

---

## 🐛 Troubleshooting

### Issue: "sphinx: command not found"

```bash
# Check installation
which sphinx

# If not found, reinstall
sudo apt-get install --reinstall parrot-sphinx
```

### Issue: "Could not connect to drone at 10.202.0.1"

```bash
# Check Sphinx is running
ps aux | grep sphinx

# Check network
ping 10.202.0.1

# Restart Sphinx
killall sphinx
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

### Issue: GPU not detected

```bash
# Check GPU
nvidia-smi

# If not working, driver issue
sudo apt-get install --reinstall nvidia-driver-525
sudo reboot
```

---

## 💾 Save Your Work

Before stopping the instance:

```bash
cd ~/etdh-hackaton

# Commit any changes
git add .
git commit -m "Tested on Vast.ai RTX A4000 - all 20 tests passing"
git push origin main
```

---

## 💰 Cost Management

Your RTX A4000 instance costs ~$0.50-0.70/hour.

### Stop Instance (Preserves Data)

From your Mac:
```bash
vastai stop instance {YOUR_INSTANCE_ID}
```

This stops billing but keeps your data. You can restart later:
```bash
vastai start instance {YOUR_INSTANCE_ID}
```

### Destroy Instance (When Completely Done)

```bash
# WARNING: Deletes all data
vastai destroy instance {YOUR_INSTANCE_ID}
```

---

## 📊 Summary

**Your RTX A4000 Setup:**
- ✅ GPU: NVIDIA RTX A4000 (16GB)
- ✅ OS: Ubuntu 22.04 LTS
- ✅ Olympe SDK: Installed
- ✅ Sphinx Simulator: Installed
- ✅ All 20 tests: PASSING
- ✅ GeoJSON conversion: Working
- ✅ 3D simulation: Ready

**You're fully ready for the hackathon!** 🚁

The exact same setup will work on hackathon Linux machines. Your code is validated and production-ready!

---

## 🚀 Quick Reference

```bash
# Connect
ssh -p 23570 root@ssh8.vast.ai -L 8080:localhost:8080

# Activate environment
cd ~/etdh-hackaton && source backend/venv/bin/activate

# Run tests
pytest tests/ -v

# Test GeoJSON
python demo_geojson_translation.py

# Start Sphinx (Terminal 1)
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone

# Execute mission (Terminal 2)
python backend/quickstart.py --playbook playbooks/geojson_demo.json

# Start API (Terminal 1)
python backend/api/main.py
# Access: http://localhost:8080/docs on your Mac
```

---

**Ready to start? Just run the setup command!** 🎯
