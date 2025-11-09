"""
Agent Factory for Drone Mission Planning
Creates the ADK Agent with tools and configuration
"""
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools import agent_tool
from backend.playbook_parser.schema import MissionPlaybook

from .tools import (
    generate_waypoints,
    validate_flight_zone,
    calculate_flight_time,
    create_mission_playbook,
    get_weather_info,
)
from .prompts import SYSTEM_INSTRUCTION
from .config import ADK_CONFIG

playbook_writer_agent = Agent(
    model="gemini-2.5-flash",
    name="playbook_writer",
    output_key="playbook",
    output_schema=MissionPlaybook,
    tools=[],
    description="You are an agent receiving a list of waypoints and instructions and generating a mission playbook.",
    instruction="""
# Drone Mission Playbook Generator
You receive a mission request (objectives, environment, constraints) and must return a JSON playbook that exactly matches the `MissionPlaybook` schema.

## Responsibilities
- Infer missing but reasonable defaults (e.g., altitude, speed, contingencies) when the user does not specify them.
- Ensure all coordinates, altitudes, durations, and speeds are realistic and safe for small UAV operations.
- Provide clear waypoint sequencing that satisfies the stated mission objective.

## Output Requirements
- Respond with **only** raw JSON (no Markdown, comments, or prose).
- The JSON must conform to `MissionPlaybook`:
  - `"mission_id"`: unique string identifier.
  - `"mission_type"`: one of `"patrol"`, `"reconnaissance"`, `"tracking"`, `"search"`, `"delivery"`.
  - `"description"`: concise summary of the mission goal.
  - `"area_of_interest"`: optional object with `center` (`lat`, `lon`) and `radius_km` if the mission references an area.
  - `"waypoints"`: array with at least one waypoint; each waypoint includes `lat`, `lon`, `alt` (meters) and may include `action` and `hover_duration_sec`.
  - `"flight_parameters"`: object containing `altitude_m`, `speed_mps`, `pattern`, and `heading_mode`.
  - `"camera_settings"`: object with `mode`, `resolution`, `gimbal_tilt`, and optional `auto_capture_interval_sec`.
  - `"contingencies"`: object covering `low_battery`, `gps_loss`, `obstacle_detected`, and `communication_loss`.
  - `"auto_execute"`: boolean indicating whether to launch immediately.
  - `"max_duration_min"`: total mission duration limit.

## Example Format (values are illustrative; do not reuse them verbatim)
{
  "mission_id": "coastal_patrol_demo",
  "mission_type": "patrol",
  "description": "Patrol the marina perimeter to detect unauthorized vessels.",
  "area_of_interest": {
    "center": { "lat": 53.503, "lon": 8.107 },
    "radius_km": 3.5
  },
  "waypoints": [
    { "lat": 53.5021, "lon": 8.1024, "alt": 110, "action": "photo" },
    { "lat": 53.5058, "lon": 8.1099, "alt": 110, "action": "video_start" },
    { "lat": 53.5003, "lon": 8.1127, "alt": 110, "action": "video_stop" }
  ],
  "flight_parameters": {
    "altitude_m": 110,
    "speed_mps": 9,
    "pattern": "perimeter",
    "heading_mode": "target_oriented"
  },
  "camera_settings": {
    "mode": "video",
    "resolution": "4K",
    "gimbal_tilt": -35
  },
  "contingencies": {
    "low_battery": "return_to_home",
    "gps_loss": "hover_and_alert",
    "obstacle_detected": "reroute",
    "communication_loss": "return_to_home"
  },
  "auto_execute": true,
  "max_duration_min": 28
}
""",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)


def get_drone_agent() -> Agent:
    """
    Create and return the drone mission planning agent.

    This agent can:
    - Generate waypoints in various patterns
    - Validate flight zones
    - Calculate flight times
    - Create mission playbooks
    - Get weather information
    """

    # Provide Python callables directly as tools.
    # ADK will wrap them as FunctionTool and infer schemas from type hints/docstrings.
    tools = [
        agent_tool.AgentTool(playbook_writer_agent),
        generate_waypoints,
        # validate_flight_zone,
        # calculate_flight_time,
        # create_mission_playbook,
        # get_weather_info,
    ]

    # Create agent
    agent = Agent(
        name="drone_mission_planner",
        model=ADK_CONFIG['model'],
        instruction=SYSTEM_INSTRUCTION,
        tools=tools,
        generate_content_config=types.GenerateContentConfig(
            temperature=ADK_CONFIG['temperature'],
        )
    )

    return agent
