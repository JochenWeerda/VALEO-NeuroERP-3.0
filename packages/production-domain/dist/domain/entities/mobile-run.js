"use strict";
/**
 * Mobile Run Entity for VALEO NeuroERP 3.0 Production Domain
 * Mobile production unit management with calibration and cleaning
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MobileRunEntity = exports.MobileRunSchema = void 0;
const zod_1 = require("zod");
// Calibration Check Schema
const CalibrationCheckSchema = zod_1.z.object({
    scaleOk: zod_1.z.boolean(),
    moistureOk: zod_1.z.boolean(),
    temperatureOk: zod_1.z.boolean(),
    date: zod_1.z.string().datetime(),
    validatedBy: zod_1.z.string(),
    notes: zod_1.z.string().optional()
});
// Cleaning Sequence Schema
const CleaningSequenceSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    type: zod_1.z.enum(['DryClean', 'Vacuum', 'Flush', 'WetClean']),
    startedAt: zod_1.z.string().datetime(),
    endedAt: zod_1.z.string().datetime().optional(),
    usedMaterialSku: zod_1.z.string().optional(),
    flushMassKg: zod_1.z.number().min(0).optional(),
    validatedBy: zod_1.z.string(),
    notes: zod_1.z.string().optional()
});
// Main Mobile Run Schema
exports.MobileRunSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    mobileUnitId: zod_1.z.string().uuid(),
    vehicleId: zod_1.z.string().uuid().optional(),
    operatorId: zod_1.z.string().uuid(),
    site: zod_1.z.object({
        customerId: zod_1.z.string().uuid(),
        location: zod_1.z.object({
            lat: zod_1.z.number().min(-90).max(90),
            lng: zod_1.z.number().min(-180).max(180),
            address: zod_1.z.string().optional()
        })
    }),
    powerSource: zod_1.z.enum(['Generator', 'Grid', 'Battery']).default('Generator'),
    calibrationCheck: CalibrationCheckSchema,
    startAt: zod_1.z.string().datetime(),
    endAt: zod_1.z.string().datetime().optional(),
    cleaningSequenceId: zod_1.z.string().uuid().optional(),
    cleaningSequences: zod_1.z.array(CleaningSequenceSchema).default([]),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class MobileRunEntity {
    data;
    constructor(data) {
        this.data = exports.MobileRunSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get mobileUnitId() { return this.data.mobileUnitId; }
    get vehicleId() { return this.data.vehicleId; }
    get operatorId() { return this.data.operatorId; }
    get site() { return this.data.site; }
    get powerSource() { return this.data.powerSource; }
    get calibrationCheck() { return this.data.calibrationCheck; }
    get startAt() { return this.data.startAt; }
    get endAt() { return this.data.endAt; }
    get cleaningSequenceId() { return this.data.cleaningSequenceId; }
    get cleaningSequences() { return [...this.data.cleaningSequences]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    isActive() {
        return !this.data.endAt;
    }
    isCompleted() {
        return !!this.data.endAt;
    }
    canStart() {
        return this.isCalibrationValid() && !this.isActive();
    }
    canFinish() {
        return this.isActive();
    }
    isCalibrationValid() {
        const check = this.data.calibrationCheck;
        return check.scaleOk && check.moistureOk && check.temperatureOk;
    }
    isCalibrationExpired(maxDays = 30) {
        const checkDate = new Date(this.data.calibrationCheck.date);
        const now = new Date();
        const diffDays = (now.getTime() - checkDate.getTime()) / (1000 * 60 * 60 * 24);
        return diffDays > maxDays;
    }
    getDurationHours() {
        if (!this.data.endAt)
            return 0;
        const startTime = new Date(this.data.startAt);
        const endTime = new Date(this.data.endAt);
        return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
    }
    getActiveCleaningSequence() {
        return this.data.cleaningSequences.find(seq => !seq.endedAt);
    }
    getCompletedCleaningSequences() {
        return this.data.cleaningSequences.filter(seq => seq.endedAt);
    }
    getTotalFlushMass() {
        return this.data.cleaningSequences
            .filter(seq => seq.type === 'Flush' && seq.flushMassKg)
            .reduce((total, seq) => total + (seq.flushMassKg || 0), 0);
    }
    getCleaningHistory() {
        return [...this.data.cleaningSequences].sort((a, b) => new Date(b.startedAt).getTime() - new Date(a.startedAt).getTime());
    }
    // Validation
    validateBusinessRules() {
        // Validate calibration check date is not in the future
        const checkDate = new Date(this.data.calibrationCheck.date);
        const now = new Date();
        if (checkDate > now) {
            throw new Error('Calibration check date cannot be in the future');
        }
        // Validate time sequence
        if (this.data.endAt) {
            const startTime = new Date(this.data.startAt);
            const endTime = new Date(this.data.endAt);
            if (endTime <= startTime) {
                throw new Error('End time must be after start time');
            }
        }
        // Validate cleaning sequences
        for (const seq of this.data.cleaningSequences) {
            if (seq.endedAt) {
                const startTime = new Date(seq.startedAt);
                const endTime = new Date(seq.endedAt);
                if (endTime <= startTime) {
                    throw new Error(`Cleaning sequence ${seq.type} has invalid time range`);
                }
            }
        }
        // Validate location coordinates
        const { lat, lng } = this.data.site.location;
        if (lat < -90 || lat > 90) {
            throw new Error('Invalid latitude');
        }
        if (lng < -180 || lng > 180) {
            throw new Error('Invalid longitude');
        }
    }
    // State Changes
    finish(endAt, updatedBy) {
        if (!this.canFinish()) {
            throw new Error('Mobile run cannot be finished in current status');
        }
        return new MobileRunEntity({
            ...this.data,
            endAt,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateCalibrationCheck(check, updatedBy) {
        return new MobileRunEntity({
            ...this.data,
            calibrationCheck: check,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    addCleaningSequence(sequence, updatedBy) {
        const newSequence = {
            ...sequence,
            id: require('uuid').v4()
        };
        // Check for overlapping cleaning sequences
        const hasActiveSequence = this.getActiveCleaningSequence();
        if (hasActiveSequence) {
            throw new Error('Cannot start new cleaning sequence while another is active');
        }
        return new MobileRunEntity({
            ...this.data,
            cleaningSequences: [...this.data.cleaningSequences, newSequence],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    endCleaningSequence(sequenceId, endedAt, notes, updatedBy) {
        const sequenceIndex = this.data.cleaningSequences.findIndex(seq => seq.id === sequenceId);
        if (sequenceIndex === -1) {
            throw new Error('Cleaning sequence not found');
        }
        const sequence = this.data.cleaningSequences[sequenceIndex];
        if (sequence.endedAt) {
            throw new Error('Cleaning sequence is already ended');
        }
        const updatedSequence = {
            ...sequence,
            endedAt,
            notes: notes ? `${sequence.notes || ''}\n${notes}`.trim() : sequence.notes
        };
        const updatedSequences = [...this.data.cleaningSequences];
        updatedSequences[sequenceIndex] = updatedSequence;
        return new MobileRunEntity({
            ...this.data,
            cleaningSequences: updatedSequences,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    // Cleaning sequence validation
    validateCleaningRequired(previousRecipeMedicated, currentRecipeMedicated) {
        // Medicated to non-medicated requires cleaning
        if (previousRecipeMedicated && !currentRecipeMedicated) {
            return true;
        }
        // Check if any cleaning was performed recently
        const recentCleaning = this.data.cleaningSequences.find(seq => {
            const endTime = seq.endedAt ? new Date(seq.endedAt) : new Date();
            const now = new Date();
            const diffHours = (now.getTime() - endTime.getTime()) / (1000 * 60 * 60);
            return diffHours < 24; // Cleaning within last 24 hours
        });
        return !recentCleaning;
    }
    getRequiredCleaningType(previousRecipeMedicated, currentRecipeMedicated) {
        if (previousRecipeMedicated && !currentRecipeMedicated) {
            return 'WetClean'; // Full cleaning for medicated to non-medicated
        }
        return 'Flush'; // Basic flush for other transitions
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new MobileRunEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new MobileRunEntity(data);
    }
}
exports.MobileRunEntity = MobileRunEntity;
//# sourceMappingURL=mobile-run.js.map