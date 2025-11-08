# 🚨 Emergency Landing Error - Debugging Guide

## Problem

When starting a mission from the frontend, the backend executes emergency landing, indicating that something failed during mission execution.

## Root Cause Analysis

The backend code uses `assert` statements to verify Olympe SDK commands succeed. If **any** command fails, it raises an `AssertionError` which triggers emergency landing:

```python
# In backend/olympe_translator/translator.py line 66-115
def translate_and_execute(self, playbook: MissionPlaybook):
    try:
        # 1. Setup flight parameters
        assert self.drone(MaxTilt(max_tilt)).wait().success()  # ❌ Could fail

        # 2. Configure camera
        assert self.drone(set_camera_mode(...)).wait().success()  # ❌ Could fail

        # 3. Takeoff
        assert self.drone(TakeOff()).wait().success()  # ❌ Could fail

        # 4. Execute waypoints
        assert self.drone(moveTo(
            latitude=waypoint.lat,
            longitude=waypoint.lon,
            altitude=waypoint.alt,
            ...
        )).wait().success()  # ❌ Could fail

        # 5. Landing
        assert self.drone(Landing()).wait().success()  # ❌ Could fail

    except Exception as e:
        logger.error(f"❌ Mission failed: {e}")
        self._emergency_land()  # ⚠️  EMERGENCY LANDING TRIGGERED
```

## Most Likely Causes

### 1. Sphinx Simulator Not Running
**Probability: HIGH**

The backend tries to connect to `10.202.0.1` (Sphinx simulator IP).

**Check:**
```bash
# On the simulator machine (10.20.1.31)
ssh hrandriama@10.20.1.31
# Password: Live39-

# Check if Sphinx is running
ps aux | grep sphinx
ps aux | grep fwman

# Check if port 1883 (Olympe) is listening
netstat -tuln | grep 1883
```

**Fix if not running:**
```bash
# Start Sphinx simulator (exact command depends on your setup)
# Typical commands:
sphinx /path/to/drone/firmware.ext2
# OR
fwman start
```

### 2. Wrong Drone IP Address
**Probability: MEDIUM**

Backend is configured to connect to `10.202.0.1`, but your Sphinx might be on a different IP.

**Check:**
```bash
# Find Sphinx simulator IP
ifconfig  # Look for simulator network interface
# OR
ip addr show

# Backend configuration:
cd ~/heimdall-app/backend
grep -r "10.202.0.1" .
```

**Fix:**
```bash
# Update drone IP in backend configuration
# Check: backend/api/main.py or backend/drone_controller/controller.py
```

### 3. Invalid Waypoint Coordinates
**Probability: MEDIUM**

The coordinates sent from frontend might be invalid for Sphinx (out of bounds, altitude too high, etc.).

**Check backend logs:**
```bash
tail -100 ~/heimdall-app/logs/backend.log

# Look for:
# - "Executing mission: mission_XXXXX"
# - "Waypoint 1/X: ..."
# - Error message before "EMERGENCY LANDING"
```

**Common coordinate issues:**
- Altitude too high (>150m might fail)
- Coordinates outside Sphinx world boundaries
- Latitude/longitude swapped

### 4. Olympe Connection Failure
**Probability: MEDIUM**

Backend can't establish connection to drone.

**Check backend logs:**
```bash
tail -100 ~/heimdall-app/logs/backend.log | grep -i connect

# Should see:
# "Connecting to drone at 10.202.0.1..."
# "✅ Connected to drone"

# If you see:
# "❌ Failed to connect: ..."
# Then connection failed
```

### 5. Drone Already Flying
**Probability: LOW**

If drone is already in flight, TakeOff command will fail.

**Check Sphinx:**
```bash
# In Sphinx console or logs, check drone state
# Should be: landed, not flying
```

## Step-by-Step Debugging

### Step 1: Check Backend Logs

```bash
ssh hrandriama@10.20.1.31
cd ~/heimdall-app
tail -200 logs/backend.log
```

**Look for:**
1. Connection attempt: `"Connecting to drone at..."`
2. Mission start: `"🚀 Executing mission: mission_XXXXX"`
3. Waypoint details: `"Waypoint 1/3: lat=..., lon=..., alt=..."`
4. Error message: `"❌ Mission failed: ..."`
5. Emergency landing: `"⚠️  EMERGENCY LANDING"`

**The error message will tell you exactly what failed!**

### Step 2: Check Sphinx Simulator Status

```bash
# Check if Sphinx processes are running
ps aux | grep -E "sphinx|fwman"

# Check network connectivity
ping 10.202.0.1

# Check if Olympe port is open
nc -zv 10.202.0.1 1883
```

### Step 3: Check Frontend Request

**In browser console (F12):**
```javascript
// Check the POST /playbook request
// Network tab → POST http://10.20.1.31:8000/playbook

// Payload should look like:
{
  "geojson": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [22.676, 49.588]  // ← Check these coordinates
        }
      }
    ]
  },
  "mission_id": "playbook-1699452123456",
  "mission_type": "patrol",
  "description": "Mission Test"
}

// Check altitude in waypoints (backend converts from GeoJSON)
// Default altitude is 100m - might be too high for Sphinx world
```

### Step 4: Test with Simple Mission

**Create minimal test mission:**

From browser console:
```javascript
// Create simple 1-waypoint mission at known-good coordinates
const testMission = {
  id: 'test-mission',
  name: 'Test Mission',
  missionType: 'surveillance',
  route: {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [22.676, 49.588]  // Near Sphinx starting point
        }
      }
    ]
  },
  status: 'planned'
};

// Then start it via UI
```

