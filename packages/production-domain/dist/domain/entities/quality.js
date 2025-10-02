"use strict";
/**
 * Quality Entities for VALEO NeuroERP 3.0 Production Domain
 * Quality management with sampling, testing, and non-conformity handling
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.CAPAEntity = exports.NonConformityEntity = exports.RetainedSampleEntity = exports.SamplingResultEntity = exports.SamplingPlanEntity = exports.CAPASchema = exports.NonConformitySchema = exports.RetainedSampleSchema = exports.SamplingResultSchema = exports.SamplingPlanSchema = void 0;
const zod_1 = require("zod");
// Sampling Plan Schema
exports.SamplingPlanSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    name: zod_1.z.string().min(1).max(200),
    for: zod_1.z.enum(['mobile', 'plant']),
    frequency: zod_1.z.enum(['perBatch', 'perN']),
    frequencyValue: zod_1.z.number().int().positive().optional(), // For perN frequency
    retainedSamples: zod_1.z.boolean().default(false),
    targetAnalytes: zod_1.z.array(zod_1.z.string()).min(1),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// Sampling Result Schema
exports.SamplingResultSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    batchId: zod_1.z.string().uuid(),
    sampleCode: zod_1.z.string().min(1).max(100),
    takenAt: zod_1.z.string().datetime(),
    labId: zod_1.z.string().uuid().optional(),
    analyte: zod_1.z.string().min(1).max(100),
    value: zod_1.z.number(),
    unit: zod_1.z.string().min(1).max(20),
    limitType: zod_1.z.enum(['Action', 'Reject']),
    decision: zod_1.z.enum(['Pass', 'Investigate', 'Reject']),
    docUri: zod_1.z.string().url().optional(),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// Retained Sample Schema
exports.RetainedSampleSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    batchId: zod_1.z.string().uuid(),
    sampleCode: zod_1.z.string().min(1).max(100),
    storageLoc: zod_1.z.string().min(1).max(200),
    expiryAt: zod_1.z.string().datetime(),
    disposedAt: zod_1.z.string().datetime().optional(),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// Non-Conformity Schema
exports.NonConformitySchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    refType: zod_1.z.enum(['batchId', 'mixOrderId', 'mobileRunId']),
    refId: zod_1.z.string().uuid(),
    type: zod_1.z.enum(['Contamination', 'SpecOut', 'Equipment', 'Process']),
    severity: zod_1.z.enum(['Low', 'Medium', 'High', 'Critical']),
    description: zod_1.z.string().min(1).max(1000),
    action: zod_1.z.enum(['Block', 'Rework', 'Dispose']),
    capaId: zod_1.z.string().uuid().optional(),
    status: zod_1.z.enum(['Open', 'InProgress', 'Closed']).default('Open'),
    discoveredAt: zod_1.z.string().datetime(),
    closedAt: zod_1.z.string().datetime().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// CAPA Schema
exports.CAPASchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    ncId: zod_1.z.string().uuid().optional(),
    title: zod_1.z.string().min(1).max(200),
    description: zod_1.z.string().min(1).max(2000),
    type: zod_1.z.enum(['Correction', 'CorrectiveAction', 'PreventiveAction']),
    priority: zod_1.z.enum(['Low', 'Medium', 'High', 'Critical']),
    status: zod_1.z.enum(['Open', 'InProgress', 'Closed']).default('Open'),
    assignedTo: zod_1.z.string().uuid().optional(),
    dueDate: zod_1.z.string().datetime().optional(),
    closedAt: zod_1.z.string().datetime().optional(),
    effectiveness: zod_1.z.enum(['Effective', 'NotEffective', 'NotEvaluated']).optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
// Sampling Plan Entity
class SamplingPlanEntity {
    data;
    constructor(data) {
        this.data = exports.SamplingPlanSchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get name() { return this.data.name; }
    get for() { return this.data.for; }
    get frequency() { return this.data.frequency; }
    get frequencyValue() { return this.data.frequencyValue; }
    get retainedSamples() { return this.data.retainedSamples; }
    get targetAnalytes() { return [...this.data.targetAnalytes]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    validateBusinessRules() {
        if (this.data.frequency === 'perN' && !this.data.frequencyValue) {
            throw new Error('Frequency value is required for perN frequency');
        }
    }
    isForMobile() {
        return this.data.for === 'mobile';
    }
    isForPlant() {
        return this.data.for === 'plant';
    }
    shouldSampleBatch(batchNumber) {
        if (this.data.frequency === 'perBatch') {
            return true;
        }
        if (this.data.frequency === 'perN' && this.data.frequencyValue) {
            return batchNumber % this.data.frequencyValue === 0;
        }
        return false;
    }
    toJSON() {
        return { ...this.data };
    }
    static create(data) {
        const now = new Date().toISOString();
        return new SamplingPlanEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
}
exports.SamplingPlanEntity = SamplingPlanEntity;
// Sampling Result Entity
class SamplingResultEntity {
    data;
    constructor(data) {
        this.data = exports.SamplingResultSchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get batchId() { return this.data.batchId; }
    get sampleCode() { return this.data.sampleCode; }
    get takenAt() { return this.data.takenAt; }
    get labId() { return this.data.labId; }
    get analyte() { return this.data.analyte; }
    get value() { return this.data.value; }
    get unit() { return this.data.unit; }
    get limitType() { return this.data.limitType; }
    get decision() { return this.data.decision; }
    get docUri() { return this.data.docUri; }
    get notes() { return this.data.notes; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    validateBusinessRules() {
        if (this.data.value < 0) {
            throw new Error('Sample value cannot be negative');
        }
    }
    isPass() {
        return this.data.decision === 'Pass';
    }
    isReject() {
        return this.data.decision === 'Reject';
    }
    requiresInvestigation() {
        return this.data.decision === 'Investigate';
    }
    isActionLimit() {
        return this.data.limitType === 'Action';
    }
    isRejectLimit() {
        return this.data.limitType === 'Reject';
    }
    updateDecision(decision, updatedBy) {
        return new SamplingResultEntity({
            ...this.data,
            decision,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    toJSON() {
        return { ...this.data };
    }
    static create(data) {
        const now = new Date().toISOString();
        return new SamplingResultEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
}
exports.SamplingResultEntity = SamplingResultEntity;
// Retained Sample Entity
class RetainedSampleEntity {
    data;
    constructor(data) {
        this.data = exports.RetainedSampleSchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get batchId() { return this.data.batchId; }
    get sampleCode() { return this.data.sampleCode; }
    get storageLoc() { return this.data.storageLoc; }
    get expiryAt() { return this.data.expiryAt; }
    get disposedAt() { return this.data.disposedAt; }
    get notes() { return this.data.notes; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    validateBusinessRules() {
        const expiryDate = new Date(this.data.expiryAt);
        const now = new Date();
        if (expiryDate <= now) {
            throw new Error('Expiry date must be in the future');
        }
    }
    isExpired() {
        return new Date(this.data.expiryAt) <= new Date();
    }
    isDisposed() {
        return !!this.data.disposedAt;
    }
    dispose(disposedAt, notes, updatedBy) {
        if (this.isDisposed()) {
            throw new Error('Sample is already disposed');
        }
        return new RetainedSampleEntity({
            ...this.data,
            disposedAt,
            notes: notes ? `${this.data.notes || ''}\n[DISPOSED] ${notes}`.trim() : this.data.notes,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    toJSON() {
        return { ...this.data };
    }
    static create(data) {
        const now = new Date().toISOString();
        return new RetainedSampleEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
}
exports.RetainedSampleEntity = RetainedSampleEntity;
// Non-Conformity Entity
class NonConformityEntity {
    data;
    constructor(data) {
        this.data = exports.NonConformitySchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get refType() { return this.data.refType; }
    get refId() { return this.data.refId; }
    get type() { return this.data.type; }
    get severity() { return this.data.severity; }
    get description() { return this.data.description; }
    get action() { return this.data.action; }
    get capaId() { return this.data.capaId; }
    get status() { return this.data.status; }
    get discoveredAt() { return this.data.discoveredAt; }
    get closedAt() { return this.data.closedAt; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    validateBusinessRules() {
        if (this.data.closedAt) {
            const discoveredDate = new Date(this.data.discoveredAt);
            const closedDate = new Date(this.data.closedAt);
            if (closedDate < discoveredDate) {
                throw new Error('Closed date cannot be before discovery date');
            }
        }
    }
    isOpen() {
        return this.data.status === 'Open';
    }
    isInProgress() {
        return this.data.status === 'InProgress';
    }
    isClosed() {
        return this.data.status === 'Closed';
    }
    isCritical() {
        return this.data.severity === 'Critical';
    }
    requiresImmediateAction() {
        return this.isCritical() || (this.data.severity === 'High' && this.data.action === 'Block');
    }
    assignCAPA(capaId, updatedBy) {
        return new NonConformityEntity({
            ...this.data,
            capaId,
            status: 'InProgress',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    close(closedAt, updatedBy) {
        if (this.isClosed()) {
            throw new Error('Non-conformity is already closed');
        }
        return new NonConformityEntity({
            ...this.data,
            status: 'Closed',
            closedAt,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    toJSON() {
        return { ...this.data };
    }
    static create(data) {
        const now = new Date().toISOString();
        return new NonConformityEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
}
exports.NonConformityEntity = NonConformityEntity;
// CAPA Entity
class CAPAEntity {
    data;
    constructor(data) {
        this.data = exports.CAPASchema.parse(data);
        this.validateBusinessRules();
    }
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get ncId() { return this.data.ncId; }
    get title() { return this.data.title; }
    get description() { return this.data.description; }
    get type() { return this.data.type; }
    get priority() { return this.data.priority; }
    get status() { return this.data.status; }
    get assignedTo() { return this.data.assignedTo; }
    get dueDate() { return this.data.dueDate; }
    get closedAt() { return this.data.closedAt; }
    get effectiveness() { return this.data.effectiveness; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    validateBusinessRules() {
        if (this.data.closedAt) {
            const createdDate = new Date(this.data.createdAt);
            const closedDate = new Date(this.data.closedAt);
            if (closedDate < createdDate) {
                throw new Error('Closed date cannot be before creation date');
            }
        }
        if (this.data.dueDate) {
            const dueDate = new Date(this.data.dueDate);
            const createdDate = new Date(this.data.createdAt);
            if (dueDate < createdDate) {
                throw new Error('Due date cannot be before creation date');
            }
        }
    }
    isOpen() {
        return this.data.status === 'Open';
    }
    isInProgress() {
        return this.data.status === 'InProgress';
    }
    isClosed() {
        return this.data.status === 'Closed';
    }
    isOverdue() {
        if (!this.data.dueDate || this.isClosed()) {
            return false;
        }
        return new Date(this.data.dueDate) < new Date();
    }
    isCritical() {
        return this.data.priority === 'Critical';
    }
    isCorrective() {
        return this.data.type === 'CorrectiveAction';
    }
    isPreventive() {
        return this.data.type === 'PreventiveAction';
    }
    assignTo(userId, updatedBy) {
        return new CAPAEntity({
            ...this.data,
            assignedTo: userId,
            status: 'InProgress',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    close(effectiveness, closedAt, updatedBy) {
        if (this.isClosed()) {
            throw new Error('CAPA is already closed');
        }
        return new CAPAEntity({
            ...this.data,
            status: 'Closed',
            effectiveness,
            closedAt,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    toJSON() {
        return { ...this.data };
    }
    static create(data) {
        const now = new Date().toISOString();
        return new CAPAEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
}
exports.CAPAEntity = CAPAEntity;
//# sourceMappingURL=quality.js.map