# Vast.ai Quick Start - 5 Minute Setup

## 🎯 Goal
Get Olympe SDK running and all tests passing on Vast.ai Linux machine.

---

## Step 1: Create Vast.ai Account (1 min)

1. Go to https://vast.ai
2. Sign up with email
3. Add credits ($5 minimum recommended)

---

## Step 2: Rent an Instance (1 min)

### Option A: Via Web Interface
1. Click "Search" in sidebar
2. Filter for **Sphinx Simulator requirements:**
   - **GPU:** ✅ **Required** (NVIDIA GPU with OpenGL support)
   - **CUDA:** ≥11.0
   - **RAM:** ≥16 GB (Sphinx needs 8GB + overhead)
   - **Disk:** ≥30 GB (Sphinx simulator files are large)
   - **vCPUs:** ≥4
3. Click "Rent" on cheapest option (~$0.30-0.50/hour with GPU)
4. Select image: `nvidia/cuda:11.8.0-devel-ubuntu22.04`
5. Check "Use direct SSH connection"
6. Click "Rent"

### Option B: Via CLI
```bash
# Install vastai CLI
pip install vastai

# Set API key (from vast.ai account page)
vastai set api-key YOUR_API_KEY

# Search for GPU instances with Sphinx requirements
vastai search offers \
  'reliability > 0.95 \
   num_gpus >= 1 \
   gpu_ram >= 6 \
   cpu_ram >= 16 \
   disk_space >= 30 \
   cuda_vers >= 11.0 \
   driver_version >= 470' \
  --order 'dph+'

# Rent the cheapest one (replace 123456 with offer ID)
vastai create instance 123456 \
  --image nvidia/cuda:11.8.0-devel-ubuntu22.04 \
  --disk 30 \
  --ssh
```

### Option C: SDK Testing Only (No Simulator - Cheaper)

If you only want to test Olympe SDK without running the simulator:

```bash
# Search for CPU-only instances (cheaper)
vastai search offers 'reliability > 0.95 num_gpus=0 cpu_ram >= 8 disk_space >= 20' --order 'dph+'

# Rent CPU-only instance (~$0.10-0.20/hour)
vastai create instance 123456 --image ubuntu:22.04 --disk 20 --ssh
```

**Note:** CPU-only instances can run all tests but cannot run Sphinx simulator (no 3D rendering).

---

## Step 3: Connect via SSH (1 min)

### Get SSH Command

**Via Web:**
1. Go to "Instances" tab
2. Click "Connect" button
3. Copy SSH command

**Via CLI:**
```bash
vastai show instances
# Note your instance ID

vastai ssh-url YOUR_INSTANCE_ID
# Returns: ssh -p PORT root@HOST -L 8080:localhost:8080
```

### Connect

```bash
# Use the SSH command from above
ssh -p PORT root@HOST

# You're now on the Vast.ai Linux machine!
```

---

## Step 4: Run Setup Script (2 min)

Once connected to Vast.ai instance:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash
```

**Or manually:**

```bash
# Clone repository
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton

# Run setup
bash scripts/setup_vastai.sh
```

**The script will automatically:**
- ✅ Install Olympe SDK
- ✅ Install all dependencies
- ✅ Run complete test suite
- ✅ Show results

---

## Expected Output

```
==================================
Heimdall Olympe Setup on Vast.ai
==================================

✅ OS: Ubuntu 22.04 LTS
✅ Python: 3.10
📦 Updating system packages...
📥 Cloning Heimdall repository...
🐍 Creating Python virtual environment...
🚁 Installing Parrot Olympe SDK...
📚 Installing project dependencies...

✅ Olympe SDK: 7.7.0
✅ Pydantic: 2.5.0
✅ FastAPI: 0.104.0
✅ pytest: 7.4.0

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

## Step 5: Test Everything

```bash
# Activate environment
cd ~/etdh-hackaton
source backend/venv/bin/activate

# Run tests again
pytest tests/ -v

# Test GeoJSON conversion
python demo_geojson_translation.py

# Start API server
python backend/api/main.py
```

---

## 💾 Save Your Work

### Push to GitHub

```bash
cd ~/etdh-hackaton

# Make changes...
git add .
git commit -m "Tested on Vast.ai - all 20 tests passing"
git push origin main
```

### Stop Instance (Preserves Data)

```bash
# From your local machine
vastai stop instance YOUR_INSTANCE_ID

# Start again later
vastai start instance YOUR_INSTANCE_ID
```

### Destroy Instance (When Done)

```bash
# WARNING: Deletes all data
vastai destroy instance YOUR_INSTANCE_ID
```

---

## 🐛 Troubleshooting

### Can't Connect via SSH

```bash
# Check instance status
vastai show instances

# Get fresh SSH URL
vastai ssh-url YOUR_INSTANCE_ID

# Try with -vvv for verbose output
ssh -vvv -p PORT root@HOST
```

### Setup Script Fails

```bash
# Check Python version
python3 --version  # Must be 3.9+

# Check OS
lsb_release -a  # Must be Ubuntu 22.04+

# Manual installation
cd ~/etdh-hackaton
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install --upgrade pip
pip install parrot-olympe pydantic fastapi uvicorn pytest
```

### Tests Fail

```bash
# Verify Olympe installation
python3 -c "import olympe; print(olympe.__version__)"

# Run tests with verbose output
pytest tests/ -v -s --tb=long

# Run specific test
pytest tests/test_schema.py::TestPlaybookValidator -v -s
```

---

## 💰 Cost Estimate

- **Instance cost:** ~$0.10 - $0.30/hour
- **Setup + testing:** ~30 minutes = ~$0.05 - $0.15
- **Full development session (3 hours):** ~$0.30 - $0.90

**Total for hackathon prep:** < $2.00

---

## ✅ Success Checklist

After running the setup:

- [ ] SSH connection works
- [ ] Setup script completed successfully
- [ ] 20/20 tests passing (including PlaybookValidator tests)
- [ ] `import olympe` works
- [ ] `demo_geojson_translation.py` runs successfully
- [ ] API server starts (`python backend/api/main.py`)

---

## 🎯 You're Ready!

Once all tests pass on Vast.ai, your code is **100% ready** for the hackathon Linux machines. The exact same setup will work there!

**Key Achievement:** All 20 tests passing on Linux with Olympe SDK! 🚁
