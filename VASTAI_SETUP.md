# Vast.ai Setup Guide for Olympe SDK Testing

## Overview

Use Vast.ai to rent a Linux machine and test the complete Heimdall system with Parrot Olympe SDK.

---

## 🚀 Quick Setup

### Step 1: Rent a Vast.ai Instance

**Choose based on your testing needs:**

#### Option A: Full Testing with Sphinx Simulator (Recommended)

**Required specifications:**
- **OS:** Ubuntu 22.04 LTS
- **GPU:** ✅ **NVIDIA GPU required** (OpenGL support for 3D rendering)
- **CUDA:** 11.0+
- **GPU RAM:** 6GB+ (8GB+ recommended)
- **RAM:** 16GB minimum (Sphinx needs ~8GB)
- **Disk:** 30GB minimum (Sphinx files are large)
- **vCPUs:** 4+

**Search command:**
```bash
vastai search offers \
  'reliability > 0.95 \
   num_gpus >= 1 \
   gpu_ram >= 6 \
   cpu_ram >= 16 \
   disk_space >= 30 \
   cuda_vers >= 11.0' \
  --order 'dph+'
```

**Cost:** ~$0.30-0.50/hour

#### Option B: SDK Testing Only (Cheaper, No Simulator)

**Specifications:**
- **OS:** Ubuntu 22.04 LTS
- **GPU:** Not required (CPU only)
- **RAM:** 8GB minimum
- **Disk:** 20GB minimum
- **vCPUs:** 2+

**Search command:**
```bash
vastai search offers 'reliability > 0.95 num_gpus=0 cpu_ram >= 8 disk_space >= 20' --order 'dph+'
```

**Cost:** ~$0.10-0.20/hour

**Note:** CPU-only can run all 20 tests but cannot run Sphinx 3D simulator.

### Step 2: Create Instance

#### For GPU Instance (with Sphinx):
```bash
# Replace {OFFER_ID} with the offer ID from search results
vastai create instance {OFFER_ID} \
  --image nvidia/cuda:11.8.0-devel-ubuntu22.04 \
  --disk 30 \
  --ssh
```

#### For CPU Instance (SDK only):
```bash
vastai create instance {OFFER_ID} \
  --image ubuntu:22.04 \
  --disk 20 \
  --ssh
```

### Step 3: SSH into Instance

```bash
# Get SSH connection string
vastai ssh-url {INSTANCE_ID}

# SSH into the machine
ssh -p {PORT} root@{HOST} -L 8080:localhost:8080
```

---

## 📦 Installation Script

Once connected to your Vast.ai instance, run this setup script:

```bash
#!/bin/bash
# setup_olympe.sh - Automated Olympe SDK installation

set -e

echo "=================================="
echo "Heimdall Olympe Setup on Vast.ai"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get install -y python3.10 python3-pip python3-venv git build-essential libgl1

# Clone repository
echo "📥 Cloning Heimdall repository..."
cd ~
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Olympe SDK
echo "🚁 Installing Parrot Olympe SDK..."
pip install parrot-olympe

# Install other dependencies
echo "📚 Installing project dependencies..."
pip install pydantic fastapi uvicorn pytest python-dotenv

# Verify installation
echo "✅ Verifying Olympe installation..."
python3 -c "import olympe; print('Olympe version:', olympe.__version__)"

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Run tests with:"
echo "  source backend/venv/bin/activate"
echo "  pytest tests/ -v"
echo ""
```

**Save and run:**
```bash
# Create the setup script
cat > setup_olympe.sh << 'EOF'
[paste the script above]
EOF

# Make executable
chmod +x setup_olympe.sh

# Run installation
./setup_olympe.sh
```

---

## 🧪 Run All Tests

### Activate Environment

```bash
cd ~/etdh-hackaton
source backend/venv/bin/activate
```

### Run Complete Test Suite

```bash
# Run all tests (including Olympe-dependent ones)
pytest tests/ -v

# Run with detailed output
pytest tests/ -v -s

# Run specific test file
pytest tests/test_schema.py -v
pytest tests/test_geojson_converter.py -v
pytest tests/test_translator.py -v
```

**Expected results:**
- ✅ 10 schema validation tests
- ✅ 5 GeoJSON converter tests
- ✅ 5 PlaybookValidator tests (NOW WORKING with Olympe)
- ✅ **Total: 20/20 tests passing**

---

## 🎯 Test with Sphinx Simulator (Optional)

If you want to test actual drone commands (not just validation):

### Install Sphinx Simulator

```bash
# Add Parrot repository
echo "deb http://plf.parrot.com/sphinx/binary $(lsb_release -cs)/" | sudo tee /etc/apt/sources.list.d/sphinx.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 508B1AE5

# Install Sphinx
sudo apt-get update
sudo apt-get install parrot-sphinx

# Verify installation
sphinx --version
```

### Start Simulator

```bash
# Terminal 1: Start Sphinx simulator
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone

# Terminal 2: Run quickstart test
cd ~/etdh-hackaton
source backend/venv/bin/activate
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 🔄 Sync Code Changes

If you make changes locally on your Mac and want to test on Vast.ai:

### Option 1: Git Push/Pull

```bash
# On Mac: Commit and push changes
git add .
git commit -m "Update code"
git push origin main

# On Vast.ai: Pull changes
cd ~/etdh-hackaton
git pull origin main
```

### Option 2: SCP File Transfer

```bash
# From Mac: Upload specific files
scp -P {PORT} /path/to/local/file.py root@{HOST}:~/etdh-hackaton/backend/

