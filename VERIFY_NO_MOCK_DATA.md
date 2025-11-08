# ✅ Vérification: Aucune Donnée Mock Utilisée

## 🎯 Objectif

S'assurer qu'**AUCUNE** donnée mockée n'est utilisée - ni frontend, ni backend.

## 🔍 Checklist de Vérification

### 1. Backend: Vérifier Quel Serveur Tourne

```bash
ssh hrandriama@10.20.1.31
# Password: Live39-

# Vérifier le processus uvicorn actif
ps aux | grep uvicorn
```

**✅ BON (Olympe réel):**
```
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
                          ^^^^
```

**❌ MAUVAIS (Demo mock):**
```
python -m uvicorn backend.api.main_demo:app
                          ^^^^^^^^^^
python -m uvicorn backend.api.main_demo_realistic:app
                          ^^^^^^^^^^^^^^^^^^^^
```

### 2. Si Mauvais Serveur Tourne: Corriger

```bash
# Tuer tous les processus uvicorn
pkill -f uvicorn

# Redémarrer avec le BON fichier
cd ~/heimdall-app/backend
nohup python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
#                                 ^^^^
#                                 Pas de "demo" ici!

# Vérifier
ps aux | grep uvicorn
tail -20 ../logs/backend.log
```

### 3. Frontend: Vérifier Configuration

**Sur le simulateur:**

```bash
cd ~/heimdall-app/frontend

# Vérifier .env
cat .env
```

**Doit contenir:**
```bash
VITE_API_URL=http://10.20.1.31:8000
VITE_WS_URL=ws://10.20.1.31:8000
VITE_USE_REAL_API=true  # ← CRITIQUE!
```

**Vérifier .env.production:**
```bash
cat .env.production
```

**Doit AUSSI contenir:**
```bash
VITE_API_URL=http://10.20.1.31:8000
VITE_WS_URL=ws://10.20.1.31:8000
VITE_USE_REAL_API=true  # ← CRITIQUE!
```

### 4. Frontend: Vérifier Console Navigateur

**Ouvrir:** `http://10.20.1.31:4173`

**Ouvrir DevTools** (F12) → Console

**Doit afficher:**
```
📦 AppStore: REAL API mode - no mock playbooks
🔧 Mission Control Mode: REAL API
```

**NE DOIT PAS afficher:**
```
❌ MOCK mode - 5 mock playbooks loaded
❌ Mission Control Mode: MOCK
```

### 5. Backend: Vérifier Import Olympe Réel

```bash
cd ~/heimdall-app/backend/api

# Vérifier que main.py importe le vrai OlympeTranslator
grep -n "OlympeTranslator\|DroneController" main.py
```

**Doit montrer:**
```python
from backend.drone_controller.controller import DroneController
from backend.olympe_translator.translator import OlympeTranslator
```

**NE DOIT PAS avoir:**
```python
❌ from backend.api.main_demo import ...
❌ class MockDroneSimulator
❌ class RealisticDroneSimulator
```

### 6. Vérifier Logs Backend: Olympe Connecté

```bash
tail -100 ~/heimdall-app/logs/backend.log | grep -i "olympe\|connected\|drone"
```

**Doit voir:**
```
INFO - Connecting to drone at 10.202.0.1...
INFO - ✅ Connected to drone
INFO - olympe.drone.ANAFI-XXXXXXX - INFO - Connected to device: ANAFI-XXXXXXX
```

**NE DOIT PAS voir:**
```
❌ REALISTIC DEMO MODE
❌ Mock
❌ Simulation
```

## 🧹 Nettoyage: Supprimer Fichiers Demo (Optionnel)

Pour éviter toute confusion, vous pouvez renommer les fichiers demo:

```bash
cd ~/heimdall-app/backend/api

# Renommer pour qu'ils ne soient pas importés par erreur
mv main_demo.py main_demo.py.OLD
mv main_demo_realistic.py main_demo_realistic.py.OLD

# Vérifier
ls -la main*.py
```

**Devrait montrer:**
```
main.py                      ← SEUL ACTIF
main_demo.py.OLD             ← DÉSACTIVÉ
main_demo_realistic.py.OLD   ← DÉSACTIVÉ
```

## 🧪 Test Final: Mission Complète

### Étape 1: Créer Mission depuis Frontend

