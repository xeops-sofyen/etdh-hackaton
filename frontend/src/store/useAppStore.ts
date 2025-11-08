import { create } from 'zustand';
import type { Playbook, DroneState, Approval } from '../types';
import { mockPlaybooks } from '../utils/mockData';

// Only use mock playbooks if REAL API is disabled
const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true';
const initialPlaybooks = USE_REAL_API ? [] : mockPlaybooks;

console.log(`📦 AppStore: ${USE_REAL_API ? 'REAL API mode - no mock playbooks' : `MOCK mode - ${mockPlaybooks.length} mock playbooks loaded`}`);

interface AppStore {
  // Playbook management
  playbooks: Playbook[];
  selectedPlaybookId: string | null;
  addPlaybook: (playbook: Playbook) => void;
  selectPlaybook: (id: string) => void;
  updatePlaybookStatus: (id: string, status: Playbook['status']) => void;

  // Live drone states (from WebSocket)
  drones: Map<string, DroneState>; // Keyed by playbookId
  updateDrone: (playbookId: string, state: Partial<DroneState>) => void;

  // Mission control
  startMission: (playbookId: string) => void;
  pauseMission: (playbookId: string) => void;
  abortMission: (playbookId: string) => void;

  // Approvals
  pendingApprovals: Approval[];
  approvalDecisions: Map<string, { decision: 'approved' | 'denied', playbookId: string }>;
  approveAction: (approvalId: string) => void;
  denyAction: (approvalId: string) => void;
  addApproval: (approval: Approval) => void;
  clearApprovalDecision: (approvalId: string) => void;

  // UI state
  isBuilderOpen: boolean;
  activeTab: 'active' | 'planned' | 'past';
  setBuilderOpen: (open: boolean) => void;
  setActiveTab: (tab: 'active' | 'planned' | 'past') => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // Initial state - preload with mock data ONLY in mock mode
  playbooks: initialPlaybooks,
  selectedPlaybookId: null,
  drones: new Map(),
  pendingApprovals: [],
  approvalDecisions: new Map(),
  isBuilderOpen: false,
  activeTab: 'active',

  // Playbook actions
  addPlaybook: (playbook) =>
    set((state) => {
      if (state.playbooks.some((p) => p.id === playbook.id)) {
        return state;
      }
      return {
        playbooks: [...state.playbooks, playbook],
      };
    }),

  selectPlaybook: (id) =>
    set({
      selectedPlaybookId: id,
    }),

  updatePlaybookStatus: (id, status) =>
    set((state) => ({
      playbooks: state.playbooks.map((p) =>
        p.id === id
          ? {
              ...p,
              status,
              completedAt:
                status === 'completed' || status === 'failed'
                  ? new Date()
                  : p.completedAt,
            }
          : p
      ),
    })),

  // Mission control actions
  startMission: (playbookId) =>
    set((state) => ({
      playbooks: state.playbooks.map((p) =>
        p.id === playbookId
          ? {
              ...p,
              status: 'active',
              startedAt: new Date(),
              completedAt: undefined,
            }
          : p
      ),
    })),

  pauseMission: (playbookId) =>
    set((state) => {
      // Keep as active but update drone status to idle
      const newDrones = new Map(state.drones);
      const existingDrone = newDrones.get(playbookId);
      if (existingDrone) {
        newDrones.set(playbookId, {
          ...existingDrone,
          status: 'idle',
        });
      }
      return { drones: newDrones };
    }),

  abortMission: (playbookId) =>
    set((state) => ({
      playbooks: state.playbooks.map((p) =>
        p.id === playbookId
          ? { ...p, status: 'failed', completedAt: new Date() }
          : p
      ),
    })),

  // Drone actions
  updateDrone: (playbookId, droneState) =>
    set((state) => {
      const newDrones = new Map(state.drones);
      const existingDrone = newDrones.get(playbookId);

      newDrones.set(playbookId, {
        ...existingDrone,
        ...droneState,
        playbookId,
      } as DroneState);

      return { drones: newDrones };
    }),

  // Approval actions
  addApproval: (approval) =>
    set((state) => ({
      pendingApprovals: [...state.pendingApprovals, approval],
    })),

  approveAction: (approvalId) =>
    set((state) => {
      const approval = state.pendingApprovals.find((a) => a.id === approvalId);
      if (!approval) return state;

      const newDecisions = new Map(state.approvalDecisions);
      newDecisions.set(approvalId, {
        decision: 'approved',
        playbookId: approval.playbookId,
      });

      return {
        pendingApprovals: state.pendingApprovals.filter(
          (a) => a.id !== approvalId
        ),
        approvalDecisions: newDecisions,
      };
    }),

  denyAction: (approvalId) =>
    set((state) => {
      const approval = state.pendingApprovals.find((a) => a.id === approvalId);
      if (!approval) return state;

      const newDecisions = new Map(state.approvalDecisions);
      newDecisions.set(approvalId, {
        decision: 'denied',
        playbookId: approval.playbookId,
      });

      return {
        pendingApprovals: state.pendingApprovals.filter(
          (a) => a.id !== approvalId
        ),
        approvalDecisions: newDecisions,
      };
    }),

  clearApprovalDecision: (approvalId) =>
    set((state) => {
      const newDecisions = new Map(state.approvalDecisions);
      newDecisions.delete(approvalId);
      return { approvalDecisions: newDecisions };
    }),

  // UI actions
  setBuilderOpen: (open) =>
    set({
      isBuilderOpen: open,
    }),

  setActiveTab: (tab) =>
    set({
      activeTab: tab,
    }),
}));
