"""
Custom Tools for ADK Agent

Function tools that the ADK agent can use to plan drone missions.
These tools help generate waypoints, validate flight zones, and create playbooks.
"""

import math
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .config import SAFETY_CONSTRAINTS


def generate_waypoints(
    center_lat: float,
    center_lon: float,
    pattern: str = "rectangular",
    count: int = 4,
    altitude: float = 50.0,
    radius_m: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Generate GPS waypoints in various patterns.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        pattern: Pattern type (rectangular, circular, grid, line)
        count: Number of waypoints
        altitude: Altitude in meters
        radius_m: Radius/size of pattern in meters

    Returns:
        List of waypoint dictionaries with lat, lon, alt
    """
    waypoints = []

    # Convert radius to degrees (approximate)
    # 1 degree latitude ≈ 111km
    # 1 degree longitude ≈ 111km * cos(latitude)
    lat_per_m = 1 / 111000
    lon_per_m = 1 / (111000 * math.cos(math.radians(center_lat)))

    radius_lat = radius_m * lat_per_m
    radius_lon = radius_m * lon_per_m

    if pattern == "rectangular":
        # Create rectangular pattern
        corners = [
            (center_lat + radius_lat, center_lon - radius_lon),  # NW
            (center_lat + radius_lat, center_lon + radius_lon),  # NE
            (center_lat - radius_lat, center_lon + radius_lon),  # SE
            (center_lat - radius_lat, center_lon - radius_lon),  # SW
        ]
        for lat, lon in corners[:count]:
            waypoints.append({
                "lat": lat,
                "lon": lon,
                "alt": altitude,
                "action": "photo"
            })

    elif pattern == "circular":
        # Create circular pattern
        for i in range(count):
            angle = (2 * math.pi * i) / count
            lat = center_lat + radius_lat * math.cos(angle)
            lon = center_lon + radius_lon * math.sin(angle)
            waypoints.append({
                "lat": lat,
                "lon": lon,
                "alt": altitude,
                "action": "photo"
            })

    elif pattern == "grid":
        # Create grid pattern
        grid_size = int(math.sqrt(count))
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center_lat + (i - grid_size/2) * radius_lat / grid_size * 2
                lon = center_lon + (j - grid_size/2) * radius_lon / grid_size * 2
                waypoints.append({
                    "lat": lat,
                    "lon": lon,
                    "alt": altitude,
                    "action": "photo"
                })

    elif pattern == "line":
        # Create linear pattern
        for i in range(count):
            progress = i / max(count - 1, 1)
            lat = center_lat + (progress - 0.5) * 2 * radius_lat
            lon = center_lon
            waypoints.append({
                "lat": lat,
                "lon": lon,
                "alt": altitude,
                "action": "photo"
            })

    return waypoints


def validate_flight_zone(waypoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check if flight area is safe and within constraints.

    Args:
        waypoints: List of waypoints to validate

    Returns:
        Validation result with status, warnings, and suggestions
    """
    warnings = []
    is_valid = True

    if not waypoints:
        return {
            "is_valid": False,
            "warnings": ["No waypoints provided"],
            "suggestions": ["Add at least one waypoint"]
        }

    # Check altitude constraints
    for i, wp in enumerate(waypoints):
        alt = wp.get("alt", 0)
        if alt > SAFETY_CONSTRAINTS['max_altitude_m']:
            warnings.append(f"Waypoint {i+1}: Altitude {alt}m exceeds maximum {SAFETY_CONSTRAINTS['max_altitude_m']}m")
            is_valid = False
        elif alt < SAFETY_CONSTRAINTS['min_altitude_m']:
            warnings.append(f"Waypoint {i+1}: Altitude {alt}m below minimum {SAFETY_CONSTRAINTS['min_altitude_m']}m")
            is_valid = False

    # Check coordinate validity
    for i, wp in enumerate(waypoints):
        lat = wp.get("lat")
        lon = wp.get("lon")
        if lat is None or lon is None:
            warnings.append(f"Waypoint {i+1}: Missing coordinates")
            is_valid = False
        elif lat < -90 or lat > 90:
            warnings.append(f"Waypoint {i+1}: Invalid latitude {lat}")
            is_valid = False
        elif lon < -180 or lon > 180:
            warnings.append(f"Waypoint {i+1}: Invalid longitude {lon}")
            is_valid = False

    # Calculate total distance
    total_distance = 0
    for i in range(len(waypoints) - 1):
        dist = calculate_distance_haversine(
            waypoints[i]["lat"], waypoints[i]["lon"],
            waypoints[i+1]["lat"], waypoints[i+1]["lon"]
        )
        total_distance += dist

    suggestions = []
    if total_distance > 10000:  # 10km
        suggestions.append("Consider breaking mission into smaller segments")

    if not warnings:
        warnings.append("All waypoints are within safe parameters")

    return {
        "is_valid": is_valid,
        "warnings": warnings,
        "suggestions": suggestions,
        "total_distance_m": round(total_distance, 2),
        "waypoint_count": len(waypoints)
    }


def calculate_flight_time(
    waypoints: List[Dict[str, Any]],
    speed_mps: float = 10.0,
    hover_time_per_action_s: float = 5.0
) -> Dict[str, Any]:
    """
    Estimate mission duration based on waypoints and speed.

    Args:
        waypoints: List of waypoints
        speed_mps: Flight speed in meters per second
        hover_time_per_action_s: Time to execute actions (photo, video, etc.)

    Returns:
        Flight time estimation with breakdown
    """
    if not waypoints:
        return {
            "total_time_s": 0,
            "flight_time_s": 0,
            "action_time_s": 0
        }

    # Calculate flight time between waypoints
    flight_time = 0
    for i in range(len(waypoints) - 1):
        dist = calculate_distance_haversine(
            waypoints[i]["lat"], waypoints[i]["lon"],
            waypoints[i+1]["lat"], waypoints[i+1]["lon"]
        )
        flight_time += dist / speed_mps

    # Add hover time for actions
    action_count = sum(1 for wp in waypoints if wp.get("action"))
    action_time = action_count * hover_time_per_action_s

    # Add takeoff and landing time
    takeoff_landing_time = 30  # 30 seconds total

    total_time = flight_time + action_time + takeoff_landing_time

    return {
        "total_time_s": round(total_time, 1),
        "total_time_min": round(total_time / 60, 2),
        "flight_time_s": round(flight_time, 1),
        "action_time_s": round(action_time, 1),
        "takeoff_landing_time_s": takeoff_landing_time,
        "speed_mps": speed_mps
    }


def create_mission_playbook(
    mission_id: str,
    mission_type: str,
    description: str,
    waypoints: List[Dict[str, Any]],
    altitude_m: float = 50.0,
    speed_mps: float = 10.0,
    pattern: str = "direct"
) -> Dict[str, Any]:
    """
    Generate complete mission playbook JSON.

    Args:
        mission_id: Unique mission identifier
        mission_type: Type of mission (patrol, reconnaissance, etc.)
        description: Mission description
        waypoints: List of waypoints
        altitude_m: Default altitude
        speed_mps: Flight speed
        pattern: Flight pattern

    Returns:
        Complete mission playbook dictionary
    """
    # Validate inputs
    if not waypoints:
        raise ValueError("At least one waypoint is required")

    # Ensure altitude is within safety bounds
    altitude_m = max(SAFETY_CONSTRAINTS['min_altitude_m'],
                    min(altitude_m, SAFETY_CONSTRAINTS['max_altitude_m']))

    # Ensure speed is within safety bounds
    speed_mps = max(SAFETY_CONSTRAINTS['min_speed_mps'],
                   min(speed_mps, SAFETY_CONSTRAINTS['max_speed_mps']))

    # Convert waypoints to proper format
    formatted_waypoints = []
    for wp in waypoints:
        formatted_wp = {
            "lat": wp["lat"],
            "lon": wp["lon"],
            "alt": wp.get("alt", altitude_m),
            "action": wp.get("action", None)
        }
        if "hover_duration_sec" in wp:
            formatted_wp["hover_duration_sec"] = wp["hover_duration_sec"]
        formatted_waypoints.append(formatted_wp)

    # Calculate flight time
    time_estimate = calculate_flight_time(formatted_waypoints, speed_mps)

    # Build playbook
    playbook = {
        "mission_id": mission_id,
        "mission_type": mission_type,
        "description": description,
        "waypoints": formatted_waypoints,
        "flight_parameters": {
            "altitude_m": altitude_m,
            "speed_mps": speed_mps,
            "pattern": pattern,
            "heading_mode": "auto"
        },
        "camera_settings": {
            "mode": "photo",
            "resolution": "4K",
            "gimbal_tilt": -45,
            "auto_capture_interval_sec": None
        },
        "contingencies": {
            "low_battery": "return_to_home",
            "gps_loss": "hover_and_alert",
            "obstacle_detected": "reroute",
            "communication_loss": "return_to_home"
        },
        "auto_execute": False,
        "max_duration_min": min(time_estimate["total_time_min"] * 1.5,
                               SAFETY_CONSTRAINTS['max_mission_duration_min'])
    }

    return playbook


def get_weather_info(location: str) -> Dict[str, Any]:
    """
    Get weather information for mission location.
    Currently returns mock data - can be integrated with real weather API.

    Args:
        location: Location string (lat,lon or place name)

    Returns:
        Weather information
    """
    # Mock weather data for now
    return {
        "location": location,
        "conditions": "Clear",
        "temperature_c": 15,
        "wind_speed_mps": 5,
        "wind_direction": "NW",
        "visibility_km": 10,
        "suitable_for_flight": True,
        "warnings": [],
        "timestamp": datetime.utcnow().isoformat()
    }


def calculate_distance_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.

    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate

    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
