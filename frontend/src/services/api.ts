/**
 * Real API Service - Connects to Heimdall Backend
 * Replaces mock services with real HTTP + WebSocket connections
 */

import type { Playbook, DroneState, Approval } from '../types';
import type { FeatureCollection } from 'geojson';

// Backend configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// ============================================================================
// TYPE CONVERTERS - Frontend GeoJSON ↔ Backend Playbook Schema
// ============================================================================

/**
 * Convert frontend Playbook (GeoJSON) to backend MissionPlaybook
 */
function playbookToBackend(playbook: Playbook) {
  // Extract waypoints from GeoJSON
  const points = playbook.route.features
    .filter((f) => f.geometry.type === 'Point')
    .map((f) => {
      const coords = f.geometry.coordinates;
      return {
        lat: coords[1],
        lon: coords[0],
        alt: 100, // Default altitude
        action: 'hover', // Default action
      };
    });

  return {
    mission_id: playbook.id,
    description: playbook.name,
    waypoints: points,
    alt_m: 100,
    speed_mps: 15,
    duration_min: 30,
    actions: [],
    contingencies: {
      low_battery: 'return_to_base',
      gps_loss: 'hover',
      obstacle: 'avoid',
    },
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

// ============================================================================
// API CLASS
// ============================================================================

export class HeimdallAPI {
  /**
   * Execute a mission playbook
   */
  async executeMission(playbook: Playbook, simulate: boolean = false): Promise<{
    status: string;
    mission_id: string;
    message?: string;
  }> {
    const backendPlaybook = playbookToBackend(playbook);

    const response = await fetch(`${API_BASE_URL}/mission/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        playbook: backendPlaybook,
        simulate,
      }),
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
   */
  async abortMission(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/mission/abort`, {
      method: 'POST',
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

  constructor(private playbookId: string) {}

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
