# Google ADK Agent Integration Plan

**Project:** AI-Powered Autonomous Drone Mission System  
**API Key Provided:** `AIzaSyC2ht1bvAsYxa-UWKaO2aCrTR3YLfI9fG8`

---

## 📋 Overview

This document outlines the plan to integrate **Google Agent Development Kit (ADK)** into the backend, enabling conversational AI-powered mission planning accessible via REST API.

### Current State ✅
- Google ADK v1.18.0 already installed in `backend/requirements.txt`
- FastAPI backend operational with existing endpoints
- Placeholder NLP endpoint at `/mission/parse-natural-language`
- Complete playbook schema and Olympe translator ready

### Goal 🎯
Enable natural language mission planning through a Google ADK agent accessible via API, allowing operators to create complex drone missions through conversation.

---

## ⚠️ Implementation Constraints

### Backend-Only Implementation
**IMPORTANT:** This integration is **backend-only**. Do NOT modify frontend code.
- Another developer is handling frontend changes
- Focus exclusively on API endpoints and backend agent logic
- Frontend will consume the API endpoints independently

### Chat API Behavior
The `/adk/chat` endpoint is the **ONLY endpoint** for natural language mission planning. It supports:
1. **Conversational responses** - Agent responds to user questions, clarifications, refinements
2. **Playbook generation** - When the agent generates a playbook during conversation, it must be included in the response

**Response Structure:**
```json
{
  "session_id": "uuid",
  "agent_response": "Agent's textual response to the user",
  "playbook": null | {...},  // Playbook JSON if generated, null otherwise
  "ready_to_execute": boolean  // true if playbook is valid and ready
}
```

**Frontend Integration:**
- Frontend displays `agent_response` in chat interface
- If `playbook` is not null, frontend also displays the playbook (visual representation)
- User can continue chatting to refine, or execute the playbook if `ready_to_execute` is true

**Important:**
- The old `/mission/parse-natural-language` endpoint will be REMOVED
- `/adk/generate-playbook` will NOT be created (redundant with `/adk/chat`)
- All natural language processing happens through `/adk/chat`

---

## 📂 Proposed File Structure

```
backend/
├── adk_agent/                    # [NEW] ADK Agent Module
│   ├── __init__.py
│   ├── agent.py                  # Main ADK agent definition
│   ├── tools.py                  # Custom function tools for drone missions
│   ├── prompts.py                # System prompts & instructions
│   ├── session_manager.py        # Conversation state management
│   └── config.py                 # ADK configuration & API key loading
│
├── api/
│   ├── main.py                   # [MODIFY] Add ADK endpoints
│   └── routes/
│       └── adk_routes.py         # [NEW] ADK-specific routes
│
├── .env                          # [MODIFY] Add GOOGLE_API_KEY
├── requirements.txt              # [ALREADY HAS google-adk==1.18.0]
│
└── tests/
    └── test_adk_agent.py         # [NEW] ADK agent tests
```

---

## 🚀 Implementation Phases

### **Phase 1: Setup & Configuration**

#### 1.1 Configure API Key

Add to `backend/.env`:
```bash
GOOGLE_API_KEY=AIzaSyC2ht1bvAsYxa-UWKaO2aCrTR3YLfI9fG8
```

#### 1.2 Verify Installation

```bash
cd /home/debian/etdh-hackaton/backend
python -c "import google.adk; print('ADK installed:', google.adk.__version__)"
```

**Acceptance Criteria:**
- ✅ API key stored securely in `.env`
- ✅ ADK import works without errors

---

### **Phase 2: ADK Agent Implementation** (1-2 hours)

#### 2.1 Create Agent Configuration (`backend/adk_agent/config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

ADK_CONFIG = {
    'model': 'gemini-2.5-flash',
    'api_key': os.getenv('GOOGLE_API_KEY'),
    'temperature': 0.7,
    'max_tokens': 2048,
}

