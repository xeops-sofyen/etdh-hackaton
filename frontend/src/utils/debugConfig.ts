/**
 * Debug configuration for development and testing
 * Access from browser console: window.droneDebug
 *
 * Examples:
 *   window.droneDebug.speedMultiplier = 10  // 10x faster
 *   window.droneDebug.approvalChance = 0.5  // 50% chance
 *   window.droneDebug.approvalProgress = 0.2  // At 20% progress
 */

export interface DebugConfig {
  // Speed multiplier for drone movement (1 = normal, 10 = 10x faster)
  speedMultiplier: number;

  // Chance of approval request per tick (0.05 = 5%, 0.5 = 50%)
  approvalChance: number;

  // Progress threshold to trigger approval (0.2 = 20% of waypoint, 1.0 = at waypoint)
  // Set to null to only trigger at waypoint reached
  approvalProgress: number | null;

  // Battery drain multiplier (1 = normal, 0 = no drain, 2 = 2x drain)
  batteryDrainMultiplier: number;
}

export const debugConfig: DebugConfig = {
  speedMultiplier: 1,
  approvalChance: 0.05,
  approvalProgress: null,
  batteryDrainMultiplier: 1,
};

// Expose to window for console access
if (typeof window !== 'undefined') {
  (window as any).droneDebug = debugConfig;
  console.log(
    '%c🚁 Drone Debug Mode Available',
    'color: #10b981; font-weight: bold; font-size: 14px;'
  );
  console.log(
    '%cAccess via window.droneDebug',
    'color: #6b7280; font-size: 12px;'
  );
  console.log('Examples:');
  console.log('  window.droneDebug.speedMultiplier = 10  // 10x faster');
  console.log('  window.droneDebug.approvalChance = 0.5   // 50% chance');
  console.log('  window.droneDebug.approvalProgress = 0.2 // At 20% waypoint progress');
  console.log('  window.droneDebug.batteryDrainMultiplier = 0 // No battery drain');
}
