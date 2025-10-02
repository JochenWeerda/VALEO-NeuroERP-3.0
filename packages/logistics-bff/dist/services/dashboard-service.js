"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LogisticsDashboardService = void 0;
class LogisticsDashboardService {
    constructor() {
        this.metrics = {
            totalShipments: 0,
            activeRoutes: 0,
            completedDeliveries: 0,
            pendingDispatches: 0,
            vehicleUtilization: 0,
            onTimeDelivery: 0
        };
        this.subscribers = [];
    }
    // Get dashboard metrics
    getMetrics(tenantId) {
        return { ...this.metrics };
    }
    // Subscribe to real-time updates
    subscribe(callback) {
        this.subscribers.push(callback);
        return () => {
            const index = this.subscribers.indexOf(callback);
            if (index > -1) {
                this.subscribers.splice(index, 1);
            }
        };
    }
    // Notify subscribers of updates
    notifySubscribers(update) {
        this.subscribers.forEach(callback => callback(update));
    }
    // Update metrics (called by domain events)
    updateMetrics(update) {
        this.metrics = { ...this.metrics, ...update };
    }
    // Handle real-time events
    handleEvent(eventType, data) {
        const update = {
            type: this.mapEventToType(eventType),
            action: this.mapEventToAction(eventType),
            data,
            timestamp: new Date().toISOString()
        };
        this.notifySubscribers(update);
    }
    mapEventToType(eventType) {
        if (eventType.includes('shipment'))
            return 'shipment';
        if (eventType.includes('route'))
            return 'route';
        if (eventType.includes('dispatch'))
            return 'dispatch';
        return 'alert';
    }
    mapEventToAction(eventType) {
        if (eventType.includes('created'))
            return 'created';
        if (eventType.includes('updated') || eventType.includes('changed'))
            return 'updated';
        if (eventType.includes('completed') || eventType.includes('delivered'))
            return 'completed';
        if (eventType.includes('cancelled'))
            return 'cancelled';
        return 'updated';
    }
}
exports.LogisticsDashboardService = LogisticsDashboardService;
//# sourceMappingURL=dashboard-service.js.map