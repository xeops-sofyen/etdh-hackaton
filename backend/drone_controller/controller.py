"""
Drone Controller

High-level interface for mission execution.
Uses the OlympeTranslator to execute playbooks.
"""

import logging
from typing import Optional, Dict, Any
from backend.olympe_translator.translator import OlympeTranslator, PlaybookValidator
from backend.playbook_parser.schema import MissionPlaybook

logger = logging.getLogger(__name__)


class DroneController:
    """
    High-level drone controller

    Manages mission lifecycle: validation → execution → monitoring
    """

    def __init__(self, drone_ip: str = "10.202.0.1", simulator_mode: bool = False):
        """
        Initialize controller

        Args:
            drone_ip: IP of physical drone or simulator
            simulator_mode: If True, uses Sphinx simulator defaults
        """
        self.drone_ip = drone_ip if not simulator_mode else "10.202.0.1"
        self.translator = OlympeTranslator(self.drone_ip)
        self.validator = PlaybookValidator()
        self.current_mission: Optional[MissionPlaybook] = None
        self.mission_status = "idle"

    def execute_mission(self, playbook: MissionPlaybook) -> Dict[str, Any]:
        """
        Execute a mission playbook

        Flow:
        1. Validate playbook
        2. Connect to drone
        3. Translate and execute
        4. Disconnect

        Args:
            playbook: Mission to execute

        Returns:
            Execution result
        """
        logger.info(f"🎯 Executing mission: {playbook.mission_id}")

        # Step 1: Validate
        is_valid, error = self.validator.validate(playbook)
        if not is_valid:
            logger.error(f"❌ Playbook validation failed: {error}")
            return {
                "status": "validation_failed",
                "error": error
            }

        # Step 2: Connect
        if not self.translator.connect():
            return {
                "status": "connection_failed",
                "error": "Could not connect to drone"
            }

        # Step 3: Execute
        try:
            self.current_mission = playbook
            self.mission_status = "executing"

            result = self.translator.translate_and_execute(playbook)

            self.mission_status = "completed"
            return result

        except Exception as e:
            logger.error(f"Mission execution failed: {e}")
            self.mission_status = "failed"
            return {
                "status": "execution_failed",
                "error": str(e)
            }

        finally:
            # Step 4: Disconnect
            self.translator.disconnect()

    def get_status(self) -> Dict[str, Any]:
        """Get current mission status"""
        telemetry = self.translator.get_telemetry()

        return {
            "mission_status": self.mission_status,
            "current_mission": self.current_mission.mission_id if self.current_mission else None,
            "telemetry": telemetry
        }

    def abort_mission(self) -> bool:
        """Emergency abort current mission"""
        logger.warning("⚠️  ABORTING MISSION")
        try:
            self.translator._emergency_land()
            self.mission_status = "aborted"
            return True
        except Exception as e:
            logger.error(f"Abort failed: {e}")
            return False
