# Autonomous Drone Mission Control Dashboard - Design Document

**Date:** 2025-11-07
**Status:** Approved
**Mission:** Build a frontend for autonomous drone task execution from human-defined playbooks

## Overview

A unified web dashboard for defining, executing, and monitoring autonomous drone missions. Operators create missions via playbooks (templates, manual building, or natural language), drones execute autonomously, and operators monitor with minimal intervention except for approval requests.

## Requirements Summary

### Mission Types
- **Surveillance/Patrol:** Area monitoring with defined routes
- **Delivery/Transport:** Point-to-point package delivery

### Key Capabilities
- Multiple simultaneous playbooks (one drone per playbook)
- Real-time updates (1-5 second intervals)
- Operator approvals for: anomalies, mission deviations, high-risk actions
- GeoJSON-based mission definitions
- Three playbook creation modes: Templates, Manual, LLM Chat

### Tech Stack
- React + TypeScript
- Leaflet (map rendering)
- Zustand (state management)
- Mock WebSocket service (real-time simulation)
- Mock LLM service (natural language processing)

---

## Architecture

### Application Structure

**Single-Page Application:**
```
/  → Unified Dashboard (library + live mission view)
```

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Drone Mission Control Dashboard           │
├──────────────┬──────────────────────────────┤
│              │                              │
│   Sidebar    │      Main View               │
│              │                              │
│  - Active    │   ┌──────────────────────┐   │
│  - Planned   │   │                      │   │
│  - Past      │   │   Leaflet Map        │   │
│              │   │   (GeoJSON Routes)   │   │
│  [+ New]     │   │                      │   │
│              │   └──────────────────────┘   │
│              │                              │
│              │   [Mission Controls]         │
│              │   [Telemetry Panel]          │
│              │   [Approval Queue]           │
└──────────────┴──────────────────────────────┘
```

### Component Hierarchy

```
App
├── Sidebar
│   ├── PlaybookList (Active/Planned/Past tabs)
│   └── NewPlaybookButton
├── MainView
│   ├── MapView (Leaflet)
│   │   ├── RouteLayer (GeoJSON route display)
│   │   ├── DroneMarker (live position with icon)
│   │   └── WaypointMarkers (numbered waypoints)
│   ├── MissionControls (Start/Pause/Abort buttons)
│   ├── TelemetryPanel (Battery, speed, altitude display)
│   └── ApprovalQueue (popup cards for pending approvals)
└── PlaybookBuilderModal
    ├── TemplateTab
    ├── ManualTab (map + task list)
    └── ChatTab (LLM interface)
```

---

## Data Model

### Core Types

```typescript
// Playbook - Mission definition using GeoJSON
interface Playbook {
  id: string;
  name: string;
  missionType: 'surveillance' | 'delivery';
  route: GeoJSON.FeatureCollection; // Mission geometry
  createdAt: Date;
  status: 'planned' | 'active' | 'completed' | 'failed';
  metadata?: Record<string, any>; // Extensible
}

// DroneState - Live telemetry data
interface DroneState {
  playbookId: string;
  position: GeoJSON.Feature<GeoJSON.Point>; // Current location
  battery: number; // Percentage
  speed: number; // m/s
  heading: number; // Degrees
  status: 'idle' | 'en_route' | 'awaiting_approval' | 'returning';
  currentWaypointIndex: number; // Progress through route
  telemetry?: Record<string, any>; // Extensible sensors
}

// Approval - Operator decision request
interface Approval {
  id: string;
  playbookId: string;
  type: 'anomaly' | 'deviation' | 'high_risk';
  description: string;
  location?: GeoJSON.Feature<GeoJSON.Point>;
  timestamp: Date;
}
```

### GeoJSON Structure Example

```json
{
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
        "coordinates": [
          [22.676025735635818, 49.58809075009475],
          [22.650759135512743, 49.57580919435844],
          [22.67371444036104, 49.55304323176125]
        ],
        "type": "LineString"
      }
    }
  ]
}
```

---

## State Management (Zustand)

```typescript
interface AppStore {
  // Playbook management
  playbooks: Playbook[];
  selectedPlaybookId: string | null;
  addPlaybook: (playbook: Playbook) => void;
  selectPlaybook: (id: string) => void;

  // Live drone states (from WebSocket)
  drones: Map<string, DroneState>; // Keyed by playbookId
  updateDrone: (playbookId: string, state: Partial<DroneState>) => void;

  // Approvals
  pendingApprovals: Approval[];
  approveAction: (approvalId: string) => void;
  denyAction: (approvalId: string) => void;