1. Ouvrir `http://10.20.1.31:4173`
2. Cliquer "New Mission"
3. Cliquer 3 points sur la carte
4. Sauvegarder avec nom "Test GPS Only"

### Étape 2: Vérifier Console Frontend

**Console doit montrer:**
```
🚀 Starting mission via REAL API
Creating playbook on backend...
Playbook created: playbook-XXXXX (3 waypoints)
Mission started: {status: "success", ...}
```

**NE DOIT PAS voir:**
```
❌ Starting mission: playbook-123456 (MOCK)
❌ MockDroneWebSocket
```

### Étape 3: Vérifier Network Tab

**Network → Filter: "playbook"**

**Doit voir:**
```
POST http://10.20.1.31:8000/playbook       200 OK
POST http://10.20.1.31:8000/mission/execute 200 OK
WS   ws://10.20.1.31:8000/ws/mission/...   101 Switching Protocols
```

### Étape 4: Vérifier Backend Logs

```bash
tail -f ~/heimdall-app/logs/backend.log
```

**Doit afficher:**
```
INFO - Received playbook creation request
INFO - Created playbook playbook-XXXXX with 3 waypoints
INFO - Executing stored playbook: playbook-XXXXX
INFO - Connecting to drone at 10.202.0.1...
INFO - ✅ Connected to drone
INFO - 🚀 Executing mission: playbook-XXXXX
INFO - ⚙️  Max tilt set to 10°
INFO - 📍 Taking off...
INFO - ✈️  Reached altitude 100m
INFO - 🗺️  Executing 3 waypoints
INFO -    Waypoint 1/3: lat=49.588, lon=22.676, alt=100
INFO -    ✅ Reached waypoint: (49.588, 22.676)
...
INFO - 🏠 Returning to home
INFO - 🛬 Landed safely
INFO - ✅ Mission completed successfully
```

**NE DOIT PAS voir:**
```
❌ REALISTIC DEMO MODE
❌ Mode: Realistic Olympe simulation
❌ Simulates EXACTLY what Olympe would do
❌ RealisticDroneSimulator
❌ simulate_step
```

## ⚠️ Si Logs Montrent "DEMO MODE"

**C'est que le mauvais serveur tourne!**

### Solution Rapide:

```bash
# Tuer tout
pkill -f uvicorn

# Redémarrer le BON serveur
cd ~/heimdall-app
./deploy_on_server.sh
```

OU manuellement:

```bash
cd ~/heimdall-app/backend
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
#                          ^^^^ Pas de "demo"!
```

## 📊 Comparaison Fichiers Backend

### backend/api/main.py ✅ (BON - Olympe Réel)

```python
from backend.drone_controller.controller import DroneController
from backend.olympe_translator.translator import OlympeTranslator

# Vrai contrôleur drone
drone_controller = DroneController()

@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest):
    # Exécute via VRAI Olympe
    result = drone_controller.execute_mission(playbook)
```

### backend/api/main_demo_realistic.py ❌ (MAUVAIS - Mock)

```python
class RealisticDroneSimulator:  # ❌ SIMULATEUR!
    def simulate_step(self):  # ❌ PAS VRAI DRONE!
        # Fake movement
        self.state["position"]["lat"] += ...
```

## ✅ Checklist Finale

- [ ] `ps aux | grep uvicorn` montre `backend.api.main:app` (PAS demo)
- [ ] Frontend `.env` a `VITE_USE_REAL_API=true`
- [ ] Console navigateur montre "REAL API mode - no mock playbooks"
- [ ] Network tab montre requêtes vers `http://10.20.1.31:8000`
- [ ] Backend logs montrent "Connecting to drone at 10.202.0.1"
- [ ] Backend logs montrent "Connected to device: ANAFI-XXXXXXX"
- [ ] Mission démarre sans "DEMO MODE" dans les logs
- [ ] Waypoints sont atteints via VRAI Olympe SDK

## 🎯 Résumé

**3 Fichiers Backend:**
1. **`backend/api/main.py`** ← ✅ UTILISER CELUI-CI (Olympe réel)
2. **`backend/api/main_demo.py`** ← ❌ NE PAS UTILISER (mock simple)
3. **`backend/api/main_demo_realistic.py`** ← ❌ NE PAS UTILISER (mock réaliste)

**Commande de démarrage correcte:**
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
#                ^^^^
#                Pas de "_demo"!
```

---

**Vérifié le:** 8 Novembre 2025
