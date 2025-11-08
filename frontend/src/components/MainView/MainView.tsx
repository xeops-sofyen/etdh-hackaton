import { useAppStore } from '../../store/useAppStore';
import { MapView } from '../MapView/MapView';
import styles from './MainView.module.css';

export const MainView = () => {
  const { selectedPlaybookId, playbooks, drones } = useAppStore();

  const selectedPlaybook = playbooks.find((p) => p.id === selectedPlaybookId);
  const droneState = selectedPlaybookId
    ? drones.get(selectedPlaybookId)
    : null;

  if (!selectedPlaybook) {
    return (
      <div className={styles.mainView}>
        <div className={styles.mapContainer}>
          <div className={styles.emptyState}>
            Select a playbook to view mission details
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.mainView}>
      <div className={styles.mapContainer}>
        <MapView route={selectedPlaybook.route} playbookId={selectedPlaybook.id} />
      </div>

      {selectedPlaybook.status === 'active' && droneState && (
        <>
          <div className={styles.telemetryPanel}>
            <div className={styles.telemetryItem}>
              <span className={styles.telemetryLabel}>Battery</span>
              <span className={styles.telemetryValue}>
                {droneState.battery}%
              </span>
            </div>
            <div className={styles.telemetryItem}>
              <span className={styles.telemetryLabel}>Speed</span>
              <span className={styles.telemetryValue}>
                {droneState.speed.toFixed(1)} m/s
              </span>
            </div>
            <div className={styles.telemetryItem}>
              <span className={styles.telemetryLabel}>Status</span>
              <span className={styles.telemetryValue}>{droneState.status}</span>
            </div>
            <div className={styles.telemetryItem}>
              <span className={styles.telemetryLabel}>Waypoint</span>
              <span className={styles.telemetryValue}>
                {droneState.currentWaypointIndex + 1}
              </span>
            </div>
          </div>

          <div className={styles.controlsPanel}>
            <button className={`${styles.button} ${styles.secondaryButton}`}>
              Pause
            </button>
            <button className={`${styles.button} ${styles.dangerButton}`}>
              Abort Mission
            </button>
          </div>
        </>
      )}

      {selectedPlaybook.status === 'planned' && (
        <div className={styles.controlsPanel}>
          <button className={`${styles.button} ${styles.primaryButton}`}>
            Start Mission
          </button>
          <button className={`${styles.button} ${styles.secondaryButton}`}>
            Edit Playbook
          </button>
        </div>
      )}
    </div>
  );
};
