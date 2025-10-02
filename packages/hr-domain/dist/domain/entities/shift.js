"use strict";
/**
 * Shift Entity for VALEO NeuroERP 3.0 HR Domain
 * Shift planning and scheduling
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ShiftEntity = exports.ShiftSchema = void 0;
const zod_1 = require("zod");
exports.ShiftSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    name: zod_1.z.string().min(1).max(200),
    location: zod_1.z.string().optional(),
    startsAt: zod_1.z.string().datetime(),
    endsAt: zod_1.z.string().datetime(),
    requiredHeadcount: zod_1.z.number().int().min(1),
    assigned: zod_1.z.array(zod_1.z.string().uuid()),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class ShiftEntity {
    data;
    constructor(data) {
        this.data = exports.ShiftSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get name() { return this.data.name; }
    get location() { return this.data.location; }
    get startsAt() { return this.data.startsAt; }
    get endsAt() { return this.data.endsAt; }
    get requiredHeadcount() { return this.data.requiredHeadcount; }
    get assigned() { return [...this.data.assigned]; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    getDurationHours() {
        const startTime = new Date(this.data.startsAt);
        const endTime = new Date(this.data.endsAt);
        return (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);
    }
    getAssignedCount() {
        return this.data.assigned.length;
    }
    isFullyStaffed() {
        return this.getAssignedCount() >= this.data.requiredHeadcount;
    }
    isOverStaffed() {
        return this.getAssignedCount() > this.data.requiredHeadcount;
    }
    isUnderStaffed() {
        return this.getAssignedCount() < this.data.requiredHeadcount;
    }
    hasEmployee(employeeId) {
        return this.data.assigned.includes(employeeId);
    }
    canAssignEmployee(employeeId) {
        return !this.hasEmployee(employeeId);
    }
    getStaffingRatio() {
        return this.getAssignedCount() / this.data.requiredHeadcount;
    }
    // Validation
    validateBusinessRules() {
        const startTime = new Date(this.data.startsAt);
        const endTime = new Date(this.data.endsAt);
        if (endTime <= startTime) {
            throw new Error('End time must be after start time');
        }
        if (this.data.requiredHeadcount < 1) {
            throw new Error('Required headcount must be at least 1');
        }
        // Check for reasonable shift duration (max 24 hours)
        const durationHours = this.getDurationHours();
        if (durationHours > 24) {
            throw new Error('Shift duration cannot exceed 24 hours');
        }
        if (durationHours < 0.5) {
            throw new Error('Shift duration must be at least 30 minutes');
        }
    }
    // State Changes
    assignEmployee(employeeId, updatedBy) {
        if (!this.canAssignEmployee(employeeId)) {
            throw new Error('Employee is already assigned to this shift');
        }
        return new ShiftEntity({
            ...this.data,
            assigned: [...this.data.assigned, employeeId],
            updatedAt: new Date().toISOString(),
            updatedBy,
            // version: (this.data as any).version ? (this.data as any).version + 1 : 1
        });
    }
    unassignEmployee(employeeId, updatedBy) {
        if (!this.hasEmployee(employeeId)) {
            throw new Error('Employee is not assigned to this shift');
        }
        return new ShiftEntity({
            ...this.data,
            assigned: this.data.assigned.filter(id => id !== employeeId),
            updatedAt: new Date().toISOString(),
            updatedBy,
            // version: (this.data as any).version ? (this.data as any).version + 1 : 1
        });
    }
    updateRequiredHeadcount(headcount, updatedBy) {
        if (headcount < 1) {
            throw new Error('Required headcount must be at least 1');
        }
        return new ShiftEntity({
            ...this.data,
            requiredHeadcount: headcount,
            updatedAt: new Date().toISOString(),
            updatedBy,
            // version: (this.data as any).version ? (this.data as any).version + 1 : 1
        });
    }
    updateLocation(location, updatedBy) {
        return new ShiftEntity({
            ...this.data,
            location,
            updatedAt: new Date().toISOString(),
            updatedBy,
            // version: (this.data as any).version ? (this.data as any).version + 1 : 1
        });
    }
    updateTimes(startsAt, endsAt, updatedBy) {
        return new ShiftEntity({
            ...this.data,
            startsAt,
            endsAt,
            updatedAt: new Date().toISOString(),
            updatedBy,
            // version: (this.data as any).version ? (this.data as any).version + 1 : 1
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new ShiftEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new ShiftEntity(data);
    }
}
exports.ShiftEntity = ShiftEntity;
//# sourceMappingURL=shift.js.map