# Safety settings for mission planning
SAFETY_CONSTRAINTS = {
    'max_altitude_m': 120,
    'min_altitude_m': 10,
    'max_speed_mps': 15,
    'min_battery_threshold': 20,
}
```

#### 2.2 Create Custom Tools (`backend/adk_agent/tools.py`)

Define tools the agent can use:

- `generate_waypoints(center_lat, center_lon, pattern, count, altitude)` - Generate GPS waypoints
- `validate_flight_zone(waypoints)` - Check if flight area is safe
- `calculate_flight_time(waypoints, speed)` - Estimate mission duration
- `create_mission_playbook(mission_params)` - Generate playbook JSON
- `get_weather_info(location)` - Mock weather data (future: real API)

#### 2.3 Define System Prompts (`backend/adk_agent/prompts.py`)

```python
SYSTEM_INSTRUCTION = """
You are an expert drone mission planner for the Heimdall autonomous drone system.

Your role:
1. Parse natural language mission requests from operators
2. Generate safe and efficient flight plans
3. Create structured JSON playbooks compatible with Parrot Olympe SDK
4. Validate missions against safety constraints
5. Provide clear explanations of mission parameters

Safety Rules:
- Altitude: 10m - 120m
- Speed: 1-15 m/s
- Always include return-to-home contingency
- Check for obstacles and no-fly zones
- Minimum 20% battery reserve

Available Actions:
- takeoff, land, hover, photo, video, moveTo, return_to_home

Output Format:
Always generate valid JSON playbooks following the MissionPlaybook schema.
"""
```

#### 2.4 Build Main Agent (`backend/adk_agent/agent.py`)

```python
from google.adk.agents.llm_agent import Agent
from .tools import (
    generate_waypoints,
    validate_flight_zone,
    calculate_flight_time,
    create_mission_playbook,
)
from .prompts import SYSTEM_INSTRUCTION
from .config import ADK_CONFIG

# Initialize the ADK agent
mission_planner_agent = Agent(
    model=ADK_CONFIG['model'],
    name='mission_planner',
    description="AI-powered drone mission planner",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        generate_waypoints,
        validate_flight_zone,
        calculate_flight_time,
        create_mission_playbook,
    ],
)

async def plan_mission(user_command: str, context: dict = None) -> dict:
    """
    Main entry point for mission planning
    
    Args:
        user_command: Natural language mission request
        context: Optional context (drone status, weather, etc.)
    
    Returns:
        dict with agent_response and generated playbook
    """
    # Add context to the prompt if provided
    enhanced_prompt = user_command
    if context:
        enhanced_prompt = f"Context: {context}\n\nUser Request: {user_command}"
    
    # Execute agent
    response = mission_planner_agent.run(enhanced_prompt)
    
    return {
        'agent_response': response.text,
        'playbook': response.artifacts.get('playbook'),
        'metadata': response.metadata,
    }
```

#### 2.5 Session Management (`backend/adk_agent/session_manager.py`)

Handle multi-turn conversations:

```python
import uuid
from typing import Dict, List
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
    
    def create_session(self, user_id: str = None) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'messages': [],
            'context': {},
        }
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id]['messages'].append({
                'role': role,
                'content': content,
                'timestamp': datetime.utcnow(),
            })
    
    def get_session(self, session_id: str) -> dict:
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
```

**Acceptance Criteria:**
- ✅ Agent successfully initializes with Gemini 2.5 Flash
- ✅ Custom tools are callable by the agent
- ✅ System prompts enforce safety constraints
- ✅ Session manager handles conversation state

---

### **Phase 3: API Integration** (1 hour)

#### 3.1 Create ADK Routes (`backend/api/routes/adk_routes.py`)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.adk_agent.agent import plan_mission
from backend.adk_agent.session_manager import SessionManager

router = APIRouter(prefix="/adk", tags=["ADK Agent"])
session_manager = SessionManager()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the ADK agent for mission planning
    
    Example:
    {
        "message": "Create a patrol mission around 48.8788, 2.3675 at 50m altitude"
    }
    """
    # Create or retrieve session
    if not request.session_id:
        session_id = session_manager.create_session()
    else:
        session_id = request.session_id
    
    # Add user message to session
    session_manager.add_message(session_id, "user", request.message)
    
    try:
        # Get agent response
        result = await plan_mission(request.message, request.context)
        
        # Add agent response to session
        session_manager.add_message(session_id, "agent", result['agent_response'])
        
        return {
            "session_id": session_id,
            "agent_response": result['agent_response'],
            "playbook": result['playbook'],
            "ready_to_execute": result['playbook'] is not None,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Retrieve conversation history"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Clear session and conversation history"""
    session_manager.delete_session(session_id)
    return {"status": "deleted"}
```

