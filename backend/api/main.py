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
import uuid

from backend.playbook_parser.schema import MissionPlaybook
from backend.playbook_parser.geojson_converter import geojson_to_playbook, validate_geojson
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

# In-memory playbook storage (use database in production)
playbook_store: Dict[str, MissionPlaybook] = {}


# ============================================================================
# API MODELS
# ============================================================================

class MissionExecuteRequest(BaseModel):
    """Request to execute a mission"""
    playbook: Optional[MissionPlaybook] = None
    playbook_id: Optional[str] = None
    simulate: bool = False


class NaturalLanguageRequest(BaseModel):
    """Natural language mission command"""
    command: str
    # e.g., "Patrol the coastal area near Wilhelmshaven"


class PlaybookCreateRequest(BaseModel):
    """Request to create a playbook from GeoJSON"""
    geojson: Dict[str, Any]
    mission_id: Optional[str] = None
    mission_type: Optional[str] = "patrol"
    description: Optional[str] = None


class PlaybookIdRequest(BaseModel):
    """Request with playbook ID"""
    playbook_id: str


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


@app.post("/playbook")
async def create_playbook(request: PlaybookCreateRequest):
    """
    Create a playbook from GeoJSON payload

    Accepts a GeoJSON FeatureCollection with Point or LineString features
    and converts it into a mission playbook.

    Returns the created playbook with a unique playbook_id.
    """
    logger.info("Received playbook creation request")

    try:
        # Validate GeoJSON
        is_valid, error_msg = validate_geojson(request.geojson)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid GeoJSON: {error_msg}")

        # Generate unique mission ID if not provided
        mission_id = request.mission_id or f"mission_{uuid.uuid4().hex[:8]}"

        # Convert GeoJSON to playbook
        playbook = geojson_to_playbook(request.geojson, mission_id=mission_id)

        # Override description if provided
        if request.description:
            playbook.description = request.description

        # Override mission type if provided
        if request.mission_type:
            playbook.mission_type = request.mission_type

        # Store playbook
        playbook_store[mission_id] = playbook

        logger.info(f"Created playbook {mission_id} with {len(playbook.waypoints)} waypoints")

        return {
            "status": "created",
            "playbook_id": mission_id,
            "playbook": playbook.model_dump(),
            "waypoint_count": len(playbook.waypoints)
        }

    except ValueError as e:
        logger.error(f"Playbook creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute a mission playbook

    Accepts either:
    - playbook_id: ID of a previously created playbook
    - playbook: Direct playbook JSON (legacy support)
    """
    # Determine which playbook to use
    if request.playbook_id:
        # Use playbook from store
        if request.playbook_id not in playbook_store:
            raise HTTPException(status_code=404, detail=f"Playbook {request.playbook_id} not found")
        playbook = playbook_store[request.playbook_id]
        logger.info(f"Executing stored playbook: {request.playbook_id}")
    elif request.playbook:
        # Use playbook from request (legacy support)
        playbook = request.playbook
        logger.info(f"Executing inline playbook: {playbook.mission_id}")
    else:
        raise HTTPException(status_code=400, detail="Either playbook_id or playbook must be provided")

    try:
        # Execute mission in background (so API returns immediately)
        if request.simulate:
            # Simulation mode: just validate, don't execute
            from backend.olympe_translator.translator import PlaybookValidator
            validator = PlaybookValidator()
            is_valid, error = validator.validate(playbook)

            if not is_valid:
                raise HTTPException(status_code=400, detail=error)

            return {
                "status": "simulation_success",
                "mission_id": playbook.mission_id,
                "message": "Playbook is valid and ready for execution"
            }
        else:
            # Real execution
            result = drone_controller.execute_mission(playbook)
            return result

    except Exception as e:
        logger.error(f"Mission execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mission/abort")
async def abort_mission(request: Optional[PlaybookIdRequest] = None):
    """
    Emergency abort current mission

    Optional: Can specify playbook_id for logging/tracking purposes
    """
    if request and request.playbook_id:
        logger.warning(f"ABORT requested via API for playbook: {request.playbook_id}")
    else:
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
