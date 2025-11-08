/**
 * Real API Service - Connects to Heimdall Backend
 * Replaces mock services with real HTTP + WebSocket connections
 */

import type { Playbook, DroneState } from '../types';
import type { Feature, FeatureCollection, Point } from 'geojson';

// Backend configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// ============================================================================
// TYPE CONVERTERS - Frontend GeoJSON ↔ Backend Playbook Schema
// ============================================================================

/**
 * Convert frontend Playbook (GeoJSON) to backend MissionPlaybook
 * Uses the complete Pydantic schema from backend/playbook_parser/schema.py
 */
function playbookToBackend(playbook: Playbook) {
  // Extract waypoints from GeoJSON
  const points = playbook.route.features
    .filter((f): f is typeof f & { geometry: Point } => f.geometry.type === 'Point')
    .map((f) => {
      const coords = f.geometry.coordinates;
      return {
        lat: coords[1],
        lon: coords[0],
        alt: 120, // Default altitude in meters
        action: 'hover', // Default action
        hover_duration_sec: 5,
      };
    });

  // Calculate center point for area_of_interest
  const centerLat = points.reduce((sum, p) => sum + p.lat, 0) / points.length;
  const centerLon = points.reduce((sum, p) => sum + p.lon, 0) / points.length;

  // Map frontend missionType to backend mission_type
  const missionTypeMap = {
    surveillance: 'patrol' as const,
    delivery: 'delivery' as const,
  };

  return {
    mission_id: playbook.id,
    mission_type: missionTypeMap[playbook.missionType] || 'patrol',
    description: playbook.name,
    area_of_interest: {
      center: {
        lat: centerLat,
        lon: centerLon,
      },
      radius_km: 5,
    },
    waypoints: points,
    flight_parameters: {
      altitude_m: 120,
      speed_mps: 10,
      pattern: 'direct' as const,
      heading_mode: 'auto' as const,
    },
    camera_settings: {
      mode: 'photo' as const,
      resolution: '4K',
      gimbal_tilt: -45,
      auto_capture_interval_sec: null,
    },
    contingencies: {
      low_battery: 'return_to_home' as const,
      gps_loss: 'hover_and_alert' as const,
      obstacle_detected: 'reroute' as const,
      communication_loss: 'return_to_home' as const,
    },
    auto_execute: true,
    max_duration_min: 30,
  };
}

/**
 * Convert backend status to frontend DroneState
 */
function backendToDroneState(playbookId: string, backendStatus: any): DroneState {
  return {
    playbookId,
    position: {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'Point',
        coordinates: [
          backendStatus.position?.lon || 0,
          backendStatus.position?.lat || 0,
        ],
      },
    },
    battery: backendStatus.battery || 100,
    speed: backendStatus.speed || 0,
    heading: backendStatus.heading || 0,
    status: backendStatus.status || 'idle',
    currentWaypointIndex: backendStatus.current_waypoint || 0,
  };
}

type BackendWaypoint = {
  lat?: number;
  lon?: number;
  alt?: number;
  altitude?: number;
  action?: string;
  hover_duration_sec?: number;
};

function waypointToFeature(waypoint: BackendWaypoint, index: number): Feature<Point> | null {
  const lat = Number(waypoint?.lat);
  const lon = Number(waypoint?.lon);

  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    return null;
  }

  return {
    type: 'Feature',
    properties: {
      action: waypoint?.action ?? null,
      altitude: waypoint?.alt ?? waypoint?.altitude ?? null,
      hoverDurationSec: waypoint?.hover_duration_sec ?? null,
      sequence: index + 1,
    },
    geometry: {
      type: 'Point',
      coordinates: [lon, lat],
    },
  };
}

function backendMissionToPlaybook(data: any): Playbook {
  const missionId = data.mission_id ?? `playbook-${Date.now()}`;
  const waypointList: BackendWaypoint[] = Array.isArray(data.waypoints)
    ? data.waypoints.filter(
        (wp: unknown): wp is BackendWaypoint => typeof wp === 'object' && wp !== null
      )
    : [];
  const features = waypointList
    .map((waypoint: BackendWaypoint, index: number) => waypointToFeature(waypoint, index))
    .filter((feature): feature is Feature<Point> => feature !== null);

  const missionType = data.mission_type === 'delivery' ? 'delivery' : 'surveillance';

  const route: FeatureCollection = {
    type: 'FeatureCollection',
    features,
  };

  return {
    id: missionId,
    name: data.description ?? missionId,
    missionType,
    route,
    createdAt: new Date(data.created_at ?? Date.now()),
    status: 'planned',
    estimatedDuration:
      typeof data.max_duration_min === 'number' ? data.max_duration_min * 60 : undefined,
    metadata: data,
  };
}

