"""
Playbook JSON Schema Definition

Defines the structure of mission playbooks that operators create
and that get translated into Olympe commands.
"""

from typing import List, Dict, Optional
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """GPS coordinates"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class AreaOfInterest(BaseModel):
    """Mission area definition"""
    center: Coordinates
    radius_km: float = Field(...,  description="Radius in kilometers")


class Waypoint(BaseModel):
    """Individual waypoint with action"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    alt: float = Field(..., ge=0, le=500, description="Altitude in meters")
    action: Optional[Literal["photo", "video_start", "video_stop", "hover", "scan"]] = None
    hover_duration_sec: Optional[float] = Field(None, ge=0, description="How long to hover")


class FlightParameters(BaseModel):
    """Flight configuration"""
    altitude_m: float = Field(120, ge=10, le=150, description="Default flight altitude")
    speed_mps: float = Field(10, ge=1, le=15, description="Flight speed in m/s")
    pattern: Literal["direct", "grid", "spiral", "perimeter"] = "direct"
    heading_mode: Literal["auto", "fixed", "target_oriented"] = "auto"


class Contingencies(BaseModel):
    """Emergency response rules"""
    low_battery: Literal["return_to_home", "land_immediately", "alert_and_hover"] = "return_to_home"
    gps_loss: Literal["hover_and_alert", "land_immediately", "switch_to_visual"] = "hover_and_alert"
    obstacle_detected: Literal["reroute", "hover", "abort_mission"] = "reroute"
    communication_loss: Literal["continue_mission", "return_to_home", "hover"] = "return_to_home"


class CameraSettings(BaseModel):
    """Camera configuration"""
    mode: Literal["photo", "video", "thermal"] = "photo"
    resolution: str = "4K"
    gimbal_tilt: float = Field(-90, ge=-90, le=0, description="Gimbal tilt angle")
    auto_capture_interval_sec: Optional[float] = None


class MissionPlaybook(BaseModel):
    """
    Complete mission definition

    This is what the conversational interface generates
    and what your Olympe translator consumes.
    """
    mission_id: str = Field(..., description="Unique mission identifier")
    mission_type: Literal["patrol", "reconnaissance", "tracking", "search", "delivery"]
    description: str = Field(..., description="Human-readable mission description")

    # Mission area
    area_of_interest: Optional[AreaOfInterest] = None

    # Flight plan
    waypoints: List[Waypoint] = Field(..., min_items=1, description="Ordered list of waypoints")
    flight_parameters: FlightParameters = Field(default_factory=FlightParameters)

    # Camera
    camera_settings: CameraSettings = Field(default_factory=CameraSettings)

    # Safety
    contingencies: Contingencies = Field(default_factory=Contingencies)

    # Execution
    auto_execute: bool = Field(True, description="Execute immediately or wait for approval")
    max_duration_min: float = Field(30, ge=5, le=60, description="Max mission duration")

    class Config:
        json_schema_extra = {
            "example": {
                "mission_id": "coastal_patrol_001",
                "mission_type": "patrol",
                "description": "Patrol German North Sea coast near Wilhelmshaven",
                "area_of_interest": {
                    "center": {"lat": 53.5, "lon": 8.1},
                    "radius_km": 5
                },
                "waypoints": [
                    {"lat": 53.5, "lon": 8.0, "alt": 120, "action": "photo"},
                    {"lat": 53.52, "lon": 8.05, "alt": 120, "action": "photo"},
                    {"lat": 53.5, "lon": 8.1, "alt": 120, "action": "hover", "hover_duration_sec": 10}
                ],
                "flight_parameters": {
                    "altitude_m": 120,
                    "speed_mps": 10,
                    "pattern": "direct"
                },
                "camera_settings": {
                    "mode": "photo",
                    "gimbal_tilt": -45
                },
                "contingencies": {
                    "low_battery": "return_to_home",
                    "gps_loss": "hover_and_alert"
                }
            }
        }
