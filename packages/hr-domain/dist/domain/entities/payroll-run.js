"use strict";
/**
 * Payroll Run Entity for VALEO NeuroERP 3.0 HR Domain
 * Payroll preparation and export (no accounting entries)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.PayrollRunEntity = exports.PayrollRunSchema = void 0;
const zod_1 = require("zod");
const PayrollItemSchema = zod_1.z.object({
    employeeId: zod_1.z.string().uuid(),
    hours: zod_1.z.number().positive(),
    allowances: zod_1.z.number().min(0).optional(),
    deductions: zod_1.z.number().min(0).optional(),
    grossAmount: zod_1.z.number().min(0).optional() // Optional preview calculation
});
const PayrollPeriodSchema = zod_1.z.object({
    from: zod_1.z.string().date(),
    to: zod_1.z.string().date()
});
exports.PayrollRunSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    period: PayrollPeriodSchema,
    status: zod_1.z.enum(['Draft', 'Locked', 'Exported']),
    items: zod_1.z.array(PayrollItemSchema),
    exportedAt: zod_1.z.string().datetime().optional(),
    exportedBy: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    createdBy: zod_1.z.string().optional(),
    updatedBy: zod_1.z.string().optional()
});
class PayrollRunEntity {
    data;
    constructor(data) {
        this.data = exports.PayrollRunSchema.parse(data);
        this.validateBusinessRules();
    }
    // Getters
    get id() { return this.data.id; }
    get tenantId() { return this.data.tenantId; }
    get period() { return this.data.period; }
    get status() { return this.data.status; }
    get items() { return [...this.data.items]; }
    get exportedAt() { return this.data.exportedAt; }
    get exportedBy() { return this.data.exportedBy; }
    get createdAt() { return this.data.createdAt; }
    get updatedAt() { return this.data.updatedAt; }
    // Business Methods
    isDraft() {
        return this.data.status === 'Draft';
    }
    isLocked() {
        return this.data.status === 'Locked';
    }
    isExported() {
        return this.data.status === 'Exported';
    }
    canEdit() {
        return this.isDraft();
    }
    canLock() {
        return this.isDraft() && this.data.items.length > 0;
    }
    canExport() {
        return this.isLocked();
    }
    getEmployeeCount() {
        return this.data.items.length;
    }
    getTotalHours() {
        return this.data.items.reduce((sum, item) => sum + item.hours, 0);
    }
    getTotalGrossAmount() {
        return this.data.items.reduce((sum, item) => sum + (item.grossAmount || 0), 0);
    }
    getTotalAllowances() {
        return this.data.items.reduce((sum, item) => sum + (item.allowances || 0), 0);
    }
    getTotalDeductions() {
        return this.data.items.reduce((sum, item) => sum + (item.deductions || 0), 0);
    }
    getPeriodDurationInDays() {
        const fromDate = new Date(this.data.period.from);
        const toDate = new Date(this.data.period.to);
        const diffTime = Math.abs(toDate.getTime() - fromDate.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    }
    hasEmployee(employeeId) {
        return this.data.items.some(item => item.employeeId === employeeId);
    }
    getEmployeeItem(employeeId) {
        return this.data.items.find(item => item.employeeId === employeeId);
    }
    // Validation
    validateBusinessRules() {
        const fromDate = new Date(this.data.period.from);
        const toDate = new Date(this.data.period.to);
        if (toDate < fromDate) {
            throw new Error('End date must be after or equal to start date');
        }
        // Check for reasonable period duration (max 1 year)
        const durationDays = this.getPeriodDurationInDays();
        if (durationDays > 365) {
            throw new Error('Payroll period cannot exceed 365 days');
        }
        // Validate items
        for (const item of this.data.items) {
            if (item.hours <= 0) {
                throw new Error('Employee hours must be positive');
            }
            if (item.allowances && item.allowances < 0) {
                throw new Error('Allowances cannot be negative');
            }
            if (item.deductions && item.deductions < 0) {
                throw new Error('Deductions cannot be negative');
            }
        }
        // Check for duplicate employees
        const employeeIds = this.data.items.map(item => item.employeeId);
        const uniqueEmployeeIds = new Set(employeeIds);
        if (employeeIds.length !== uniqueEmployeeIds.size) {
            throw new Error('Duplicate employees found in payroll run');
        }
    }
    // State Changes
    lock(updatedBy) {
        if (!this.canLock()) {
            throw new Error('Payroll run cannot be locked in current status');
        }
        return new PayrollRunEntity({
            ...this.data,
            status: 'Locked',
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    export(exportedBy) {
        if (!this.canExport()) {
            throw new Error('Payroll run cannot be exported in current status');
        }
        return new PayrollRunEntity({
            ...this.data,
            status: 'Exported',
            exportedAt: new Date().toISOString(),
            exportedBy,
            updatedAt: new Date().toISOString(),
            updatedBy: exportedBy
        });
    }
    addEmployeeItem(item, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Payroll run cannot be edited in current status');
        }
        if (this.hasEmployee(item.employeeId)) {
            throw new Error('Employee already exists in payroll run');
        }
        return new PayrollRunEntity({
            ...this.data,
            items: [...this.data.items, item],
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    updateEmployeeItem(employeeId, updates, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Payroll run cannot be edited in current status');
        }
        const updatedItems = this.data.items.map(item => item.employeeId === employeeId ? { ...item, ...updates } : item);
        return new PayrollRunEntity({
            ...this.data,
            items: updatedItems,
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    removeEmployeeItem(employeeId, updatedBy) {
        if (!this.canEdit()) {
            throw new Error('Payroll run cannot be edited in current status');
        }
        return new PayrollRunEntity({
            ...this.data,
            items: this.data.items.filter(item => item.employeeId !== employeeId),
            updatedAt: new Date().toISOString(),
            updatedBy
        });
    }
    // Export for persistence
    toJSON() {
        return { ...this.data };
    }
    // Factory methods
    static create(data) {
        const now = new Date().toISOString();
        return new PayrollRunEntity({
            ...data,
            id: require('uuid').v4(),
            createdAt: now,
            updatedAt: now
        });
    }
    static fromJSON(data) {
        return new PayrollRunEntity(data);
    }
}
exports.PayrollRunEntity = PayrollRunEntity;
//# sourceMappingURL=payroll-run.js.map