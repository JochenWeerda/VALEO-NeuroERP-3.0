"use strict";
/**
 * Time Entry Entity for VALEO NeuroERP 3.0 HR Domain
 * Time tracking with validation and business rules
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.TimeEntryEntity = exports.TimeEntrySchema = void 0;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
const MAX_BREAK_MINUTES = 480;
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MILLISECONDS_PER_MINUTE = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE;
const MINUTES_PER_DAY = HOURS_PER_DAY * MINUTES_PER_HOUR;
const DEFAULT_MAX_DAILY_HOURS = 8;
const INITIAL_VERSION = 1;
const timeEntrySourceSchema = zod_1.z.enum(['Manual', 'Terminal', 'Mobile']);
const timeEntryStatusSchema = zod_1.z.enum(['Draft', 'Approved', 'Rejected']);
exports.TimeEntrySchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    employeeId: zod_1.z.string().uuid(),
    date: zod_1.z.string().date(),
    start: zod_1.z.string().datetime(),
    end: zod_1.z.string().datetime(),
    breakMinutes: zod_1.z.number().int().min(0).max(MAX_BREAK_MINUTES), // Max 8 hours break
    projectId: zod_1.z.string().uuid().optional(),
    costCenter: zod_1.z.string().optional(),
    source: timeEntrySourceSchema,
    status: timeEntryStatusSchema,
    approvedBy: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number().int().min(INITIAL_VERSION),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class TimeEntryEntity {
    data;
    constructor(data) {
        this.data = exports.TimeEntrySchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get employeeId() { return this.data.employeeId; }
    get date() { return this.data.date; }
    get start() { return this.data.start; }
    get end() { return this.data.end; }
    get breakMinutes() { return this.data.breakMinutes; }
    get projectId() { return this.data.projectId; }
    get costCenter() { return this.data.costCenter; }
    get source() { return this.data.source; }
    get status() { return this.data.status; }
    get approvedBy() { return this.data.approvedBy; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    get version() { return this.data.version; }
    // Business Methods
    isDraft() {
        return this.data.status === 'Draft';
    }
    isApproved() {
        return this.data.status === 'Approved';
    }
    isRejected() {
        return this.data.status === 'Rejected';
    }
    canEdit() {
        return this.isDraft();
    }
    canApprove() {
        return this.isDraft();
    }
    canReject() {
        return this.isDraft();
    }
    getWorkingMinutes() {
        const startTime = new Date(this.data.start);
        const endTime = new Date(this.data.end);
        const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_MINUTE);
        return Math.max(0, totalMinutes - this.data.breakMinutes);
    }
    getWorkingHours() {
        return this.getWorkingMinutes() / MINUTES_PER_HOUR;
    }
    getOvertimeMinutes(maxDailyHours = DEFAULT_MAX_DAILY_HOURS) {
        const maxMinutes = maxDailyHours * MINUTES_PER_HOUR;
        const workingMinutes = this.getWorkingMinutes();
        return Math.max(0, workingMinutes - maxMinutes);
    }
    // Validation
    validateBusinessRules() {
        const startTime = new Date(this.data.start);
        const endTime = new Date(this.data.end);
        if (endTime <= startTime) {
            throw new Error('End time must be after start time');
        }
        const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / MILLISECONDS_PER_MINUTE);
        if (this.data.breakMinutes > totalMinutes) {
            throw new Error('Break time cannot exceed total time');
        }
        // Check for reasonable working hours (max 24 hours)
        if (totalMinutes > MINUTES_PER_DAY) {
            throw new Error('Working time cannot exceed 24 hours');
        }
    }
    // State Changes
    approve(approvedBy) {
        if (!this.canApprove()) {
            throw new Error('Time entry cannot be approved in current status');
        }
        return this.clone({
            status: 'Approved',
            approvedBy,
            updatedBy: approvedBy
        });
    }
    reject(approvedBy) {
        if (!this.canReject()) {
            throw new Error('Time entry cannot be rejected in current status');
        }
        return this.clone({
            status: 'Rejected',
            approvedBy,
            updatedBy: approvedBy
        });
    }
    updateTimes(start, end, breakMinutes, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return this.clone({
            start,
            end,
            breakMinutes,
            updatedBy
        });
    }
    updateProject(projectId, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return this.clone({ projectId, updatedBy });
    }
    updateCostCenter(costCenter, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return this.clone({ costCenter, updatedBy });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    clone(overrides) {
        const now = new Date().toISOString();
        return new TimeEntryEntity({
            ...this.data,
            ...overrides,
            updatedAt: now,
            version: this.data.version + 1
        });
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new TimeEntryEntity({
            ...data,
            id: (0, uuid_1.v4)(),
            createdAt: now,
            updatedAt: now,
            version: INITIAL_VERSION
        });
    }
    static fromJSON(data) {
        return new TimeEntryEntity(data);
    }
}
exports.TimeEntryEntity = TimeEntryEntity;
//# sourceMappingURL=time-entry.js.map