#### 3.2 Update Main API (`backend/api/main.py`)

Add to imports:
```python
from backend.api.routes import adk_routes
```

Add route registration:
```python
# Include ADK routes
app.include_router(adk_routes.router)
```

#### 3.3 Remove Old Endpoint

The existing `/mission/parse-natural-language` endpoint will be REMOVED as all natural language processing is now handled by `/adk/chat`.

**Acceptance Criteria:**
- ✅ `/adk/chat` endpoint returns agent responses and playbooks
- ✅ Session management works across requests
- ✅ Integration with existing validation pipeline
- ✅ Old `/mission/parse-natural-language` endpoint removed

---

#### 4 Safety Layer

Add automatic risk assessment:

```python
def assess_mission_risk(playbook: MissionPlaybook) -> dict:
    """
    Analyze mission risk factors
    Returns: risk_level (low/medium/high), warnings, suggestions
    """
    risks = []
    
    # Check altitude
    if playbook.flight_parameters.altitude_m > 100:
        risks.append("High altitude flight")
    
    # Check waypoint density
    # Check weather conditions
    # Check no-fly zones
    
    return {
        'risk_level': calculate_risk(risks),
        'warnings': risks,
        'suggestions': generate_alternatives(playbook),
    }
```

**Acceptance Criteria:**
- ✅ Automatic safety checks and suggestions

---

## 📊 API Endpoints Summary

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/adk/chat` | **PRIMARY ENDPOINT**: Chat with agent for mission planning & playbook generation |
| `GET` | `/adk/sessions/{session_id}` | Get conversation history |
| `DELETE` | `/adk/sessions/{session_id}` | Clear session |
| `WS` | `/adk/ws/chat` | Stream agent responses (Future: Phase 4) |

### Removed Endpoints

| Method | Endpoint | Reason |
|--------|----------|--------|
| `POST` | `/mission/parse-natural-language` | Replaced by `/adk/chat` |

---

## 🎯 Example Usage

### Example 1: Simple Chat

**Request:**
```bash
curl -X POST http://localhost:8000/adk/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a patrol mission around the Eiffel Tower at 50m altitude"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "agent_response": "I'll create a patrol mission around the Eiffel Tower. For safety, I'll use a rectangular pattern with 4 waypoints at 50m altitude...",
  "playbook": {
    "mission_id": "patrol_eiffel_tower_001",
    "mission_type": "patrol",
    "flight_parameters": {
      "altitude_m": 50,
      "speed_mps": 5,
      "pattern": "rectangular"
    },
    "waypoints": [...]
  },
  "ready_to_execute": true
}
```

### Example 2: Generate and Execute

```bash
# 1. Generate playbook via chat
curl -X POST http://localhost:8000/adk/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Simple test flight at 30m"}'
# Returns: playbook in response

# 2. Execute mission
curl -X POST http://localhost:8000/mission/execute \
  -H "Content-Type: application/json" \
  -d '{"playbook": {...}}'
```

### Example 3: Multi-turn Conversation

```bash
# Turn 1
curl -X POST http://localhost:8000/adk/chat \
  -d '{"message": "Create a patrol mission"}'
# Returns: session_id = "xyz-789"

# Turn 2 (refine)
curl -X POST http://localhost:8000/adk/chat \
  -d '{"session_id": "xyz-789", "message": "Make it a circular pattern with 8 waypoints"}'

# Turn 3 (adjust)
curl -X POST http://localhost:8000/adk/chat \
  -d '{"session_id": "xyz-789", "message": "Increase altitude to 60m and add photo at each waypoint"}'
```

---

## 🎓 References

- [Google ADK Documentation](https://google.github.io/adk-docs/get-started/python/ ; https://google.github.io/adk-docs/get-started/quickstart/)
- [ADK Python API Reference](https://google.github.io/adk-docs/reference/api-reference/python-adk/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---
