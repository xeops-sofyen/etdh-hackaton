"""
FastAPI Server for Heimdall Mission Control - REALISTIC DEMO MODE

This demo simulates EXACTLY what will happen with Olympe/Sphinx:
- Realistic drone movement following waypoints
- Authentic telemetry (battery drain, GPS, altitude, speed)
- Simulates the OlympeTranslator behavior
- Same WebSocket events as real drone
- Demonstrates the complete integration for Dmytro

This shows what the frontend will see when we integrate Olympe/Sphinx!
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
import math
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Heimdall Mission Control API - REALISTIC DEMO",
    description="AI-Powered Autonomous Drone Mission System (Realistic Olympe Simulation)",
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
# API MODELS (Same as real backend)
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
# REALISTIC OLYMPE DRONE SIMULATOR
# ============================================================================

class RealisticDroneSimulator:
    """
    Simulates EXACTLY what Olympe/Sphinx would do

    Mimics the behavior of:
    - OlympeTranslator.translate_and_execute()
    - Real drone physics and telemetry
    """

    def __init__(self):
        self.current_mission: Optional[Dict] = None
        self.state = {
            "mission_id": None,
            "status": "idle",  # idle, takeoff, en_route, hovering, landing, completed
            "position": {"lat": 0, "lon": 0, "alt": 0},
            "battery": 100.0,
            "speed": 0.0,
            "heading": 0.0,
            "current_waypoint": -1,
            "total_waypoints": 0,
            "gps_satellites": 12,
            "signal_strength": 100,
            "temperature": 25.0,
            "timestamp": datetime.now().isoformat()
        }
        self.takeoff_altitude = 0
        self.mission_start_time = None

    def start_mission(self, playbook: Dict):
        """Start a mission (mimics OlympeTranslator.translate_and_execute)"""
        self.current_mission = playbook
        self.state["mission_id"] = playbook["mission_id"]
        self.state["status"] = "takeoff"
        self.state["total_waypoints"] = len(playbook["waypoints"])
        self.state["current_waypoint"] = -1
        self.mission_start_time = datetime.now()

        # Set starting position (first waypoint or default)
        if playbook["waypoints"]:
            first_wp = playbook["waypoints"][0]
            self.state["position"] = {
                "lat": first_wp["lat"],
                "lon": first_wp["lon"],
                "alt": 0  # Start on ground
            }
            self.takeoff_altitude = first_wp.get("alt", 120)

        logger.info(f"🚀 Mission started: {playbook['mission_id']}")
        logger.info(f"   Type: {playbook['mission_type']}")
        logger.info(f"   Waypoints: {len(playbook['waypoints'])}")
        logger.info(f"   Target altitude: {self.takeoff_altitude}m")

    def abort_mission(self):
        """Emergency abort (mimics OlympeTranslator._emergency_land)"""
        logger.warning("⚠️  EMERGENCY ABORT - Landing immediately")
        self.state["status"] = "landing"
        self.state["speed"] = 0

    async def simulate_step(self):
        """
        Simulate one time step of drone behavior

        This mimics what Olympe SDK does:
        1. Takeoff sequence
        2. Navigate to waypoints
        3. Execute actions at waypoints
        4. Landing sequence
        """
        if self.state["status"] == "idle":
            return

        # Update timestamp
        self.state["timestamp"] = datetime.now().isoformat()

        # Battery drain (realistic consumption)
        if self.state["status"] != "idle":
            # Drain faster when moving
            drain_rate = 0.15 if self.state["speed"] > 0 else 0.05
            self.state["battery"] = max(0, self.state["battery"] - drain_rate)

        # Temperature variation
        self.state["temperature"] = 25 + random.uniform(-2, 2)

        # GPS satellites (realistic variation)
        self.state["gps_satellites"] = max(8, min(15, self.state["gps_satellites"] + random.randint(-1, 1)))

        # --- TAKEOFF PHASE ---
        if self.state["status"] == "takeoff":
            # Simulate gradual altitude increase (like real Olympe TakeOff())
            target_alt = self.takeoff_altitude
            current_alt = self.state["position"]["alt"]

            if current_alt < target_alt:
                # Climb at 2 m/s (realistic climb rate)
                self.state["position"]["alt"] = min(target_alt, current_alt + 2)
                self.state["speed"] = 2.0
                logger.info(f"   ✈️  Climbing... {self.state['position']['alt']:.1f}m / {target_alt}m")
            else:
                # Reached altitude, start waypoint navigation
                logger.info(f"   ✅ Takeoff complete at {target_alt}m")
                self.state["status"] = "en_route"
                self.state["current_waypoint"] = 0
                self.state["speed"] = 0

        # --- WAYPOINT NAVIGATION ---
        elif self.state["status"] == "en_route":
            if not self.current_mission or self.state["current_waypoint"] >= len(self.current_mission["waypoints"]):
                # All waypoints completed, land
                logger.info("   🏠 All waypoints completed, landing...")
                self.state["status"] = "landing"
                return

            # Get target waypoint
            waypoint = self.current_mission["waypoints"][self.state["current_waypoint"]]
            target_lat = waypoint["lat"]
            target_lon = waypoint["lon"]
            target_alt = waypoint["alt"]

            current_lat = self.state["position"]["lat"]
            current_lon = self.state["position"]["lon"]
            current_alt = self.state["position"]["alt"]

            # Calculate distance to target (in degrees, rough approximation)
            distance = math.sqrt(
                (target_lat - current_lat)**2 +
                (target_lon - current_lon)**2
            )

            # Simulate Olympe moveTo() behavior
            if distance > 0.0001:  # Not yet at waypoint
                # Move towards waypoint at realistic speed (10 m/s ≈ 0.0001 deg/s)
                speed_mps = self.current_mission.get("flight_parameters", {}).get("speed_mps", 10)
                move_distance = speed_mps * 0.00001  # Convert to degrees

                # Interpolate position
                factor = min(1.0, move_distance / distance)
                self.state["position"]["lat"] += (target_lat - current_lat) * factor
                self.state["position"]["lon"] += (target_lon - current_lon) * factor
                self.state["position"]["alt"] = target_alt  # Match altitude

                # Update heading (bearing to target)
                self.state["heading"] = math.degrees(math.atan2(
                    target_lon - current_lon,
                    target_lat - current_lat
                )) % 360

                self.state["speed"] = speed_mps

            else:
                # Reached waypoint!
                logger.info(f"   ✅ Reached waypoint {self.state['current_waypoint'] + 1}/{len(self.current_mission['waypoints'])}: ({target_lat:.6f}, {target_lon:.6f})")

                # Execute action at waypoint (if any)
                action = waypoint.get("action")
                if action:
                    logger.info(f"   🎬 Executing action: {action}")
                    self.state["status"] = "hovering"
                    self.state["speed"] = 0
                    # Will transition back to en_route after hover
                else:
                    # No action, move to next waypoint
                    self.state["current_waypoint"] += 1

        # --- HOVERING (Action Execution) ---
        elif self.state["status"] == "hovering":
            # Simulate hover duration
            waypoint = self.current_mission["waypoints"][self.state["current_waypoint"]]
            hover_duration = waypoint.get("hover_duration_sec", 3)

            # Simulate hover (in real demo, this would pause for hover_duration)
            # For simplicity, we transition immediately in next step
            await asyncio.sleep(hover_duration)

            logger.info(f"   ⏸️  Hover complete")
            self.state["current_waypoint"] += 1
            self.state["status"] = "en_route"

        # --- LANDING PHASE ---
        elif self.state["status"] == "landing":
            current_alt = self.state["position"]["alt"]

            if current_alt > 0:
                # Descend at 1 m/s (realistic descent rate)
                self.state["position"]["alt"] = max(0, current_alt - 1)
                self.state["speed"] = 1.0
                logger.info(f"   🛬 Landing... {self.state['position']['alt']:.1f}m")
            else:
                # Landed!
                logger.info("   ✅ Landed safely - Mission complete")
                self.state["status"] = "completed"
                self.state["speed"] = 0

    def get_state(self) -> Dict:
        """Get current drone state (for WebSocket updates)"""
        return self.state.copy()

# Global drone simulator instance
drone_simulator = RealisticDroneSimulator()

# ============================================================================
# ENDPOINTS (Same as real backend)
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Heimdall Mission Control - REALISTIC DEMO MODE",
        "status": "operational",
        "version": "1.0.0",
        "mode": "realistic_demo (simulates Olympe/Sphinx behavior)"
    }

@app.get("/status")
async def get_status():
    """Get current drone status"""
    return drone_simulator.get_state()

@app.post("/mission/execute")
async def execute_mission(request: MissionExecuteRequest):
    """Execute a mission playbook (REALISTIC DEMO MODE)"""
    logger.info(f"🚁 Received mission: {request.playbook.mission_id}")
    logger.info(f"   Type: {request.playbook.mission_type}")
    logger.info(f"   Waypoints: {len(request.playbook.waypoints)}")
    logger.info(f"   Description: {request.playbook.description}")

    if request.simulate:
        logger.info("   Mode: SIMULATION (validation only)")
        # TODO: Add PlaybookValidator from translator.py
        return {
            "status": "simulation_success",
            "mission_id": request.playbook.mission_id,
            "message": "Playbook is valid (Demo mode)"
        }
    else:
        logger.info("   Mode: EXECUTION (Realistic Olympe simulation)")
        drone_simulator.start_mission(request.playbook.dict())

        return {
            "status": "started",
            "mission_id": request.playbook.mission_id,
            "message": "Mission started in realistic demo mode"
        }

@app.post("/mission/abort")
async def abort_mission():
    """Emergency abort"""
    logger.warning("⚠️  ABORT requested via API")
    drone_simulator.abort_mission()
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
# WEBSOCKET - REALISTIC TELEMETRY STREAMING
# ============================================================================

active_connections: Dict[str, List[WebSocket]] = {}

@app.websocket("/ws/mission/{mission_id}")
async def websocket_mission_updates(websocket: WebSocket, mission_id: str):
    """
    WebSocket for real-time updates (REALISTIC DEMO MODE)

    Streams telemetry EXACTLY like Olympe would:
    - Position updates every 1 second
    - Waypoint reached events
    - Mission completion events
    - Realistic drone physics
    """
    await websocket.accept()

    if mission_id not in active_connections:
        active_connections[mission_id] = []
    active_connections[mission_id].append(websocket)

    logger.info(f"✅ WebSocket connected for mission {mission_id}")

    try:
        # Send initial status
        state = drone_simulator.get_state()
        await websocket.send_json({
            "type": "connected",
            "data": state
        })

        # Stream telemetry updates
        previous_waypoint = -1
        previous_status = None

        while True:
            await asyncio.sleep(1)  # 1 Hz update rate (like Olympe)

            # Simulate one step
            await drone_simulator.simulate_step()

            # Get current state
            state = drone_simulator.get_state()

            # Check for waypoint changes
            if state["current_waypoint"] != previous_waypoint and state["current_waypoint"] >= 0:
                await websocket.send_json({
                    "type": "waypoint_reached",
                    "data": {
                        "waypoint_index": state["current_waypoint"],
                        "total_waypoints": state["total_waypoints"]
                    }
                })
                previous_waypoint = state["current_waypoint"]

            # Check for status changes
            if state["status"] != previous_status:
                await websocket.send_json({
                    "type": "status_change",
                    "data": {
                        "old_status": previous_status,
                        "new_status": state["status"]
                    }
                })
                previous_status = state["status"]

            # Send position update
            await websocket.send_json({
                "type": "position_update",
                "data": state
            })

            # Check for mission completion
            if state["status"] == "completed":
                await websocket.send_json({
                    "type": "mission_complete",
                    "data": state
                })
                logger.info(f"✅ Mission {mission_id} completed")
                break

            # Check for low battery
            if state["battery"] < 20:
                await websocket.send_json({
                    "type": "warning",
                    "data": {
                        "level": "warning",
                        "message": f"Low battery: {state['battery']:.1f}%"
                    }
                })

            # Auto-abort if battery critical
            if state["battery"] < 10:
                await websocket.send_json({
                    "type": "emergency",
                    "data": {
                        "level": "critical",
                        "message": "Critical battery - Auto landing"
                    }
                })
                drone_simulator.abort_mission()

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
    print("=" * 80)
    print("🚁 Heimdall Backend - REALISTIC DEMO MODE")
    print("=" * 80)
    print("Mode: Realistic Olympe/Sphinx Simulation")
    print("This demo shows EXACTLY what will happen with real Olympe SDK!")
    print("")
    print("Features:")
    print("  ✅ Realistic drone physics (takeoff, navigation, landing)")
    print("  ✅ Authentic telemetry (battery, GPS, speed, altitude)")
    print("  ✅ WebSocket streaming (1 Hz updates)")
    print("  ✅ Waypoint navigation with actions")
    print("  ✅ Emergency abort handling")
    print("")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
