import { useEffect, useRef } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { MapView } from '../MapView/MapView';
import { MockDroneWebSocket } from '../../services/mockWebSocket';
import { ApprovalQueue } from '../ApprovalQueue/ApprovalQueue';
import styles from './MainView.module.css';

export const MainView = () => {
  const {
    selectedPlaybookId,
    playbooks,
    drones,
    updateDrone,
    addApproval,
    startMission,
    pauseMission,
    abortMission,
    updatePlaybookStatus,
    approvalDecisions,
    clearApprovalDecision,
  } = useAppStore();

  const webSocketRef = useRef<MockDroneWebSocket | null>(null);

  const selectedPlaybook = playbooks.find((p) => p.id === selectedPlaybookId);
  const droneState = selectedPlaybookId
    ? drones.get(selectedPlaybookId)
    : null;

  // Handle approval decisions
  useEffect(() => {
    approvalDecisions.forEach((decision, approvalId) => {
      if (decision.playbookId === selectedPlaybookId && webSocketRef.current) {
        if (decision.decision === 'approved') {
          // Resume mission
          webSocketRef.current.resume();
        } else if (decision.decision === 'denied') {
          // Abort mission
          webSocketRef.current.abort();
          abortMission(decision.playbookId);
        }
        // Clear the decision after handling
        clearApprovalDecision(approvalId);
      }
    });
  }, [approvalDecisions, selectedPlaybookId, abortMission, clearApprovalDecision]);

  // Handle WebSocket connection for active missions
  useEffect(() => {
    if (!selectedPlaybook || selectedPlaybook.status !== 'active') {
      // Clean up existing connection if mission is not active
      if (webSocketRef.current) {
        webSocketRef.current.disconnect();
        webSocketRef.current = null;
      }
      return;
    }

    // Create WebSocket connection for active mission
    const ws = new MockDroneWebSocket(selectedPlaybook.id, selectedPlaybook.route, selectedPlaybook.missionType);

    ws.onMessage((message) => {
      switch (message.type) {
        case 'position_update':
          if (message.data) {
            updateDrone(selectedPlaybook.id, message.data);
          }
          break;

        case 'waypoint_reached':
          if (message.data) {
            updateDrone(selectedPlaybook.id, message.data);
          }
          break;

        case 'approval_required':
          if (message.approval) {
            addApproval(message.approval);
          }
          break;

        case 'mission_complete':
          updatePlaybookStatus(selectedPlaybook.id, 'completed');
          break;

        case 'error':
          console.error('Mission error:', message.error);
          break;
      }
    });

    ws.start();
    webSocketRef.current = ws;

    return () => {
      ws.disconnect();
    };
  }, [selectedPlaybook?.id, selectedPlaybook?.status]);

  // Handle mission controls
  const handleStartMission = () => {
    if (selectedPlaybookId) {
      startMission(selectedPlaybookId);
    }
  };

  const handlePauseMission = () => {
    if (selectedPlaybookId && webSocketRef.current) {
      webSocketRef.current.pause();
      pauseMission(selectedPlaybookId);
    }
  };

  const handleResumeMission = () => {
    if (webSocketRef.current) {
      webSocketRef.current.resume();
    }
  };

  const handleAbortMission = () => {
    if (selectedPlaybookId && webSocketRef.current) {
      webSocketRef.current.abort();
      abortMission(selectedPlaybookId);
    }
  };

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

  const isPaused = droneState?.status === 'idle';

  return (
    <div className={styles.mainView}>
      <div className={styles.mapContainer}>
        <MapView
          route={selectedPlaybook.route}
          playbookId={selectedPlaybook.id}
          droneState={droneState}
        />
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
            {isPaused ? (
              <button
                className={`${styles.button} ${styles.primaryButton}`}
                onClick={handleResumeMission}
              >
                Resume
              </button>
            ) : (
              <button
                className={`${styles.button} ${styles.secondaryButton}`}
                onClick={handlePauseMission}
              >
                Pause
              </button>
            )}
            <button
              className={`${styles.button} ${styles.dangerButton}`}
              onClick={handleAbortMission}
            >
              Abort Mission
            </button>
          </div>
        </>
      )}

      {selectedPlaybook.status === 'planned' && (
        <div className={styles.controlsPanel}>
          <button
            className={`${styles.button} ${styles.primaryButton}`}
            onClick={handleStartMission}
          >
            Start Mission
          </button>
          <button className={`${styles.button} ${styles.secondaryButton}`}>
            Edit Playbook
          </button>
        </div>
      )}

      <ApprovalQueue />
    </div>
  );
};