# From Mac: Upload entire directory
scp -P {PORT} -r /path/to/local/dir root@{HOST}:~/etdh-hackaton/
```

### Option 3: rsync (Recommended for large changes)

```bash
# From Mac: Sync entire project
rsync -avz -e "ssh -p {PORT}" \
  --exclude 'backend/venv' \
  --exclude '.git' \
  --exclude '__pycache__' \
  /Users/sofyenmarzougui/etdh-hackaton/ \
  root@{HOST}:~/etdh-hackaton/
```

---

## 🐛 Troubleshooting

### Error: "No module named 'olympe'"

```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall Olympe
pip install --force-reinstall parrot-olympe
```

### Error: "Could not find a version that satisfies the requirement parrot-olympe"

```bash
# Check Python version (must be 3.9+)
python3 --version

# Check OS (must be Ubuntu/Debian)
lsb_release -a

# Upgrade pip
pip install --upgrade pip
```

### Error: "Connection refused" (Sphinx)

```bash
# Check Sphinx is running
ps aux | grep sphinx

# Restart Sphinx
killall sphinx
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

### SSH Connection Issues

```bash
# Check instance status
vastai show instances

# Get fresh SSH URL
vastai ssh-url {INSTANCE_ID}

# Test connection
ping {HOST}
```

---

## 💰 Cost Optimization

### Stop Instance When Not in Use

```bash
# Stop instance (preserves data, stops billing)
vastai stop instance {INSTANCE_ID}

# Start instance again
vastai start instance {INSTANCE_ID}
```

### Destroy Instance (When Done)

```bash
# WARNING: This deletes all data
vastai destroy instance {INSTANCE_ID}
```

### Estimated Costs

#### Option A: GPU Instance (with Sphinx Simulator)
- **Hourly rate:** ~$0.30 - $0.50/hour
- **Setup + initial testing (1 hour):** ~$0.30 - $0.50
- **Full development session (3 hours):** ~$0.90 - $1.50
- **Complete hackathon prep (5 hours):** ~$1.50 - $2.50

#### Option B: CPU Instance (SDK Testing Only)
- **Hourly rate:** ~$0.10 - $0.20/hour
- **Setup + testing (30 min):** ~$0.05 - $0.10
- **Development session (2 hours):** ~$0.20 - $0.40
- **Complete testing (3 hours):** ~$0.30 - $0.60

**Recommendation:** Use CPU instance for initial testing ($0.10/hr), then upgrade to GPU instance only if you need to test Sphinx simulator before the hackathon.

---

## 📋 Pre-Hackathon Checklist

### On Vast.ai Linux Instance

- [ ] Olympe SDK installed and verified
- [ ] All 20 tests passing
- [ ] Sphinx simulator tested (optional)
- [ ] Simple test mission executed successfully
- [ ] GeoJSON demo playbook tested
- [ ] API server starts without errors

### Validation Commands

```bash
# 1. Check Olympe installation
python3 -c "import olympe; print('✅ Olympe:', olympe.__version__)"

# 2. Run full test suite
pytest tests/ -v --tb=short

# 3. Test GeoJSON conversion
python demo_geojson_translation.py

# 4. Validate all playbooks
for playbook in playbooks/*.json; do
    echo "Testing $playbook"
    python -c "
import json
from backend.playbook_parser.schema import MissionPlaybook
with open('$playbook') as f:
    MissionPlaybook(**json.load(f))
print('✅ Valid')
"
done

# 5. Test quickstart (with simulator)
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 🎯 Demo Preparation

Once everything works on Vast.ai, you're ready for the hackathon!

### Create Demo Recording

```bash
# Install asciinema for terminal recording
pip install asciinema

# Record a demo
asciinema rec demo.cast

# Run your demo commands
python demo_geojson_translation.py
pytest tests/ -v

# Stop recording (Ctrl+D)
```

### Test API Endpoints

```bash
# Terminal 1: Start API server
cd ~/etdh-hackaton
source backend/venv/bin/activate
python backend/api/main.py

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/playbooks/list
curl -X POST http://localhost:8000/mission/execute \
  -H 'Content-Type: application/json' \
  -d @playbooks/geojson_demo.json
```

---

## 🚀 Quick Commands Reference

```bash
# Connect to Vast.ai
vastai ssh-url {INSTANCE_ID}
ssh -p {PORT} root@{HOST}

# Activate environment
cd ~/etdh-hackaton && source backend/venv/bin/activate

# Run tests
pytest tests/ -v

# Run demo
python demo_geojson_translation.py

# Start API
python backend/api/main.py

# Start Sphinx
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone

# Execute mission
python backend/quickstart.py --playbook playbooks/geojson_demo.json
```

---

## 📞 Support

If you encounter issues:

1. **Check Olympe installation:** `python3 -c "import olympe; print(olympe.__version__)"`
2. **Check Python version:** `python3 --version` (must be 3.9+)
3. **Check OS:** `lsb_release -a` (must be Ubuntu 22.04+)
4. **View logs:** Check terminal output for specific error messages

---

## ✅ Success Criteria

You're ready for the hackathon when:

- ✅ Olympe SDK installed on Vast.ai
- ✅ All 20 tests passing (including validator tests)
- ✅ GeoJSON conversion working
- ✅ Demo script runs successfully
- ✅ API server starts and responds
- ✅ (Optional) Sphinx simulator tested

**Ready to test on Vast.ai!** 🚁