  // UI state
  isBuilderOpen: boolean;
  activeTab: 'active' | 'planned' | 'past';
  setBuilderOpen: (open: boolean) => void;
  setActiveTab: (tab: string) => void;
}
```

**Key Benefits:**
- Single source of truth for all application state
- Automatic re-renders on state changes
- Simple API with minimal boilerplate
- Easy WebSocket integration via `updateDrone`

---

## Real-Time Communication

### Mock WebSocket Service

```typescript
class MockDroneWebSocket {
  private interval: NodeJS.Timeout;
  private currentWaypoint: number = 0;

  connect(playbookId: string) {
    // Send position updates every 1-2 seconds
    this.interval = setInterval(() => {
      const update = {
        type: 'position_update',
        playbookId,
        data: {
          position: this.interpolatePosition(), // Smooth movement
          battery: this.simulateBatteryDrain(),
          speed: 15 + Math.random() * 5, // 15-20 m/s
          heading: this.calculateHeading(),
          currentWaypointIndex: this.currentWaypoint
        }
      };

      // 5% chance of approval request
      if (Math.random() < 0.05) {
        this.sendApprovalRequest();
      }

      return update;
    }, 1500);
  }

  disconnect() {
    clearInterval(this.interval);
  }
}
```

### Message Types

- `position_update`: Telemetry (position, battery, speed, heading)
- `waypoint_reached`: Waypoint completion notification
- `approval_required`: Operator decision needed
- `mission_complete`: Playbook execution finished
- `error`: Mission error occurred

### Integration Pattern

```typescript
// In React component
useEffect(() => {
  if (selectedPlaybookId && playbook.status === 'active') {
    const ws = new MockDroneWebSocket();
    ws.connect(selectedPlaybookId);

    ws.onMessage((msg) => {
      updateDrone(msg.playbookId, msg.data);
    });

    return () => ws.disconnect();
  }
}, [selectedPlaybookId]);
```

---

## User Interface

### Sidebar - Playbook List

**Three Tab Views:**
- **Active:** Currently executing missions (pulsing status indicator)
- **Planned:** Ready to launch (calendar icon)
- **Past:** Completed/failed missions (timestamp)

**Playbook Card:**
- Mission name
- Mission type icon (eye for surveillance, box for delivery)
- Status badge
- Timestamp
- Click → Shows details in main view

**New Playbook Button:**
- Prominent at top of sidebar
- Opens Playbook Builder Modal

### Main View - Dynamic Content

**When Playbook Selected:**

**Planned Playbooks:**
- Blue dashed line showing route
- Numbered waypoint markers (1, 2, 3...)
- [Edit] and [Start Mission] buttons

**Active Missions:**
- Green solid line showing planned route
- Purple trail showing drone's actual path
- Animated drone icon (rotates based on heading)
- Current waypoint highlighted yellow
- Completed waypoints show green checkmarks
- Mission controls: [Pause] [Abort]
- Telemetry panel: Battery %, Speed, Altitude, Status

**Past Missions:**
- Gray line for historical route
- Red markers for failure/deviation points
- Summary stats overlay (duration, distance, success/failure)

### Playbook Builder Modal

**Three Creation Modes (Tabs):**

#### 1. Templates Tab
- Visual cards: "Patrol Route" and "Delivery Mission"
- **Patrol Template:**
  - Draw polygon on embedded map
  - Set altitude, patrol pattern (perimeter/zigzag), frequency
  - Preview route generation
- **Delivery Template:**
  - Click pickup point on map
  - Click dropoff point on map
  - Set altitude, package details
  - Shows direct line route

#### 2. Manual Builder Tab
- Full interactive map for coordinate selection
- Task list panel:
  - "Add Waypoint" button
  - "Add Patrol Zone" button
  - "Add Delivery Stop" button
- Click map → Adds task with coordinates
- Drag tasks in list to reorder
- Expand task → Configure parameters (altitude, speed, loiter time, approval required)
- Live route preview updates as tasks added

#### 3. Chat Tab
- LLM conversational interface
- Input: "Describe your mission in natural language..."
- Examples shown:
  - "Patrol the perimeter of Central Park at 100m altitude"
  - "Deliver package from Warehouse A to Drop Zone B"
- LLM converts natural language → structured playbook
- Shows interpreted tasks with map preview
- User can refine: "Make altitude 150m" or "Add waypoint at coordinates"
- [Accept Playbook] saves to store

### Approval Workflow

**Approval Card (slides in from right):**
- Alert icon (color-coded by severity)
  - Yellow: Deviation
  - Orange: Anomaly
  - Red: High-risk
- Map thumbnail showing drone + issue location
- Description text
- Suggested action from drone AI
- Action buttons:
  - [Approve]: Continue with suggested action
  - [Deny]: Drone hovers, awaits instruction
  - [Modify Route]: Opens map editor for new route segment

**Approval Types:**
- **Anomaly Detection:** Surveillance detected unusual activity
- **Mission Deviation:** Weather/obstacle requires route change
- **High-Risk Action:** Landing in unverified area, approaching obstacles

---

## Map Visualization (Leaflet)

### Configuration
- **Base Layer:** OpenStreetMap tiles (no API key required)
- **Auto-fit:** Bounds adjust to show entire route on playbook selection
- **Smooth Animations:** `flyTo` with duration for drone movement

### Layers

**Route Layer:**
- Planned: Blue dashed LineString
- Active: Green solid LineString
- Past: Gray LineString

**Waypoint Markers:**
- Numbered circle markers (1, 2, 3...)
- Yellow highlight for current waypoint
- Green checkmark for completed waypoints

**Drone Marker:**
- Custom icon (drone silhouette)
- Rotates based on heading angle
- Position updates smoothly interpolated

**Path Trail:**
- Purple polyline showing drone's actual flight path
- Fades with opacity gradient (recent → old)

**Patrol Zones (if applicable):**
- Semi-transparent polygon overlay
- Blue fill with dashed border

---

## LLM Chat Integration

### Mock LLM Service

```typescript
class MockLLMService {
  async generatePlaybook(conversation: ChatMessage[]): Promise<Playbook> {
    // Pattern matching for mock implementation:
    // "patrol around X" → Generate polygon from geocoding
    // "deliver from A to B" → Two points + LineString
    // "waypoint at lat,lng" → Add Point to FeatureCollection

    return {
      id: generateId(),
      name: extractMissionName(conversation),
      route: generateGeoJSON(conversation),
      missionType: detectMissionType(conversation),
      status: 'planned',
      createdAt: new Date()
    };
  }
}
```

### Chat Message Structure

```typescript
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  generatedPlaybook?: Playbook; // If assistant created playbook
}
```

### Example Conversation Flow

```
User: "Create a patrol mission around Central Park"
Assistant: "I'll create a patrol route. What altitude should the drone fly at?"
User: "100 meters"
Assistant: [Generates GeoJSON] "I've created a perimeter patrol at 100m..."
[Map preview updates]
User: "Add a waypoint at the north entrance"
Assistant: [Updates GeoJSON] "Added waypoint. Route updated."
[Accept Playbook] → Saves to Zustand store
```

### Future: Real LLM Integration

When connecting to OpenAI/Anthropic API:
- Use function calling:
  - `create_waypoint(lat, lng, altitude)`
  - `create_patrol_zone(coordinates[])`
  - `create_route(waypoints[])`
- Frontend converts function calls → GeoJSON
- Maintains same chat interface UX

---

## Error Handling & Resilience

### WebSocket Disconnection

- Show warning banner: "Connection lost - Reconnecting..."
- Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s...)
- After 30s: "Mission data may be stale"
- Continue attempting reconnection in background

### Mission Failures

- **Low Battery:** Auto-trigger return-to-base approval request
- **Lost GPS:** Drone hovers, operator notified immediately
- **Unreachable Waypoint:** Mark task failed, request operator decision

---

## Development Phases

### Phase 1: Foundation
- [ ] Project setup (Vite + React + TypeScript)
- [ ] Zustand store structure
- [ ] Basic layout (Sidebar + Main View)
- [ ] Leaflet map integration
- [ ] Mock playbooks data

### Phase 2: Playbook Management
- [ ] Playbook list rendering (Active/Planned/Past)
- [ ] Playbook selection
- [ ] Map visualization of routes
- [ ] Template builder (Patrol & Delivery)
- [ ] Manual builder with map interaction

### Phase 3: Real-Time Execution
- [ ] Mock WebSocket service
- [ ] Drone state updates
- [ ] Live map animations
- [ ] Telemetry panel
- [ ] Mission controls (Start/Pause/Abort)

### Phase 4: Approvals & Chat
- [ ] Approval card UI
- [ ] Approve/Deny actions
- [ ] Mock LLM service
- [ ] Chat interface
- [ ] Natural language → GeoJSON conversion

### Phase 5: Polish
- [ ] Responsive design
- [ ] Loading states
- [ ] Error messages
- [ ] UI/UX refinements
- [ ] Testing

---

## Success Criteria

- Operators can create playbooks via templates, manual building, or chat
- Multiple playbooks can be managed simultaneously
- Real-time drone position updates render smoothly on map
- Approval requests appear promptly with clear action options
- GeoJSON routes render correctly in Leaflet
- Application is responsive and intuitive

---

## Future Enhancements

- Real backend integration (replace mocks)
- Multi-drone coordination
- Mission replay/scrubbing
- Telemetry graphs and analytics
- User authentication
- Cloud playbook storage
- Mobile responsive design
- 3D terrain visualization
- Weather overlay integration
