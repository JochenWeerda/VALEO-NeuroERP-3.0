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
    timeline: zod_1.z.array(zod_1.z.object({
        event: zod_1.z.string(),
        timestamp: zod_1.z.string().datetime(),
        qty: zod_1.z.number().optional(),
        price: zod_1.z.number().optional(),
        notes: zod_1.z.string().optional(),
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
        this.timeline = props.timeline;
        this.lastUpdated = props.lastUpdated;
    }
    addDelivery(qty, notes) {
        this.deliveredQty += qty;
        this.openQty -= qty;
        const timelineEntry = {
            event: 'DELIVERY',
            timestamp: new Date(),
            qty,
        };
        if (notes)
            timelineEntry.notes = notes;
        this.timeline.push(timelineEntry);
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
    getFulfilmentPercentage() {
        const totalContracted = this.deliveredQty + this.openQty;
        return totalContracted > 0 ? (this.deliveredQty / totalContracted) * 100 : 0;
    }
    isFullyFulfilled() {
        return this.openQty === 0;
    }
}
exports.Fulfilment = Fulfilment;
//# sourceMappingURL=fulfilment.js.map