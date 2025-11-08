# Frontend API Connection - Fix Documentation

## 🔴 Problème Identifié

Le frontend n'envoyait **AUCUNE** requête au backend malgré la configuration. Il utilisait uniquement des données mockées (simulées).

### Causes Racines

1. **Fichier `.env` manquant**
   - Variable `VITE_USE_REAL_API` non définie
   - Par défaut = `false` (mode MOCK)

2. **MainView.tsx utilisait MockDroneWebSocket directement**
   - Ligne 4: Import de `MockDroneWebSocket`
   - Ligne 79: Création directe de `new MockDroneWebSocket()`
   - **Contournait complètement le hook `useMissionControl`**

3. **Le hook useMissionControl n'était jamais appelé**
   - Toute la logique REAL API vs MOCK API était ignorée
   - Les fonctions de l'API (createPlaybook, executeMission) n'étaient jamais invoquées

## ✅ Solutions Appliquées

### 1. Configuration des Variables d'Environnement

**Fichiers créés:**

`frontend/.env` (développement):
```bash
VITE_API_URL=http://10.20.1.31:8000
VITE_WS_URL=ws://10.20.1.31:8000
VITE_USE_REAL_API=true  # ← CRITIQUE!
```

`frontend/.env.production` (production):
```bash
VITE_API_URL=http://10.20.1.31:8000
VITE_WS_URL=ws://10.20.1.31:8000
VITE_USE_REAL_API=true  # ← CRITIQUE!
```

### 2. Modification de MainView.tsx

**Avant (❌ MAUVAIS):**
```typescript
import { MockDroneWebSocket } from '../../services/mockWebSocket';

export const MainView = () => {
  const { startMission, pauseMission, ... } = useAppStore(); // ❌ Store local
  const webSocketRef = useRef<MockDroneWebSocket | null>(null); // ❌ Mock en dur

  useEffect(() => {
    // ❌ Création directe de MockDroneWebSocket
    const ws = new MockDroneWebSocket(...);
    ws.start();
  }, [...]);

  const handleStartMission = () => {
    startMission(selectedPlaybookId); // ❌ Appelle store local
  };
}
```

**Après (✅ CORRECT):**
```typescript
import { useMissionControl } from '../../hooks/useMissionControl';

export const MainView = () => {
  // ✅ Utilise le hook qui gère REAL API vs MOCK
  const {
    startMission,
    pauseMission,
    resumeMission,
    abortMission,
    isRealAPI  // ✅ Peut vérifier le mode
  } = useMissionControl();

  const handleStartMission = async () => {
    console.log(`🚀 Starting mission via ${isRealAPI ? 'REAL API' : 'MOCK'}`);
    await startMission(selectedPlaybook); // ✅ Appelle le vrai backend
  };
}
```

### 3. Script de Déploiement Mis à Jour

`deploy_on_server.sh` crée maintenant **les deux fichiers** `.env`:

```bash
# Create environment files for both dev and production
cat > .env <<EOF
VITE_API_URL=http://${SERVER_IP}:8000
VITE_WS_URL=ws://${SERVER_IP}:8000
VITE_USE_REAL_API=true
EOF

cat > .env.production <<EOF
VITE_API_URL=http://${SERVER_IP}:8000
VITE_WS_URL=ws://${SERVER_IP}:8000
VITE_USE_REAL_API=true
EOF
```

## 📊 Flux de Données - Avant vs Après

### ❌ AVANT (Données Mockées)

```
User clicks "Start Mission"
        ↓
MainView.handleStartMission()
        ↓
useAppStore.startMission() (local state only)
        ↓
new MockDroneWebSocket()
        ↓
Simulated data
        ❌ Aucune communication avec le backend!
```

### ✅ APRÈS (Vraie API)

```
User clicks "Start Mission"
        ↓
MainView.handleStartMission()
        ↓
useMissionControl.startMission() ← Check VITE_USE_REAL_API
        ↓
heimdallAPI.createPlaybook(geojson)
        ↓
POST http://10.20.1.31:8000/playbook
        ↓
Backend receives GeoJSON
        ↓
heimdallAPI.executeMission(playbook_id)
        ↓
POST http://10.20.1.31:8000/mission/execute
        ↓
Backend sends to Olympe/Sphinx
        ↓
Drone vole! 🚁
```

## 🧪 Vérification

### Dans la Console du Navigateur

**Mode MOCK (ancien comportement):**
```
🔧 Mission Control Mode: MOCK
Starting mission: playbook-123456 (MOCK)
```

