"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreditNoteEntity = exports.UpdateCreditNoteInputSchema = exports.CreateCreditNoteInputSchema = exports.CreditNoteSchema = exports.CreditNoteLineSchema = exports.CreditNoteStatus = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Credit Note Status Enum
exports.CreditNoteStatus = {
    ISSUED: 'Issued',
    SETTLED: 'Settled'
};
// Credit Note Line Item Schema
exports.CreditNoteLineSchema = zod_1.z.object({
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
// Credit Note Entity Schema
exports.CreditNoteSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    invoiceId: zod_1.z.string().uuid(),
    creditNumber: zod_1.z.string().min(1),
    lines: zod_1.z.array(exports.CreditNoteLineSchema),
    subtotalNet: zod_1.z.number().nonnegative(),
    totalDiscount: zod_1.z.number().nonnegative(),
    totalNet: zod_1.z.number().nonnegative(),
    totalGross: zod_1.z.number().nonnegative(),
    taxRate: zod_1.z.number().min(0).max(100).default(19), // Default 19% VAT
    currency: zod_1.z.string().length(3).default('EUR'),
    reason: zod_1.z.string().min(1),
    notes: zod_1.z.string().optional(),
    status: zod_1.z.enum([
        exports.CreditNoteStatus.ISSUED,
        exports.CreditNoteStatus.SETTLED
    ]),
    settledAt: zod_1.z.date().optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Credit Note Input Schema (for API)
exports.CreateCreditNoteInputSchema = exports.CreditNoteSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true,
    subtotalNet: true,
    totalDiscount: true,
    totalNet: true,
    totalGross: true,
    status: true,
    settledAt: true
}).extend({
    lines: zod_1.z.array(exports.CreditNoteLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});
// Update Credit Note Input Schema (for API)
exports.UpdateCreditNoteInputSchema = zod_1.z.object({
    reason: zod_1.z.string().min(1).optional(),
    notes: zod_1.z.string().nullish(),
    status: zod_1.z.enum([
        exports.CreditNoteStatus.ISSUED,
        exports.CreditNoteStatus.SETTLED
    ]).optional()
});
// Credit Note Aggregate Root
class CreditNoteEntity {
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
        const creditNote = {
            ...props,
            id: (0, uuid_1.v4)(),
            lines,
            subtotalNet,
            totalDiscount,
            totalNet,
            totalGross,
            status: exports.CreditNoteStatus.ISSUED,
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new CreditNoteEntity(creditNote);
    }
    static fromPersistence(props) {
        return new CreditNoteEntity({
            ...props,
            subtotalNet: Number(props.subtotalNet),
            totalDiscount: Number(props.totalDiscount),
            totalNet: Number(props.totalNet),
            totalGross: Number(props.totalGross),
            lines: props.lines.map((line) => ({
                ...line,
                unitPrice: Number(line.unitPrice),
                discount: Number(line.discount),
                totalNet: Number(line.totalNet),
                totalGross: Number(line.totalGross),
            })),
            settledAt: props.settledAt ?? undefined,
        });
    }
    update(props) {
        if (props.reason !== undefined) {
            this.props.reason = props.reason;
        }
        if (props.notes !== undefined) {
            this.props.notes = props.notes ?? undefined;
        }
        if (props.status !== undefined) {
            this.validateStatusTransition(this.props.status, props.status);
            this.props.status = props.status;
            if (props.status === exports.CreditNoteStatus.SETTLED && !this.props.settledAt) {
                this.props.settledAt = new Date();
            }
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    settle() {
        if (this.props.status !== exports.CreditNoteStatus.ISSUED) {
            throw new Error('Only issued credit notes can be settled');
        }
        this.props.status = exports.CreditNoteStatus.SETTLED;
        this.props.settledAt = new Date();
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    canBeSettled() {
        return this.props.status === exports.CreditNoteStatus.ISSUED;
    }
    validateStatusTransition(currentStatus, newStatus) {
        const validTransitions = {
            'Issued': ['Settled'],
            'Settled': [] // Terminal state
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
    get invoiceId() { return this.props.invoiceId; }
    get creditNumber() { return this.props.creditNumber; }
    get lines() { return [...this.props.lines]; }
    get subtotalNet() { return this.props.subtotalNet; }
    get totalDiscount() { return this.props.totalDiscount; }
    get totalNet() { return this.props.totalNet; }
    get totalGross() { return this.props.totalGross; }
    get taxRate() { return this.props.taxRate; }
    get currency() { return this.props.currency; }
    get reason() { return this.props.reason; }
    get notes() { return this.props.notes; }
    get status() { return this.props.status; }
    get settledAt() { return this.props.settledAt; }
    get createdAt() { return this.props.createdAt; }
    get updatedAt() { return this.props.updatedAt; }
    get version() { return this.props.version; }
    // Export for persistence
    toPersistence() {
        return { ...this.props };
    }
    // Export for API responses
    toJSON() {
        const { tenantId, ...creditNoteWithoutTenant } = this.props;
        return creditNoteWithoutTenant;
    }
}
exports.CreditNoteEntity = CreditNoteEntity;
//# sourceMappingURL=credit-note.js.map