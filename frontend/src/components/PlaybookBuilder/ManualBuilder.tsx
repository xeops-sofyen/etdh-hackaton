import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents } from 'react-leaflet';
import type { FeatureCollection, Feature } from 'geojson';
import { useAppStore } from '../../store/useAppStore';
import styles from './ManualBuilder.module.css';

interface Waypoint {
  id: string;
  lat: number;
  lng: number;
  altitude: number;
  speed: number;
}

// Component to handle map clicks
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export const ManualBuilder = () => {
  const { addPlaybook, setBuilderOpen } = useAppStore();
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);
  const [playbookName, setPlaybookName] = useState('');
  const [missionType, setMissionType] = useState<'surveillance' | 'delivery'>('surveillance');

  const handleMapClick = (lat: number, lng: number) => {
    const newWaypoint: Waypoint = {
      id: `wp-${Date.now()}`,
      lat,
      lng,
      altitude: 100, // Default altitude in meters
      speed: 15, // Default speed in m/s
    };
    setWaypoints([...waypoints, newWaypoint]);
  };

  const handleRemoveWaypoint = (id: string) => {
    setWaypoints(waypoints.filter((wp) => wp.id !== id));
  };

  const handleUpdateWaypoint = (id: string, updates: Partial<Waypoint>) => {
    setWaypoints(
      waypoints.map((wp) => (wp.id === id ? { ...wp, ...updates } : wp))
    );
  };

  const handleSavePlaybook = () => {
    if (waypoints.length < 2) {
      alert('Please add at least 2 waypoints');
      return;
    }

    if (!playbookName.trim()) {
      alert('Please enter a playbook name');
      return;
    }

    // Convert waypoints to GeoJSON FeatureCollection
    const features: Feature[] = [];

    // Add point features for each waypoint
    waypoints.forEach((wp) => {
      features.push({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'Point',
          coordinates: [wp.lng, wp.lat],
        },
      });
    });

    // Add a LineString connecting all waypoints
    const lineCoordinates = waypoints.map((wp) => [wp.lng, wp.lat]);
    features.push({
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'LineString',
        coordinates: lineCoordinates,
      },
    });

    const route: FeatureCollection = {
      type: 'FeatureCollection',
      features,
    };

    // Estimate duration based on waypoints (rough calculation: 60 seconds per waypoint)
    const estimatedDuration = waypoints.length * 60;

    const newPlaybook = {
      id: `playbook-${Date.now()}`,
      name: playbookName,
      missionType,
      route,
      createdAt: new Date(),
      status: 'planned' as const,
      estimatedDuration,
    };

    addPlaybook(newPlaybook);
    setBuilderOpen(false);
  };

  return (
    <div className={styles.container}>
      <div className={styles.mapSection}>
        <MapContainer
          center={[49.58, 22.67]}
          zoom={13}
          className={styles.map}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          <MapClickHandler onMapClick={handleMapClick} />

          {waypoints.map((wp) => (
            <Marker key={wp.id} position={[wp.lat, wp.lng]} />
          ))}

          {waypoints.length > 1 && (
            <Polyline
              positions={waypoints.map((wp) => [wp.lat, wp.lng] as [number, number])}
              color="#10b981"
              weight={3}
              dashArray="10, 5"
            />
          )}
        </MapContainer>
      </div>

      <div className={styles.sidebar}>
        <div className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.label}>Playbook Name</label>
            <input
              type="text"
              className={styles.input}
              placeholder="Enter mission name"
              value={playbookName}
              onChange={(e) => setPlaybookName(e.target.value)}
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Mission Type</label>
            <select
              className={styles.select}
              value={missionType}
              onChange={(e) => setMissionType(e.target.value as 'surveillance' | 'delivery')}
            >
              <option value="surveillance">Surveillance</option>
              <option value="delivery">Delivery</option>
            </select>
          </div>

          <div className={styles.instructions}>
            <p>Click on the map to add waypoints. Waypoints will connect automatically in order.</p>
          </div>
        </div>

        <div className={styles.waypointList}>
          <div className={styles.waypointHeader}>
            <h3 className={styles.waypointTitle}>Waypoints ({waypoints.length})</h3>
          </div>

          {waypoints.length === 0 ? (
            <div className={styles.emptyState}>
              No waypoints yet. Click on the map to add.
            </div>
          ) : (
            waypoints.map((wp, index) => (
              <div key={wp.id} className={styles.waypoint}>
                <div className={styles.waypointHeader}>
                  <span className={styles.waypointNumber}>{index + 1}</span>
                  <button
                    className={styles.removeButton}
                    onClick={() => handleRemoveWaypoint(wp.id)}
                  >
                    ×
                  </button>
                </div>
                <div className={styles.waypointDetails}>
                  <div className={styles.waypointField}>
                    <label>Lat: {wp.lat.toFixed(5)}</label>
                  </div>
                  <div className={styles.waypointField}>
                    <label>Lng: {wp.lng.toFixed(5)}</label>
                  </div>
                  <div className={styles.waypointField}>
                    <label>Altitude (m)</label>
                    <input
                      type="number"
                      className={styles.smallInput}
                      value={wp.altitude}
                      onChange={(e) =>
                        handleUpdateWaypoint(wp.id, {
                          altitude: Number(e.target.value),
                        })
                      }
                    />
                  </div>
                  <div className={styles.waypointField}>
                    <label>Speed (m/s)</label>
                    <input
                      type="number"
                      className={styles.smallInput}
                      value={wp.speed}
                      onChange={(e) =>
                        handleUpdateWaypoint(wp.id, {
                          speed: Number(e.target.value),
                        })
                      }
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className={styles.actions}>
          <button
            className={styles.cancelButton}
            onClick={() => setBuilderOpen(false)}
          >
            Cancel
          </button>
          <button
            className={styles.saveButton}
            onClick={handleSavePlaybook}
            disabled={waypoints.length < 2 || !playbookName.trim()}
          >
            Create Playbook
          </button>
        </div>
      </div>
    </div>
  );
};