// ============================================================================
// API CLASS
// ============================================================================

export class HeimdallAPI {
  /**
   * Create a playbook from GeoJSON
   * Returns the playbook_id that can be used for execution
   */
  async createPlaybook(playbook: Playbook): Promise<{
    status: string;
    playbook_id: string;
    playbook: any;
    waypoint_count: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/playbook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        geojson: playbook.route,
        mission_id: playbook.id,
        mission_type: playbook.missionType === 'surveillance' ? 'patrol' : 'delivery',
        description: playbook.name,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Playbook creation failed');
    }

    return response.json();
  }

  /**
   * Execute a mission playbook
   *
   * Accepts either:
   * - playbook_id: For playbooks created via /playbook endpoint (preferred)
   * - playbook: Direct playbook object (legacy)
   */
  async executeMission(
    playbookOrId: Playbook | string,
    simulate: boolean = false
  ): Promise<{
    status: string;
    mission_id: string;
    message?: string;
  }> {
    let requestBody: any;

    if (typeof playbookOrId === 'string') {
      // Use playbook_id (new approach)
      requestBody = {
        playbook_id: playbookOrId,
        simulate,
      };
    } else {
      // Use inline playbook (legacy support)
      const backendPlaybook = playbookToBackend(playbookOrId);
      requestBody = {
        playbook: backendPlaybook,
        simulate,
      };
    }

    const response = await fetch(`${API_BASE_URL}/mission/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Mission execution failed');
    }

    return response.json();
  }

  /**
   * Get current drone status
   */
  async getStatus(): Promise<DroneState | null> {
    const response = await fetch(`${API_BASE_URL}/status`);

    if (!response.ok) {
      throw new Error('Failed to fetch status');
    }

    const data = await response.json();

    if (!data || !data.current_mission) {
      return null;
    }

    return backendToDroneState(data.current_mission, data);
  }

  /**
   * Abort current mission
   * Optionally pass playbook_id for tracking
   */
  async abortMission(playbookId?: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/mission/abort`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: playbookId ? JSON.stringify({ playbook_id: playbookId }) : undefined,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Abort failed');
    }
  }

  /**
   * List available playbooks
   */
  async listPlaybooks(): Promise<Array<{ filename: string; mission_id: string; description: string }>> {
    const response = await fetch(`${API_BASE_URL}/playbooks/list`);

    if (!response.ok) {
      throw new Error('Failed to list playbooks');
    }

    const data = await response.json();
    return data.playbooks || [];
  }

  /**
   * Get a specific playbook
   */
  async getPlaybook(filename: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/playbooks/${filename}`);

    if (!response.ok) {
      throw new Error('Playbook not found');
    }

    return response.json();
  }

  /**
   * Fetch and convert all example playbooks from the backend
   */
  async fetchPlaybooks(): Promise<Playbook[]> {
    const storedList = await this.listPlaybooks();
    if (!storedList.length) {
      return [];
    }

    const fetchers = storedList.map(async (entry) => {
      try {
        const data = await this.getPlaybook(entry.filename);
        return backendMissionToPlaybook(data);
      } catch (error) {
        console.warn(`Failed to load playbook ${entry.filename}:`, error);
        return null;
      }
    });

    const results = await Promise.all(fetchers);
    return results.filter((playbook): playbook is Playbook => Boolean(playbook));
  }

  /**
   * Parse natural language command into playbook
   */
  async parseNaturalLanguage(command: string): Promise<{
    status: string;
    playbook: any;
    note?: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/mission/parse-natural-language`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to parse command');
    }

    return response.json();
  }
}

// ============================================================================
// WEBSOCKET FOR REAL-TIME UPDATES
// ============================================================================

type WSMessageHandler = (message: {
  type: 'position_update' | 'waypoint_reached' | 'mission_complete' | 'error';
  data?: Partial<DroneState>;
  error?: string;
}) => void;

export class HeimdallWebSocket {
  private ws: WebSocket | null = null;
  private messageHandler: WSMessageHandler | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private playbookId: string;

  constructor(playbookId: string) {
    this.playbookId = playbookId;
  }

  connect() {
    try {
      this.ws = new WebSocket(`${WS_BASE_URL}/ws/mission/${this.playbookId}`);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected for mission:', this.playbookId);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (this.messageHandler) {
            this.messageHandler(message);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.attemptReconnect();
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    } else {
      console.error('Max reconnect attempts reached');
    }
  }

  onMessage(handler: WSMessageHandler) {
    this.messageHandler = handler;
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandler = null;
  }
}

// Export singleton instance
export const heimdallAPI = new HeimdallAPI();
