/**
 * Custom Hook - Mission Control
 * Abstraction layer that can use either Mock or Real API
 */

import { useEffect, useRef } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Playbook } from '../types';

// Import both services
import { MockDroneWebSocket } from '../services/mockWebSocket';
import { HeimdallWebSocket, heimdallAPI } from '../services/api';

// ============================================================================
// CONFIGURATION - Toggle between Mock and Real API
// ============================================================================

const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true' || false;

console.log(`🔧 Mission Control Mode: ${USE_REAL_API ? 'REAL API' : 'MOCK'}`);

// ============================================================================
// HOOK
// ============================================================================

export function useMissionControl() {
  const { updateDrone, addApproval, updatePlaybookStatus } = useAppStore();
  const webSocketsRef = useRef<Map<string, MockDroneWebSocket | HeimdallWebSocket>>(new Map());

  /**
   * Start a mission
   */
  const startMission = async (playbook: Playbook) => {
    console.log(`Starting mission: ${playbook.id} (${USE_REAL_API ? 'REAL' : 'MOCK'})`);

    try {
      if (USE_REAL_API) {
        // ====== REAL API ======

        // 1. Execute mission on backend
        const result = await heimdallAPI.executeMission(playbook, false);
        console.log('Mission started:', result);

        // 2. Connect WebSocket for real-time updates
        const ws = new HeimdallWebSocket(playbook.id);

        ws.onMessage((message) => {
          if (message.type === 'position_update' && message.data) {
            updateDrone(playbook.id, message.data);
          } else if (message.type === 'mission_complete') {
            updatePlaybookStatus(playbook.id, 'completed');
            ws.disconnect();
          } else if (message.type === 'error') {
            console.error('Mission error:', message.error);
            updatePlaybookStatus(playbook.id, 'failed');
            ws.disconnect();
          }
        });

        ws.connect();
        webSocketsRef.current.set(playbook.id, ws);

      } else {
        // ====== MOCK API ======

        const ws = new MockDroneWebSocket(playbook.id, playbook.route, playbook.missionType);

        ws.onMessage((message) => {
          if (message.type === 'position_update' && message.data) {
            updateDrone(playbook.id, message.data);
          } else if (message.type === 'waypoint_reached') {
            console.log('Waypoint reached:', message.data?.currentWaypointIndex);
          } else if (message.type === 'approval_required' && message.approval) {
            addApproval(message.approval);
          } else if (message.type === 'mission_complete') {
            updatePlaybookStatus(playbook.id, 'completed');
            ws.disconnect();
          } else if (message.type === 'error') {
            console.error('Mission error:', message.error);
            updatePlaybookStatus(playbook.id, 'failed');
            ws.disconnect();
          }
        });

        ws.start();
        webSocketsRef.current.set(playbook.id, ws);
      }

    } catch (error) {
      console.error('Failed to start mission:', error);
      updatePlaybookStatus(playbook.id, 'failed');
      throw error;
    }
  };

  /**
   * Pause a mission
   */
  const pauseMission = async (playbookId: string) => {
    const ws = webSocketsRef.current.get(playbookId);
    if (!ws) {
      console.warn('No WebSocket found for mission:', playbookId);
      return;
    }

    if (ws instanceof MockDroneWebSocket) {
      ws.pause();
    } else {
      // For real API, send pause command via WebSocket or REST
      ws.send({ action: 'pause' });
    }
  };

  /**
   * Resume a mission
   */
  const resumeMission = async (playbookId: string) => {
    const ws = webSocketsRef.current.get(playbookId);
    if (!ws) {
      console.warn('No WebSocket found for mission:', playbookId);
      return;
    }

    if (ws instanceof MockDroneWebSocket) {
      ws.resume();
    } else {
      // For real API, send resume command
      ws.send({ action: 'resume' });
    }
  };

  /**
   * Abort a mission
   */
  const abortMission = async (playbookId: string) => {
    const ws = webSocketsRef.current.get(playbookId);

    if (USE_REAL_API) {
      // Call REST API to abort
      await heimdallAPI.abortMission();
    }

    if (ws) {
      if (ws instanceof MockDroneWebSocket) {
        ws.abort();
      } else {
        ws.send({ action: 'abort' });
      }

      ws.disconnect();
      webSocketsRef.current.delete(playbookId);
    }

    updatePlaybookStatus(playbookId, 'failed');
  };

  /**
   * Approve an action
   */
  const approveAction = async (approvalId: string, playbookId: string) => {
    console.log('Approving action:', approvalId);

    const ws = webSocketsRef.current.get(playbookId);
    if (ws instanceof MockDroneWebSocket) {
      ws.resume(); // Resume mission after approval
    } else if (ws) {
      ws.send({ action: 'approve', approvalId });
    }
  };

  /**
   * Deny an action
   */
  const denyAction = async (approvalId: string, playbookId: string) => {
    console.log('Denying action:', approvalId);

    const ws = webSocketsRef.current.get(playbookId);
    if (ws) {
      if (ws instanceof MockDroneWebSocket) {
        ws.abort();
      } else {
        ws.send({ action: 'deny', approvalId });
      }

      ws.disconnect();
      webSocketsRef.current.delete(playbookId);
    }

    updatePlaybookStatus(playbookId, 'failed');
  };

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      // Disconnect all WebSockets
      webSocketsRef.current.forEach((ws) => {
        ws.disconnect();
      });
      webSocketsRef.current.clear();
    };
  }, []);

  return {
    startMission,
    pauseMission,
    resumeMission,
    abortMission,
    approveAction,
    denyAction,
    isRealAPI: USE_REAL_API,
  };
}
