
export interface DashboardMetrics {
  totalShipments: number;
  activeRoutes: number;
  completedDeliveries: number;
  pendingDispatches: number;
  vehicleUtilization: number;
  onTimeDelivery: number;
}

export interface RealtimeUpdate {
  type: 'shipment' | 'route' | 'dispatch' | 'alert';
  action: 'created' | 'updated' | 'completed' | 'cancelled';
  data: any;
  timestamp: string;
}

export class LogisticsDashboardService {
  private metrics: DashboardMetrics = {
    totalShipments: 0,
    activeRoutes: 0,
    completedDeliveries: 0,
    pendingDispatches: 0,
    vehicleUtilization: 0,
    onTimeDelivery: 0
  };

  private subscribers: Array<(update: RealtimeUpdate) => void> = [];

  // Get dashboard metrics
  getMetrics(tenantId: string): DashboardMetrics {
    return { ...this.metrics };
  }

  // Subscribe to real-time updates
  subscribe(callback: (update: RealtimeUpdate) => void): () => void {
    this.subscribers.push(callback);
    return () => {
      const index = this.subscribers.indexOf(callback);
      if (index > -1) {
        this.subscribers.splice(index, 1);
      }
    };
  }

  // Notify subscribers of updates
  private notifySubscribers(update: RealtimeUpdate): void {
    this.subscribers.forEach(callback => callback(update));
  }

  // Update metrics (called by domain events)
  updateMetrics(update: Partial<DashboardMetrics>): void {
    this.metrics = { ...this.metrics, ...update };
  }

  // Handle real-time events
  handleEvent(eventType: string, data: any): void {
    const update: RealtimeUpdate = {
      type: this.mapEventToType(eventType),
      action: this.mapEventToAction(eventType),
      data,
      timestamp: new Date().toISOString()
    };

    this.notifySubscribers(update);
  }

  private mapEventToType(eventType: string): RealtimeUpdate['type'] {
    if (eventType.includes('shipment')) return 'shipment';
    if (eventType.includes('route')) return 'route';
    if (eventType.includes('dispatch')) return 'dispatch';
    return 'alert';
  }

  private mapEventToAction(eventType: string): RealtimeUpdate['action'] {
    if (eventType.includes('created')) return 'created';
    if (eventType.includes('updated') || eventType.includes('changed')) return 'updated';
    if (eventType.includes('completed') || eventType.includes('delivered')) return 'completed';
    if (eventType.includes('cancelled')) return 'cancelled';
    return 'updated';
  }
}