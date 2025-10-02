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
export declare class LogisticsDashboardService {
    private metrics;
    private subscribers;
    getMetrics(tenantId: string): DashboardMetrics;
    subscribe(callback: (update: RealtimeUpdate) => void): () => void;
    private notifySubscribers;
    updateMetrics(update: Partial<DashboardMetrics>): void;
    handleEvent(eventType: string, data: any): void;
    private mapEventToType;
    private mapEventToAction;
}
//# sourceMappingURL=dashboard-service.d.ts.map