import type { DroneState, Approval } from '../types';
import type { Point, FeatureCollection } from 'geojson';
import { debugConfig } from '../utils/debugConfig';

type MessageHandler = (message: WebSocketMessage) => void;

interface WebSocketMessage {
  type: 'position_update' | 'waypoint_reached' | 'approval_required' | 'mission_complete' | 'error';
  playbookId: string;
  data?: Partial<DroneState>;
  approval?: Approval;
  error?: string;
}

export class MockDroneWebSocket {
  private interval: ReturnType<typeof setInterval> | null = null;
  private playbookId: string;
  private route: FeatureCollection;
  private missionType: 'surveillance' | 'delivery';
  private currentWaypointIndex: number = 0;
  private progress: number = 0; // 0-1 progress between current and next waypoint
  private battery: number = 100;
  private isRunning: boolean = false;
  private messageHandler: MessageHandler | null = null;
  private waypoints: [number, number][] = [];

  constructor(playbookId: string, route: FeatureCollection, missionType: 'surveillance' | 'delivery') {
    this.playbookId = playbookId;
    this.route = route;
    this.missionType = missionType;
    this.extractWaypoints();
  }

  private extractWaypoints() {
    // Extract waypoints from GeoJSON
    this.waypoints = this.route.features
      .filter((f) => f.geometry.type === 'Point')
      .map((f) => {
        const coords = (f.geometry as Point).coordinates;
        return [coords[1], coords[0]] as [number, number]; // lat, lng
      });
  }

  onMessage(handler: MessageHandler) {
    this.messageHandler = handler;
  }

  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.currentWaypointIndex = 0;
    this.progress = 0;
    this.battery = 100;

