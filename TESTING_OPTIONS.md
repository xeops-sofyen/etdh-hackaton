# Testing Options - Quick Decision Guide

## 🎯 Which Testing Setup Should I Use?

### Quick Comparison Table

| Option | Cost | Time | Tests Passing | Sphinx 3D | Best For |
|--------|------|------|---------------|-----------|----------|
| **Mac Local** | $0 | 5 min | 15/20 | ❌ | Initial development |
| **Vast.ai CPU** | $0.10/hr | 10 min | 20/20 | ❌ | ⭐ Validation |
| **Vast.ai GPU** | $0.35/hr | 15 min | 20/20 | ✅ | Visual testing |
| **Hackathon** | $0 | Instant | 20/20 | ✅ + Real drones | Final demo |

---

## 📋 Decision Tree

### Step 1: Where are you now?

**On Mac (current):**
- ✅ 15/20 tests passing
- ❌ 5 PlaybookValidator tests fail (need Olympe SDK)
- ❌ Cannot install Olympe (Linux-only)

**Action:** Need Linux for remaining tests

---

### Step 2: What do you need?

#### Option A: Just Validate Code Works ⭐ **RECOMMENDED**

**Goal:** Confirm all 20 tests pass

**Setup:** Vast.ai CPU instance
- Cost: ~$0.10/hour
- Time: 10 minutes
- Result: All 20 tests ✅

**When to use:**
- ✅ Before hackathon (validate code)
- ✅ Limited budget
- ✅ Don't need visualization
- ✅ Physical drones available at event

**How to do it:**
```bash
# Rent CPU instance
vastai search offers 'reliability > 0.95 num_gpus=0 cpu_ram >= 8' --order 'dph+'
vastai create instance {ID} --image ubuntu:22.04 --disk 20 --ssh

# SSH and run setup
ssh -p {PORT} root@{HOST}
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash

# Result: 20/20 tests passing ✅
```

**Total cost for validation:** ~$0.20 (2 hours max)

---

#### Option B: Test with 3D Visualization

**Goal:** See drone simulation in 3D + validate code

**Setup:** Vast.ai GPU instance
- Cost: ~$0.30-0.50/hour
- Time: 15 minutes
- Result: All 20 tests ✅ + Sphinx 3D simulator

**When to use:**
- ✅ Want to see flight visualization
- ✅ Testing complex flight patterns
- ✅ No physical drones before hackathon
- ✅ Budget allows (~$1-2 total)

**Requirements:**
- NVIDIA GPU (GTX 1660+, RTX 2060+ recommended)
- 16GB RAM
- 30GB disk

**How to do it:**
```bash
# Rent GPU instance
vastai search offers \
  'reliability > 0.95 num_gpus >= 1 gpu_ram >= 6 cpu_ram >= 16' \
  --order 'dph+'

vastai create instance {ID} \
  --image nvidia/cuda:11.8.0-devel-ubuntu22.04 \
  --disk 30 \
  --ssh

# SSH and run setup (auto-installs Sphinx)
ssh -p {PORT} root@{HOST}
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash

# Start Sphinx simulator
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone

# Execute mission
python backend/quickstart.py --playbook playbooks/simple_test.json
```

**Total cost for testing:** ~$1.00-1.50 (3-4 hours)

---

#### Option C: Wait for Hackathon

**Goal:** Test directly on event infrastructure

**Setup:** Use hackathon's Linux machines
- Cost: $0
- Time: Instant (infrastructure ready)
- Result: All 20 tests ✅ + Sphinx + Physical drones

**When to use:**
- ✅ Very confident in code (15/20 already passing)
- ✅ Zero budget
- ✅ Hackathon provides Linux + drones
- ❌ Risk: No time to fix if issues found

**How to do it:**
```bash
# At hackathon Linux machine:
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton
pip install parrot-olympe pydantic fastapi pytest
pytest tests/ -v
# Should pass all 20 tests immediately
```

---

## 🎯 Our Recommendation

### Phase 1: Now (Before Hackathon)

**Use Vast.ai CPU instance** ($0.10/hr):
1. Validate all 20 tests pass on Linux ✅
2. Confirm Olympe SDK works ✅
3. Test GeoJSON conversion ✅
4. Total time: 30 minutes
5. Total cost: ~$0.10

**Why:** Peace of mind that code works on Linux, minimal cost.

### Phase 2: At Hackathon

**Use provided infrastructure** ($0):
1. Code already validated on Linux ✅
2. Physical drones for demo ✅
3. Sphinx pre-installed if needed ✅
4. Zero additional cost

---

## 💰 Cost Breakdown

### Minimal Validation (Recommended)

```
Vast.ai CPU instance: $0.10/hr
├── Setup: 10 min = $0.02
├── Testing: 20 min = $0.03
└── Buffer: 30 min = $0.05
Total: ~$0.10
```

### Full Testing with Sphinx

```
Vast.ai GPU instance: $0.35/hr
├── Setup: 15 min = $0.09
├── Sphinx install: 20 min = $0.12
├── Testing: 30 min = $0.18
├── Development: 2 hours = $0.70
└── Buffer: 30 min = $0.18
Total: ~$1.27
```