**Mode REAL API (nouveau comportement):**
```
🔧 Mission Control Mode: REAL API
🚀 Starting mission via REAL API
Creating playbook on backend...
Playbook created: mission_abc123 (3 waypoints)
Mission started: {status: "success", mission_id: "mission_abc123"}
```

### Dans les Network Requests (DevTools)

**Vous devriez voir:**
```
POST http://10.20.1.31:8000/playbook
POST http://10.20.1.31:8000/mission/execute
WS   ws://10.20.1.31:8000/ws/mission/mission_abc123
```

### Dans les Logs Backend

**Sur le simulateur:**
```bash
tail -f ~/heimdall-app/logs/backend.log

# Vous devriez voir:
INFO - Received playbook creation request
INFO - Created playbook mission_abc123 with 3 waypoints
INFO - Executing stored playbook: mission_abc123
```

## 🚀 Déploiement

### Déploiement Automatique

```bash
# Sur votre Mac
cd /Users/sofyenmarzougui/etdh-hackaton-1

# Deploy to simulator
./deploy_full_stack.sh hrandriama@10.20.1.31
# Password: Live39-
```

Le script configure automatiquement `VITE_USE_REAL_API=true`.

### Vérification Manuelle

**Sur le simulateur après déploiement:**

```bash
cd ~/heimdall-app/frontend

# Vérifier la configuration
cat .env
cat .env.production

# Les deux devraient contenir:
# VITE_USE_REAL_API=true
```

## 📝 Checklist de Vérification

- [ ] Fichier `frontend/.env` existe avec `VITE_USE_REAL_API=true`
- [ ] Fichier `frontend/.env.production` existe avec `VITE_USE_REAL_API=true`
- [ ] MainView importe `useMissionControl` (pas `MockDroneWebSocket`)
- [ ] Console affiche "REAL API" au démarrage
- [ ] Network tab montre requêtes POST vers backend
- [ ] Backend logs montrent réception des requêtes

## ⚠️ Points d'Attention

### Si vous développez localement sur votre Mac:

```bash
cd frontend
cp .env.example .env

# Modifier .env:
VITE_API_URL=http://10.20.1.31:8000
VITE_WS_URL=ws://10.20.1.31:8000
VITE_USE_REAL_API=true  # ← IMPORTANT!

npm run dev
```

### Si le frontend montre toujours des données mockées:

1. **Vérifier la console:**
   ```javascript
   // Devrait afficher:
   🔧 Mission Control Mode: REAL API
   ```

2. **Vider le cache du navigateur:**
   - Chrome: Cmd+Shift+R (Mac) ou Ctrl+Shift+R (Windows)
   - Ou: DevTools → Network → "Disable cache"

3. **Rebuild le frontend:**
   ```bash
   cd ~/heimdall-app/frontend
   rm -rf dist node_modules/.vite
   npm run build
   npm run preview -- --host 0.0.0.0
   ```

## 📞 Debugging

### Vérifier le mode actuel

**Dans la console du navigateur:**
```javascript
// Vérifier les variables d'environnement
console.log(import.meta.env.VITE_USE_REAL_API);
// Devrait afficher: "true"

console.log(import.meta.env.VITE_API_URL);
// Devrait afficher: "http://10.20.1.31:8000"
```

### Forcer le mode REAL API (temporaire)

**Dans `useMissionControl.ts` ligne 18:**
```typescript
// Temporaire pour debug
const USE_REAL_API = true; // Force REAL API mode
```

## 📚 Fichiers Modifiés

1. `frontend/.env` (créé)
2. `frontend/.env.production` (créé)
3. `frontend/src/components/MainView/MainView.tsx` (modifié)
4. `deploy_on_server.sh` (modifié)

## ✅ Résultat Final

Maintenant quand vous cliquez "Start Mission":

1. ✅ Frontend crée le playbook via POST `/playbook`
2. ✅ Backend reçoit le GeoJSON
3. ✅ Backend convertit en MissionPlaybook
4. ✅ Backend stocke avec un playbook_id
5. ✅ Frontend exécute via POST `/mission/execute` avec playbook_id
6. ✅ Backend envoie à Olympe/Sphinx
7. ✅ **Le drone vole vraiment!** 🚁

---

**Fix vérifié et committé le:** 8 Novembre 2025
**Commits:**
- `d074978` - Fix frontend API connection configuration
- `49a1223` - Fix MainView to use real API via useMissionControl hook
