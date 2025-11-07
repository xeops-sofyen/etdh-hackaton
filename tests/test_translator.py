"""
Tests for the Olympe Translator

Run with: pytest tests/test_translator.py
"""

import pytest
import json
from pathlib import Path
from backend.playbook_parser.schema import MissionPlaybook
from backend.olympe_translator.translator import OlympeTranslator, PlaybookValidator
from backend.drone_controller.controller import DroneController


class TestPlaybookSchema:
    """Test playbook JSON schema validation"""

    def test_load_simple_playbook(self):
        """Test loading a simple playbook"""
        playbook_path = Path("playbooks/simple_test.json")
        with open(playbook_path) as f:
            data = json.load(f)

        playbook = MissionPlaybook(**data)
        assert playbook.mission_id == "test_flight_001"
        assert len(playbook.waypoints) == 3
        assert playbook.waypoints[0].lat == 48.8788

    def test_load_coastal_patrol(self):
        """Test loading coastal patrol mission"""
        playbook_path = Path("playbooks/coastal_patrol.json")
        with open(playbook_path) as f:
            data = json.load(f)

        playbook = MissionPlaybook(**data)
        assert playbook.mission_type == "patrol"
        assert len(playbook.waypoints) == 4
        assert playbook.area_of_interest is not None


class TestPlaybookValidator:
    """Test playbook validation logic"""

    def test_valid_playbook(self):
        """Test that valid playbooks pass validation"""
        with open("playbooks/simple_test.json") as f:
            data = json.load(f)

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)
        assert is_valid
        assert error is None

    def test_altitude_too_high(self):
        """Test that excessive altitude is rejected"""
        with open("playbooks/simple_test.json") as f:
            data = json.load(f)

        # Modify altitude to exceed limit
        data["waypoints"][0]["alt"] = 200

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)
        assert not is_valid
        assert "exceeds max 150m" in error

    def test_speed_too_high(self):
        """Test that excessive speed is rejected"""
        with open("playbooks/simple_test.json") as f:
            data = json.load(f)

        data["flight_parameters"]["speed_mps"] = 20

        playbook = MissionPlaybook(**data)
        validator = PlaybookValidator()

        is_valid, error = validator.validate(playbook)
        assert not is_valid
        assert "exceeds safe limit" in error


class TestOlympeTranslator:
    """Test Olympe translator (requires simulator)"""

    @pytest.mark.skipif(True, reason="Requires Sphinx simulator")
    def test_connect_to_simulator(self):
        """Test connection to Sphinx simulator"""
        translator = OlympeTranslator("10.202.0.1")
        result = translator.connect()
        assert result is True
        translator.disconnect()

    def test_translator_initialization(self):
        """Test translator can be initialized"""
        translator = OlympeTranslator()
        assert translator.drone_ip == "10.202.0.1"


class TestDroneController:
    """Test drone controller"""

    def test_controller_initialization(self):
        """Test controller can be initialized"""
        controller = DroneController(simulator_mode=True)
        assert controller.mission_status == "idle"

    def test_get_status(self):
        """Test status reporting"""
        controller = DroneController()
        status = controller.get_status()

        assert "mission_status" in status
        assert status["mission_status"] == "idle"


# ============================================================================
# INTEGRATION TEST (Manual - requires simulator)
# ============================================================================

def test_full_mission_execution():
    """
    Full integration test

    RUN MANUALLY with Sphinx simulator:
    1. Start Sphinx: sphinx /path/to/drone.drone
    2. Run: pytest tests/test_translator.py::test_full_mission_execution -v
    """
    print("\n🚁 Starting full mission execution test")

    # Load playbook
    with open("playbooks/simple_test.json") as f:
        data = json.load(f)
    playbook = MissionPlaybook(**data)

    # Execute mission
    controller = DroneController(simulator_mode=True)
    result = controller.execute_mission(playbook)

    print(f"Result: {result}")
    assert result["status"] == "success"


if __name__ == "__main__":
    # Run quick tests without simulator
    print("Running basic tests...")
    pytest.main([__file__, "-v", "-k", "not simulator"])
