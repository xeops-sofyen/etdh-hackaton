# Architecture Clarification - Frontend/Backend

## ❓ Question: "Pourquoi as-tu créé une API dans services ?"

**Réponse courte:** Je n'ai **PAS** créé une nouvelle API backend. J'ai créé un **client HTTP** pour consommer votre API backend existante.

---

## 🏗️ Architecture Complète

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/TypeScript)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Composants React (Dmytro)                                      │
│      │                                                          │
│      ▼                                                          │
│  useMissionControl() Hook                                       │
│      │                                                          │
│      ├─► Mode Mock                                             │
│      │   └─► mockWebSocket.ts (Dmytro)                         │
│      │       └─► Simule le backend localement                  │
│      │                                                          │
│      └─► Mode Real                                             │
│          └─► api.ts (Sofyen - CLIENT HTTP) ⭐                  │
│              └─► Appelle votre backend via fetch()             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Python/FastAPI)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  backend/api/main.py (Sofyen - SERVEUR API) ⭐                 │
│      │                                                          │
│      ├─► POST /mission/execute                                 │
│      ├─► GET /status                                           │
│      ├─► POST /mission/abort                                   │
│      └─► WebSocket /ws/mission/{id}                            │
│                                                                 │
│  backend/playbook_parser/schema.py                              │
│      └─► MissionPlaybook (Pydantic schema)                     │
│                                                                 │
│  backend/olympe_translator/translator.py                        │
│      └─► Convertit Playbook → Olympe SDK                       │
│                                                                 │
│  backend/drone_controller/controller.py                         │
│      └─► Exécute sur le drone                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Parrot Drone (Olympe SDK)
```

---

## 📁 Fichiers et Leurs Rôles

### Backend (Sofyen - DÉJÀ EXISTANT)

| Fichier | Rôle | Type |
|---------|------|------|
| `backend/api/main.py` | **Serveur API REST** | FastAPI Server |
| `backend/playbook_parser/schema.py` | Schéma Pydantic | Data Model |
| `backend/olympe_translator/translator.py` | Traducteur Playbook → Olympe | Business Logic |
| `backend/drone_controller/controller.py` | Contrôleur drone | Business Logic |

### Frontend Services (Dmytro + Sofyen)

| Fichier | Rôle | Type | Auteur |
|---------|------|------|--------|
| `frontend/src/services/mockWebSocket.ts` | **Simulation backend** | Mock Service | Dmytro |
| `frontend/src/services/mockLLM.ts` | **Simulation LLM** | Mock Service | Dmytro |
| `frontend/src/services/api.ts` | **Client HTTP** | HTTP Client | Sofyen |

---

## 🔍 Qu'est-ce qu'un "Client API" ?

### Analogie Restaurant :

- **Backend API** = Le restaurant (cuisine, serveurs)
- **Client API** = L'application de livraison (Uber Eats)
- **Mock** = Photos du menu pour tester l'app sans commander

### Code Exemple :

**Backend (Serveur API) - `backend/api/main.py`**
```python
@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest):
    # Exécute la mission sur le drone
    return {"status": "started"}
```

**Frontend (Client API) - `frontend/src/services/api.ts`**
```typescript
export class HeimdallAPI {
  async executeMission(playbook: Playbook) {
    // APPELLE le serveur backend
    const response = await fetch('http://localhost:8000/mission/execute', {
      method: 'POST',
      body: JSON.stringify(playbook)
    });
    return response.json();
  }
}
```

**C'est comme :**
```typescript
// Client
const uberEats = new UberEatsApp();
await uberEats.orderPizza(); // Appelle le restaurant

