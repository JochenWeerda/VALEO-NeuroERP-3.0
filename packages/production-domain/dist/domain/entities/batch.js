"use strict";
/**
 * Batch Entity for VALEO NeuroERP 3.0 Production Domain
 * Batch management with traceability and quality control
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.BatchEntity = exports.BatchSchema = void 0;
const zod_1 = require("zod");
// Batch Input Schema
const BatchInputSchema = zod_1.z.object({
    batchId: zod_1.z.string().uuid(),
    ingredientLotId: zod_1.z.string().uuid(),
    plannedKg: zod_1.z.number().positive(),
    actualKg: zod_1.z.number().positive()
});
// Batch Output Lot Schema
const BatchOutputLotSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    batchId: zod_1.z.string().uuid(),
    lotNumber: zod_1.z.string().min(1).max(100),
    qtyKg: zod_1.z.number().positive(),
    packing: zod_1.z.object({
        form: zod_1.z.enum(['Bulk', 'Bag', 'Silo']),
        size: zod_1.z.number().optional(),
        unit: zod_1.z.string().optional()
    }),
    destination: zod_1.z.enum(['Inventory', 'DirectFarm']),
    gmpPlusMarkings: zod_1.z.array(zod_1.z.string()).optional()
});
// Main Batch Schema
exports.BatchSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    batchNumber: zod_1.z.string().min(1).max(100),
    mixOrderId: zod_1.z.string().uuid(),
    producedQtyKg: zod_1.z.number().positive(),
    startAt: zod_1.z.string().datetime(),
    endAt: zod_1.z.string().datetime().optional(),
    status: zod_1.z.enum(['Released', 'Quarantine', 'Rejected']).default('Quarantine'),
    parentBatches: zod_1.z.array(zod_1.z.string().uuid()).default([]),
    labels: zod_1.z.array(zod_1.z.string()).default([]),
    inputs: zod_1.z.array(BatchInputSchema).default([]),
    outputs: zod_1.z.array(BatchOutputLotSchema).default([]),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class BatchEntity {
    data;
    constructor(data) {
        this.data = exports.BatchSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get batchNumber() { return this.data.batchNumber; }
    get mixOrderId() { return this.data.mixOrderId; }
    get producedQtyKg() { return this.data.producedQtyKg; }
    get startAt() { return this.data.startAt; }
    get endAt() { return this.data.endAt; }
    get status() { return this.data.status; }
    get parentBatches() { return [...this.data.parentBatches]; }
    get labels() { return [...this.data.labels]; }
    get inputs() { return [...this.data.inputs]; }
    get outputs() { return [...this.data.outputs]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    isReleased() {
        return this.data.status === 'Released';
    }
    isInQuarantine() {
        return this.data.status === 'Quarantine';
    }
    isRejected() {
        return this.data.status === 'Rejected';
    }
    isCompleted() {
        return !!this.data.endAt;
    }
    isInProgress() {
        return !this.data.endAt;
    }
    canRelease() {
        return this.isInQuarantine() && this.isCompleted();
    }
    canReject() {
        return !this.isRejected();
    }
    canQuarantine() {
        return this.isReleased();
    }
    isRework() {
        return this.data.parentBatches.length > 0;
    }
    hasGMPPlusMarking() {
        return this.data.outputs.some(output => output.gmpPlusMarkings && output.gmpPlusMarkings.length > 0);
    }
    getTotalInputKg() {
        return this.data.inputs.reduce((total, input) => total + input.actualKg, 0);
    }
    getTotalOutputKg() {
        return this.data.outputs.reduce((total, output) => total + output.qtyKg, 0);
    }
    getYield() {
        const inputKg = this.getTotalInputKg();
        const outputKg = this.getTotalOutputKg();
        return inputKg > 0 ? (outputKg / inputKg) * 100 : 0;
    }
    getDurationHours() {
        if (!this.data.endAt)
            return 0;
        const startTime = new Date(this.data.startAt);
        const endTime = new Date(this.data.endAt);
        return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
    }
    getIngredientLotIds() {
        return this.data.inputs.map(input => input.ingredientLotId);
    }
    getOutputLotNumbers() {
        return this.data.outputs.map(output => output.lotNumber);
    }
    // Validation
    validateBusinessRules() {
        // Validate batch number format (should be unique within tenant)
        if (!this.data.batchNumber.match(/^[A-Z0-9-_]+$/)) {
            throw new Error('Batch number must contain only uppercase letters, numbers, hyphens and underscores');
        }
        // Validate time sequence
        if (this.data.endAt) {
            const startTime = new Date(this.data.startAt);
            const endTime = new Date(this.data.endAt);
            if (endTime <= startTime) {
                throw new Error('End time must be after start time');
            }
        }
        // Validate inputs
        for (const input of this.data.inputs) {
            if (input.actualKg <= 0) {
                throw new Error('Actual input quantity must be positive');
            }
        }
        // Validate outputs
        for (const output of this.data.outputs) {
            if (output.qtyKg <= 0) {
                throw new Error('Output quantity must be positive');
            }
        }
        // Validate mass balance (allow some tolerance)
        const inputKg = this.getTotalInputKg();
        const outputKg = this.getTotalOutputKg();
        const tolerance = 0.05; // 5% tolerance
        if (outputKg > inputKg * (1 + tolerance)) {
            throw new Error('Output quantity exceeds input quantity beyond acceptable tolerance');
        }
    }
    // State Changes
    release(updatedBy) {
        if (!this.canRelease()) {
            throw new Error('Batch cannot be released in current status');
        }
        return new BatchEntity({
            ...this.data,
            status: 'Released',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    reject(reason, updatedBy) {
        if (!this.canReject()) {
            throw new Error('Batch cannot be rejected in current status');
        }
        const notes = reason ? `REJECTED: ${reason}` : 'REJECTED';
        const updatedLabels = [...this.data.labels, notes];
        return new BatchEntity({
            ...this.data,
            status: 'Rejected',
            labels: updatedLabels,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    quarantine(reason, updatedBy) {
        if (!this.canQuarantine()) {
            throw new Error('Batch cannot be quarantined in current status');
        }
        const notes = reason ? `QUARANTINED: ${reason}` : 'QUARANTINED';
        const updatedLabels = [...this.data.labels, notes];
        return new BatchEntity({
            ...this.data,
            status: 'Quarantine',
            labels: updatedLabels,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    complete(endAt, updatedBy) {
        if (this.isCompleted()) {
            throw new Error('Batch is already completed');
        }
        return new BatchEntity({
            ...this.data,
            endAt,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addInput(input, updatedBy) {
        // Check for duplicate ingredient lots
        const existingLotIds = this.data.inputs.map(i => i.ingredientLotId);
        if (existingLotIds.includes(input.ingredientLotId)) {
            throw new Error('Ingredient lot already added to batch');
        }
        return new BatchEntity({
            ...this.data,
            inputs: [...this.data.inputs, input],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addOutput(output, updatedBy) {
        // Check for duplicate lot numbers
        const existingLotNumbers = this.data.outputs.map(o => o.lotNumber);
        if (existingLotNumbers.includes(output.lotNumber)) {
            throw new Error('Lot number already exists in batch');
        }
        return new BatchEntity({
            ...this.data,
            outputs: [...this.data.outputs, output],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addLabel(label, updatedBy) {
        if (this.data.labels.includes(label)) {
            return this; // Label already exists
        }
        return new BatchEntity({
            ...this.data,
            labels: [...this.data.labels, label],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    removeLabel(label, updatedBy) {
        return new BatchEntity({
            ...this.data,
            labels: this.data.labels.filter(l => l !== label),
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addParentBatch(parentBatchId, updatedBy) {
        if (this.data.parentBatches.includes(parentBatchId)) {
            return this; // Parent batch already exists
        }
        return new BatchEntity({
            ...this.data,
            parentBatches: [...this.data.parentBatches, parentBatchId],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    // Traceability methods
    getTraceabilityData() {
        return {
            batchId: this.data.id,
            batchNumber: this.data.batchNumber,
            mixOrderId: this.data.mixOrderId,
            status: this.data.status,
            startAt: this.data.startAt,
            endAt: this.data.endAt,
            inputs: this.data.inputs.map(input => ({
                ingredientLotId: input.ingredientLotId,
                plannedKg: input.plannedKg,
                actualKg: input.actualKg
            })),
            outputs: this.data.outputs.map(output => ({
                lotNumber: output.lotNumber,
                qtyKg: output.qtyKg,
                destination: output.destination,
                packing: output.packing
            })),
            parentBatches: this.data.parentBatches,
            labels: this.data.labels
        };
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new BatchEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new BatchEntity(data);
    }
}
exports.BatchEntity = BatchEntity;
//# sourceMappingURL=batch.js.map