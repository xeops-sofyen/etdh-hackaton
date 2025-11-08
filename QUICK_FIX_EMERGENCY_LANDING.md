# 🚨 Emergency Landing - Quick Fix Guide

## TL;DR - Most Likely Causes

1. **Sphinx simulator not running** (90% of cases)
2. **Wrong drone IP address** (5% of cases)
3. **Invalid coordinates or altitude** (5% of cases)

---

## Quick Diagnosis (60 seconds)

```bash
# SSH to simulator
ssh hrandriama@10.20.1.31
# Password: Live39-

# Run automated check
cd ~/heimdall-app
./check_system_status.sh
```

The script will tell you exactly what's wrong!

---

## Quick Fix #1: Sphinx Not Running (90% probability)

### Check:
```bash
ps aux | grep sphinx
# OR
ps aux | grep fwman
```

### Fix:
```bash
# Start Sphinx (command depends on your installation)
# Check your Sphinx setup documentation

# Common commands:
sphinx /path/to/firmware.ext2
# OR
fwman start anafi_ai
# OR
./start_sphinx.sh
```

**Then retry mission from frontend.**

---

## Quick Fix #2: Backend Logs Check (Always do this!)

```bash
cd ~/heimdall-app
tail -100 logs/backend.log
```

**Look for the line BEFORE "⚠️ EMERGENCY LANDING":**

### Example 1: Connection Error
```
❌ Failed to connect: [Errno 113] No route to host
⚠️  EMERGENCY LANDING
```
**→ Fix: Sphinx not running or wrong IP**

### Example 2: TakeOff Error
```
🚀 Executing mission: playbook-1234
📍 Taking off...
AssertionError
❌ Mission failed:
⚠️  EMERGENCY LANDING
```
**→ Fix: Drone already flying, restart Sphinx**

### Example 3: MoveTo Error
```
Waypoint 1/3: lat=49.588, lon=22.676, alt=100
AssertionError
❌ Mission failed:
⚠️  EMERGENCY LANDING
```
**→ Fix: Invalid coordinates or altitude too high**

---

## Quick Fix #3: Restart Everything

When in doubt, restart:

```bash
# 1. Kill all processes
pkill -f uvicorn
pkill -f "npm run preview"
pkill -f sphinx
pkill -f fwman

# 2. Start Sphinx first
# (Use your specific Sphinx start command)

# 3. Wait 10 seconds for Sphinx to initialize
sleep 10

# 4. Start backend
cd ~/heimdall-app/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &

# 5. Check backend connected to drone
sleep 5
tail -20 ../logs/backend.log | grep "Connected to drone"
# Should see: "✅ Connected to drone"

# 6. Start frontend
cd ~/heimdall-app/frontend
npm run build
nohup npm run preview -- --host 0.0.0.0 > ../logs/frontend.log 2>&1 &

# 7. Test mission
```

---

## Quick Fix #4: Lower Altitude

If coordinates are fine but still failing, try lower altitude:

```bash
# Edit default altitude in backend
cd ~/heimdall-app/backend/playbook_parser
nano geojson_converter.py

# Find line ~275:
# alt=100,  # ← Change to 50 or 30

# Save and restart backend
```

---

## Quick Fix #5: Test Backend Directly

Skip frontend, test backend API directly:

```bash
# Create simple playbook
curl -X POST http://localhost:8000/playbook \
  -H "Content-Type: application/json" \
  -d '{
    "geojson": {
      "type": "FeatureCollection",
      "features": [{
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [22.676, 49.588]
        }
      }]
    },
    "mission_id": "test-123",
    "mission_type": "patrol"
  }'

# Watch logs in another terminal
tail -f ~/heimdall-app/logs/backend.log

# Execute mission
curl -X POST http://localhost:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d '{
    "playbook_id": "test-123",
    "simulate": false
  }'
```

**If this fails, problem is backend/Sphinx, not frontend.**
**If this succeeds, problem is frontend configuration.**

---

## Expected SUCCESS Logs

When everything works, backend logs should show:

```
INFO - Connecting to drone at 10.202.0.1...
INFO - ✅ Connected to drone
INFO - Received playbook creation request
INFO - Created playbook test-123 with 1 waypoints
INFO - Executing stored playbook: test-123
INFO - 🚀 Executing mission: test-123
INFO - ⚙️  Max tilt set to 10°
INFO - 📷 Camera configured: photo, gimbal=-90°
INFO - 📍 Taking off...
INFO - ✈️  Reached altitude 100m
INFO - 🗺️  Executing 1 waypoints
INFO -    Waypoint 1/1: lat=49.588, lon=22.676, alt=100, action=photo
INFO -    ✅ Reached waypoint: (49.588, 22.676)
INFO - 🏠 Returning to home
INFO - 🛬 Landed safely
INFO - ✅ Mission completed successfully
```

**No "EMERGENCY LANDING" = SUCCESS! 🎉**

---

## If Still Failing After All Fixes

Provide these 4 things:

1. **Backend logs:**
   ```bash
   tail -200 ~/heimdall-app/logs/backend.log > debug_logs.txt
   ```

2. **System status:**
   ```bash
   ./check_system_status.sh > debug_status.txt
   ```

3. **Sphinx status:**
   ```bash
   ps aux | grep -E "sphinx|fwman" > debug_sphinx.txt
   ```

4. **Network connectivity:**
   ```bash
   ping -c 5 10.202.0.1 > debug_network.txt
   nc -zv 10.202.0.1 1883 >> debug_network.txt 2>&1
   ```

---

## Common Mistake Checklist

- [ ] Sphinx is running (`ps aux | grep sphinx`)
- [ ] Backend is running (`ps aux | grep uvicorn`)
- [ ] Backend connected to drone (check logs for "✅ Connected")
- [ ] Frontend has `.env` with `VITE_USE_REAL_API=true`
- [ ] Coordinates are valid (lat ~49.5-49.6, lon ~22.6-22.7)
- [ ] Altitude is reasonable (<100m)
- [ ] Can ping Sphinx IP: `ping 10.202.0.1`
- [ ] Olympe port open: `nc -zv 10.202.0.1 1883`

---

**For detailed debugging, see:** [EMERGENCY_LANDING_DEBUG.md](EMERGENCY_LANDING_DEBUG.md)

**Created:** November 8, 2025
