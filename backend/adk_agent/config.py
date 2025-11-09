"""
ADK Agent Configuration

Configuration for Google ADK agent including API keys,
model settings, and safety constraints.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ADK Configuration
ADK_CONFIG = {
    'model': 'gemini-2.0-flash-exp',
    'api_key': os.getenv('GOOGLE_API_KEY'),
    'temperature': 0.7,
    'max_tokens': 2048,
}

# Safety settings for mission planning
SAFETY_CONSTRAINTS = {
    'max_altitude_m': 120,
    'min_altitude_m': 10,
    'max_speed_mps': 15,
    'min_speed_mps': 1,
    'min_battery_threshold': 20,
    'max_mission_duration_min': 60,
}

# Supported mission types
MISSION_TYPES = [
    "patrol",
    "reconnaissance",
    "tracking",
    "search",
    "delivery"
]

# Supported actions
SUPPORTED_ACTIONS = [
    "photo",
    "video_start",
    "video_stop",
    "hover",
    "scan"
]
