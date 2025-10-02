"use strict";
/**
 * Leave Request Entity for VALEO NeuroERP 3.0 HR Domain
 * Vacation, sick leave, and other absence management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.LeaveRequestEntity = exports.LeaveRequestSchema = void 0;
const zod_1 = require("zod");
exports.LeaveRequestSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    employeeId: zod_1.z.string().uuid(),
    type: zod_1.z.enum(['Vacation', 'Sick', 'Unpaid', 'Other']),
    from: zod_1.z.string().date(),
    to: zod_1.z.string().date(),
    days: zod_1.z.number().positive(),
    status: zod_1.z.enum(['Pending', 'Approved', 'Rejected']),
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
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // +1 to include both start and end days
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
        // Check for reasonable leave duration (max 365 days)
        if (this.data.days > 365) {
            throw new Error('Leave duration cannot exceed 365 days');
        }
        // Validate that days matches the actual date range
        const actualDays = this.getDurationInDays();
        if (Math.abs(this.data.days - actualDays) > 1) { // Allow 1 day tolerance for weekend handling
            throw new Error('Declared days must match the date range');
        }
    }
    // State Changes
    approve(approvedBy, note) {
        if (!this.canApprove()) {
            throw new Error('Leave request cannot be approved in current status');
        }
        return new LeaveRequestEntity({
            ...this.data,
            status: 'Approved',
            approvedBy,
            note: note || this.data.note,
            updatedAt: new Date().toISOString(),
            updatedBy: approvedBy,
            version: this.data.version + 1
        });
    }
    reject(approvedBy, note) {
        if (!this.canReject()) {
            throw new Error('Leave request cannot be rejected in current status');
        }
        return new LeaveRequestEntity({
            ...this.data,
            status: 'Rejected',
            approvedBy,
            note: note || this.data.note,
            updatedAt: new Date().toISOString(),
            updatedBy: approvedBy,
            version: this.data.version + 1
        });
    }
    updateNote(note, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Leave request cannot be edited in current status');
        }
        return new LeaveRequestEntity({
            ...this.data,
            note,
            updatedAt: new Date().toISOString(),
            updatedBy,
            version: this.data.version + 1
        });
    }
    updateDates(from, to, days, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Leave request cannot be edited in current status');
        }
        return new LeaveRequestEntity({
            ...this.data,
            from,
            to,
            days,
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
        return new LeaveRequestEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now,
            version: 1
        });
    }
    static fromJSON(data) {
        return new LeaveRequestEntity(data);
    }
}
exports.LeaveRequestEntity = LeaveRequestEntity;
//# sourceMappingURL=leave-request.js.map