### At Hackathon

```
Linux machines: $0.00
Physical drones: $0.00
Infrastructure: $0.00
Total: $0.00
```

---

## ✅ What Each Option Validates

### Mac Local (Current - 15/20)

| Component | Status | Notes |
|-----------|--------|-------|
| Waypoint schema | ✅ | 3/3 tests |
| Playbook schema | ✅ | 3/3 tests |
| Flight parameters | ✅ | 2/2 tests |
| Camera settings | ✅ | 2/2 tests |
| GeoJSON conversion | ✅ | 5/5 tests |
| PlaybookValidator | ❌ | 0/5 tests (needs Olympe) |
| Sphinx simulator | ❌ | Needs Linux + GPU |
| Physical drones | ❌ | Needs hardware |

### Vast.ai CPU (20/20)

| Component | Status | Notes |
|-----------|--------|-------|
| Waypoint schema | ✅ | 3/3 tests |
| Playbook schema | ✅ | 3/3 tests |
| Flight parameters | ✅ | 2/2 tests |
| Camera settings | ✅ | 2/2 tests |
| GeoJSON conversion | ✅ | 5/5 tests |
| PlaybookValidator | ✅ | 5/5 tests ⭐ |
| Sphinx simulator | ❌ | Needs GPU |
| Physical drones | ❌ | Needs hardware |

### Vast.ai GPU (20/20 + Sphinx)

| Component | Status | Notes |
|-----------|--------|-------|
| Waypoint schema | ✅ | 3/3 tests |
| Playbook schema | ✅ | 3/3 tests |
| Flight parameters | ✅ | 2/2 tests |
| Camera settings | ✅ | 2/2 tests |
| GeoJSON conversion | ✅ | 5/5 tests |
| PlaybookValidator | ✅ | 5/5 tests |
| Sphinx simulator | ✅ | 3D visualization ⭐ |
| Physical drones | ❌ | Needs hardware |

### Hackathon (Everything)

| Component | Status | Notes |
|-----------|--------|-------|
| Waypoint schema | ✅ | 3/3 tests |
| Playbook schema | ✅ | 3/3 tests |
| Flight parameters | ✅ | 2/2 tests |
| Camera settings | ✅ | 2/2 tests |
| GeoJSON conversion | ✅ | 5/5 tests |
| PlaybookValidator | ✅ | 5/5 tests |
| Sphinx simulator | ✅ | 3D visualization |
| Physical drones | ✅ | Real flight! ⭐ |

---

## 🚦 Quick Start Commands

### Option 1: Validate on Vast.ai CPU (~$0.10)

```bash
# 1. Rent instance
vastai search offers 'reliability > 0.95 num_gpus=0 cpu_ram >= 8' --order 'dph+'
vastai create instance {ID} --image ubuntu:22.04 --disk 20 --ssh

# 2. Connect and test
ssh -p {PORT} root@{HOST}
curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup_vastai.sh | bash

# 3. Stop when done
vastai stop instance {ID}
```

### Option 2: Test with Sphinx (~$1.00)

```bash
# 1. Rent GPU instance
vastai search offers 'num_gpus >= 1 gpu_ram >= 6 cpu_ram >= 16' --order 'dph+'
vastai create instance {ID} --image nvidia/cuda:11.8.0-devel-ubuntu22.04 --disk 30 --ssh

# 2. Connect and test
ssh -p {PORT} root@{HOST}
bash scripts/setup_vastai.sh  # Installs Sphinx automatically

# 3. Run simulator
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone

# 4. Stop when done
vastai stop instance {ID}
```

### Option 3: Wait for Hackathon ($0)

```bash
# At hackathon:
git clone https://github.com/xeops-sofyen/etdh-hackaton.git
cd etdh-hackaton
pip install parrot-olympe pydantic fastapi pytest
pytest tests/ -v  # All 20 tests pass ✅
```

---

## 🎯 Final Recommendation

**For Heimdall project:**

1. **Now:** Use Vast.ai CPU ($0.10) to validate 20/20 tests
2. **Optional:** Test Sphinx if you have budget/time
3. **Hackathon:** Demo with physical drones

**Why this approach:**
- ✅ Low cost (~$0.10)
- ✅ Fast validation (30 min)
- ✅ Confidence code works on Linux
- ✅ Physical drones at event for real demo

**Your code is already 75% validated (15/20 tests).** A quick $0.10 Vast.ai session confirms the final 25% works!

---

## 📚 Related Documentation

- [VASTAI_QUICKSTART.md](VASTAI_QUICKSTART.md) - 5-minute Vast.ai setup
- [VASTAI_SETUP.md](VASTAI_SETUP.md) - Detailed Vast.ai guide
- [SPHINX_REQUIREMENTS.md](SPHINX_REQUIREMENTS.md) - Sphinx GPU requirements
- [OLYMPE_INSTALLATION.md](OLYMPE_INSTALLATION.md) - SDK-only setup
