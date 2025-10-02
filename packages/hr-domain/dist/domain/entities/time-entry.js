"use strict";
/**
 * Time Entry Entity for VALEO NeuroERP 3.0 HR Domain
 * Time tracking with validation and business rules
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.TimeEntryEntity = exports.TimeEntrySchema = void 0;
const zod_1 = require("zod");
exports.TimeEntrySchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    employeeId: zod_1.z.string().uuid(),
    date: zod_1.z.string().date(),
    start: zod_1.z.string().datetime(),
    end: zod_1.z.string().datetime(),
    breakMinutes: zod_1.z.number().int().min(0).max(480), // Max 8 hours break
    projectId: zod_1.z.string().uuid().optional(),
    costCenter: zod_1.z.string().optional(),
    source: zod_1.z.enum(['Manual', 'Terminal', 'Mobile']),
    status: zod_1.z.enum(['Draft', 'Approved', 'Rejected']),
    approvedBy: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number().int().min(1),
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
        const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
        return Math.max(0, totalMinutes - this.data.breakMinutes);
    }
    getWorkingHours() {
        return this.getWorkingMinutes() / 60;
    }
    getOvertimeMinutes(maxDailyHours = 8) {
        const maxMinutes = maxDailyHours * 60;
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
        const totalMinutes = Math.floor((endTime.getTime() - startTime.getTime()) / (1000 * 60));
        if (this.data.breakMinutes > totalMinutes) {
            throw new Error('Break time cannot exceed total time');
        }
        // Check for reasonable working hours (max 24 hours)
        if (totalMinutes > 24 * 60) {
            throw new Error('Working time cannot exceed 24 hours');
        }
    }
    // State Changes
    approve(approvedBy) {
        if (!this.canApprove()) {
            throw new Error('Time entry cannot be approved in current status');
        }
        return new TimeEntryEntity({
            ...this.data,
            status: 'Approved',
            approvedBy,
            updatedAt: new Date().toISOString(),
            updatedBy: approvedBy,
            version: this.data.version + 1
        });
    }
    reject(approvedBy) {
        if (!this.canReject()) {
            throw new Error('Time entry cannot be rejected in current status');
        }
        return new TimeEntryEntity({
            ...this.data,
            status: 'Rejected',
            approvedBy,
            updatedAt: new Date().toISOString(),
            updatedBy: approvedBy,
            version: this.data.version + 1
        });
    }
    updateTimes(start, end, breakMinutes, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return new TimeEntryEntity({
            ...this.data,
            start,
            end,
            breakMinutes,
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    updateProject(projectId, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return new TimeEntryEntity({
            ...this.data,
            projectId,
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    updateCostCenter(costCenter, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Time entry cannot be edited in current status');
        }
        return new TimeEntryEntity({
            ...this.data,
            costCenter,
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new TimeEntryEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now,
            version: 1
        });
    }
    static fromJSON(data) {
        return new TimeEntryEntity(data);
    }
}
exports.TimeEntryEntity = TimeEntryEntity;
//# sourceMappingURL=time-entry.js.map