import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, Marker, Polyline, CircleMarker } from 'react-leaflet';
import type { FeatureCollection, Point } from 'geojson';
import type { DroneState } from '../../types';
import L from 'leaflet';
import styles from './MapView.module.css';

interface MapViewProps {
  route: FeatureCollection;
  playbookId: string;
  droneState?: DroneState | null;
  center?: [number, number];
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
      <div style="transform: rotate(${heading}deg); width: 30px; height: 30px;">
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="15" cy="15" r="14" fill="#10b981" opacity="0.2"/>
          <circle cx="15" cy="15" r="10" fill="#10b981" opacity="0.4"/>
          <path d="M15 5 L20 20 L15 17 L10 20 Z" fill="#10b981" stroke="#34d399" stroke-width="1.5"/>
          <circle cx="15" cy="15" r="3" fill="#34d399"/>
        </svg>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
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
        color: '#a855f7',
        weight: 3,
        opacity: 0.7,
      }}
    />
  );
}

export const MapView = ({ route, playbookId, droneState, center = [49.58, 22.67] }: MapViewProps) => {
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
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
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
