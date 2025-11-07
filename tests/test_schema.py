"""
Test Playbook Schema Validation

Tests that don't require Olympe SDK or drone simulator.
"""

import pytest
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.playbook_parser.schema import (
    MissionPlaybook,
    Waypoint,
    FlightParameters,
    CameraSettings,
    Contingencies
)


class TestWaypointSchema:
    """Test waypoint validation"""

    def test_valid_waypoint(self):
        """Test creating a valid waypoint"""
        wp = Waypoint(lat=48.8788, lon=2.3675, alt=50, action="photo")
        assert wp.lat == 48.8788
        assert wp.lon == 2.3675
        assert wp.alt == 50
        assert wp.action == "photo"

    def test_waypoint_altitude_validation(self):
        """Test altitude bounds"""
        # Valid altitude
        wp = Waypoint(lat=48.8788, lon=2.3675, alt=50)
        assert wp.alt == 50

        # Test minimum
        wp_min = Waypoint(lat=48.8788, lon=2.3675, alt=0)
        assert wp_min.alt == 0

        # Test maximum
        wp_max = Waypoint(lat=48.8788, lon=2.3675, alt=500)
        assert wp_max.alt == 500

    def test_waypoint_coordinates_validation(self):
        """Test GPS coordinate validation"""
        # Valid coordinates
        wp = Waypoint(lat=48.8788, lon=2.3675, alt=50)
        assert -90 <= wp.lat <= 90
        assert -180 <= wp.lon <= 180

        # Edge cases
        wp_north = Waypoint(lat=90, lon=0, alt=50)
        wp_south = Waypoint(lat=-90, lon=0, alt=50)
        wp_east = Waypoint(lat=0, lon=180, alt=50)
        wp_west = Waypoint(lat=0, lon=-180, alt=50)

        assert wp_north.lat == 90
        assert wp_south.lat == -90
        assert wp_east.lon == 180
        assert wp_west.lon == -180


class TestPlaybookSchema:
    """Test complete playbook validation"""

    def test_load_simple_playbook(self):
        """Test loading the simple_test.json playbook"""
        playbook_path = Path("playbooks/simple_test.json")

        with open(playbook_path) as f:
            data = json.load(f)

        playbook = MissionPlaybook(**data)

        assert playbook.mission_id == "test_flight_001"
        assert playbook.mission_type == "patrol"
        assert len(playbook.waypoints) == 3
        assert playbook.flight_parameters.altitude_m == 50
        assert playbook.flight_parameters.speed_mps == 5

    def test_minimal_playbook(self):
        """Test minimal valid playbook"""
        data = {
            "mission_id": "minimal_001",
            "mission_type": "patrol",
            "description": "Minimal test",
            "waypoints": [
                {"lat": 48.8788, "lon": 2.3675, "alt": 50}
            ]
        }

        playbook = MissionPlaybook(**data)

        assert playbook.mission_id == "minimal_001"
        assert len(playbook.waypoints) == 1
        # Check defaults are applied
        assert playbook.flight_parameters.altitude_m == 120
        assert playbook.contingencies.low_battery == "return_to_home"

    def test_full_playbook(self):
        """Test playbook with all optional fields"""
        data = {
            "mission_id": "full_001",
            "mission_type": "reconnaissance",
            "description": "Full featured mission",
            "area_of_interest": {
                "center": {"lat": 48.8788, "lon": 2.3675},
                "radius_km": 2
            },
            "waypoints": [
                {"lat": 48.8788, "lon": 2.3675, "alt": 50, "action": "photo"},
                {"lat": 48.8790, "lon": 2.3680, "alt": 50, "action": "hover", "hover_duration_sec": 10}
            ],
            "flight_parameters": {
                "altitude_m": 100,
                "speed_mps": 8,
                "pattern": "grid",
                "heading_mode": "auto"
            },
            "camera_settings": {
                "mode": "video",
                "resolution": "4K",
                "gimbal_tilt": -45,
                "auto_capture_interval_sec": 5
            },
            "contingencies": {
                "low_battery": "land_immediately",
                "gps_loss": "hover_and_alert",
                "obstacle_detected": "reroute",
                "communication_loss": "return_to_home"
            },
            "auto_execute": False,
            "max_duration_min": 25
        }

        playbook = MissionPlaybook(**data)

        assert playbook.mission_type == "reconnaissance"
        assert playbook.area_of_interest.radius_km == 2
        assert len(playbook.waypoints) == 2
        assert playbook.waypoints[1].hover_duration_sec == 10
        assert playbook.camera_settings.mode == "video"
        assert playbook.max_duration_min == 25