// Serveur (backend)
restaurant.receivePizzaOrder(); // Reçoit la commande
```

---

## 🔄 Pourquoi Deux "APIs" ?

### Ce N'est PAS Deux APIs, C'est :

1. **Serveur API** (`backend/api/main.py`)
   - Fournit les endpoints REST
   - Exécute la logique métier
   - Contrôle le drone

2. **Client API** (`frontend/src/services/api.ts`)
   - **Consomme** le serveur API
   - Convertit les types (GeoJSON ↔ Pydantic)
   - Gère WebSocket côté frontend

### Pourquoi Avoir un Client ?

Sans client (`api.ts`), Dmytro devrait écrire dans chaque composant :

```typescript
// ❌ SANS CLIENT - Code répété partout
const response = await fetch('http://localhost:8000/mission/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mission_id: playbook.id,
    waypoints: playbook.route.features.map(f => ({
      lat: f.geometry.coordinates[1],
      lon: f.geometry.coordinates[0],
      // ... conversion complexe
    }))
  })
});
```

Avec client (`api.ts`) :

```typescript
// ✅ AVEC CLIENT - Simple et réutilisable
await heimdallAPI.executeMission(playbook);
// Le client gère toute la conversion automatiquement
```

---

## ✅ Récapitulatif - Qui Fait Quoi ?

### Votre Backend (Sofyen) :

- ✅ `backend/api/main.py` - **Serveur API** (écoute sur port 8000)
- ✅ `backend/playbook_parser/schema.py` - Schéma Pydantic
- ✅ `backend/olympe_translator/` - Traduction Olympe
- ✅ `backend/drone_controller/` - Contrôle drone

### Mon Contribution (Sofyen - Intégration) :

- ✅ `frontend/src/services/api.ts` - **Client HTTP** pour appeler votre backend
- ✅ `frontend/src/hooks/useMissionControl.ts` - Hook React
- ✅ Ajout WebSocket dans `backend/api/main.py`
- ✅ Correction de la conversion GeoJSON → Pydantic schema

### Frontend Dmytro :

- ✅ Composants React (MainView, MapView, etc.)
- ✅ Mocks pour développement isolé
- ✅ Interface utilisateur

---

## 🎯 Flow Complet d'une Mission

```
1. User clicks "Start Mission" dans le frontend
   ↓
2. useMissionControl() hook
   ↓
3. frontend/src/services/api.ts (CLIENT)
   └─► playbookToBackend() convertit GeoJSON → Pydantic
   └─► fetch('http://localhost:8000/mission/execute')
   ↓
4. backend/api/main.py (SERVEUR) reçoit la requête
   ↓
5. backend/drone_controller/controller.py
   ↓
6. backend/olympe_translator/translator.py
   ↓
7. Parrot Olympe SDK
   ↓
8. Drone physique exécute la mission
   ↓
9. WebSocket envoie updates en temps réel
   ↓
10. frontend/src/services/api.ts (CLIENT) reçoit updates
   ↓
11. Map affiche position du drone
```

---

## 💡 Pourquoi Cette Architecture ?

### Avantages :

1. **Séparation Frontend/Backend** - Équipes travaillent indépendamment
2. **Type Safety** - TypeScript (frontend) + Pydantic (backend)
3. **Testabilité** - Mocks pour dev frontend sans backend
4. **Réutilisabilité** - Client API utilisable par plusieurs composants
5. **Maintenance** - Logique de conversion centralisée

### Alternative (Sans Client) :

```typescript
// ❌ Chaque composant doit connaître le format backend
// ❌ Conversion répétée partout
// ❌ Difficile à maintenir si le backend change
```

---

## 🔧 Modifications Faites à Votre Backend

**J'ai SEULEMENT ajouté :**

1. **WebSocket endpoint** (`/ws/mission/{id}`) dans `backend/api/main.py`
2. **Imports** (`asyncio`, `WebSocket`)

**Je N'AI PAS modifié :**
- ❌ Votre schéma Pydantic
- ❌ Votre Olympe translator
- ❌ Votre drone controller
- ❌ La logique métier

---

## ✅ Conclusion

**Ce que j'ai créé :**
- Un **HTTP client** (`api.ts`) pour **appeler** votre backend
- Pas un nouveau backend !

**Analogie finale :**
- Votre backend = La Poste (service postal)
- Mon client = L'application mobile de La Poste (pour envoyer des lettres)
- Les mocks de Dmytro = Enveloppes factices pour tester l'app

**Tout est interconnecté, rien n'est dupliqué !** ✨

---

Questions ? Slack/Discord ! 🚀
