import type { FeatureCollection, Feature, Point } from 'geojson';

// Playbook - Mission definition using GeoJSON
export interface Playbook {
  id: string;
  name: string;
  missionType: 'surveillance' | 'delivery';
  route: FeatureCollection; // Mission geometry
  createdAt: Date;
  status: 'planned' | 'active' | 'completed' | 'failed';
  startedAt?: Date; // When mission was started
  completedAt?: Date; // When mission completed/failed
  estimatedDuration?: number; // Estimated duration in seconds
  metadata?: Record<string, any>; // Extensible
}

// DroneState - Live telemetry data
export interface DroneState {
  playbookId: string;
  position: Feature<Point>; // Current location
  battery: number; // Percentage
  speed: number; // m/s
  heading: number; // Degrees
  status: 'idle' | 'en_route' | 'awaiting_approval' | 'returning';
  currentWaypointIndex: number; // Progress through route
  telemetry?: Record<string, any>; // Extensible sensors
}

// Approval - Operator decision request
export interface Approval {
  id: string;
  playbookId: string;
  type: 'anomaly' | 'deviation' | 'high_risk';
  description: string;
  location?: Feature<Point>;
  timestamp: Date;
}
