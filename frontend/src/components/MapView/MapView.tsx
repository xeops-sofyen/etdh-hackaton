import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, ImageOverlay, GeoJSON, useMap, Marker, Polyline, CircleMarker } from 'react-leaflet';
import type { FeatureCollection, Point } from 'geojson';
import type { DroneState } from '../../types';
import L from 'leaflet';
import styles from './MapView.module.css';

// Define the sector bounds (coordinates matching the aerial image area)
// Image dimensions: 1456 × 970 (aspect ratio ~1.5:1)
// Bounds adjusted to prevent distortion at latitude ~49.5°
const SECTOR_BOUNDS: [[number, number], [number, number]] = [
  [49.55, 22.61], // Southwest corner
  [49.60, 22.73], // Northeast corner
];

interface MapViewProps {
  route: FeatureCollection;
  playbookId: string;
  droneState?: DroneState | null;
  center?: [number, number];
}

// Tactical grid overlay
function TacticalGrid() {
  const map = useMap();
  const [gridLines, setGridLines] = useState<React.ReactElement[]>([]);

  useEffect(() => {
    const bounds = map.getBounds();
    const lines: React.ReactElement[] = [];

    // Calculate grid spacing (every 0.01 degrees)
    const latSpacing = 0.01;
    const lngSpacing = 0.01;

    // Vertical lines (longitude)
    for (let lng = Math.floor(bounds.getWest() / lngSpacing) * lngSpacing; lng <= bounds.getEast(); lng += lngSpacing) {
      lines.push(
        <Polyline
          key={`v-${lng}`}
          positions={[
            [bounds.getSouth(), lng],
            [bounds.getNorth(), lng],
          ]}
          pathOptions={{
            color: '#10b981',
            weight: 1,
            opacity: 0.2,
          }}
        />
      );
    }

    // Horizontal lines (latitude)
    for (let lat = Math.floor(bounds.getSouth() / latSpacing) * latSpacing; lat <= bounds.getNorth(); lat += latSpacing) {
      lines.push(
        <Polyline
          key={`h-${lat}`}
          positions={[
            [lat, bounds.getWest()],
            [lat, bounds.getEast()],
          ]}
          pathOptions={{
            color: '#10b981',
            weight: 1,
            opacity: 0.2,
          }}
        />
      );
    }

    setGridLines(lines);
  }, [map]);

  return <>{gridLines}</>;
}

// Component to fit bounds when route changes
function FitBounds({ route, droneState }: { route: FeatureCollection; droneState?: DroneState | null }) {
  const map = useMap();
  const hasDroneStateRef = useRef(false);

  useEffect(() => {
    const hasDroneState = !!droneState;
    const droneStateJustAppeared = !hasDroneStateRef.current && hasDroneState;
    hasDroneStateRef.current = hasDroneState;

    if (route.features.length > 0) {
      const geoJsonLayer = L.geoJSON(route);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        // If telemetry panel just appeared, invalidate map size first
        if (droneStateJustAppeared) {
          setTimeout(() => {
            map.invalidateSize();
            map.fitBounds(bounds, {
              padding: [80, 80],
              maxZoom: 15,
            });
          }, 100); // Small delay to let DOM update
        } else {
          map.fitBounds(bounds, {
            padding: [80, 80],
            maxZoom: 15, // Prevent zooming too close on small routes
          });
        }
      }
    }
  }, [route, map, droneState]);

  return null;
}

// Create custom drone icon
const createDroneIcon = (heading: number) => {
  return L.divIcon({
    className: 'custom-drone-icon',
    html: `
      <div style="transform: rotate(${heading}deg); width: 50px; height: 50px;">
        <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Outer glow rings -->
          <circle cx="25" cy="25" r="22" fill="#00d9ff" opacity="0.15"/>
          <circle cx="25" cy="25" r="18" fill="#00d9ff" opacity="0.25"/>
          <circle cx="25" cy="25" r="14" fill="#00d9ff" opacity="0.35"/>

          <!-- Center core -->
          <circle cx="25" cy="25" r="5" fill="#ffffff" stroke="#0a0e14" stroke-width="2"/>
          <circle cx="25" cy="25" r="3" fill="#00d9ff"/>
        </svg>
      </div>
    `,
    iconSize: [50, 50],
    iconAnchor: [25, 25],
  });
};

