import type { FeatureCollection, Feature } from 'geojson';
import type { Playbook } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export class MockLLMService {
  private conversation: ChatMessage[] = [];

  async chat(userMessage: string): Promise<{ message: string; playbook?: Playbook }> {
    this.conversation.push({ role: 'user', content: userMessage });

    // Pattern matching for mock responses
    const lowerMessage = userMessage.toLowerCase();

    // Check if user is describing a mission
    if (this.isFirstMessage()) {
      if (lowerMessage.includes('patrol') || lowerMessage.includes('surveillance')) {
        const response = this.generatePatrolResponse(userMessage);
        this.conversation.push({ role: 'assistant', content: response.message });
        return response;
      } else if (lowerMessage.includes('deliver') || lowerMessage.includes('delivery')) {
        const response = this.generateDeliveryResponse(userMessage);
        this.conversation.push({ role: 'assistant', content: response.message });
        return response;
      } else {
        const message = "I can help you create a drone mission! Would you like to create a patrol/surveillance mission or a delivery mission?";
        this.conversation.push({ role: 'assistant', content: message });
        return { message };
      }
    } else {
      // Follow-up conversation
      const message = "I've created your playbook based on your description. You can accept it or describe changes you'd like to make.";
      this.conversation.push({ role: 'assistant', content: message });
      return { message };
    }
  }

  private isFirstMessage(): boolean {
    return this.conversation.filter(m => m.role === 'user').length === 1;
  }

  private generatePatrolResponse(message: string): { message: string; playbook: Playbook } {
    // Generate a patrol route (rectangle around a center point)
    const centerLat = 49.58;
    const centerLng = 22.67;
    const size = 0.02; // ~2km

    const waypoints = [
      [centerLng - size, centerLat + size],
      [centerLng + size, centerLat + size],
      [centerLng + size, centerLat - size],
      [centerLng - size, centerLat - size],
      [centerLng - size, centerLat + size], // Close the loop
    ];

    const features: Feature[] = [];

    // Add point features
    waypoints.slice(0, -1).forEach((coord) => {
      features.push({
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'Point',
          coordinates: coord,
        },
      });
    });

    // Add LineString
    features.push({
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'LineString',
        coordinates: waypoints,
      },
    });

    const route: FeatureCollection = {
      type: 'FeatureCollection',
      features,
    };

    const playbook: Playbook = {
      id: `playbook-${Date.now()}`,
      name: this.extractMissionName(message) || 'Patrol Mission',
      missionType: 'surveillance',
      route,
      createdAt: new Date(),
      status: 'planned',
    };

    const responseMessage = `I've created a rectangular patrol route with 4 waypoints at 100m altitude. The drone will survey the designated area. Would you like to accept this playbook or make any changes?`;

    return { message: responseMessage, playbook };
  }

  private generateDeliveryResponse(message: string): { message: string; playbook: Playbook } {
    // Generate a simple point-to-point delivery route
    const startLat = 49.588;
    const startLng = 22.676;
    const endLat = 49.576;
    const endLng = 22.651;

    const features: Feature[] = [
      {
        type: 'Feature',
        properties: { type: 'pickup' },
        geometry: {
          type: 'Point',
          coordinates: [startLng, startLat],
        },
      },
      {
        type: 'Feature',
        properties: { type: 'dropoff' },
        geometry: {
          type: 'Point',
          coordinates: [endLng, endLat],
        },
      },
      {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: [
            [startLng, startLat],
            [endLng, endLat],
          ],
        },
      },
    ];

    const route: FeatureCollection = {
      type: 'FeatureCollection',
      features,
    };

    const playbook: Playbook = {
      id: `playbook-${Date.now()}`,
      name: this.extractMissionName(message) || 'Delivery Mission',
      missionType: 'delivery',
      route,
      createdAt: new Date(),
      status: 'planned',
    };

    const responseMessage = `I've created a delivery route from the pickup point to the dropoff location. The drone will fly direct at 100m altitude. Would you like to accept this playbook?`;

    return { message: responseMessage, playbook };
  }

  private extractMissionName(message: string): string | null {
    // Very simple extraction - look for quoted text or first few words
    const quotedMatch = message.match(/"([^"]+)"/);
    if (quotedMatch) {
      return quotedMatch[1];
    }

    // Take first 5 words if available
    const words = message.split(' ').slice(0, 5).join(' ');
    return words.length > 0 ? words : null;
  }

  resetConversation() {
    this.conversation = [];
  }
}
