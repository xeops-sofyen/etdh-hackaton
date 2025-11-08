"""
GeoJSON to Playbook Converter

Converts GeoJSON feature collections into mission playbooks.
Extracts waypoints from Points and LineStrings.
"""

from typing import Dict, Any, List, Tuple
from backend.playbook_parser.schema import MissionPlaybook, Waypoint


def geojson_to_playbook(geojson: Dict[str, Any], mission_id: str = "geojson_mission") -> MissionPlaybook:
    """
    Convert GeoJSON FeatureCollection to mission playbook

    Args:
        geojson: GeoJSON FeatureCollection with Point or LineString features
        mission_id: Unique mission identifier

    Returns:
        MissionPlaybook ready for execution
    """
    waypoints = []

    if geojson.get("type") != "FeatureCollection":
        raise ValueError("Only FeatureCollection type is supported")

    features = geojson.get("features", [])

    # Extract waypoints from Point features
    for feature in features:
        geometry = feature.get("geometry", {})
        geo_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        if geo_type == "Point":
            # GeoJSON format: [longitude, latitude] or [longitude, latitude, altitude]
            # We need: [latitude, longitude] for drone commands
            if len(coordinates) >= 2:
                lon, lat = coordinates[0], coordinates[1]
                
                # Get altitude from properties, coordinate z-value, or default to 100m
                properties = feature.get("properties", {})
                alt = properties.get("altitude") or (coordinates[2] if len(coordinates) >= 3 else None) or 100

                # Create waypoint with altitude from properties
                waypoint = Waypoint(
                    lat=lat,
                    lon=lon,
                    alt=alt,
                    action="photo"  # Take photo at each point
                )
                waypoints.append(waypoint)

        elif geo_type == "LineString":
            # LineString contains ordered waypoints
            properties = feature.get("properties", {})
            for coord in coordinates:
                if len(coord) >= 2:
                    lon, lat = coord[0], coord[1]
                    
                    # Get altitude from properties, coordinate z-value, or default to 100m
                    alt = properties.get("altitude") or (coord[2] if len(coord) >= 3 else None) or 100

                    waypoint = Waypoint(
                        lat=lat,
                        lon=lon,
                        alt=alt,
                        action="photo"
                    )
                    waypoints.append(waypoint)

    # Remove duplicates while preserving order
    seen = set()
    unique_waypoints = []
    for wp in waypoints:
        key = (wp.lat, wp.lon)
        if key not in seen:
            seen.add(key)
            unique_waypoints.append(wp)

    if not unique_waypoints:
        raise ValueError("No valid waypoints found in GeoJSON")

    # Create playbook
    playbook = MissionPlaybook(
        mission_id=mission_id,
        mission_type="patrol",
        description=f"GeoJSON mission with {len(unique_waypoints)} waypoints",
        waypoints=unique_waypoints,
        flight_parameters={
            "altitude_m": 100,
            "speed_mps": 10,
            "pattern": "direct"
        },
        contingencies={
            "low_battery": "return_to_home",
            "gps_loss": "hover_and_alert",
            "obstacle_detected": "reroute",
            "communication_loss": "return_to_home"
        },
        auto_execute=False,
        max_duration_min=30
    )

    return playbook


def validate_geojson(geojson: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate GeoJSON structure

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(geojson, dict):
        return False, "GeoJSON must be a dictionary"

    if geojson.get("type") != "FeatureCollection":
        return False, "Only FeatureCollection type is supported"

    features = geojson.get("features")
    if not features:
        return False, "No features found in FeatureCollection"

    if not isinstance(features, list):
        return False, "Features must be a list"

    # Check for at least one Point or LineString
    has_valid_geometry = False
    for feature in features:
        geometry = feature.get("geometry", {})
        geo_type = geometry.get("type")
        if geo_type in ["Point", "LineString"]:
            has_valid_geometry = True
            break

    if not has_valid_geometry:
        return False, "No Point or LineString geometries found"

    return True, ""


if __name__ == "__main__":
    # Example usage
    sample_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [22.676025735635818, 49.58809075009475],
                    "type": "Point"
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [22.650759135512743, 49.57580919435844],
                    "type": "Point"
                }
            }
        ]
    }

    playbook = geojson_to_playbook(sample_geojson)
    print(f"Mission: {playbook.mission_id}")
    print(f"Waypoints: {len(playbook.waypoints)}")
    for i, wp in enumerate(playbook.waypoints):
        print(f"  {i+1}. ({wp.lat:.6f}, {wp.lon:.6f}) @ {wp.alt}m")
