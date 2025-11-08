# 🚁 Heimdall - Quick Start Guide

## Configuration Actuelle ✅

Votre environnement Vast.ai est **entièrement configuré et Sphinx est INSTALLÉ**!

---

## 🎯 Accès VNC (1 minute)

### Terminal 1 - SSH Tunnel
```bash
ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080 -L 5901:localhost:5901
```
⚠️ **Ne fermez JAMAIS ce terminal!**

### Navigateur
```
http://localhost:6080/vnc.html
```
**Mot de passe:** `heimdall2025`

---

## ⚡ Lancer Sphinx (30 secondes)

Dans le terminal xterm VNC, en tant qu'utilisateur heimdall:

```bash
cd /home/heimdall
./run_sphinx.sh
```

Une fenêtre 3D va s'ouvrir avec le drone ANAFI AI!

---

## 🧪 Test Rapide

### GeoJSON Demo (utilisateur heimdall)
```bash
cd /home/heimdall/etdh-hackaton
source backend/venv/bin/activate
python demo_geojson_translation.py
```

### Mission Complète avec Sphinx 3D

**Terminal 1 (xterm VNC) - Lancer Sphinx:**
```bash
cd /home/heimdall
./run_sphinx.sh
```

**Terminal 2 (nouveau xterm) - Exécuter Mission:**
```bash
cd /home/heimdall/etdh-hackaton
source backend/venv/bin/activate
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 📊 État du Setup

| Composant | État |
|-----------|------|
| Vast.ai RTX A4000 | ✅ Active |
| Ubuntu 20.04 | ✅ Configuré |
| VNC Desktop | ✅ Accessible |
| Olympe SDK 7.7.5 | ✅ Installé |
| Tests (25/30) | ✅ Passants |
| **Sphinx 2.15.1** | ✅ **INSTALLÉ** |
| **Gazebo 11.11.0** | ✅ **Configuré** |

---

## 👥 Partager avec l'Équipe

```
Host: ssh8.vast.ai
Port: 23570
Password: heimdall2025

Commande:
ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080

URL: http://localhost:6080/vnc.html
```

---

## 📖 Documentation

- [SPHINX_INSTALLATION_READY.md](SPHINX_INSTALLATION_READY.md) - Guide installation Sphinx
- [NEXT_STEPS.md](NEXT_STEPS.md) - Guide complet post-installation
- [VAST_AI_VNC_SETUP_COMPLETE.md](VAST_AI_VNC_SETUP_COMPLETE.md) - Configuration VNC détaillée

---

## 💰 Gestion Instance

**Arrêter (préserve données):**
```bash
vastai stop instance {ID}
```

**Coût:** ~$0.35/heure

---

## 🎯 Action NOW

1. Ouvrez http://localhost:6080/vnc.html (mot de passe: heimdall2025)
2. Dans xterm VNC, lancez:
   ```bash
   cd /home/heimdall
   ./run_sphinx.sh
   ```
3. Une fenêtre 3D va s'ouvrir avec le drone ANAFI AI
4. Pour tester une mission, ouvrez un 2e terminal xterm et lancez:
   ```bash
   cd /home/heimdall
   ./test_mission.sh
   ```

**Sphinx est prêt - Lancez-le maintenant!** 🚁✅

---

**Team Heimdall - ETDH Hackathon Paris 2025**
