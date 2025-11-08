import type { Playbook } from '../types';
import type { FeatureCollection } from 'geojson';

// Mock playbook data based on the design document
export const mockPlaybooks: Playbook[] = [
  {
    id: 'pb-001',
    name: 'Central Park Patrol',
    missionType: 'surveillance',
    status: 'active',
    createdAt: new Date('2025-11-08T00:30:00'),
    startedAt: new Date(Date.now() - 30000), // Started 30 seconds ago
    estimatedDuration: 180, // 3 minutes
    route: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 0 },
          geometry: {
            type: 'Point',
            coordinates: [22.676025735635818, 49.58809075009475],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 1 },
          geometry: {
            type: 'Point',
            coordinates: [22.650759135512743, 49.57580919435844],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 2 },
          geometry: {
            type: 'Point',
            coordinates: [22.67371444036104, 49.55304323176125],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'route' },
          geometry: {
            type: 'LineString',
            coordinates: [
              [22.676025735635818, 49.58809075009475],
              [22.650759135512743, 49.57580919435844],
              [22.67371444036104, 49.55304323176125],
            ],
          },
        },
      ],
    } as FeatureCollection,
    metadata: {
      altitude: 100,
      patternType: 'perimeter',
    },
  },
  {
    id: 'pb-002',
    name: 'Warehouse Delivery Route',
    missionType: 'delivery',
    status: 'planned',
    createdAt: new Date('2025-11-08T01:00:00'),
    estimatedDuration: 120, // 2 minutes
    route: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 0, label: 'Pickup' },
          geometry: {
            type: 'Point',
            coordinates: [22.68, 49.59],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 1, label: 'Dropoff' },
          geometry: {
            type: 'Point',
            coordinates: [22.65, 49.56],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'route' },
          geometry: {
            type: 'LineString',
            coordinates: [
              [22.68, 49.59],
              [22.65, 49.56],
            ],
          },
        },
      ],
    } as FeatureCollection,
    metadata: {
      altitude: 120,
      packageWeight: '2kg',
    },
  },
  {
    id: 'pb-003',
    name: 'River Surveillance',
    missionType: 'surveillance',
    status: 'planned',
    createdAt: new Date('2025-11-07T22:15:00'),
    estimatedDuration: 240, // 4 minutes
    route: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 0 },
          geometry: {
            type: 'Point',
            coordinates: [22.66, 49.585],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 1 },
          geometry: {
            type: 'Point',
            coordinates: [22.665, 49.58],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 2 },
          geometry: {
            type: 'Point',
            coordinates: [22.67, 49.575],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 3 },
          geometry: {
            type: 'Point',
            coordinates: [22.675, 49.57],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'route' },
          geometry: {
            type: 'LineString',
            coordinates: [
              [22.66, 49.585],
              [22.665, 49.58],
              [22.67, 49.575],
              [22.675, 49.57],
            ],
          },
        },
      ],
    } as FeatureCollection,
    metadata: {
      altitude: 80,
      patternType: 'linear',
    },
  },
  {
    id: 'pb-004',
    name: 'East District Patrol',
    missionType: 'surveillance',
    status: 'completed',
    createdAt: new Date('2025-11-07T18:00:00'),
    estimatedDuration: 90, // 1.5 minutes
    route: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 0 },
          geometry: {
            type: 'Point',
            coordinates: [22.69, 49.58],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 1 },
          geometry: {
            type: 'Point',
            coordinates: [22.695, 49.575],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'route' },
          geometry: {
            type: 'LineString',
            coordinates: [
              [22.69, 49.58],
              [22.695, 49.575],
            ],
          },
        },
      ],
    } as FeatureCollection,
  },
  {
    id: 'pb-005',
    name: 'Medical Supply Delivery',
    missionType: 'delivery',
    status: 'failed',
    createdAt: new Date('2025-11-07T16:30:00'),
    estimatedDuration: 150, // 2.5 minutes
    route: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 0, label: 'Hospital' },
          geometry: {
            type: 'Point',
            coordinates: [22.64, 49.59],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'waypoint', index: 1, label: 'Clinic' },
          geometry: {
            type: 'Point',
            coordinates: [22.655, 49.565],
          },
        },
        {
          type: 'Feature',
          properties: { type: 'route' },
          geometry: {
            type: 'LineString',
            coordinates: [
              [22.64, 49.59],
              [22.655, 49.565],
            ],
          },
        },
      ],
    } as FeatureCollection,
    metadata: {
      altitude: 150,
      packageWeight: '500g',
      failureReason: 'Low battery - returned to base',
    },
  },
];
