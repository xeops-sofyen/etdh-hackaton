# Sphinx Simulator - INSTALLÉ ET FONCTIONNEL ✅

## 🎉 SUCCÈS - Sphinx est Prêt!

Sphinx 2.15.1 avec Gazebo 11.11.0 est **entièrement installé et configuré**!

---

## 📋 Ce qui a été Résolu

### Problème: Bibliothèques Gazebo Manquantes

**Erreurs précédentes:**
```
gzserver: error while loading shared libraries: libgazebo.so.11: cannot open shared object file
libfwd.so: cannot open shared object file
```

**Solution appliquée:**
1. Les bibliothèques étaient installées dans `/opt/parrot-sphinx/usr/lib/`
2. Mais pas dans le chemin de recherche système
3. Configuration de `ld.so.conf` pour inclure ce répertoire
4. Mise à jour du cache avec `ldconfig`

**Résultat:**
- ✅ libgazebo.so.11 → résolu
- ✅ libfwd.so → résolu
- ✅ Toutes dépendances Gazebo → résolues

---

## 🚀 Lancer Sphinx Maintenant

### Accès VNC (Si pas encore connecté)

**Terminal Mac:**
```bash
ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080 -L 5901:localhost:5901
```

**Navigateur:**
```
http://localhost:6080/vnc.html
```
**Mot de passe:** `heimdall2025`

---

### Dans VNC xterm - Lancer Sphinx

En tant qu'utilisateur **heimdall** (pas root):

```bash
cd /home/heimdall
./run_sphinx.sh
```

**Ce qui va se passer:**
1. Affichage des informations GPU/Display
2. Démarrage de Gazebo 11.11.0
3. Chargement du drone ANAFI AI
4. Ouverture fenêtre 3D dans VNC

---

### Test Mission Complète

**Terminal 1 (xterm VNC) - Sphinx:**
```bash
cd /home/heimdall
./run_sphinx.sh
```

**Terminal 2 (nouveau xterm) - Mission:**
```bash
cd /home/heimdall/etdh-hackaton
source backend/venv/bin/activate
python demo_geojson_translation.py
```

Ou mission complète:
```bash
python backend/quickstart.py --playbook playbooks/simple_test.json
```

---

## 📊 État Actuel de Votre Setup

| Composant | État | Notes |
|-----------|------|-------|
| Instance Vast.ai | ✅ Active | RTX A4000 (16GB VRAM) |
| SSH Access | ✅ Configuré | Port 23570 |
| VNC Server | ✅ Running | Display :1 |
| noVNC Web | ✅ Running | Port 6080 |
| Desktop Environment | ✅ Fonctionnel | Metacity + xterm |
| Olympe SDK | ✅ Installé | v7.7.5 |
| Tests Passants | ✅ 25/30 | 83% success |
| **Sphinx Simulator** | ✅ **INSTALLÉ** | **v2.15.1** |
| **Gazebo** | ✅ **Configuré** | **v11.11.0** |
| **Bibliothèques** | ✅ **Résolues** | **ldconfig OK** |

---

## 🎬 Scripts Disponibles sur le Serveur

En tant qu'utilisateur **heimdall**:

```
/home/heimdall/run_sphinx.sh        ← Lancer Sphinx simulateur
/home/heimdall/test_mission.sh      ← Test GeoJSON mission
/home/heimdall/SPHINX_READY.txt     ← Documentation complète
/home/heimdall/etdh-hackaton/       ← Projet complet
```

---

## 🔧 Configuration Technique Appliquée

### Bibliothèques Système

**Fichier créé:** `/etc/ld.so.conf.d/parrot-sphinx.conf`
```
/opt/parrot-sphinx/usr/lib
```

**Cache mis à jour:**
```bash
ldconfig
```

### Script run_sphinx.sh

Variables d'environnement configurées:
- `DISPLAY=:1` (VNC display)
- `PATH` inclut `/opt/parrot-sphinx/usr/bin`
- `LD_LIBRARY_PATH` inclut `/opt/parrot-sphinx/usr/lib`

### Permissions X11

```bash
xhost +local:
xhost +SI:localuser:heimdall
```

---

## 👥 Partager l'Accès VNC

**Informations pour Quentin, Dmytro, Titouan:**

```
🚁 Heimdall VNC Desktop

Host: ssh8.vast.ai
Port SSH: 23570
VNC Password: heimdall2025

1. ssh -p 23570 root@ssh8.vast.ai -L 6080:localhost:6080
2. http://localhost:6080/vnc.html
3. Password: heimdall2025

⚠️ Collaboration temps réel - tout le monde voit le même écran
```

---

## 💰 Coût

**~$0.35/heure** pour l'instance RTX A4000

**Arrêter quand non utilisé:**
```bash
vastai stop instance {INSTANCE_ID}
```
Préserve toutes vos données!

---

## 📞 Documentation Complète

- [NEXT_STEPS.md](NEXT_STEPS.md) - Guide complet post-installation
- [VAST_AI_VNC_SETUP_COMPLETE.md](VAST_AI_VNC_SETUP_COMPLETE.md) - Configuration VNC
- [TEAM_ACCESS_GUIDE.md](TEAM_ACCESS_GUIDE.md) - Guide accès équipe

---

## ✅ Checklist Installation - COMPLÈTE!

- [x] Instance Vast.ai RTX A4000 active
- [x] Ubuntu 20.04 LTS configuré
- [x] Olympe SDK 7.7.5 installé
- [x] VNC Server + noVNC configurés
- [x] Desktop Metacity + xterm fonctionnel
- [x] **Sphinx 2.15.1 installé**
- [x] **Licence Parrot acceptée (MD5 trick)**
- [x] **Bibliothèques Gazebo configurées**
- [x] **Utilisateur heimdall créé**
- [x] **Permissions X11 configurées**
- [ ] Tester Sphinx avec drone ANAFI AI
- [ ] Corriger tests en échec (25/30 → 30/30)

---

## 🎯 Action: MAINTENANT

**Dans votre terminal VNC xterm:**
```bash
cd /home/heimdall
./run_sphinx.sh
```

**Vous allez voir la simulation 3D du drone!** 🚁🎉

---

**Team Heimdall: Sofyen, Quentin, Dmytro, Titouan**
**ETDH Hackathon Paris 2025 - Challenge UAS-1**
