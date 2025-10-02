"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighingTicket = exports.WeighingTicketSchema = exports.WeighingDataSchema = exports.WeighingMode = exports.CommodityType = exports.WeighingStatus = exports.WeighingType = void 0;
const zod_1 = require("zod");
exports.WeighingType = {
    VEHICLE: 'Vehicle',
    CONTAINER: 'Container',
    SILO: 'Silo',
    MANUAL: 'Manual',
};
exports.WeighingStatus = {
    DRAFT: 'Draft',
    IN_PROGRESS: 'InProgress',
    COMPLETED: 'Completed',
    CANCELLED: 'Cancelled',
    ERROR: 'Error',
};
exports.CommodityType = {
    WHEAT: 'WHEAT',
    BARLEY: 'BARLEY',
    RAPESEED: 'RAPESEED',
    SOYMEAL: 'SOYMEAL',
    COMPOUND_FEED: 'COMPOUND_FEED',
    FERTILIZER: 'FERTILIZER',
    OTHER: 'OTHER',
};
exports.WeighingMode = {
    GROSS: 'Gross',
    TARE: 'Tare',
    NET: 'Net',
};
exports.WeighingDataSchema = zod_1.z.object({
    weight: zod_1.z.number().positive(),
    unit: zod_1.z.enum(['kg', 't']),
    timestamp: zod_1.z.string().datetime(),
    scaleId: zod_1.z.string(),
    operatorId: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional(),
});
exports.WeighingTicketSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string(),
    ticketNumber: zod_1.z.string(),
    type: zod_1.z.enum([exports.WeighingType.VEHICLE, exports.WeighingType.CONTAINER, exports.WeighingType.SILO, exports.WeighingType.MANUAL]),
    status: zod_1.z.enum([exports.WeighingStatus.DRAFT, exports.WeighingStatus.IN_PROGRESS, exports.WeighingStatus.COMPLETED, exports.WeighingStatus.CANCELLED, exports.WeighingStatus.ERROR]).default(exports.WeighingStatus.DRAFT),
    licensePlate: zod_1.z.string().optional(),
    containerNumber: zod_1.z.string().optional(),
    siloId: zod_1.z.string().optional(),
    commodity: zod_1.z.enum([exports.CommodityType.WHEAT, exports.CommodityType.BARLEY, exports.CommodityType.RAPESEED, exports.CommodityType.SOYMEAL, exports.CommodityType.COMPOUND_FEED, exports.CommodityType.FERTILIZER, exports.CommodityType.OTHER]),
    commodityDescription: zod_1.z.string().optional(),
    grossWeight: exports.WeighingDataSchema.optional(),
    tareWeight: exports.WeighingDataSchema.optional(),
    netWeight: zod_1.z.number().optional(),
    netWeightUnit: zod_1.z.enum(['kg', 't']).optional(),
    expectedWeight: zod_1.z.number().optional(),
    tolerancePercent: zod_1.z.number().min(0).max(20).default(2),
    isWithinTolerance: zod_1.z.boolean().optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    deliveryNoteId: zod_1.z.string().uuid().optional(),
    anprRecordId: zod_1.z.string().uuid().optional(),
    autoAssigned: zod_1.z.boolean().default(false),
    gateId: zod_1.z.string().optional(),
    slotId: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.date().optional(),
    updatedAt: zod_1.z.date().optional(),
    completedAt: zod_1.z.date().optional(),
    version: zod_1.z.number().default(1),
});
class WeighingTicket {
    id;
    tenantId;
    ticketNumber;
    type;
    status;
    licensePlate;
    containerNumber;
    siloId;
    commodity;
    commodityDescription;
    grossWeight;
    tareWeight;
    netWeight;
    netWeightUnit;
    expectedWeight;
    tolerancePercent;
    isWithinTolerance;
    contractId;
    orderId;
    deliveryNoteId;
    anprRecordId;
    autoAssigned;
    gateId;
    slotId;
    createdAt;
    updatedAt;
    completedAt;
    version;
    constructor(props) {
        this.id = props.id;
        this.tenantId = props.tenantId;
        this.ticketNumber = props.ticketNumber;
        this.type = props.type;
        this.status = props.status;
        if (props.licensePlate)
            this.licensePlate = props.licensePlate;
        if (props.containerNumber)
            this.containerNumber = props.containerNumber;
        if (props.siloId)
            this.siloId = props.siloId;
        this.commodity = props.commodity;
        if (props.commodityDescription)
            this.commodityDescription = props.commodityDescription;
        if (props.grossWeight)
            this.grossWeight = props.grossWeight;
        if (props.tareWeight)
            this.tareWeight = props.tareWeight;
        if (props.netWeight !== undefined)
            this.netWeight = props.netWeight;
        if (props.netWeightUnit)
            this.netWeightUnit = props.netWeightUnit;
        if (props.expectedWeight)
            this.expectedWeight = props.expectedWeight;
        this.tolerancePercent = props.tolerancePercent;
        if (props.isWithinTolerance !== undefined)
            this.isWithinTolerance = props.isWithinTolerance;
        if (props.contractId)
            this.contractId = props.contractId;
        if (props.orderId)
            this.orderId = props.orderId;
        if (props.deliveryNoteId)
            this.deliveryNoteId = props.deliveryNoteId;
        if (props.anprRecordId)
            this.anprRecordId = props.anprRecordId;
        this.autoAssigned = props.autoAssigned;
        if (props.gateId)
            this.gateId = props.gateId;
        if (props.slotId)
            this.slotId = props.slotId;
        this.createdAt = props.createdAt;
        this.updatedAt = props.updatedAt;
        if (props.completedAt)
            this.completedAt = props.completedAt;
        this.version = props.version;
    }
    addGrossWeight(weight, unit, scaleId, operatorId, notes) {
        if (this.status === exports.WeighingStatus.COMPLETED) {
            throw new Error('Cannot modify completed ticket');
        }
        const weighingData = {
            weight,
            unit,
            timestamp: new Date(),
            scaleId,
        };
        if (operatorId)
            weighingData.operatorId = operatorId;
        if (notes)
            weighingData.notes = notes;
        this.grossWeight = weighingData;
        this.calculateNetWeight();
        this.updatedAt = new Date();
        this.version++;
    }
    addTareWeight(weight, unit, scaleId, operatorId, notes) {
        if (this.status === exports.WeighingStatus.COMPLETED) {
            throw new Error('Cannot modify completed ticket');
        }
        const weighingData = {
            weight,
            unit,
            timestamp: new Date(),
            scaleId,
        };
        if (operatorId)
            weighingData.operatorId = operatorId;
        if (notes)
            weighingData.notes = notes;
        this.tareWeight = weighingData;
        this.calculateNetWeight();
        this.updatedAt = new Date();
        this.version++;
    }
    calculateNetWeight() {
        if (this.grossWeight && this.tareWeight) {
            const grossKg = this.grossWeight.unit === 't' ? this.grossWeight.weight * 1000 : this.grossWeight.weight;
            const tareKg = this.tareWeight.unit === 't' ? this.tareWeight.weight * 1000 : this.tareWeight.weight;
            this.netWeight = grossKg - tareKg;
            this.netWeightUnit = 'kg';
            if (this.expectedWeight) {
                const tolerance = (this.expectedWeight * this.tolerancePercent) / 100;
                this.isWithinTolerance = Math.abs(this.netWeight - this.expectedWeight) <= tolerance;
            }
        }
    }
    complete() {
        if (this.status === exports.WeighingStatus.COMPLETED) {
            throw new Error('Ticket is already completed');
        }
        if (!this.netWeight) {
            throw new Error('Cannot complete ticket without net weight');
        }
        this.status = exports.WeighingStatus.COMPLETED;
        this.completedAt = new Date();
        this.updatedAt = new Date();
        this.version++;
    }
    cancel() {
        if (this.status === exports.WeighingStatus.COMPLETED) {
            throw new Error('Cannot cancel completed ticket');
        }
        this.status = exports.WeighingStatus.CANCELLED;
        this.updatedAt = new Date();
        this.version++;
    }
    canBeModified() {
        const modifiableStatuses = [exports.WeighingStatus.DRAFT, exports.WeighingStatus.IN_PROGRESS];
        return modifiableStatuses.includes(this.status);
    }
    isValid() {
        return this.netWeight !== undefined && this.netWeight > 0;
    }
    getWeightSummary() {
        const summary = {
            unit: this.netWeightUnit || 'kg',
        };
        if (this.grossWeight?.weight)
            summary.gross = this.grossWeight.weight;
        if (this.tareWeight?.weight)
            summary.tare = this.tareWeight.weight;
        if (this.netWeight !== undefined)
            summary.net = this.netWeight;
        if (this.isWithinTolerance !== undefined)
            summary.isWithinTolerance = this.isWithinTolerance;
        return summary;
    }
}
exports.WeighingTicket = WeighingTicket;
//# sourceMappingURL=weighing-ticket.js.map