# Heimdall - Configuration VNC sur Vast.ai ✅

## 📋 Résumé de la Configuration

**Instance Vast.ai:** RTX A4000 (16GB VRAM)
**Host:** ssh8.vast.ai
**Port SSH:** 23570
**Système:** Ubuntu 20.04 LTS + GNOME Desktop
**Mot de passe VNC:** `heimdall2025`

---

## 🖥️ Accès au Bureau VNC

### ⚠️ Important: Utiliser SSH Port Forwarding

Vast.ai ne mappe pas automatiquement le port 6080. Il faut créer un tunnel SSH.

### Étape 1: Créer le Tunnel SSH

Ouvrez un **nouveau terminal** sur votre Mac et exécutez:

```bash
ssh -p 23570 root@ssh8.vast.ai \
  -L 6080:localhost:6080 \
  -L 5901:localhost:5901
```

**⚠️ Laissez cette connexion SSH ouverte!** Ne fermez pas ce terminal.

### Étape 2: Accéder au VNC Web

Dans votre **navigateur**, ouvrez:

```
http://localhost:6080/vnc.html
```

### Étape 3: Se Connecter

1. Cliquez sur "Connect"
2. Entrez le mot de passe: `heimdall2025`
3. Vous accédez maintenant au bureau Ubuntu avec GPU!

---

## 👥 Partage avec l'Équipe

### Option A: Chaque Membre Crée Son Tunnel (Recommandé)

**Informations à partager avec Quentin, Dmytro, Titouan:**

```
🚁 Accès Heimdall VNC Desktop

Host: ssh8.vast.ai
Port SSH: 23570
VNC Password: heimdall2025

Commandes:
1. ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080
2. Ouvrir: http://localhost:6080/vnc.html
3. Mot de passe: heimdall2025

⚠️ Gardez le terminal SSH ouvert!
```

**Note:** Tous les membres verront le même bureau (collaboration en temps réel).

### Option B: Client VNC Natif

Si vous préférez un client VNC natif (TigerVNC, RealVNC):

1. **Créer le tunnel:**
   ```bash
   ssh -p 23570 root@ssh8.vast.ai -L 5901:localhost:5901
   ```

2. **Se connecter avec le client VNC:**
   - Adresse: `localhost:5901`
   - Mot de passe: `heimdall2025`

---

## 🚁 Installation de Sphinx Simulator

Une fois connecté au VNC Desktop:

### Étape 1: Ouvrir un Terminal

Dans le bureau VNC, cliquez sur "Activities" (coin supérieur gauche) → "Terminal"

### Étape 2: Exécuter le Script d'Installation

```bash
~/install_sphinx.sh
```

### Étape 3: Accepter la Licence

Quand demandé, tapez `Y` pour accepter la licence Parrot.

### Étape 4: Vérifier l'Installation

```bash
sphinx --version
```

---

## 🧪 Tests et Démo

### Test Système Complet

```bash
~/test_heimdall.sh
```

### Démo GeoJSON (Poland/Ukraine Border)

```bash
cd ~/etdh-hackaton
source backend/venv/bin/activate
python demo_geojson_translation.py
```

### Lancer Sphinx Simulator

**Terminal 1:**
```bash
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone
```

**Terminal 2:**
```bash
cd ~/etdh-hackaton
source backend/venv/bin/activate
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 📊 État Actuel du Projet

### ✅ Fonctionnel
- Ubuntu Desktop avec GNOME
- VNC Server (TigerVNC) sur display :1
- noVNC Web Interface sur port 6080
- NVIDIA RTX A4000 (16GB VRAM) détecté
- Olympe SDK 7.7.5 installé
- Python 3.10.13
- 25/30 tests qui passent (83%)
- GeoJSON conversion fonctionnelle

### ⏳ À Compléter
- Installation Sphinx Simulator (script prêt)
- Correction des 4 tests en échec
- Test de mission complète avec visualisation 3D

---

## 📁 Fichiers Disponibles sur le Serveur

```
~/install_sphinx.sh         - Script d'installation Sphinx
~/test_heimdall.sh          - Script de test système
~/TEAM_ACCESS_GUIDE.md      - Guide d'accès équipe (version complète)
~/VNC_ACCESS_GUIDE.md       - Guide VNC (ce fichier)
~/etdh-hackaton/            - Projet Heimdall
```

---

## 🔧 Dépannage

### Problème: "Connection refused" sur localhost:6080

**Solution:**
1. Vérifiez que le tunnel SSH est actif (terminal ouvert)
2. Vérifiez que websockify tourne:
   ```bash
   ssh -p 23570 root@ssh8.vast.ai "ps aux | grep websockify"
   ```

### Problème: VNC ne répond pas

**Redémarrer VNC/noVNC:**
```bash
ssh -p 23570 root@ssh8.vast.ai << 'EOF'
vncserver -kill :1
killall websockify
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
websockify -D --web=/usr/share/novnc/ 0.0.0.0:6080 localhost:5901
EOF
```

### Problème: Clavier/Souris ne fonctionne pas dans VNC

- Cliquez dans la fenêtre VNC pour activer le focus
- Utilisez la barre d'outils VNC (côté gauche) pour options clavier/souris

---

## 💰 Gestion des Coûts

**Coût actuel:** ~$0.35/hour

### Arrêter l'Instance (Préserve les Données)
```bash
vastai stop instance {INSTANCE_ID}
```

### Redémarrer l'Instance
```bash
vastai start instance {INSTANCE_ID}
```

**Note:** Arrêtez l'instance quand vous ne l'utilisez pas pour économiser!

---

## 🎯 Prochaines Étapes

1. ✅ **Accéder au VNC Desktop** (via tunnel SSH)
2. ⏳ **Installer Sphinx** (~/install_sphinx.sh)
3. ⏳ **Tester visualisation 3D** (avec mission de démonstration)
4. ⏳ **Corriger les 4 tests en échec**
5. ⏳ **Préparer la démo finale** pour le hackathon

---

## 📞 Support

### Vérifier l'État du Système

```bash
ssh -p 23570 root@ssh8.vast.ai << 'EOF'
echo "=== VNC Status ==="
ps aux | grep vnc | grep -v grep
echo ""
echo "=== noVNC Status ==="
ps aux | grep websockify | grep -v grep
echo ""
echo "=== GPU Status ==="
nvidia-smi --query-gpu=name,utilization.gpu --format=csv,noheader
EOF
```

### Accès SSH Direct

```bash
ssh -p 23570 root@ssh8.vast.ai
```

---

## 🚀 Quick Reference

```bash
# Tunnel SSH pour VNC
ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080 -L 5901:localhost:5901

# Accès VNC Web
http://localhost:6080/vnc.html

# Mot de passe VNC
heimdall2025

# Installer Sphinx (dans VNC terminal)
~/install_sphinx.sh

# Test système
~/test_heimdall.sh

# Démo GeoJSON
cd ~/etdh-hackaton && source backend/venv/bin/activate
python demo_geojson_translation.py
```

---

**Bonne chance pour le hackathon! 🚁🎯**

Team Heimdall: Sofyen, Quentin, Dmytro, Titouan
