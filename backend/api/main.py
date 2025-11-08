"""
FastAPI Server for Heimdall Mission Control

Exposes REST API for mission execution
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging
from pathlib import Path
import asyncio

from backend.playbook_parser.schema import MissionPlaybook
from backend.drone_controller.controller import DroneController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Heimdall Mission Control API",
    description="AI-Powered Autonomous Drone Mission System",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global drone controller
drone_controller = DroneController(simulator_mode=True)


# ============================================================================
# API MODELS
# ============================================================================

class MissionExecuteRequest(BaseModel):
    """Request to execute a mission"""
    playbook: MissionPlaybook
    simulate: bool = False


class NaturalLanguageRequest(BaseModel):
    """Natural language mission command"""
    command: str
    # e.g., "Patrol the coastal area near Wilhelmshaven"


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Heimdall Mission Control",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """Get current drone and mission status"""
    return drone_controller.get_status()


@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute a mission playbook

    This endpoint validates and executes a complete mission.
    """
    logger.info(f"Received mission: {request.playbook.mission_id}")

    try:
        # Execute mission in background (so API returns immediately)
        if request.simulate:
            # Simulation mode: just validate, don't execute
            from backend.olympe_translator.translator import PlaybookValidator
            validator = PlaybookValidator()
            is_valid, error = validator.validate(request.playbook)

            if not is_valid:
                raise HTTPException(status_code=400, detail=error)

            return {
                "status": "simulation_success",
                "mission_id": request.playbook.mission_id,
                "message": "Playbook is valid and ready for execution"
            }
        else:
            # Real execution
            result = drone_controller.execute_mission(request.playbook)
            return result

    except Exception as e:
        logger.error(f"Mission execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mission/abort")
async def abort_mission():
    """Emergency abort current mission"""
    logger.warning("ABORT requested via API")
    success = drone_controller.abort_mission()

    if success:
        return {"status": "aborted"}
    else:
        raise HTTPException(status_code=500, detail="Abort failed")


@app.get("/playbooks/list")
async def list_playbooks():
    """List available example playbooks"""
    playbooks_dir = Path("playbooks")
    playbooks = []

    for pb_file in playbooks_dir.glob("*.json"):
        with open(pb_file) as f:
            data = json.load(f)
            playbooks.append({
                "filename": pb_file.name,
                "mission_id": data.get("mission_id"),
                "description": data.get("description")
            })

    return {"playbooks": playbooks}


@app.get("/playbooks/{filename}")
async def get_playbook(filename: str):
    """Get a specific playbook"""
    playbook_path = Path("playbooks") / filename

    if not playbook_path.exists():
        raise HTTPException(status_code=404, detail="Playbook not found")

    with open(playbook_path) as f:
        data = json.load(f)

    return data


@app.post("/mission/parse-natural-language")
async def parse_natural_language(request: NaturalLanguageRequest):
    """
    Parse natural language into a playbook

    Example: "Patrol the coast near Wilhelmshaven"
    → Generates structured playbook JSON
    """
    # TODO: Integrate with GPT-4 / LLM
    # For now, return a template

    logger.info(f"Parsing command: {request.command}")

    # Simple keyword matching (replace with LLM in production)
    if "patrol" in request.command.lower():
        with open("playbooks/coastal_patrol.json") as f:
            template = json.load(f)
        return {
            "status": "parsed",
            "playbook": template,
            "note": "Using template - integrate GPT-4 for real parsing"
        }
    elif "test" in request.command.lower():
        with open("playbooks/simple_test.json") as f:
            template = json.load(f)
        return {
            "status": "parsed",
            "playbook": template
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Could not parse command. Try: 'patrol coastal area' or 'simple test flight'"
        )


# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

# Store active WebSocket connections
active_connections: Dict[str, list[WebSocket]] = {}


@app.websocket("/ws/mission/{mission_id}")
async def websocket_mission_updates(websocket: WebSocket, mission_id: str):
    """
    WebSocket endpoint for real-time mission updates

    Streams:
    - position_update: Drone position, battery, speed
    - waypoint_reached: When drone reaches a waypoint
    - mission_complete: When mission finishes
    - error: When errors occur
    """
    await websocket.accept()

    # Register connection
    if mission_id not in active_connections:
        active_connections[mission_id] = []
    active_connections[mission_id].append(websocket)

    logger.info(f"WebSocket connected for mission {mission_id}")

    try:
        # Send initial status
        status = drone_controller.get_status()
        await websocket.send_json({
            "type": "position_update",
            "data": status
        })

        # Keep connection alive and stream updates
        while True:
            # Get latest status every second
            await asyncio.sleep(1)
            status = drone_controller.get_status()

            await websocket.send_json({
                "type": "position_update",
                "data": status
            })

            # Check if mission is complete
            if status.get("status") == "completed":
                await websocket.send_json({
                    "type": "mission_complete",
                    "data": status
                })
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for mission {mission_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    finally:
        # Cleanup connection
        if mission_id in active_connections:
            active_connections[mission_id].remove(websocket)
            if not active_connections[mission_id]:
                del active_connections[mission_id]


async def broadcast_to_mission(mission_id: str, message: dict):
    """Helper to broadcast updates to all connected clients for a mission"""
    if mission_id in active_connections:
        for connection in active_connections[mission_id]:
            try:
                await connection.send_json(message)
            except:
                pass


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