    // Use debug speed multiplier (higher = faster updates)
    const interval = 1000 / debugConfig.speedMultiplier;
    this.interval = setInterval(() => {
      this.tick();
    }, interval);
  }

  pause() {
    this.isRunning = false;
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }

    // Send final update with speed 0 when paused
    const position = this.interpolatePosition();
    const heading = this.calculateHeading();

    this.sendMessage({
      type: 'position_update',
      playbookId: this.playbookId,
      data: {
        playbookId: this.playbookId,
        position: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'Point',
            coordinates: [position[1], position[0]],
          },
        },
        battery: Math.round(this.battery),
        speed: 0, // Speed is 0 when paused
        heading: Math.round(heading),
        status: 'idle',
        currentWaypointIndex: this.currentWaypointIndex,
      },
    });
  }

  resume() {
    if (this.isRunning) return;
    this.start();
  }

  abort() {
    this.pause();
    this.sendMessage({
      type: 'error',
      playbookId: this.playbookId,
      error: 'Mission aborted by operator',
    });
  }

  disconnect() {
    this.pause();
    this.messageHandler = null;
  }

  private tick() {
    if (!this.isRunning || this.waypoints.length === 0) return;

    // Update progress (move 2% per tick, multiplied by speed)
    const progressIncrement = 0.02 * debugConfig.speedMultiplier;
    this.progress += progressIncrement;

    // Battery drain (0.5% per tick, affected by multiplier)
    const batteryDrain = 0.5 * debugConfig.batteryDrainMultiplier;
    this.battery = Math.max(0, this.battery - batteryDrain);

    // Check for battery depletion
    if (this.battery <= 0) {
      this.pause();
      this.sendMessage({
        type: 'error',
        playbookId: this.playbookId,
        error: 'Battery depleted - mission aborted',
      });
      return;
    }

    // Check if reached next waypoint
    if (this.progress >= 1) {
      this.progress = 0;
      this.currentWaypointIndex++;

      // Check if mission complete (delivery missions only)
      if (this.missionType === 'delivery' && this.currentWaypointIndex >= this.waypoints.length) {
        this.pause();
        this.sendMessage({
          type: 'mission_complete',
          playbookId: this.playbookId,
        });
        return;
      }

      // Handle patrol looping for surveillance missions
      // When we've passed the last waypoint, we're now on the "return to base" segment
      // The next tick will reset us to 0 after completing this segment
      if (this.missionType === 'surveillance' && this.currentWaypointIndex > this.waypoints.length) {
        this.currentWaypointIndex = 0; // Now actually loop back
      }

      if (this.currentWaypointIndex < this.waypoints.length) {
        this.sendMessage({
          type: 'waypoint_reached',
          playbookId: this.playbookId,
          data: {
            currentWaypointIndex: this.currentWaypointIndex,
          },
        });

        // Check for approval at waypoint if approvalProgress is null (default behavior)
        if (debugConfig.approvalProgress === null) {
          if (Math.random() < debugConfig.approvalChance && this.currentWaypointIndex < this.waypoints.length - 1) {
            this.sendApprovalRequest();
          }
        }
      }
    }

    // Check for approval at specific progress point (debug mode)
    if (debugConfig.approvalProgress !== null) {
      const prevProgress = this.progress - progressIncrement;
      const crossedThreshold = prevProgress < debugConfig.approvalProgress && this.progress >= debugConfig.approvalProgress;

      if (crossedThreshold && Math.random() < debugConfig.approvalChance && this.currentWaypointIndex < this.waypoints.length - 1) {
        this.sendApprovalRequest();
      }
    }

    // Interpolate position
    const position = this.interpolatePosition();
    const heading = this.calculateHeading();
    const speed = 15 + Math.random() * 5; // 15-20 m/s

    // Send position update
    this.sendMessage({
      type: 'position_update',
      playbookId: this.playbookId,
      data: {
        playbookId: this.playbookId,
        position: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'Point',
            coordinates: [position[1], position[0]], // lng, lat for GeoJSON
          },
        },
        battery: Math.round(this.battery),
        speed: parseFloat(speed.toFixed(1)),
        heading: Math.round(heading),
        status: 'en_route',
        currentWaypointIndex: this.currentWaypointIndex,
      },
    });
  }

  private interpolatePosition(): [number, number] {
    // Special case: returning to base (surveillance patrol loop)
    if (this.currentWaypointIndex === this.waypoints.length) {
      const current = this.waypoints[this.waypoints.length - 1]; // Last waypoint
      const next = this.waypoints[0]; // First waypoint

      const lat = current[0] + (next[0] - current[0]) * this.progress;
      const lng = current[1] + (next[1] - current[1]) * this.progress;

      return [lat, lng];
    }

    if (this.currentWaypointIndex >= this.waypoints.length - 1) {
      return this.waypoints[this.waypoints.length - 1];
    }

    const current = this.waypoints[this.currentWaypointIndex];
    const next = this.waypoints[this.currentWaypointIndex + 1];

    const lat = current[0] + (next[0] - current[0]) * this.progress;
    const lng = current[1] + (next[1] - current[1]) * this.progress;

    return [lat, lng];
  }

  private calculateHeading(): number {
    // Special case: returning to base (surveillance patrol loop)
    if (this.currentWaypointIndex === this.waypoints.length) {
      const current = this.waypoints[this.waypoints.length - 1]; // Last waypoint
      const next = this.waypoints[0]; // First waypoint

      const dLat = next[0] - current[0];
      const dLng = next[1] - current[1];

      let heading = Math.atan2(dLng, dLat) * (180 / Math.PI);
      heading = (heading + 360) % 360;

      return heading;
    }

    if (this.currentWaypointIndex >= this.waypoints.length - 1) {
      return 0;
    }

    const current = this.waypoints[this.currentWaypointIndex];
    const next = this.waypoints[this.currentWaypointIndex + 1];

    const dLat = next[0] - current[0];
    const dLng = next[1] - current[1];

    // Calculate bearing in degrees
    let heading = Math.atan2(dLng, dLat) * (180 / Math.PI);
    heading = (heading + 360) % 360; // Normalize to 0-360

    return heading;
  }

  private sendApprovalRequest() {
    // Pause drone while waiting for approval
    this.pause();

    const approvalTypes: Array<'anomaly' | 'deviation' | 'high_risk'> = [
      'anomaly',
      'deviation',
      'high_risk',
    ];
    const type = approvalTypes[Math.floor(Math.random() * approvalTypes.length)];

    const descriptions = {
      anomaly: 'Unusual thermal signature detected in patrol area',
      deviation: 'Strong wind detected, requesting route adjustment',
      high_risk: 'Approaching restricted airspace, requesting clearance',
    };

    const position = this.interpolatePosition();

    const approval: Approval = {
      id: `approval-${Date.now()}`,
      playbookId: this.playbookId,
      type,
      description: descriptions[type],
      location: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'Point',
          coordinates: [position[1], position[0]],
        },
      },
      timestamp: new Date(),
    };

    this.sendMessage({
      type: 'approval_required',
      playbookId: this.playbookId,
      approval,
    });
  }

  private sendMessage(message: WebSocketMessage) {
    if (this.messageHandler) {
      this.messageHandler(message);
    }
  }
}
