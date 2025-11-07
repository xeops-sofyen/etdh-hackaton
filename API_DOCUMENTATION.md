# Heimdall API Documentation

REST API for drone mission control. Use these endpoints to integrate the frontend dashboard.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. Health Check

**GET** `/`

Check if the API server is running.

**Response:**
```json
{
  "service": "Heimdall Mission Control",
  "status": "operational",
  "version": "1.0.0"
}
```

---

### 2. Get System Status

**GET** `/status`

Get current drone connection status and active mission.

**Response:**
```json
{
  "mission_status": "idle",  // idle | executing | completed | failed | aborted
  "current_mission": null,   // mission_id or null
  "telemetry": {
    "connected": true,
    "battery": "85%",
    "gps": "locked",
    "altitude": "120m"
  }
}
```

---

### 3. List Available Playbooks

**GET** `/playbooks/list`

Get list of all example mission playbooks.

**Response:**
```json
{
  "playbooks": [
    {
      "filename": "simple_test.json",
      "mission_id": "test_flight_001",
      "description": "Simple test flight for initial validation"
    },
    {
      "filename": "coastal_patrol.json",
      "mission_id": "coastal_patrol_001",
      "description": "Patrol German North Sea coast"
    }
  ]
}
```

---

### 4. Get Specific Playbook

**GET** `/playbooks/{filename}`

Retrieve a specific playbook by filename.

**Parameters:**
- `filename` (path): Playbook filename (e.g., `simple_test.json`)

**Example:**
```bash
GET /playbooks/simple_test.json
```

**Response:**
```json
{
  "mission_id": "test_flight_001",
  "mission_type": "patrol",
  "description": "Simple test flight",
  "waypoints": [
    {"lat": 48.8788, "lon": 2.3675, "alt": 50, "action": "photo"}
  ],
  "flight_parameters": {
    "altitude_m": 50,
    "speed_mps": 5
  }
}
```

---

### 5. Execute Mission

**POST** `/mission/execute`

Execute a mission playbook on the drone.

**Request Body:**
```json
{
  "playbook": {
    "mission_id": "my_mission",
    "mission_type": "patrol",
    "description": "My custom mission",
    "waypoints": [
      {
        "lat": 48.8788,
        "lon": 2.3675,
        "alt": 50,
        "action": "photo"
      }
    ],
    "flight_parameters": {
      "altitude_m": 50,
      "speed_mps": 5,
      "pattern": "direct"
    },
    "camera_settings": {
      "mode": "photo",
      "gimbal_tilt": -90
    },
    "contingencies": {
      "low_battery": "return_to_home",
      "gps_loss": "hover_and_alert"
    }
  },
  "simulate": false  // true = validate only, don't execute
}
```

**Response (Success):**
```json
{
  "status": "success",
  "mission_id": "my_mission",
  "waypoints_completed": 3
}
```

**Response (Validation Failed):**
```json
{
  "status": "validation_failed",
  "error": "Waypoint altitude 200m exceeds max 150m"
}
```

**Response (Execution Failed):**
```json
{
  "status": "execution_failed",
  "error": "Could not connect to drone"
}
```

---

### 6. Abort Mission

**POST** `/mission/abort`

Emergency abort the current mission. Drone will land immediately.

**Response:**
```json
{
  "status": "aborted"
}
```

---

### 7. Parse Natural Language Command

**POST** `/mission/parse-natural-language`

Convert natural language command to structured playbook.

**Request Body:**
```json
{
  "command": "Patrol the coastal area near Wilhelmshaven"
}
```

**Response:**
```json
{
  "status": "parsed",
  "playbook": {
    "mission_id": "coastal_patrol_001",
    "mission_type": "patrol",
    "waypoints": [...]
  },
  "note": "Using template - integrate GPT-4 for real parsing"
}
```

---

## Playbook Schema

Complete schema for mission playbooks:

```typescript
interface MissionPlaybook {
  mission_id: string
  mission_type: 'patrol' | 'reconnaissance' | 'tracking' | 'search' | 'delivery'
  description: string

  // Optional area definition
  area_of_interest?: {
    center: { lat: number, lon: number }
    radius_km: number
  }

  // Flight plan (required)
  waypoints: Array<{
    lat: number          // -90 to 90
    lon: number          // -180 to 180
    alt: number          // 10 to 150 (meters)
    action?: 'photo' | 'video_start' | 'video_stop' | 'hover' | 'scan'
    hover_duration_sec?: number
  }>

  // Flight parameters
  flight_parameters: {
    altitude_m: number   // 10-150
    speed_mps: number    // 1-15
    pattern: 'direct' | 'grid' | 'spiral' | 'perimeter'
    heading_mode?: 'auto' | 'fixed' | 'target_oriented'
  }

  // Camera settings
  camera_settings?: {
    mode: 'photo' | 'video' | 'thermal'
    resolution?: string
    gimbal_tilt: number  // -90 to 0 (degrees)
    auto_capture_interval_sec?: number
  }

  // Safety rules
  contingencies: {
    low_battery: 'return_to_home' | 'land_immediately' | 'alert_and_hover'
    gps_loss: 'hover_and_alert' | 'land_immediately' | 'switch_to_visual'
    obstacle_detected: 'reroute' | 'hover' | 'abort_mission'
    communication_loss: 'continue_mission' | 'return_to_home' | 'hover'
  }

  // Execution settings
  auto_execute: boolean
  max_duration_min: number  // 5-60
}
```

---

## Frontend Integration Guide

### Example: Execute a mission from React

```typescript
// Execute mission
const response = await fetch('http://localhost:8000/mission/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    playbook: {
      mission_id: 'test_001',
      mission_type: 'patrol',
      description: 'Test patrol',
      waypoints: [
        { lat: 48.8788, lon: 2.3675, alt: 50, action: 'photo' }
      ],
      flight_parameters: {
        altitude_m: 50,
        speed_mps: 5,
        pattern: 'direct'
      },
      contingencies: {
        low_battery: 'return_to_home',
        gps_loss: 'hover_and_alert',
        obstacle_detected: 'reroute',
        communication_loss: 'return_to_home'
      },
      auto_execute: true,
      max_duration_min: 15
    },
    simulate: false
  })
})

const result = await response.json()
console.log(result) // { status: 'success', ... }
```

### Example: Poll for mission status

```typescript
// Poll every 2 seconds
setInterval(async () => {
  const response = await fetch('http://localhost:8000/status')
  const status = await response.json()

  console.log(`Mission: ${status.mission_status}`)
  console.log(`Battery: ${status.telemetry.battery}`)
}, 2000)
```

### Example: Emergency abort

```typescript
const abort = async () => {
  await fetch('http://localhost:8000/mission/abort', {
    method: 'POST'
  })
  alert('Mission aborted!')
}
```

---

## Interactive API Documentation

Once the server is running, visit:

**http://localhost:8000/docs**

You'll get a Swagger UI where you can:
- Test all endpoints
- See request/response schemas
- Execute API calls directly from the browser

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (e.g., invalid playbook)
- **404**: Not found (e.g., playbook doesn't exist)
- **500**: Server error (e.g., drone connection failed)

Error response format:
```json
{
  "detail": "Error message here"
}
```

---

## CORS Configuration

The API allows requests from all origins (configured for development).

In production, update `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## WebSocket Support (TODO)

For real-time telemetry streaming, a WebSocket endpoint will be added:

```
ws://localhost:8000/ws/telemetry
```

This will stream:
- GPS coordinates
- Battery level
- Altitude
- Speed
- Camera feed status

---

## Questions?

Contact the backend team or check `backend/api/main.py` for implementation details.
