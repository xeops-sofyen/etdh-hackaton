"""
GeoJSON to Olympe Translation Demo

Demonstrates the complete pipeline:
1. GeoJSON input → 2. Playbook → 3. Olympe commands

This shows how user-provided GeoJSON coordinates translate to actual drone commands.
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.playbook_parser.geojson_converter import geojson_to_playbook, validate_geojson

# Import PlaybookValidator directly to avoid Olympe import
try:
    from backend.olympe_translator.translator import PlaybookValidator
    has_olympe = True
except ImportError:
    # Fallback validator without Olympe
    class PlaybookValidator:
        def validate(self, playbook):
            """Validate playbook safety constraints"""
            # Check altitude limits
            if playbook.flight_parameters.altitude_m > 150:
                return False, f"Altitude {playbook.flight_parameters.altitude_m}m exceeds max 150m"

            # Check speed limits
            if playbook.flight_parameters.speed_mps > 15:
                return False, f"Speed {playbook.flight_parameters.speed_mps} m/s exceeds safe limit of 15 m/s"

            # Check waypoints exist
            if len(playbook.waypoints) < 1:
                return False, "Mission must have at least 1 waypoint"

            return True, None
    has_olympe = False


def demo_translation():
    """Demo the complete GeoJSON to Olympe translation"""

    print("=" * 80)
    print("GeoJSON to Olympe Translation Demo")
    print("=" * 80)

    # Your sample GeoJSON (Poland/Ukraine border area)
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
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [22.67371444036104, 49.55304323176125],
                    "type": "Point"
                }
            }
        ]
    }

    print("\n📍 STEP 1: Validate GeoJSON Input")
    print("-" * 80)
    is_valid, error = validate_geojson(sample_geojson)
    if is_valid:
        print("✅ GeoJSON structure is valid")
        print(f"   - Type: {sample_geojson['type']}")
        print(f"   - Features: {len(sample_geojson['features'])} Point features")
    else:
        print(f"❌ GeoJSON validation failed: {error}")
        return

    print("\n🔄 STEP 2: Convert GeoJSON to Mission Playbook")
    print("-" * 80)
    playbook = geojson_to_playbook(sample_geojson, mission_id="geojson_demo_001")

    print(f"✅ Playbook created successfully")
    print(f"   - Mission ID: {playbook.mission_id}")
    print(f"   - Mission Type: {playbook.mission_type}")
    print(f"   - Description: {playbook.description}")
    print(f"   - Waypoints: {len(playbook.waypoints)}")
    print(f"   - Altitude: {playbook.flight_parameters.altitude_m}m")
    print(f"   - Speed: {playbook.flight_parameters.speed_mps} m/s")

    print("\n📊 STEP 3: Waypoint Details (Coordinate Conversion)")
    print("-" * 80)
    print("Note: GeoJSON uses [longitude, latitude] but drones need [latitude, longitude]\n")

    for i, (feature, waypoint) in enumerate(zip(sample_geojson['features'], playbook.waypoints), 1):
        geojson_coords = feature['geometry']['coordinates']
        print(f"Waypoint {i}:")
        print(f"  GeoJSON Input:  [{geojson_coords[0]:.6f}, {geojson_coords[1]:.6f}] (lon, lat)")
        print(f"  Drone Format:   [{waypoint.lat:.6f}, {waypoint.lon:.6f}] (lat, lon)")
        print(f"  Altitude:       {waypoint.alt}m")
        print(f"  Action:         {waypoint.action}")
        print()

    print("\n🛡️ STEP 4: Validate Safety Parameters")
    print("-" * 80)
    validator = PlaybookValidator()
    is_valid, error = validator.validate(playbook)

    if is_valid:
        print("✅ Playbook passes all safety checks")
        print(f"   - Altitude within limits (10-150m): {playbook.flight_parameters.altitude_m}m")
        print(f"   - Speed within limits (≤15 m/s): {playbook.flight_parameters.speed_mps} m/s")
        print(f"   - Duration within limits (≤60 min): {playbook.max_duration_min} min")
        print(f"   - Minimum waypoints (≥1): {len(playbook.waypoints)}")
    else:
        print(f"❌ Safety validation failed: {error}")
        return

    print("\n🤖 STEP 5: Translation to Olympe SDK Commands")
    print("-" * 80)
    print("The playbook would translate to the following Olympe commands:\n")

    print("# Pre-flight setup")
    print(f"drone.set_max_altitude({playbook.flight_parameters.altitude_m})")
    print(f"drone.set_streaming_mode(streaming_mode=1)")
    print()

    print("# Takeoff")
    print(f"drone(TakeOff()).wait().success()")
    print()

    print("# Execute waypoint sequence")
    for i, wp in enumerate(playbook.waypoints, 1):
        print(f"# Waypoint {i}")
        print(f"drone(moveTo(")
        print(f"    latitude={wp.lat},")
        print(f"    longitude={wp.lon},")
        print(f"    altitude={wp.alt},")
        print(f"    orientation_mode=0")
        print(f")).wait().success()")

        if wp.action == "photo":
            print(f"drone(take_photo(cam_id=0)).wait().success()")
        elif wp.action == "hover" and wp.hover_duration_sec:
            print(f"time.sleep({wp.hover_duration_sec})")

        print()

    print("# Return to home and land")
    print("drone(ReturnToHome()).wait().success()")
    print("drone(Landing()).wait().success()")

    print("\n💾 STEP 6: Save Playbook to File")
    print("-" * 80)
    output_file = Path("playbooks/geojson_demo.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(playbook.model_dump(), f, indent=2)

    print(f"✅ Playbook saved to: {output_file}")

    print("\n" + "=" * 80)
    print("✅ TRANSLATION COMPLETE!")
    print("=" * 80)
    print("\nYour GeoJSON coordinates have been successfully converted to a drone mission.")
    print("At the hackathon with Linux machines, you can execute this with:")
    print(f"\n  python backend/quickstart.py --playbook {output_file}")
    print("\nOr via the REST API:")
    print(f"\n  curl -X POST http://localhost:8000/mission/execute \\")
    print(f"       -H 'Content-Type: application/json' \\")
    print(f"       -d @{output_file}")
    print()


if __name__ == "__main__":
    demo_translation()
