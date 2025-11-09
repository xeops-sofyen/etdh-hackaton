"""
Playbook to GeoJSON Converter

Converts mission playbooks to GeoJSON format for map visualization.
Generates Point features for waypoints and LineString for flight path.
"""

from typing import Dict, List, Optional
import math


def playbook_to_geojson(playbook: dict) -> dict:
    """
    Convert a mission playbook to GeoJSON FeatureCollection

    Args:
        playbook: MissionPlaybook dict with waypoints and actions

    Returns:
        GeoJSON FeatureCollection with Points (waypoints) and LineString (flight path)
    """
    features = []
    coordinates = []

    # Extract mission metadata
    mission_id = playbook.get('mission_id', 'unknown')
    mission_type = playbook.get('mission_type', 'unknown')
    flight_params = playbook.get('flight_parameters', {})
    waypoints = playbook.get('waypoints', [])

    # Create Point features for each waypoint/action
    for idx, waypoint in enumerate(waypoints):
        action = waypoint.get('action', 'moveTo')
        lat = waypoint.get('lat')
        lon = waypoint.get('lon')
        alt = waypoint.get('alt', flight_params.get('altitude_m', 0))

        if lat is not None and lon is not None:
            # GeoJSON uses [longitude, latitude] order
            coordinates.append([lon, lat, alt])

            # Create description
            description = f"{action or 'waypoint'} at waypoint {idx}"
            if waypoint.get('hover_duration_sec'):
                description += f" (hover {waypoint['hover_duration_sec']}s)"

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat, alt]
                },
                "properties": {
                    "action": action,
                    "sequence": idx,
                    "altitude_m": alt,
                    "description": description,
                    "duration_s": waypoint.get('hover_duration_sec'),
                    "metadata": {}
                }
            })

    # Create LineString for flight path
    if len(coordinates) > 1:
        # Calculate total distance
        total_distance = sum(
            calculate_distance(coordinates[i], coordinates[i+1])
            for i in range(len(coordinates) - 1)
        )

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "type": "flight_path",
                "speed_mps": flight_params.get('speed_mps'),
                "total_distance_m": round(total_distance, 2),
                "pattern": flight_params.get('pattern')
            }
        })

    # Calculate bounding box
    bounding_box = calculate_bounding_box(coordinates) if coordinates else None

    # Calculate estimated duration
    estimated_duration = estimate_mission_duration(playbook)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def calculate_distance(coord1: List[float], coord2: List[float]) -> float:
    """
    Calculate distance between two coordinates using Haversine formula

    Args:
        coord1: [longitude, latitude, altitude] or [longitude, latitude]
        coord2: [longitude, latitude, altitude] or [longitude, latitude]

    Returns:
        Distance in meters
    """
    lon1, lat1 = coord1[0], coord1[1]
    lon2, lat2 = coord2[0], coord2[1]

    # Convert to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Radius of earth in meters

    return c * r


def calculate_bounding_box(coordinates: List[List[float]]) -> List[List[float]]:
    """
    Calculate bounding box from coordinates

    Args:
        coordinates: List of [longitude, latitude] or [longitude, latitude, altitude]

    Returns:
        [[min_lon, min_lat], [max_lon, max_lat]]
    """
    if not coordinates:
        return None

    lons = [c[0] for c in coordinates]
    lats = [c[1] for c in coordinates]

    return [
        [min(lons), min(lats)],
        [max(lons), max(lats)]
    ]


def estimate_mission_duration(playbook: dict) -> float:
    """
    Estimate total mission duration in seconds

    Args:
        playbook: Mission playbook dictionary

    Returns:
        Estimated duration in seconds
    """
    waypoints = playbook.get('waypoints', [])
    flight_params = playbook.get('flight_parameters', {})
    speed_mps = flight_params.get('speed_mps', 10)

    if len(waypoints) < 2:
        return 60  # Minimum 1 minute

    # Calculate flight time
    total_distance = 0
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i+1]

        # Convert to [lon, lat] for distance calculation
        coord1 = [wp1['lon'], wp1['lat']]
        coord2 = [wp2['lon'], wp2['lat']]

        total_distance += calculate_distance(coord1, coord2)

    flight_time = total_distance / speed_mps

    # Add hover time for actions
    action_time = 0
    for wp in waypoints:
        if wp.get('hover_duration_sec'):
            action_time += wp['hover_duration_sec']
        elif wp.get('action') in ['photo', 'video_start', 'video_stop']:
            action_time += 5  # Default 5 seconds per action

    # Add takeoff and landing time
    takeoff_landing_time = 30

    return round(flight_time + action_time + takeoff_landing_time, 1)


def geojson_to_playbook_waypoints(geojson: dict) -> List[dict]:
    """
    Extract waypoints from GeoJSON (reverse conversion)

    Args:
        geojson: GeoJSON FeatureCollection

    Returns:
        List of waypoint dictionaries
    """
    waypoints = []

    if geojson.get("type") != "FeatureCollection":
        return waypoints

    features = geojson.get("features", [])

    # Extract Point features only (skip LineString)
    for feature in features:
        geometry = feature.get("geometry", {})

        if geometry.get("type") == "Point":
            coordinates = geometry.get("coordinates", [])
            properties = feature.get("properties", {})

            if len(coordinates) >= 2:
                lon, lat = coordinates[0], coordinates[1]
                alt = coordinates[2] if len(coordinates) > 2 else 50

                waypoint = {
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "action": properties.get("action")
                }

                if properties.get("duration_s"):
                    waypoint["hover_duration_sec"] = properties["duration_s"]

                waypoints.append(waypoint)

    return waypoints
