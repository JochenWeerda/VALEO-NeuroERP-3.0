"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InMemoryLogisticsRepository = void 0;
class InMemoryLogisticsRepository {
    constructor() {
        this.shipments = {};
        this.routesById = {};
        this.routesByShipment = {};
        this.assignments = {};
        this.yardVisits = {};
        this.telemetry = {};
        this.pods = {};
        this.weighings = {};
        this.freightRates = {};
        this.carrierDocs = {};
        this.emissions = {};
        this.safetyAlerts = {};
        this.returnOrders = {};
    }
    async saveShipment(shipment) {
        const bucket = this.ensureBucket(this.shipments, shipment.tenantId);
        bucket.set(shipment.shipmentId, shipment);
    }
    async findShipmentById(tenantId, shipmentId) {
        return this.shipments[tenantId]?.get(shipmentId);
    }
    async listShipmentsByTenant(tenantId) {
        return Array.from(this.shipments[tenantId]?.values() ?? []);
    }
    async saveRoutePlan(routePlan) {
        const byId = this.ensureBucket(this.routesById, routePlan.tenantId);
        byId.set(routePlan.routeId, routePlan);
        const byShipment = this.ensureBucket(this.routesByShipment, routePlan.tenantId);
        byShipment.set(routePlan.shipmentId, routePlan);
    }
    async findRoutePlanById(tenantId, routeId) {
        return this.routesById[tenantId]?.get(routeId);
    }
    async findRoutePlanByShipmentId(tenantId, shipmentId) {
        return this.routesByShipment[tenantId]?.get(shipmentId);
    }
    async saveAssignment(assignment) {
        const bucket = this.ensureBucket(this.assignments, assignment.tenantId);
        bucket.set(assignment.routeId, assignment);
    }
    async findAssignmentByRouteId(tenantId, routeId) {
        return this.assignments[tenantId]?.get(routeId);
    }
    async saveYardVisit(visit) {
        const bucket = this.ensureBucket(this.yardVisits, visit.tenantId);
        bucket.set(visit.shipmentId, visit);
    }
    async findYardVisitByShipmentId(tenantId, shipmentId) {
        return this.yardVisits[tenantId]?.get(shipmentId);
    }
    async saveTelemetry(record) {
        const bucket = this.ensureTelemetryBucket(record.tenantId, record.vehicleId);
        bucket.unshift(record);
        if (bucket.length > 1000) {
            bucket.pop();
        }
    }
    async listRecentTelemetryByVehicle(tenantId, vehicleId, limit) {
        return (this.telemetry[tenantId]?.get(vehicleId) ?? []).slice(0, limit);
    }
    async saveProofOfDelivery(pod) {
        const bucket = this.ensureBucket(this.pods, pod.tenantId);
        bucket.set(pod.shipmentId, pod);
    }
    async saveWeighing(record) {
        const bucket = this.ensureBucket(this.weighings, record.tenantId);
        bucket.set(record.weighingId, record);
    }
    async saveFreightRate(rate) {
        const bucket = this.ensureBucket(this.freightRates, rate.tenantId);
        bucket.set(rate.shipmentId, rate);
    }
    async saveCarrierDocument(document) {
        const bucket = this.ensureBucket(this.carrierDocs, document.tenantId);
        bucket.set(document.documentId, document);
    }
    async saveEmission(record) {
        const bucket = this.ensureBucket(this.emissions, record.tenantId);
        bucket.set(record.shipmentId, record);
    }
    async saveSafetyAlert(alert) {
        const bucket = this.ensureBucket(this.safetyAlerts, alert.tenantId);
        bucket.set(alert.alertId, alert);
    }
    async saveReturnOrder(order) {
        const bucket = this.ensureBucket(this.returnOrders, order.tenantId);
        bucket.set(order.returnId, order);
    }
    async findReturnOrderById(tenantId, returnId) {
        return this.returnOrders[tenantId]?.get(returnId);
    }
    ensureBucket(store, tenantId) {
        if (!store[tenantId]) {
            store[tenantId] = new Map();
        }
        return store[tenantId];
    }
    ensureTelemetryBucket(tenantId, vehicleId) {
        if (!this.telemetry[tenantId]) {
            this.telemetry[tenantId] = new Map();
        }
        if (!this.telemetry[tenantId].get(vehicleId)) {
            this.telemetry[tenantId].set(vehicleId, []);
        }
        return this.telemetry[tenantId].get(vehicleId);
    }
}
exports.InMemoryLogisticsRepository = InMemoryLogisticsRepository;
//# sourceMappingURL=in-memory-logistics-repository.js.map