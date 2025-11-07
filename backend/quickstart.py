#!/usr/bin/env python3
"""
Quickstart Script

Test your Olympe translator without the full API stack.

Usage:
    python backend/quickstart.py --playbook playbooks/simple_test.json
"""

import argparse
import json
import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.playbook_parser.schema import MissionPlaybook
from backend.olympe_translator.translator import OlympeTranslator, PlaybookValidator
from backend.drone_controller.controller import DroneController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    parser = argparse.ArgumentParser(description="Execute a drone mission playbook")
    parser.add_argument("--playbook", required=True, help="Path to playbook JSON")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't execute")
    parser.add_argument("--simulator", action="store_true", default=True, help="Use simulator mode")
    args = parser.parse_args()

    # Load playbook
    print(f"\n📂 Loading playbook: {args.playbook}")
    with open(args.playbook) as f:
        data = json.load(f)

    playbook = MissionPlaybook(**data)
    print(f"✅ Playbook loaded: {playbook.mission_id}")
    print(f"   Description: {playbook.description}")
    print(f"   Waypoints: {len(playbook.waypoints)}")

    # Validate
    print("\n🔍 Validating playbook...")
    validator = PlaybookValidator()
    is_valid, error = validator.validate(playbook)

    if not is_valid:
        print(f"❌ Validation failed: {error}")
        return 1

    print("✅ Playbook is valid")

    if args.validate_only:
        print("\n✓ Validation complete (--validate-only flag set)")
        return 0

    # Execute
    print("\n🚁 Executing mission...")
    print("⚠️  Make sure Sphinx simulator is running!")
    input("Press ENTER to continue or Ctrl+C to abort...")

    controller = DroneController(simulator_mode=args.simulator)
    result = controller.execute_mission(playbook)

    print(f"\n📊 Result: {result}")

    if result["status"] == "success":
        print("✅ Mission completed successfully!")
        return 0
    else:
        print(f"❌ Mission failed: {result.get('error')}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
