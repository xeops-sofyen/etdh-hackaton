"""
Playbook → Olympe Command Translator

YOUR CORE COMPONENT for the hackathon.

Translates high-level mission playbooks into executable Olympe SDK commands.
"""

import olympe
from olympe.messages.ardrone3.Piloting import (
    TakeOff, Landing, moveTo, moveBy, Circle, PCMD
)
from olympe.messages.ardrone3.PilotingSettings import MaxTilt
from olympe.messages.camera import (
    set_camera_mode, take_photo, start_recording, stop_recording
)
from olympe.messages.gimbal import set_target

from typing import List, Dict, Any, Optional
import logging
import time

from backend.playbook_parser.schema import MissionPlaybook, Waypoint, CameraSettings

logger = logging.getLogger(__name__)


class OlympeTranslator:
    """
    Translates mission playbooks into Olympe commands

    This is the bridge between high-level operator intent
    and low-level drone control.
    """

    def __init__(self, drone_ip: str = "10.202.0.1"):
        """
        Initialize translator with drone connection

        Args:
            drone_ip: IP address of physical drone or simulator
        """
        self.drone_ip = drone_ip
        self.drone: Optional[olympe.Drone] = None
        self.current_mission: Optional[MissionPlaybook] = None
        self.telemetry_callback = None

    def connect(self) -> bool:
        """Connect to drone"""
        try:
            logger.info(f"Connecting to drone at {self.drone_ip}...")
            self.drone = olympe.Drone(self.drone_ip)
            self.drone.connect()
            logger.info("✅ Connected to drone")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from drone"""
        if self.drone:
            self.drone.disconnect()
            logger.info("Disconnected from drone")

    def translate_and_execute(self, playbook: MissionPlaybook) -> Dict[str, Any]:
        """
        Main translation method

        Takes a playbook and executes it on the drone

        Args:
            playbook: Mission playbook to execute

        Returns:
            Execution result with telemetry and status
        """
        self.current_mission = playbook
        logger.info(f"🚀 Executing mission: {playbook.mission_id}")
        logger.info(f"   Description: {playbook.description}")

        try:
            # 1. Pre-flight setup
            # self._setup_flight_parameters(playbook) # TODO disabled until fix is found
            # Camera configuration disabled - focusing on GPS navigation only
            # self._configure_camera(playbook.camera_settings)

            # 1. Takeoff
            logger.info("📍 Taking off...")
            self._execute_takeoff(playbook.flight_parameters.altitude_m)

            # 3. Execute waypoint sequence
            logger.info(f"🗺️  Executing {len(playbook.waypoints)} waypoints")
            for idx, waypoint in enumerate(playbook.waypoints):
                logger.info(f"   Waypoint {idx+1}/{len(playbook.waypoints)}: {waypoint}")
                self._execute_waypoint(waypoint)

            # 4. Return to home and land
            logger.info("🏠 Returning to home")
            self._execute_landing()

            logger.info("✅ Mission completed successfully")
            return {
                "status": "success",
                "mission_id": playbook.mission_id,
                "waypoints_completed": len(playbook.waypoints)
            }

        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown error (timeout or assertion failure)"
            logger.error(f"❌ Mission failed: {error_msg}")
            logger.exception("Full exception traceback:")
            self._emergency_land()
            return {
                "status": "failed",
                "mission_id": playbook.mission_id,
                "error": error_msg
            }

    def _setup_flight_parameters(self, playbook: MissionPlaybook):
        """Configure drone flight parameters"""
        params = playbook.flight_parameters

        # Set max tilt (affects max speed)
        if params.speed_mps > 10:
            max_tilt = 20  # degrees
        else:
            max_tilt = 10

        logger.info(f"⚙️  Setting max tilt to {max_tilt}°...")
        result = self.drone(MaxTilt(max_tilt)).wait(_timeout=5)
        if not result.success():
            logger.warning(f"⚠️  Max tilt configuration failed, using default drone settings")
        else:
            logger.info(f"✅ Max tilt set to {max_tilt}°")

    def _configure_camera(self, settings: CameraSettings):
        """Configure camera settings"""
        # Set camera mode
        if settings.mode == "photo":
            mode = set_camera_mode.mode.photo
        elif settings.mode == "video":
            mode = set_camera_mode.mode.recording
        else:
            mode = set_camera_mode.mode.photo  # default

        logger.info(f"📷 Setting camera mode to {settings.mode}...")
        result = self.drone(set_camera_mode(cam_id=0, value=mode)).wait(_timeout=5)
        if not result.success():
            logger.warning(f"⚠️  Camera mode configuration failed, continuing anyway...")
        else:
            logger.info(f"✅ Camera mode set to {settings.mode}")

        # Set gimbal tilt
        logger.info(f"📷 Setting gimbal tilt to {settings.gimbal_tilt}°...")
        result = self.drone(set_target(
            gimbal_id=0,
            control_mode="position",
            yaw_frame_of_reference="none",
            yaw=0.0,
            pitch_frame_of_reference="absolute",
            pitch=settings.gimbal_tilt,
            roll_frame_of_reference="none",
            roll=0.0
        )).wait(_timeout=5)

        if not result.success():
            logger.warning(f"⚠️  Gimbal configuration failed, continuing anyway...")
        else:
            logger.info(f"✅ Gimbal tilt set to {settings.gimbal_tilt}°")

        logger.info(f"📷 Camera configuration complete")

    def _execute_takeoff(self, target_altitude: float):
        """Execute takeoff to specified altitude"""
        assert self.drone(TakeOff()).wait().success()

        # Wait to reach altitude
        time.sleep(5)  # Basic wait (should use telemetry in production)
        logger.info(f"✈️  Reached altitude {target_altitude}m")

    def _execute_waypoint(self, waypoint: Waypoint):
        """
        Translate and execute a single waypoint

        This is the core translation logic:
        Waypoint JSON → Olympe moveTo() command
        """
        # Navigate to waypoint
        assert self.drone(moveTo(
            latitude=waypoint.lat,
            longitude=waypoint.lon,
            altitude=waypoint.alt,
            orientation_mode=0,  # 0 = heading to target, 1 = keep current heading
            heading=0.0, #mandatory parameter
            max_horizontal_speed=10.0,
            max_vertical_speed=2.0,
            max_yaw_rotation_speed=45.0
        )).wait().success()

        logger.info(f"   ✅ Reached waypoint: ({waypoint.lat}, {waypoint.lon})")

        # Actions at waypoints disabled - focusing on GPS navigation only
        # if waypoint.action:
        #     self._execute_action(waypoint)

    def _execute_action(self, waypoint: Waypoint):
        """Execute action at waypoint (photo, video, hover, etc.)"""
        action = waypoint.action

        if action == "photo":
            logger.info("   📸 Taking photo")
            assert self.drone(take_photo(cam_id=0)).wait().success()
            time.sleep(1)  # Wait for capture

        elif action == "video_start":
            logger.info("   🎥 Starting video recording")
            assert self.drone(start_recording(cam_id=0)).wait().success()

        elif action == "video_stop":
            logger.info("   ⏹️  Stopping video recording")
            assert self.drone(stop_recording(cam_id=0)).wait().success()

        elif action == "hover":
            duration = waypoint.hover_duration_sec or 5
            logger.info(f"   ⏸️  Hovering for {duration}s")
            time.sleep(duration)

        elif action == "scan":
            logger.info("   🔄 Performing 360° scan")
            self._execute_360_scan()

    def _execute_360_scan(self):
        """Rotate 360° to scan surroundings"""
        # Circle command for 360° rotation
        assert self.drone(Circle(direction=0)).wait(timeout=30).success()

    def _execute_landing(self):
        """Execute landing sequence"""
        assert self.drone(Landing()).wait().success()
        logger.info("🛬 Landed safely")

    def _emergency_land(self):
        """Emergency landing in case of error"""
        try:
            logger.warning("⚠️  EMERGENCY LANDING")
            assert self.drone(Landing()).wait().success()
        except Exception as e:
            logger.error(f"Emergency landing failed: {e}")

    def get_telemetry(self) -> Dict[str, Any]:
        """Get current drone telemetry"""
        if not self.drone:
            return {}

        # Extract telemetry from Olympe
        # (Simplified - in production you'd subscribe to telemetry streams)
        return {
            "connected": self.drone.connection_state(),
            "battery": "unknown",  # Would query battery state
            "gps": "unknown",  # Would query GPS position
            "altitude": "unknown"  # Would query altitude
        }


# ============================================================================
# VALIDATION LAYER
# ============================================================================

class PlaybookValidator:
    """
    Validates playbooks before execution

    Safety-first approach: catch issues before they become drone crashes
    """

    @staticmethod
    def validate(playbook: MissionPlaybook) -> tuple[bool, Optional[str]]:
        """
        Validate a playbook for safety and feasibility

        Returns:
            (is_valid, error_message)
        """
        # Check 1: Waypoints within safe range
        for wp in playbook.waypoints:
            if wp.alt > 150:
                return False, f"Waypoint altitude {wp.alt}m exceeds max 150m"
            if wp.alt < 10:
                return False, f"Waypoint altitude {wp.alt}m below min 10m"

        # Check 2: Mission duration reasonable
        if playbook.max_duration_min > 60:
            return False, "Mission duration exceeds 60 minutes"

        # Check 3: At least one waypoint
        if len(playbook.waypoints) < 1:
            return False, "Mission must have at least one waypoint"

        # Check 4: Speed limits
        if playbook.flight_parameters.speed_mps > 15:
            return False, "Speed exceeds safe limit (15 m/s)"

        logger.info("✅ Playbook validation passed")
        return True, None


# ============================================================================
# HELPER: GRID PATTERN GENERATOR
# ============================================================================

def generate_grid_pattern(center_lat: float, center_lon: float,
                         radius_km: float, altitude: float,
                         spacing_m: float = 100) -> List[Waypoint]:
    """
    Generate a grid search pattern

    Useful for area coverage missions like "patrol this zone"
    """
    import math

    waypoints = []

    # Convert radius to degrees (rough approximation)
    radius_deg = radius_km / 111  # 1 degree ≈ 111 km

    # Generate grid
    num_lines = int((2 * radius_km * 1000) / spacing_m)

    for i in range(num_lines):
        offset = -radius_deg + (i * spacing_m / 111000)

        if i % 2 == 0:
            # Left to right
            wp1 = Waypoint(lat=center_lat + offset, lon=center_lon - radius_deg, alt=altitude)
            wp2 = Waypoint(lat=center_lat + offset, lon=center_lon + radius_deg, alt=altitude, action="photo")
        else:
            # Right to left
            wp1 = Waypoint(lat=center_lat + offset, lon=center_lon + radius_deg, alt=altitude)
            wp2 = Waypoint(lat=center_lat + offset, lon=center_lon - radius_deg, alt=altitude, action="photo")

        waypoints.extend([wp1, wp2])

    return waypoints
