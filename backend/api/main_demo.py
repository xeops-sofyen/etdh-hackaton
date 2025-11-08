"""
FastAPI Server for Heimdall Mission Control - DEMO MODE
(Sans Olympe SDK pour tester l'intégration frontend/backend)
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import logging
from pathlib import Path
import asyncio
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Heimdall Mission Control API - DEMO",
    description="AI-Powered Autonomous Drone Mission System (Demo Mode)",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API MODELS (Simplified from schema.py)
# ============================================================================

class Waypoint(BaseModel):
    lat: float
    lon: float
    alt: float
    action: Optional[str] = None
    hover_duration_sec: Optional[float] = None

class MissionPlaybook(BaseModel):
    mission_id: str
    mission_type: str
    description: str
    waypoints: List[Waypoint]
    flight_parameters: Optional[Dict] = None
    camera_settings: Optional[Dict] = None
    contingencies: Optional[Dict] = None
    auto_execute: bool = True
    max_duration_min: float = 30

class MissionExecuteRequest(BaseModel):
    playbook: MissionPlaybook
    simulate: bool = False

# ============================================================================
# MOCK DRONE STATE
# ============================================================================

current_mission: Optional[Dict] = None
drone_state = {
    "mission_id": None,
    "status": "idle",
    "position": {"lat": 0, "lon": 0},
    "battery": 100,
    "speed": 0,
    "heading": 0,
    "current_waypoint": 0
}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Heimdall Mission Control - DEMO MODE",
        "status": "operational",
        "version": "1.0.0",
        "mode": "demo (no Olympe SDK)"
    }

@app.get("/status")
async def get_status():
    """Get current drone status"""
    return drone_state

@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest):
    """Execute a mission playbook (DEMO MODE)"""
    global current_mission, drone_state

    logger.info(f"🚁 Received mission: {request.playbook.mission_id}")
    logger.info(f"   Type: {request.playbook.mission_type}")
    logger.info(f"   Waypoints: {len(request.playbook.waypoints)}")
    logger.info(f"   Description: {request.playbook.description}")

    if request.simulate:
        logger.info("   Mode: SIMULATION")
        return {
            "status": "simulation_success",
            "mission_id": request.playbook.mission_id,
            "message": "Playbook is valid (Demo mode - no actual validation)"
        }
    else:
        logger.info("   Mode: EXECUTION (Demo - no real drone)")
        current_mission = request.playbook.dict()
        drone_state["mission_id"] = request.playbook.mission_id
        drone_state["status"] = "en_route"
        drone_state["current_waypoint"] = 0

        if request.playbook.waypoints:
            drone_state["position"] = {
                "lat": request.playbook.waypoints[0].lat,
                "lon": request.playbook.waypoints[0].lon
            }

        return {
            "status": "started",
            "mission_id": request.playbook.mission_id,
            "message": "Mission started in demo mode"
        }

@app.post("/mission/abort")
async def abort_mission():
    """Emergency abort"""
    global drone_state
    logger.warning("⚠️ ABORT requested via API")
    drone_state["status"] = "idle"
    drone_state["speed"] = 0
    return {"status": "aborted", "message": "Mission aborted (demo mode)"}

@app.get("/playbooks/list")
async def list_playbooks():
    """List available playbooks"""
    playbooks_dir = Path("playbooks")
    if not playbooks_dir.exists():
        return {"playbooks": []}

    playbooks = []
    for pb_file in playbooks_dir.glob("*.json"):
        try:
            with open(pb_file) as f:
                data = json.load(f)
                playbooks.append({
                    "filename": pb_file.name,
                    "mission_id": data.get("mission_id"),
                    "description": data.get("description")
                })
        except:
            pass

    return {"playbooks": playbooks}

# ============================================================================
# WEBSOCKET
# ============================================================================

active_connections: Dict[str, List[WebSocket]] = {}

@app.websocket("/ws/mission/{mission_id}")
async def websocket_mission_updates(websocket: WebSocket, mission_id: str):
    """WebSocket for real-time updates (DEMO MODE)"""
    await websocket.accept()

    if mission_id not in active_connections:
        active_connections[mission_id] = []
    active_connections[mission_id].append(websocket)

    logger.info(f"✅ WebSocket connected for mission {mission_id}")

    try:
        # Send initial status
        await websocket.send_json({
            "type": "position_update",
            "data": drone_state
        })

        # Simulate drone movement if mission is active
        waypoint_index = 0
        if current_mission and current_mission.get("mission_id") == mission_id:
            waypoints = current_mission.get("waypoints", [])

            while True:
                await asyncio.sleep(1)

                if drone_state["status"] == "idle":
                    await websocket.send_json({
                        "type": "position_update",
                        "data": drone_state
                    })
                    continue

                # Simulate movement
                if waypoint_index < len(waypoints):
                    target = waypoints[waypoint_index]
                    drone_state["position"] = {
                        "lat": target["lat"] + random.uniform(-0.0001, 0.0001),
                        "lon": target["lon"] + random.uniform(-0.0001, 0.0001)
                    }
                    drone_state["battery"] = max(0, drone_state["battery"] - 0.1)
                    drone_state["speed"] = random.uniform(10, 15)
                    drone_state["heading"] = random.randint(0, 360)
                    drone_state["current_waypoint"] = waypoint_index

                    await websocket.send_json({
                        "type": "position_update",
                        "data": drone_state
                    })

                    # Move to next waypoint every 10 seconds
                    if random.random() < 0.1:
                        waypoint_index += 1
                        if waypoint_index < len(waypoints):
                            await websocket.send_json({
                                "type": "waypoint_reached",
                                "data": {"current_waypoint": waypoint_index}
                            })
                        else:
                            # Mission complete
                            drone_state["status"] = "idle"
                            await websocket.send_json({
                                "type": "mission_complete",
                                "data": drone_state
                            })
                            break
                else:
                    break
        else:
            # No active mission, just send periodic updates
            while True:
                await asyncio.sleep(2)
                await websocket.send_json({
                    "type": "position_update",
                    "data": drone_state
                })

    except WebSocketDisconnect:
        logger.info(f"❌ WebSocket disconnected for mission {mission_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if mission_id in active_connections:
            active_connections[mission_id].remove(websocket)
            if not active_connections[mission_id]:
                del active_connections[mission_id]

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚁 Heimdall Backend - DEMO MODE")
    print("=" * 60)
    print("Mode: Demo (no Olympe SDK required)")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
