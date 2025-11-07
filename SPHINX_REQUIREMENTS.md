# Parrot Sphinx Simulator Requirements

## Overview

Parrot Sphinx is a 3D drone simulator for testing Olympe SDK commands without a physical drone. It requires specific hardware and software to run properly.

---

## 🖥️ Hardware Requirements

### Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **GPU** | NVIDIA GTX 1050 | NVIDIA RTX 2060+ | Required for 3D rendering |
| **GPU RAM** | 4GB | 8GB+ | More = better performance |
| **CPU** | 4 cores | 6+ cores | Intel or AMD |
| **RAM** | 8GB | 16GB+ | Sphinx uses ~4-8GB |
| **Disk** | 20GB free | 30GB+ free | Simulator files are large |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS | **Linux only** |

### GPU Requirements Details

✅ **Supported:**
- NVIDIA GPUs with CUDA support (GTX 10xx, RTX 20xx, RTX 30xx, RTX 40xx series)
- NVIDIA driver version 470.0+
- CUDA 11.0+
- OpenGL 4.5+

❌ **Not Supported:**
- AMD GPUs (no official support)
- Intel integrated graphics
- macOS (no Linux, no Sphinx)
- Windows (use WSL2 with GPU passthrough - complex)

---

## 📦 Software Requirements

### Operating System

**Supported:**
- Ubuntu 22.04 LTS (recommended)
- Ubuntu 20.04 LTS
- Debian 11+ (Bullseye)

**Not Supported:**
- macOS (Sphinx is Linux-only)
- Windows (unless using WSL2 with GPU passthrough)

### System Packages

```bash
# Graphics libraries
libgl1-mesa-glx
libglu1-mesa
libxext6
libx11-6

# Parrot SDK dependencies
python3-pip
python3-dev
build-essential

# NVIDIA drivers (if not already installed)
nvidia-driver-525  # or latest
nvidia-cuda-toolkit
```

### Python Requirements

- Python 3.9+
- pip 20.3+
- virtualenv (recommended)

---

## 🚀 Installation

### 1. Install NVIDIA Drivers (if needed)

```bash
# Check current driver
nvidia-smi

# If not installed or outdated, install latest
sudo apt-get update
sudo apt-get install -y nvidia-driver-525 nvidia-cuda-toolkit

# Reboot
sudo reboot

# Verify installation
nvidia-smi
```

### 2. Add Parrot Repository

```bash
# Add Parrot Sphinx repository
echo "deb http://plf.parrot.com/sphinx/binary $(lsb_release -cs)/" | sudo tee /etc/apt/sources.list.d/sphinx.list

# Add GPG key
wget -qO - http://plf.parrot.com/sphinx/gpg.asc | sudo apt-key add -

# Update package list
sudo apt-get update
```

### 3. Install Sphinx

```bash
# Install Parrot Sphinx
sudo apt-get install -y parrot-sphinx

# Verify installation
sphinx --version
```

### 4. Install Olympe SDK

```bash
# Install Olympe (required to control simulated drone)
pip3 install parrot-olympe

# Verify
python3 -c "import olympe; print('Olympe:', olympe.__version__)"
```

---

## 🧪 Test Sphinx Installation

### Start Sphinx Simulator

```bash
# Start with default ANAFI AI drone
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

**Expected output:**
```
Sphinx 2.11.0 starting...
Loading drone model: anafi_ai.drone
Firmware loaded: ANAFI AI v7.7.0
World ready.
Drone ready. Listening on 10.202.0.1
```

### Test Drone Connection

In a new terminal:

```bash
# Test connection with Olympe
python3 << 'EOF'
import olympe
from olympe.messages.ardrone3.Piloting import TakeOff

drone = olympe.Drone("10.202.0.1")
drone.connect()
print("✅ Connected to simulated drone!")
drone.disconnect()
EOF
```

---

## 🐛 Common Issues

### Issue 1: "sphinx: command not found"

**Cause:** Sphinx not installed or not in PATH

**Solution:**
```bash
# Reinstall Sphinx
sudo apt-get install --reinstall parrot-sphinx

# Check installation
which sphinx
```

### Issue 2: "Failed to initialize OpenGL"

**Cause:** No GPU or driver issues

**Solution:**
```bash
# Check GPU
nvidia-smi

# If not working, reinstall drivers
sudo apt-get install --reinstall nvidia-driver-525

# Reboot
sudo reboot
```

### Issue 3: "Could not connect to drone at 10.202.0.1"

**Cause:** Sphinx not running or firewall blocking

**Solution:**
```bash
# Check Sphinx is running
ps aux | grep sphinx

# Check drone IP is reachable
ping 10.202.0.1

# Disable firewall (temporary)
sudo ufw disable

# Restart Sphinx
killall sphinx
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

