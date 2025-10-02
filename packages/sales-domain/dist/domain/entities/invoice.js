"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceEntity = exports.UpdateInvoiceInputSchema = exports.CreateInvoiceInputSchema = exports.InvoiceSchema = exports.InvoiceLineSchema = exports.InvoiceStatus = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Invoice Status Enum
exports.InvoiceStatus = {
    ISSUED: 'Issued',
    PAID: 'Paid',
    OVERDUE: 'Overdue',
    CANCELLED: 'Cancelled'
};
// Invoice Line Item Schema
exports.InvoiceLineSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    sku: zod_1.z.string().min(1),
    name: zod_1.z.string().min(1),
    description: zod_1.z.string().optional(),
    quantity: zod_1.z.number().positive(),
    unitPrice: zod_1.z.number().nonnegative(),
    discount: zod_1.z.number().min(0).max(100).default(0), // Percentage
    totalNet: zod_1.z.number().nonnegative(),
    totalGross: zod_1.z.number().nonnegative()
});
// Invoice Entity Schema
exports.InvoiceSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    orderId: zod_1.z.string().uuid().optional(), // Optional for ad-hoc invoices
    invoiceNumber: zod_1.z.string().min(1),
    lines: zod_1.z.array(exports.InvoiceLineSchema),
    subtotalNet: zod_1.z.number().nonnegative(),
    totalDiscount: zod_1.z.number().nonnegative(),
    totalNet: zod_1.z.number().nonnegative(),
    totalGross: zod_1.z.number().nonnegative(),
    taxRate: zod_1.z.number().min(0).max(100).default(19), // Default 19% VAT
    currency: zod_1.z.string().length(3).default('EUR'),
    dueDate: zod_1.z.date(),
    paidAt: zod_1.z.date().optional(),
    notes: zod_1.z.string().optional(),
    status: zod_1.z.enum([
        exports.InvoiceStatus.ISSUED,
        exports.InvoiceStatus.PAID,
        exports.InvoiceStatus.OVERDUE,
        exports.InvoiceStatus.CANCELLED
    ]),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Invoice Input Schema (for API)
exports.CreateInvoiceInputSchema = exports.InvoiceSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true,
    subtotalNet: true,
    totalDiscount: true,
    totalNet: true,
    totalGross: true,
    status: true,
    paidAt: true
}).extend({
    lines: zod_1.z.array(exports.InvoiceLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});
// Update Invoice Input Schema (for API)
exports.UpdateInvoiceInputSchema = zod_1.z.object({
    dueDate: zod_1.z.date().optional(),
    notes: zod_1.z.string().nullish(),
    status: zod_1.z.enum([
        exports.InvoiceStatus.ISSUED,
        exports.InvoiceStatus.PAID,
        exports.InvoiceStatus.OVERDUE,
        exports.InvoiceStatus.CANCELLED
    ]).optional()
});
// Invoice Aggregate Root
class InvoiceEntity {
    props;
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        const now = new Date();
        // Calculate totals from lines
        const lines = props.lines.map((line, index) => ({
            ...line,
            id: (0, uuid_1.v4)(),
            totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100),
            totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100)
        }));
        const subtotalNet = lines.reduce((sum, line) => sum + line.totalNet, 0);
        const totalDiscount = lines.reduce((sum, line) => sum + (line.quantity * line.unitPrice * line.discount / 100), 0);
        const totalNet = subtotalNet;
        const totalGross = lines.reduce((sum, line) => sum + line.totalGross, 0);
        const invoice = {
            ...props,
            id: (0, uuid_1.v4)(),
            lines,
            subtotalNet,
            totalDiscount,
            totalNet,
            totalGross,
            status: exports.InvoiceStatus.ISSUED,
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new InvoiceEntity(invoice);
    }
    static fromPersistence(props) {
        return new InvoiceEntity(props);
    }
    update(props) {
        if (props.dueDate !== undefined) {
            this.props.dueDate = props.dueDate;
        }
        if (props.notes !== undefined) {
            this.props.notes = props.notes;
        }
        if (props.status !== undefined) {
            this.validateStatusTransition(this.props.status, props.status);
            this.props.status = props.status;
            if (props.status === exports.InvoiceStatus.PAID && !this.props.paidAt) {
                this.props.paidAt = new Date();
            }
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    markAsPaid() {
        if (this.props.status !== exports.InvoiceStatus.ISSUED) {
            throw new Error('Only issued invoices can be marked as paid');
        }
        this.props.status = exports.InvoiceStatus.PAID;
        this.props.paidAt = new Date();
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    markAsOverdue() {
        if (this.props.status !== exports.InvoiceStatus.ISSUED) {
            return; // Only issued invoices can become overdue
        }
        if (this.props.dueDate < new Date()) {
            this.props.status = exports.InvoiceStatus.OVERDUE;
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    }
    cancel() {
        if (this.props.status === exports.InvoiceStatus.PAID) {
            throw new Error('Paid invoices cannot be cancelled');
        }
        this.props.status = exports.InvoiceStatus.CANCELLED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    isOverdue() {
        return this.props.status === exports.InvoiceStatus.ISSUED && this.props.dueDate < new Date();
    }
    canBePaid() {
        return this.props.status === exports.InvoiceStatus.ISSUED;
    }
    canBeCancelled() {
        return this.props.status !== exports.InvoiceStatus.PAID;
    }
    validateStatusTransition(currentStatus, newStatus) {
        const validTransitions = {
            'Issued': ['Paid', 'Overdue', 'Cancelled'],
            'Paid': [], // Terminal state
            'Overdue': ['Paid', 'Cancelled'],
            'Cancelled': [] // Terminal state
        };
        const allowedStatuses = validTransitions[currentStatus];
        if (!allowedStatuses?.includes(newStatus)) {
            throw new Error(`Cannot change status from ${currentStatus} to ${newStatus}`);
        }
    }
    // Getters
    get id() { return this.props.id; }
    get tenantId() { return this.props.tenantId; }
    get customerId() { return this.props.customerId; }
    get orderId() { return this.props.orderId; }
    get invoiceNumber() { return this.props.invoiceNumber; }
    get lines() { return [...this.props.lines]; }
    get subtotalNet() { return this.props.subtotalNet; }
    get totalDiscount() { return this.props.totalDiscount; }
    get totalNet() { return this.props.totalNet; }
    get totalGross() { return this.props.totalGross; }
    get taxRate() { return this.props.taxRate; }
    get currency() { return this.props.currency; }
    get dueDate() { return this.props.dueDate; }
    get paidAt() { return this.props.paidAt; }
    get notes() { return this.props.notes; }
    get status() { return this.props.status; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...invoiceWithoutTenant } = this.props;
        return invoiceWithoutTenant;
    }
}
exports.InvoiceEntity = InvoiceEntity;
//# sourceMappingURL=invoice.js.map