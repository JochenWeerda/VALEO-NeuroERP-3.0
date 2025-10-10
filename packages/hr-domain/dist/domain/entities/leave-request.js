"use strict";
/**
 * Leave Request Entity for VALEO NeuroERP 3.0 HR Domain
 * Vacation, sick leave, and other absence management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.LeaveRequestEntity = exports.LeaveRequestSchema = void 0;
const uuid_1 = require("uuid");
const zod_1 = require("zod");
const MILLISECONDS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MILLISECONDS_PER_DAY = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;
const MAX_LEAVE_DURATION_DAYS = 365;
const INCLUSIVE_DAY_OFFSET = 1;
const DAY_TOLERANCE = 1;
const INITIAL_VERSION = 1;
const leaveTypeSchema = zod_1.z.enum(['Vacation', 'Sick', 'Unpaid', 'Other']);
const leaveStatusSchema = zod_1.z.enum(['Pending', 'Approved', 'Rejected']);
exports.LeaveRequestSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    employeeId: zod_1.z.string().uuid(),
    type: leaveTypeSchema,
    from: zod_1.z.string().date(),
    to: zod_1.z.string().date(),
    days: zod_1.z.number().positive(),
    status: leaveStatusSchema,
    approvedBy: zod_1.z.string().uuid().optional(),
    note: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number().int().min(1),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class LeaveRequestEntity {
    data;
    constructor(data) {
        this.data = exports.LeaveRequestSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get employeeId() { return this.data.employeeId; }
    get type() { return this.data.type; }
    get from() { return this.data.from; }
    get to() { return this.data.to; }
    get days() { return this.data.days; }
    get status() { return this.data.status; }
    get approvedBy() { return this.data.approvedBy; }
    get note() { return this.data.note; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    get version() { return this.data.version; }
    // Business Methods
    isPending() {
        return this.data.status === 'Pending';
    }
    isApproved() {
        return this.data.status === 'Approved';
    }
    isRejected() {
        return this.data.status === 'Rejected';
    }
    canEdit() {
        return this.isPending();
    }
    canApprove() {
        return this.isPending();
    }
    canReject() {
        return this.isPending();
    }
    isVacation() {
        return this.data.type === 'Vacation';
    }
    isSickLeave() {
        return this.data.type === 'Sick';
    }
    isUnpaid() {
        return this.data.type === 'Unpaid';
    }
    getDurationInDays() {
        const fromDate = new Date(this.data.from);
        const toDate = new Date(this.data.to);
        const diffTime = Math.abs(toDate.getTime() - fromDate.getTime());
        return Math.ceil(diffTime / MILLISECONDS_PER_DAY) + INCLUSIVE_DAY_OFFSET; // include start and end days
    }
    isInPeriod(date) {
        return date >= this.data.from && date <= this.data.to;
    }
    overlapsWith(other) {
        return this.isInPeriod(other.from) ||
            this.isInPeriod(other.to) ||
            other.isInPeriod(this.from) ||
            other.isInPeriod(this.to);
    }
    // Validation
    validateBusinessRules() {
        const fromDate = new Date(this.data.from);
        const toDate = new Date(this.data.to);
        if (toDate < fromDate) {
            throw new Error('End date must be after or equal to start date');
        }
        if (this.data.days <= 0) {
            throw new Error('Days must be positive');
        }
        if (this.data.days > MAX_LEAVE_DURATION_DAYS) {
            throw new Error('Leave duration cannot exceed 365 days');
        }
        const actualDays = this.getDurationInDays();
        if (Math.abs(this.data.days - actualDays) > DAY_TOLERANCE) {
            throw new Error('Declared days must match the date range');
        }
    }
    // State Changes
    approve(approvedBy, note) {
        if (!this.canApprove()) {
            throw new Error('Leave request cannot be approved in current status');
        }
        return this.clone({
            status: 'Approved',
            approvedBy,
            note: note ?? this.data.note,
            updatedBy: approvedBy
        });
    }
    reject(approvedBy, note) {
        if (!this.canReject()) {
            throw new Error('Leave request cannot be rejected in current status');
        }
        return this.clone({
            status: 'Rejected',
            approvedBy,
            note: note ?? this.data.note,
            updatedBy: approvedBy
        });
    }
    updateNote(note, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Leave request cannot be edited in current status');
        }
        return this.clone({ note, updatedBy });
    }
    updateDates(from, to, days, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Leave request cannot be edited in current status');
        }
        return this.clone({
            from,
            to,
            days,
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    clone(overrides) {
        const now = new Date().toISOString();
        return new LeaveRequestEntity({
            ...this.data,
            ...overrides,
            updatedAt: now,
            version: this.data.version + 1
        });
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new LeaveRequestEntity({
            ...data,
            id: (0, uuid_1.v4)(),
            createdAt: now,
            updatedAt: now,
            version: INITIAL_VERSION
        });
    }
    static fromJSON(data) {
        return new LeaveRequestEntity(data);
    }
}
exports.LeaveRequestEntity = LeaveRequestEntity;
//# sourceMappingURL=leave-request.js.map