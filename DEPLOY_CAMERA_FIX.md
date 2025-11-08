# 🚀 Déploiement du Fix Camera Timeout

## ⚡ Déploiement Rapide (1 Commande)

### Sur Votre Mac

```bash
cd /Users/sofyenmarzougui/etdh-hackaton-1

# Déployer tout le stack avec les derniers fixes
./deploy_full_stack.sh hrandriama@10.20.1.31
# Password: Live39-
```

Le script va automatiquement:
1. ✅ Copier les derniers fichiers backend (avec fix caméra)
2. ✅ Copier les derniers fichiers frontend
3. ✅ SSH vers le simulateur
4. ✅ Installer dépendances
5. ✅ Build le frontend
6. ✅ Démarrer backend et frontend
7. ✅ Créer les fichiers `.env` avec `VITE_USE_REAL_API=true`

## 🔧 Déploiement Manuel Backend Seulement

Si vous voulez juste mettre à jour le backend:

### Étape 1: SSH vers le Simulateur

```bash
ssh hrandriama@10.20.1.31
# Password: Live39-
```

### Étape 2: Arrêter Backend

```bash
# Trouver le PID
ps aux | grep uvicorn

# Tuer le processus
pkill -f uvicorn
```

### Étape 3: Pull Derniers Changements

```bash
cd ~/heimdall-app
git pull origin master
```

### Étape 4: Redémarrer Backend

```bash
cd ~/heimdall-app/backend

# Démarrer avec logs
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &

# Vérifier que ça tourne
ps aux | grep uvicorn

# Voir les logs en temps réel
tail -f ../logs/backend.log
```

## 🧪 Test du Fix

### 1. Vérifier Backend Logs

```bash
ssh hrandriama@10.20.1.31
tail -f ~/heimdall-app/logs/backend.log
```

**Dans un autre terminal, lancer une mission depuis le frontend.**

### 2. Logs Attendus (Succès)

```
INFO - 🚀 Executing mission: playbook-XXXXX
INFO -    Description: test
INFO - ⚙️  Max tilt set to 10°
INFO - 📍 Taking off...
INFO - ✈️  Reached altitude 100m
INFO - 🗺️  Executing 4 waypoints
INFO -    Waypoint 1/4: lat=49.588, lon=22.676, alt=100
INFO -    ✅ Reached waypoint: (49.588, 22.676)
INFO -    Waypoint 2/4: lat=49.576, lon=22.651, alt=100
INFO -    ✅ Reached waypoint: (49.576, 22.651)
...
INFO - 🏠 Returning to home
INFO - 🛬 Landed safely
INFO - ✅ Mission completed successfully
```

### 3. Ce Que Vous Ne Devez PLUS Voir

```
❌ "📷 Setting camera mode..."
❌ "📸 Taking photo"
❌ "⚠️  Camera mode configuration failed"
❌ "⚠️  EMERGENCY LANDING"
❌ 10 secondes de silence après MaxTilt
```

## 🐛 Debugging

### Si Emergency Landing Persiste

**1. Vérifier que le fix est bien déployé:**

```bash
ssh hrandriama@10.20.1.31
cd ~/heimdall-app/backend/olympe_translator

# Chercher la ligne commentée
grep -n "# self._configure_camera" translator.py

# Devrait afficher:
# 86:            # self._configure_camera(playbook.camera_settings)
```

Si la ligne n'est PAS commentée, le fix n'est pas déployé!

**2. Vérifier les logs complets:**

```bash
# Dernières 200 lignes
tail -200 ~/heimdall-app/logs/backend.log

# Chercher "Mission failed"
grep -A5 "Mission failed" ~/heimdall-app/logs/backend.log
```

**3. Vérifier Sphinx est actif:**

```bash
ps aux | grep sphinx
nc -zv 10.202.0.1 1883
```

### Si Nouveau Type d'Erreur

**Capturer l'erreur complète:**

```bash
# Sur le simulateur
tail -100 ~/heimdall-app/logs/backend.log > ~/debug_mission.txt

# Copier sur votre Mac
scp hrandriama@10.20.1.31:~/debug_mission.txt .
```

Puis analysez `debug_mission.txt` pour voir l'erreur exacte.

## ✅ Checklist Après Déploiement

### Backend

- [ ] Backend tourne: `ps aux | grep uvicorn`
- [ ] Logs accessibles: `tail -f ~/heimdall-app/logs/backend.log`
- [ ] Fix caméra présent: `grep "# self._configure_camera" ~/heimdall-app/backend/olympe_translator/translator.py`

### Frontend

- [ ] Frontend tourne: `ps aux | grep "npm run preview"`
- [ ] Accessible: `http://10.20.1.31:4173`
- [ ] Console montre: `📦 AppStore: REAL API mode - no mock playbooks`
- [ ] Console montre: `🔧 Mission Control Mode: REAL API`

### Sphinx

- [ ] Sphinx actif: `ps aux | grep sphinx`
- [ ] Port Olympe ouvert: `nc -zv 10.202.0.1 1883`

### Test Mission

- [ ] Créer mission avec 3-4 waypoints
- [ ] Cliquer "Start Mission"
- [ ] Logs montrent "Taking off..." immédiatement
- [ ] Pas de timeout 10s
- [ ] Waypoints atteints un par un
- [ ] "Mission completed successfully"
- [ ] Drone atterrit normalement

## 📊 Comparaison Avant/Après

### ❌ AVANT (Avec Bug)

```
Timeline:
00s - MaxTilt command sent
10s - [SILENCE - timeout]
10s - Emergency landing
```

**Durée:** 10 secondes → ÉCHEC

### ✅ APRÈS (Fix)

```
Timeline:
00s - MaxTilt command sent
00s - Takeoff
05s - Waypoint 1 reached
10s - Waypoint 2 reached
15s - Waypoint 3 reached
20s - Landing
21s - Mission completed successfully
```

**Durée:** ~21 secondes → SUCCÈS

## 🎯 Prochaines Étapes

### Si Mission GPS Fonctionne

**Vous pouvez maintenant:**
1. ✅ Tester différentes missions
2. ✅ Ajouter plus de waypoints
3. ✅ Tester différentes altitudes
4. ✅ Intégrer avec système d'approbation
5. ✅ Tester WebSocket real-time updates

### Si Vous Voulez Réactiver Caméra

**Plus tard, une fois GPS stable:**

1. Débugger pourquoi `set_camera_mode` timeout
2. Vérifier configuration Sphinx caméra
3. Décommenter ligne 86 dans `translator.py`
4. Tester avec timeout de 5s
5. Ajouter fallback si caméra échoue

---

**Déployé:** 8 Novembre 2025
**Version:** GPS Navigation Only (v1.0)
**Status:** ✅ Production Ready