### Issue 4: "Sphinx using 100% CPU / High memory usage"

**Cause:** Normal for 3D simulator

**Solution:**
- Ensure you have enough RAM (16GB recommended)
- Close other applications
- Use a more powerful GPU
- Consider using CPU-only testing (no simulator)

### Issue 5: Black screen / No rendering

**Cause:** GPU acceleration not working

**Solution:**
```bash
# Check OpenGL support
glxinfo | grep "OpenGL version"

# Should show OpenGL 4.5+
# If not, driver issue

# Reinstall Mesa drivers
sudo apt-get install --reinstall libgl1-mesa-glx libglu1-mesa
```

---

## 💡 Vast.ai GPU Selection

### Recommended Vast.ai Filters

```bash
vastai search offers \
  'reliability > 0.95 \
   num_gpus >= 1 \
   gpu_ram >= 6 \
   cpu_ram >= 16 \
   disk_space >= 30 \
   cuda_vers >= 11.0 \
   driver_version >= 470 \
   gpu_name has "RTX" OR gpu_name has "GTX"' \
  --order 'dph+'
```

### Good GPU Options (Sorted by Cost)

| GPU Model | VRAM | Cost/hr | Sphinx? | Notes |
|-----------|------|---------|---------|-------|
| GTX 1050 Ti | 4GB | $0.10-0.20 | ⚠️ Slow | Minimum for testing |
| GTX 1660 | 6GB | $0.15-0.25 | ✅ Good | Budget option |
| RTX 2060 | 6GB | $0.20-0.35 | ✅ Good | Recommended |
| RTX 3060 | 12GB | $0.30-0.50 | ✅ Excellent | Best value |
| RTX 3070 | 8GB | $0.40-0.60 | ✅ Excellent | High performance |
| RTX 4080 | 16GB | $0.80+ | ✅ Overkill | Unnecessary |

**Recommendation:** RTX 2060 or RTX 3060 offers best balance of cost/performance.

---

## 🔄 Alternative: No Simulator Testing

If you don't need 3D visualization, you can test everything without Sphinx:

### What Works Without Sphinx

✅ **All Olympe SDK tests** (20/20 tests)
✅ **Playbook validation**
✅ **GeoJSON conversion**
✅ **API endpoints**
✅ **Safety checks**

❌ **What Requires Sphinx:**
- Visual 3D drone simulation
- Real-time position feedback
- Camera view visualization
- Physics-based flight testing

### Cost Comparison

| Setup | Cost | Tests Passing | Use Case |
|-------|------|---------------|----------|
| **Mac Local** | $0 | 15/20 | Development only |
| **Vast.ai CPU** | $0.10/hr | 20/20 | SDK validation ⭐ |
| **Vast.ai GPU** | $0.30/hr | 20/20 + 3D | Full simulation |
| **Hackathon** | $0 | 20/20 + Physical | Real drone |

**Recommendation:** Use Vast.ai CPU instance ($0.10/hr) to validate all 20 tests pass, then test physical drones at hackathon.

---

## 📊 Summary

### Do I Need Sphinx?

**Yes, if:**
- You want to see 3D visualization of drone flight
- You need to test camera positioning
- You want to validate complex flight patterns visually
- You have time and budget for GPU instance

**No, if:**
- You just need to validate code works (all 20 tests)
- You're on a tight budget
- Physical drones available at hackathon
- Your code is well-tested with unit tests

### Recommended Approach

1. **Now (Local Mac):** Test schema + GeoJSON (15 tests) - $0
2. **Before Hackathon:** Validate on Vast.ai CPU (20 tests) - ~$0.20
3. **Optional:** Test Sphinx on Vast.ai GPU (visual validation) - ~$1.00
4. **At Hackathon:** Use physical drones (real demo) - $0

**Total cost:** < $1.50 for complete validation

---

## 🎯 Hackathon Environment

The hackathon will likely provide:

✅ Ubuntu Linux machines (22.04+)
✅ NVIDIA GPUs with drivers installed
✅ Sphinx simulator pre-installed
✅ Physical Parrot ANAFI drones
✅ Network-connected drone infrastructure

**Your code will work immediately** because you tested on Vast.ai Linux!

---

## 📞 Support

**Parrot Sphinx Documentation:**
- https://developer.parrot.com/docs/sphinx/

**Olympe SDK Documentation:**
- https://developer.parrot.com/docs/olympe/

**Vast.ai Support:**
- https://vast.ai/docs/

**Our Guides:**
- [VASTAI_QUICKSTART.md](VASTAI_QUICKSTART.md) - 5-minute setup
- [VASTAI_SETUP.md](VASTAI_SETUP.md) - Detailed guide
- [OLYMPE_INSTALLATION.md](OLYMPE_INSTALLATION.md) - SDK-only setup