class TestPlaybookValidator:
    """Test playbook validation logic"""

    def test_validator_import(self):
        """Test that validator can be imported"""
        from backend.olympe_translator.translator import PlaybookValidator

        validator = PlaybookValidator()
        assert validator is not None

    def test_validate_simple_playbook(self):
        """Test validating the simple test playbook"""
        from backend.olympe_translator.translator import PlaybookValidator

        playbook_path = Path("playbooks/simple_test.json")
        with open(playbook_path) as f:
            data = json.load(f)

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)

        assert is_valid is True
        assert error is None

    def test_validate_altitude_too_high(self):
        """Test that excessive altitude is rejected"""
        from backend.olympe_translator.translator import PlaybookValidator

        data = {
            "mission_id": "invalid_altitude",
            "mission_type": "patrol",
            "description": "Invalid altitude test",
            "waypoints": [
                {"lat": 48.8788, "lon": 2.3675, "alt": 200}  # Too high
            ]
        }

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)

        assert is_valid is False
        assert "exceeds max 150m" in error

    def test_validate_speed_too_high(self):
        """Test that excessive speed is rejected"""
        from backend.olympe_translator.translator import PlaybookValidator

        data = {
            "mission_id": "invalid_speed",
            "mission_type": "patrol",
            "description": "Invalid speed test",
            "waypoints": [
                {"lat": 48.8788, "lon": 2.3675, "alt": 50}
            ],
            "flight_parameters": {
                "altitude_m": 50,
                "speed_mps": 20,  # Too fast
                "pattern": "direct"
            }
        }

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)

        assert is_valid is False
        assert "exceeds safe limit" in error

    def test_validate_no_waypoints(self):
        """Test that playbook with no waypoints is rejected"""
        from backend.olympe_translator.translator import PlaybookValidator

        # This should fail at Pydantic level
        with pytest.raises(Exception):
            data = {
                "mission_id": "no_waypoints",
                "mission_type": "patrol",
                "description": "No waypoints",
                "waypoints": []
            }
            playbook = MissionPlaybook(**data)


class TestFlightParameters:
    """Test flight parameters"""

    def test_default_flight_parameters(self):
        """Test default values"""
        params = FlightParameters()

        assert params.altitude_m == 120
        assert params.speed_mps == 10
        assert params.pattern == "direct"
        assert params.heading_mode == "auto"

    def test_custom_flight_parameters(self):
        """Test custom values"""
        params = FlightParameters(
            altitude_m=80,
            speed_mps=12,
            pattern="grid",
            heading_mode="fixed"
        )

        assert params.altitude_m == 80
        assert params.speed_mps == 12
        assert params.pattern == "grid"
        assert params.heading_mode == "fixed"


class TestCameraSettings:
    """Test camera configuration"""

    def test_default_camera_settings(self):
        """Test default camera settings"""
        camera = CameraSettings()

        assert camera.mode == "photo"
        assert camera.resolution == "4K"
        assert camera.gimbal_tilt == -90

    def test_video_mode(self):
        """Test video mode configuration"""
        camera = CameraSettings(
            mode="video",
            gimbal_tilt=-45,
            auto_capture_interval_sec=2
        )

        assert camera.mode == "video"
        assert camera.gimbal_tilt == -45
        assert camera.auto_capture_interval_sec == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
