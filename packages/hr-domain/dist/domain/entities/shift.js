"use strict";
/**
 * Shift Entity for VALEO NeuroERP 3.0 HR Domain
 * Shift planning and scheduling
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ShiftEntity = exports.ShiftSchema = void 0;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
const SHIFT_NAME_MIN_LENGTH = 1;
const SHIFT_NAME_MAX_LENGTH = 200;
const MIN_REQUIRED_HEADCOUNT = 1;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const MILLISECONDS_PER_HOUR = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
const MAX_SHIFT_DURATION_HOURS = 24;
const MIN_SHIFT_DURATION_HOURS = 0.5;
exports.ShiftSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    name: zod_1.z.string().min(SHIFT_NAME_MIN_LENGTH).max(SHIFT_NAME_MAX_LENGTH),
    location: zod_1.z.string().optional(),
    startsAt: zod_1.z.string().datetime(),
    endsAt: zod_1.z.string().datetime(),
    requiredHeadcount: zod_1.z.number().int().min(MIN_REQUIRED_HEADCOUNT),
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
        return (endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_HOUR;
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
        if (this.data.requiredHeadcount < MIN_REQUIRED_HEADCOUNT) {
            throw new Error('Required headcount must be at least 1');
        }
        const durationHours = this.getDurationHours();
        if (durationHours > MAX_SHIFT_DURATION_HOURS) {
            throw new Error('Shift duration cannot exceed 24 hours');
        }
        if (durationHours < MIN_SHIFT_DURATION_HOURS) {
            throw new Error('Shift duration must be at least 30 minutes');
        }
    }
    // State Changes
    assignEmployee(employeeId, updatedBy) {
        if (!this.canAssignEmployee(employeeId)) {
            throw new Error('Employee is already assigned to this shift');
        }
        return this.clone({
            assigned: [...this.data.assigned, employeeId],
            updatedBy
        });
    }
    unassignEmployee(employeeId, updatedBy) {
        if (!this.hasEmployee(employeeId)) {
            throw new Error('Employee is not assigned to this shift');
        }
        return this.clone({
            assigned: this.data.assigned.filter(id => id !== employeeId),
            updatedBy
        });
    }
    updateRequiredHeadcount(headcount, updatedBy) {
        if (headcount < 1) {
            throw new Error('Required headcount must be at least 1');
        }
        return this.clone({
            requiredHeadcount: headcount,
            updatedBy
        });
    }
    updateLocation(location, updatedBy) {
        return this.clone({
            location,
            updatedBy
        });
    }
    updateTimes(startsAt, endsAt, updatedBy) {
        return this.clone({
            startsAt,
            endsAt,
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    clone(overrides) {
        const now = new Date().toISOString();
        return new ShiftEntity({
            ...this.data,
            ...overrides,
            updatedAt: now
        });
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new ShiftEntity({
            ...data,
            id: (0, uuid_1.v4)(),
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