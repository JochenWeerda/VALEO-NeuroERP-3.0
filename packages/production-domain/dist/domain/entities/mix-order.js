"use strict";
/**
 * Mix Order Entity for VALEO NeuroERP 3.0 Production Domain
 * Mix order management for both plant and mobile production
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MixOrderEntity = exports.MixOrderSchema = void 0;
const zod_1 = require("zod");
// Location Schema
const LocationSchema = zod_1.z.object({
    lat: zod_1.z.number().min(-90).max(90),
    lng: zod_1.z.number().min(-180).max(180),
    address: zod_1.z.string().optional()
});
// Mix Step Schema (runtime data)
const MixStepSchema = zod_1.z.object({
    type: zod_1.z.enum(['weigh', 'dose', 'grind', 'mix', 'flushing', 'transfer']),
    startedAt: zod_1.z.string().datetime(),
    endedAt: zod_1.z.string().datetime().optional(),
    equipmentId: zod_1.z.string().optional(),
    actuals: zod_1.z.object({
        massKg: zod_1.z.number().min(0).optional(),
        timeSec: zod_1.z.number().min(0).optional(),
        energyKWh: zod_1.z.number().min(0).optional(),
        moisturePercent: zod_1.z.number().min(0).max(100).optional()
    }).optional()
});
// Main Mix Order Schema
exports.MixOrderSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    orderNumber: zod_1.z.string().min(1).max(100),
    type: zod_1.z.enum(['Plant', 'Mobile']),
    recipeId: zod_1.z.string().uuid(),
    targetQtyKg: zod_1.z.number().positive(),
    plannedAt: zod_1.z.string().datetime(),
    location: LocationSchema.optional(),
    customerId: zod_1.z.string().uuid().optional(),
    mobileUnitId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum(['Draft', 'Staged', 'Running', 'Hold', 'Completed', 'Aborted']).default('Draft'),
    notes: zod_1.z.string().optional(),
    steps: zod_1.z.array(MixStepSchema).default([]),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class MixOrderEntity {
    data;
    constructor(data) {
        this.data = exports.MixOrderSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get orderNumber() { return this.data.orderNumber; }
    get type() { return this.data.type; }
    get recipeId() { return this.data.recipeId; }
    get targetQtyKg() { return this.data.targetQtyKg; }
    get plannedAt() { return this.data.plannedAt; }
    get location() { return this.data.location; }
    get customerId() { return this.data.customerId; }
    get mobileUnitId() { return this.data.mobileUnitId; }
    get status() { return this.data.status; }
    get notes() { return this.data.notes; }
    get steps() { return [...this.data.steps]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    isDraft() {
        return this.data.status === 'Draft';
    }
    isStaged() {
        return this.data.status === 'Staged';
    }
    isRunning() {
        return this.data.status === 'Running';
    }
    isOnHold() {
        return this.data.status === 'Hold';
    }
    isCompleted() {
        return this.data.status === 'Completed';
    }
    isAborted() {
        return this.data.status === 'Aborted';
    }
    isMobile() {
        return this.data.type === 'Mobile';
    }
    isPlant() {
        return this.data.type === 'Plant';
    }
    canStart() {
        return this.isStaged();
    }
    canStage() {
        return this.isDraft();
    }
    canHold() {
        return this.isRunning() || this.isStaged();
    }
    canComplete() {
        return this.isRunning();
    }
    canAbort() {
        return !this.isCompleted() && !this.isAborted();
    }
    getDurationMinutes() {
        if (!this.data.steps.length)
            return 0;
        const startTime = new Date(this.data.steps[0].startedAt);
        const lastStep = this.data.steps[this.data.steps.length - 1];
        const endTime = lastStep.endedAt ? new Date(lastStep.endedAt) : new Date();
        return Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
    }
    getTotalMassProcessed() {
        return this.data.steps.reduce((total, step) => {
            return total + (step.actuals?.massKg || 0);
        }, 0);
    }
    getTotalEnergyConsumed() {
        return this.data.steps.reduce((total, step) => {
            return total + (step.actuals?.energyKWh || 0);
        }, 0);
    }
    getActiveSteps() {
        return this.data.steps.filter(step => !step.endedAt);
    }
    getCompletedSteps() {
        return this.data.steps.filter(step => step.endedAt);
    }
    // Validation
    validateBusinessRules() {
        // Mobile orders must have location
        if (this.isMobile() && !this.data.location) {
            throw new Error('Mobile mix orders must have location');
        }
        // Mobile orders must have mobileUnitId
        if (this.isMobile() && !this.data.mobileUnitId) {
            throw new Error('Mobile mix orders must have mobileUnitId');
        }
        // Customer orders should have customerId
        if (this.data.customerId && !this.data.customerId.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
            throw new Error('Invalid customerId format');
        }
        // Validate step sequence
        const stepsWithEndTime = this.data.steps.filter(step => step.endedAt);
        for (const step of stepsWithEndTime) {
            const startTime = new Date(step.startedAt);
            const endTime = new Date(step.endedAt);
            if (endTime <= startTime) {
                throw new Error(`Step ${step.type} has invalid time range`);
            }
        }
    }
    // State Changes
    stage(updatedBy) {
        if (!this.canStage()) {
            throw new Error('Mix order cannot be staged in current status');
        }
        return new MixOrderEntity({
            ...this.data,
            status: 'Staged',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    start(updatedBy) {
        if (!this.canStart()) {
            throw new Error('Mix order cannot be started in current status');
        }
        return new MixOrderEntity({
            ...this.data,
            status: 'Running',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    hold(reason, updatedBy) {
        if (!this.canHold()) {
            throw new Error('Mix order cannot be put on hold in current status');
        }
        const notes = reason ? `${this.data.notes || ''}\n[HOLD] ${reason}`.trim() : this.data.notes;
        return new MixOrderEntity({
            ...this.data,
            status: 'Hold',
            notes,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    complete(updatedBy) {
        if (!this.canComplete()) {
            throw new Error('Mix order cannot be completed in current status');
        }
        return new MixOrderEntity({
            ...this.data,
            status: 'Completed',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    abort(reason, updatedBy) {
        if (!this.canAbort()) {
            throw new Error('Mix order cannot be aborted in current status');
        }
        const notes = reason ? `${this.data.notes || ''}\n[ABORTED] ${reason}`.trim() : this.data.notes;
        return new MixOrderEntity({
            ...this.data,
            status: 'Aborted',
            notes,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addStep(step, updatedBy) {
        // Validate step sequence
        if (this.data.steps.length > 0) {
            const lastStep = this.data.steps[this.data.steps.length - 1];
            if (!lastStep.endedAt) {
                throw new Error('Cannot add new step while previous step is still running');
            }
        }
        return new MixOrderEntity({
            ...this.data,
            steps: [...this.data.steps, step],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateStep(stepIndex, updates, updatedBy) {
        if (stepIndex < 0 || stepIndex >= this.data.steps.length) {
            throw new Error('Invalid step index');
        }
        const updatedSteps = [...this.data.steps];
        updatedSteps[stepIndex] = { ...updatedSteps[stepIndex], ...updates };
        return new MixOrderEntity({
            ...this.data,
            steps: updatedSteps,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    endStep(stepIndex, endedAt, actuals, updatedBy) {
        if (stepIndex < 0 || stepIndex >= this.data.steps.length) {
            throw new Error('Invalid step index');
        }
        const step = this.data.steps[stepIndex];
        if (step.endedAt) {
            throw new Error('Step is already ended');
        }
        const updatedStep = {
            ...step,
            endedAt,
            actuals: actuals ? { ...step.actuals, ...actuals } : step.actuals
        };
        return this.updateStep(stepIndex, updatedStep, updatedBy);
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new MixOrderEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new MixOrderEntity(data);
    }
}
exports.MixOrderEntity = MixOrderEntity;
//# sourceMappingURL=mix-order.js.map