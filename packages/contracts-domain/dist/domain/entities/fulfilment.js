"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Fulfilment = exports.FulfilmentSchema = void 0;
const zod_1 = require("zod");
exports.FulfilmentSchema = zod_1.z.object({
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    deliveredQty: zod_1.z.number().default(0),
    pricedQty: zod_1.z.number().default(0),
    invoicedQty: zod_1.z.number().default(0),
    openQty: zod_1.z.number(),
    avgPrice: zod_1.z.number().optional(),
    qualityScore: zod_1.z.number().min(0).max(100).optional(),
    onTimeDeliveryRate: zod_1.z.number().min(0).max(100).optional(),
    deliverySchedule: zod_1.z.array(zod_1.z.object({
        plannedDate: zod_1.z.string().datetime(),
        actualDate: zod_1.z.string().datetime().optional(),
        qty: zod_1.z.number(),
        status: zod_1.z.enum(['PENDING', 'DELIVERED', 'DELAYED', 'CANCELLED']),
        qualityCheck: zod_1.z.object({
            passed: zod_1.z.boolean(),
            score: zod_1.z.number().min(0).max(100).optional(),
            notes: zod_1.z.string().optional(),
            inspector: zod_1.z.string().optional(),
            inspectionDate: zod_1.z.string().datetime().optional(),
        }).optional(),
    })).default([]),
    timeline: zod_1.z.array(zod_1.z.object({
        event: zod_1.z.string(),
        timestamp: zod_1.z.string().datetime(),
        qty: zod_1.z.number().optional(),
        price: zod_1.z.number().optional(),
        notes: zod_1.z.string().optional(),
        qualityData: zod_1.z.object({
            score: zod_1.z.number().optional(),
            issues: zod_1.z.array(zod_1.z.string()).optional(),
        }).optional(),
        deliveryData: zod_1.z.object({
            deliveryNote: zod_1.z.string().optional(),
            batchNumbers: zod_1.z.array(zod_1.z.string()).optional(),
            storageLocation: zod_1.z.string().optional(),
        }).optional(),
    })).default([]),
    lastUpdated: zod_1.z.date().optional(),
});
class Fulfilment {
    contractId;
    tenantId;
    deliveredQty;
    pricedQty;
    invoicedQty;
    openQty;
    avgPrice;
    qualityScore;
    onTimeDeliveryRate;
    deliverySchedule;
    timeline;
    lastUpdated;
    constructor(props) {
        this.contractId = props.contractId;
        this.tenantId = props.tenantId;
        this.deliveredQty = props.deliveredQty;
        this.pricedQty = props.pricedQty;
        this.invoicedQty = props.invoicedQty;
        this.openQty = props.openQty;
        if (props.avgPrice)
            this.avgPrice = props.avgPrice;
        if (props.qualityScore)
            this.qualityScore = props.qualityScore;
        if (props.onTimeDeliveryRate)
            this.onTimeDeliveryRate = props.onTimeDeliveryRate;
        this.deliverySchedule = props.deliverySchedule;
        this.timeline = props.timeline;
        this.lastUpdated = props.lastUpdated;
    }
    addDelivery(qty, deliveryData, notes) {
        this.deliveredQty += qty;
        this.openQty -= qty;
        const timelineEntry = {
            event: 'DELIVERY',
            timestamp: new Date(),
            qty,
        };
        if (deliveryData) {
            timelineEntry.deliveryData = deliveryData;
            if (deliveryData.qualityData) {
                timelineEntry.qualityData = deliveryData.qualityData;
                this.updateQualityScore();
            }
        }
        if (notes)
            timelineEntry.notes = notes;
        this.timeline.push(timelineEntry);
        this.updateDeliveryMetrics();
        this.lastUpdated = new Date();
    }
    addPricing(qty, price, notes) {
        this.pricedQty += qty;
        const timelineEntry = {
            event: 'PRICING',
            timestamp: new Date(),
            qty,
            price,
        };
        if (notes)
            timelineEntry.notes = notes;
        this.timeline.push(timelineEntry);
        this.updateAveragePrice();
        this.lastUpdated = new Date();
    }
    addInvoicing(qty, notes) {
        this.invoicedQty += qty;
        const timelineEntry = {
            event: 'INVOICING',
            timestamp: new Date(),
            qty,
        };
        if (notes)
            timelineEntry.notes = notes;
        this.timeline.push(timelineEntry);
        this.lastUpdated = new Date();
    }
    updateAveragePrice() {
        const pricedEvents = this.timeline.filter(t => t.event === 'PRICING' && t.price && t.qty);
        if (pricedEvents.length === 0)
            return;
        const totalValue = pricedEvents.reduce((sum, event) => sum + (event.price * event.qty), 0);
        const totalQty = pricedEvents.reduce((sum, event) => sum + event.qty, 0);
        this.avgPrice = totalValue / totalQty;
    }
    updateQualityScore() {
        const qualityEvents = this.timeline.filter(t => t.qualityData?.score !== undefined);
        if (qualityEvents.length === 0)
            return;
        const totalScore = qualityEvents.reduce((sum, event) => sum + (event.qualityData.score || 0), 0);
        this.qualityScore = totalScore / qualityEvents.length;
    }
    updateDeliveryMetrics() {
        const completedDeliveries = this.deliverySchedule.filter(d => d.status === 'DELIVERED');
        if (completedDeliveries.length === 0)
            return;
        const onTimeDeliveries = completedDeliveries.filter(delivery => {
            if (!delivery.actualDate)
                return false;
            return delivery.actualDate <= delivery.plannedDate;
        });
        this.onTimeDeliveryRate = (onTimeDeliveries.length / completedDeliveries.length) * 100;
    }
    getFulfilmentPercentage() {
        const totalContracted = this.deliveredQty + this.openQty;
        return totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;
    }
    isFullyFulfilled() {
        return this.openQty === 0;
    }
    addDeliveryScheduleItem(plannedDate, qty) {
        this.deliverySchedule.push({
            plannedDate,
            qty,
            status: 'PENDING'
        });
        this.lastUpdated = new Date();
    }
    updateDeliveryStatus(index, status, actualDate) {
        if (index >= 0 && index < this.deliverySchedule.length) {
            const delivery = this.deliverySchedule[index];
            if (delivery) {
                delivery.status = status;
                if (actualDate) {
                    delivery.actualDate = actualDate;
                }
                this.updateDeliveryMetrics();
                this.lastUpdated = new Date();
            }
        }
    }
    addQualityCheck(deliveryIndex, qualityCheck) {
        if (deliveryIndex >= 0 && deliveryIndex < this.deliverySchedule.length) {
            const delivery = this.deliverySchedule[deliveryIndex];
            if (delivery) {
                delivery.qualityCheck = {
                    ...qualityCheck,
                    inspectionDate: new Date()
                };
                this.updateQualityScore();
                this.lastUpdated = new Date();
            }
        }
    }
    getDelayedDeliveries() {
        return this.deliverySchedule
            .filter(d => d.status === 'DELAYED' && d.actualDate && d.plannedDate)
            .map(d => ({
            plannedDate: d.plannedDate,
            delayDays: Math.ceil((d.actualDate.getTime() - d.plannedDate.getTime()) / (1000 * 60 * 60 * 24))
        }));
    }
    getUpcomingDeliveries(daysAhead = 7) {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() + daysAhead);
        return this.deliverySchedule
            .filter(d => d.status === 'PENDING' && d.plannedDate <= cutoffDate)
            .map(d => ({
            plannedDate: d.plannedDate,
            qty: d.qty
        }))
            .sort((a, b) => a.plannedDate.getTime() - b.plannedDate.getTime());
    }
    getFulfilmentSummary() {
        const totalContracted = this.deliveredQty + this.openQty;
        const fulfilmentRate = totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;
        const nextDelivery = this.deliverySchedule
            .filter(d => d.status === 'PENDING')
            .sort((a, b) => a.plannedDate.getTime() - b.plannedDate.getTime())[0]?.plannedDate;
        return {
            totalContracted,
            delivered: this.deliveredQty,
            remaining: this.openQty,
            fulfilmentRate,
            qualityScore: this.qualityScore,
            onTimeDeliveryRate: this.onTimeDeliveryRate,
            nextDelivery
        };
    }
}
exports.Fulfilment = Fulfilment;
//# sourceMappingURL=fulfilment.js.map