### Step 5: Check Backend API Directly

**Test backend without frontend:**

```bash
ssh hrandriama@10.20.1.31

# Create test playbook
curl -X POST http://localhost:8000/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Point",
            "coordinates": [22.676, 49.588]
          }
        }
      ]
    },
    "mission_id": "test-curl-123",
    "mission_type": "patrol",
    "description": "Test from curl"
  }'

# Should return:
# {"status":"created","playbook_id":"test-curl-123","playbook":{...},"waypoint_count":1}

# Then execute
curl -X POST http://localhost:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_id": "test-curl-123",
    "simulate": false
  }'

# Watch logs in another terminal:
tail -f ~/heimdall-app/logs/backend.log
```

## Common Fixes

### Fix 1: Sphinx Simulator Not Running

```bash
# Start Sphinx (exact command depends on your installation)
# Check with Parrot documentation or your setup scripts

# Example (adjust to your setup):
cd /path/to/sphinx
./start_simulator.sh

# OR
fwman start anafi_ai
```

### Fix 2: Wrong Olympe Connection IP

**Edit backend configuration:**

`backend/olympe_translator/translator.py` line 36:
```python
# Change from:
def __init__(self, drone_ip: str = "10.202.0.1"):

# To your actual Sphinx IP:
def __init__(self, drone_ip: str = "YOUR_SPHINX_IP"):
```

**OR** set environment variable:
```bash
export DRONE_IP=10.202.0.1
```

### Fix 3: Altitude Too High

**Edit GeoJSON converter default altitude:**

`backend/playbook_parser/geojson_converter.py`:
```python
# Find the altitude setting (around line 270-275)
waypoint = Waypoint(
    lat=lat,
    lon=lon,
    alt=100,  # ← Change to 50 or 30 if 100m is too high
    action="photo"
)
```

### Fix 4: Add Better Error Handling

**Improve error messages in translator:**

`backend/olympe_translator/translator.py` line 172:

```python
# BEFORE (line 172-181):
assert self.drone(moveTo(
    latitude=waypoint.lat,
    longitude=waypoint.lon,
    altitude=waypoint.alt,
    ...
)).wait().success()

# AFTER (better error reporting):
logger.info(f"   Moving to waypoint: lat={waypoint.lat}, lon={waypoint.lon}, alt={waypoint.alt}")
result = self.drone(moveTo(
    latitude=waypoint.lat,
    longitude=waypoint.lon,
    altitude=waypoint.alt,
    orientation_mode=0,
    heading=0.0,
    max_horizontal_speed=10.0,
    max_vertical_speed=2.0,
    max_yaw_rotation_speed=45.0
)).wait()

if not result.success():
    error_msg = f"Failed to reach waypoint ({waypoint.lat}, {waypoint.lon}, {waypoint.alt}m)"
    logger.error(f"   ❌ {error_msg}")
    raise Exception(error_msg)

assert result.success()  # Will raise AssertionError with better context
```

## Quick Checklist

Run through this checklist:

- [ ] Sphinx simulator is running (`ps aux | grep sphinx`)
- [ ] Backend is running (`ps aux | grep uvicorn`)
- [ ] Frontend is running and served from correct IP
- [ ] Backend logs show connection to drone (`grep "Connected to drone" logs/backend.log`)
- [ ] Frontend sends POST requests to backend (check Network tab)
- [ ] Coordinates are valid (latitude: ~49.5-49.6, longitude: ~22.6-22.7)
- [ ] Altitude is reasonable (<100m)
- [ ] No existing mission is running

## Expected Good Flow

**Backend logs should show:**
```
INFO - Connecting to drone at 10.202.0.1...
INFO - ✅ Connected to drone
INFO - 🚀 Executing mission: playbook-1699452123456
INFO -    Description: Mission Test
INFO - ⚙️  Max tilt set to 10°
INFO - 📷 Camera configured: photo, gimbal=-90°
INFO - 📍 Taking off...
INFO - ✈️  Reached altitude 100m
INFO - 🗺️  Executing 3 waypoints
INFO -    Waypoint 1/3: lat=49.588, lon=22.676, alt=100, action=photo
INFO -    ✅ Reached waypoint: (49.588, 22.676)
INFO -    📸 Taking photo
INFO -    Waypoint 2/3: ...
INFO - 🏠 Returning to home
INFO - 🛬 Landed safely
INFO - ✅ Mission completed successfully
```

**If you see anything different, that's where the problem is!**

## Next Steps After Identifying Error

Once you identify the error from backend logs:

1. **Connection error**: Fix Sphinx IP or start Sphinx
2. **TakeOff error**: Check if drone is already flying, reset Sphinx
3. **moveTo error**: Check coordinates, reduce altitude
4. **Camera error**: Disable camera setup temporarily
5. **Other error**: Share full error message for further debugging

## Contact Points

If none of the above helps, provide:
1. Full backend logs: `cat ~/heimdall-app/logs/backend.log | tail -200`
2. Sphinx status: `ps aux | grep sphinx`
3. Network status: `netstat -tuln | grep 1883`
4. Frontend Network tab screenshot showing POST requests

---

**Created:** November 8, 2025
**Related Docs:**
- [DATA_FLOW_VERIFICATION.md](DATA_FLOW_VERIFICATION.md) - Full data flow
- [FRONTEND_API_FIX.md](FRONTEND_API_FIX.md) - Frontend configuration
- [DEPLOY_LOCAL_SIMULATOR.md](DEPLOY_LOCAL_SIMULATOR.md) - Deployment guide
