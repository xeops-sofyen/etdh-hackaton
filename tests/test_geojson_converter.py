"""
Test GeoJSON to Playbook Converter

Tests converting GeoJSON FeatureCollections to mission playbooks.
"""

import pytest
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.playbook_parser.schema import MissionPlaybook
from backend.playbook_parser.geojson_converter import geojson_to_playbook, validate_geojson


class TestGeoJSONConverter:
    """Test GeoJSON conversion functionality"""

    def test_user_sample_geojson(self):
        """Test with user-provided sample (Poland/Ukraine border area)"""
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

        # Convert to playbook
        playbook = geojson_to_playbook(sample_geojson, mission_id="user_test_001")

        # Verify conversion
        assert playbook.mission_id == "user_test_001"
        assert playbook.mission_type == "patrol"
        assert len(playbook.waypoints) == 3

        # Verify coordinate conversion (GeoJSON [lon, lat] → Drone [lat, lon])
        assert playbook.waypoints[0].lat == 49.58809075009475
        assert playbook.waypoints[0].lon == 22.676025735635818
        assert playbook.waypoints[0].alt == 100
        assert playbook.waypoints[0].action == "photo"

        # Verify all waypoints have correct structure
        for wp in playbook.waypoints:
            assert 49.5 <= wp.lat <= 49.6  # Poland/Ukraine border latitude range
            assert 22.6 <= wp.lon <= 22.7  # Poland/Ukraine border longitude range
            assert wp.alt == 100
            assert wp.action == "photo"

        print("\n✅ User sample GeoJSON converted successfully!")
        print(f"Mission: {playbook.mission_id}")
        print(f"Waypoints: {len(playbook.waypoints)}")
        for i, wp in enumerate(playbook.waypoints):
            print(f"  {i+1}. ({wp.lat:.6f}, {wp.lon:.6f}) @ {wp.alt}m - {wp.action}")

    def test_validate_geojson(self):
        """Test GeoJSON validation"""
        valid_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [22.676025735635818, 49.58809075009475],
                        "type": "Point"
                    }
                }
            ]
        }

        is_valid, error = validate_geojson(valid_geojson)
        assert is_valid is True
        assert error == ""

    def test_validate_invalid_geojson(self):
        """Test validation rejects invalid GeoJSON"""
        # Missing FeatureCollection type
        invalid_geojson = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [0, 0]}
        }

        is_valid, error = validate_geojson(invalid_geojson)
        assert is_valid is False
        assert "FeatureCollection" in error

    def test_linestring_conversion(self):
        """Test LineString geometry conversion"""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [22.676025735635818, 49.58809075009475],
                            [22.650759135512743, 49.57580919435844]
                        ]
                    }
                }
            ]
        }

        playbook = geojson_to_playbook(geojson)

        assert len(playbook.waypoints) == 2
        assert playbook.waypoints[0].lat == 49.58809075009475
        assert playbook.waypoints[1].lat == 49.57580919435844

    def test_duplicate_waypoint_removal(self):
        """Test that duplicate waypoints are removed"""
        geojson = {
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
                        "coordinates": [22.676025735635818, 49.58809075009475],  # Duplicate
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

        playbook = geojson_to_playbook(geojson)

        # Should have 2 unique waypoints, not 3
        assert len(playbook.waypoints) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