// Component to track and display drone path trail
function DronePathTrail({ droneState, route }: { droneState: DroneState; route: FeatureCollection }) {
  const [pathPoints, setPathPoints] = useState<[number, number][]>([]);
  const [initialized, setInitialized] = useState(false);

  // Initialize with starting waypoint position
  useEffect(() => {
    if (!initialized && route.features.length > 0) {
      const firstWaypoint = route.features.find((f) => f.geometry.type === 'Point');
      if (firstWaypoint) {
        const coords = (firstWaypoint.geometry as Point).coordinates;
        setPathPoints([[coords[1], coords[0]]]);
        setInitialized(true);
      }
    }
  }, [initialized, route]);

  useEffect(() => {
    if (droneState.position) {
      const coords = (droneState.position.geometry as Point).coordinates;
      const latLng: [number, number] = [coords[1], coords[0]];

      setPathPoints((prev) => {
        // Keep last 50 points
        const newPoints = [...prev, latLng];
        return newPoints.slice(-50);
      });
    }
  }, [droneState.position]);

  if (pathPoints.length < 2) return null;

  return (
    <Polyline
      positions={pathPoints}
      pathOptions={{
        color: '#ef4444',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 5',
      }}
    />
  );
}

export const MapView = ({ route, playbookId, droneState, center = [49.575, 22.67] }: MapViewProps) => {
  const mapRef = useRef(null);

  // Extract drone position
  const dronePosition = droneState?.position
    ? ((droneState.position.geometry as Point).coordinates as [number, number])
    : null;

  return (
    <div className={styles.mapView}>
      <MapContainer
        center={center}
        zoom={13}
        className={styles.leafletContainer}
        ref={mapRef}
      >
        {/* Sector aerial image overlay */}
        <ImageOverlay
          url="/sector.jpg"
          bounds={SECTOR_BOUNDS}
          opacity={1}
        />

        {/* Tactical grid overlay */}
        <TacticalGrid />
        <GeoJSON
          key={playbookId}
          data={route}
          style={() => ({
            color: '#10b981',
            weight: 3,
            opacity: 0.8,
          })}
        />
        <FitBounds route={route} droneState={droneState} />

        {/* Render waypoint markers */}
        {route.features
          .filter((f) => f.geometry.type === 'Point')
          .map((feature, index) => {
            const coords = (feature.geometry as Point).coordinates;
            const isCurrentWaypoint = droneState?.currentWaypointIndex === index;
            const isCompletedWaypoint = droneState && droneState.currentWaypointIndex > index;

            return (
              <CircleMarker
                key={`waypoint-${index}`}
                center={[coords[1], coords[0]]}
                radius={8}
                pathOptions={{
                  color: isCurrentWaypoint ? '#fbbf24' : isCompletedWaypoint ? '#34d399' : '#60a5fa',
                  fillColor: isCurrentWaypoint ? '#fbbf24' : isCompletedWaypoint ? '#34d399' : '#60a5fa',
                  fillOpacity: 0.9,
                  weight: 3,
                }}
              >
              </CircleMarker>
            );
          })}

        {/* Render drone marker and path trail */}
        {droneState && dronePosition && (
          <>
            <DronePathTrail droneState={droneState} route={route} />
            <Marker
              position={[dronePosition[1], dronePosition[0]]}
              icon={createDroneIcon(droneState.heading || 0)}
            />
          </>
        )}
      </MapContainer>
    </div>
  );
};
