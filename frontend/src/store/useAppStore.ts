import { create } from 'zustand';
import type { Playbook, DroneState, Approval } from '../types';
import { mockPlaybooks } from '../utils/mockData';

interface AppStore {
  // Playbook management
  playbooks: Playbook[];
  selectedPlaybookId: string | null;
  addPlaybook: (playbook: Playbook) => void;
  selectPlaybook: (id: string) => void;

  // Live drone states (from WebSocket)
  drones: Map<string, DroneState>; // Keyed by playbookId
  updateDrone: (playbookId: string, state: Partial<DroneState>) => void;

  // Approvals
  pendingApprovals: Approval[];
  approveAction: (approvalId: string) => void;
  denyAction: (approvalId: string) => void;
  addApproval: (approval: Approval) => void;

  // UI state
  isBuilderOpen: boolean;
  activeTab: 'active' | 'planned' | 'past';
  setBuilderOpen: (open: boolean) => void;
  setActiveTab: (tab: 'active' | 'planned' | 'past') => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // Initial state - preload with mock data
  playbooks: mockPlaybooks,
  selectedPlaybookId: null,
  drones: new Map(),
  pendingApprovals: [],
  isBuilderOpen: false,
  activeTab: 'active',

  // Playbook actions
  addPlaybook: (playbook) =>
    set((state) => ({
      playbooks: [...state.playbooks, playbook],
    })),

  selectPlaybook: (id) =>
    set({
      selectedPlaybookId: id,
    }),

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
    set((state) => ({
      pendingApprovals: state.pendingApprovals.filter(
        (approval) => approval.id !== approvalId
      ),
    })),

  denyAction: (approvalId) =>
    set((state) => ({
      pendingApprovals: state.pendingApprovals.filter(
        (approval) => approval.id !== approvalId
      ),
    })),

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
