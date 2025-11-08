import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import type { FeatureCollection } from 'geojson';
import L from 'leaflet';
import styles from './MapView.module.css';

interface MapViewProps {
  route: FeatureCollection;
  playbookId: string;
  center?: [number, number];
}

// Component to fit bounds when route changes
function FitBounds({ route }: { route: FeatureCollection }) {
  const map = useMap();

  useEffect(() => {
    if (route.features.length > 0) {
      const geoJsonLayer = L.geoJSON(route);
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [route, map]);

  return null;
}

export const MapView = ({ route, playbookId, center = [49.58, 22.67] }: MapViewProps) => {
  const mapRef = useRef(null);

  return (
    <div className={styles.mapView}>
      <MapContainer
        center={center}
        zoom={13}
        className={styles.leafletContainer}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON key={playbookId} data={route} />
        <FitBounds route={route} />
      </MapContainer>
    </div>
  );
};
