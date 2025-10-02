"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QuoteEntity = exports.UpdateQuoteInputSchema = exports.CreateQuoteInputSchema = exports.QuoteSchema = exports.QuoteLineSchema = exports.QuoteStatus = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Quote Status Enum
exports.QuoteStatus = {
    DRAFT: 'Draft',
    SENT: 'Sent',
    ACCEPTED: 'Accepted',
    REJECTED: 'Rejected',
    EXPIRED: 'Expired'
};
// Quote Line Item Schema
exports.QuoteLineSchema = zod_1.z.object({
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
// Quote Entity Schema
exports.QuoteSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    quoteNumber: zod_1.z.string().min(1),
    lines: zod_1.z.array(exports.QuoteLineSchema),
    subtotalNet: zod_1.z.number().nonnegative(),
    totalDiscount: zod_1.z.number().nonnegative(),
    totalNet: zod_1.z.number().nonnegative(),
    totalGross: zod_1.z.number().nonnegative(),
    taxRate: zod_1.z.number().min(0).max(100).default(19), // Default 19% VAT
    currency: zod_1.z.string().length(3).default('EUR'),
    validUntil: zod_1.z.date(),
    notes: zod_1.z.string().optional(),
    status: zod_1.z.enum([
        exports.QuoteStatus.DRAFT,
        exports.QuoteStatus.SENT,
        exports.QuoteStatus.ACCEPTED,
        exports.QuoteStatus.REJECTED,
        exports.QuoteStatus.EXPIRED
    ]),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Quote Input Schema (for API)
exports.CreateQuoteInputSchema = exports.QuoteSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true,
    subtotalNet: true,
    totalDiscount: true,
    totalNet: true,
    totalGross: true
}).extend({
    lines: zod_1.z.array(exports.QuoteLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});
// Update Quote Input Schema (for API)
exports.UpdateQuoteInputSchema = zod_1.z.object({
    lines: zod_1.z.array(exports.QuoteLineSchema.omit({ id: true, totalNet: true, totalGross: true })).optional(),
    validUntil: zod_1.z.date().optional(),
    notes: zod_1.z.string().nullish(),
    status: zod_1.z.enum([
        exports.QuoteStatus.DRAFT,
        exports.QuoteStatus.SENT,
        exports.QuoteStatus.ACCEPTED,
        exports.QuoteStatus.REJECTED,
        exports.QuoteStatus.EXPIRED
    ]).optional()
});
// Quote Aggregate Root
class QuoteEntity {
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
        const quote = {
            ...props,
            id: (0, uuid_1.v4)(),
            lines,
            subtotalNet,
            totalDiscount,
            totalNet,
            totalGross,
            status: props.status || exports.QuoteStatus.DRAFT,
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new QuoteEntity(quote);
    }
    static fromPersistence(props) {
        return new QuoteEntity({
            ...props,
            subtotalNet: Number(props.subtotalNet),
            totalDiscount: Number(props.totalDiscount),
            totalNet: Number(props.totalNet),
            totalTax: Number(props.totalTax),
            totalGross: Number(props.totalGross),
            lines: props.lines.map((line) => ({
                ...line,
                unitPrice: Number(line.unitPrice),
                discount: Number(line.discount),
                totalNet: Number(line.totalNet),
                totalGross: Number(line.totalGross),
            })),
            notes: props.notes ?? undefined,
        });
    }
    update(props) {
        if (props.lines) {
            this.props.lines = props.lines.map((line, index) => ({
                ...line,
                id: this.props.lines[index]?.id || (0, uuid_1.v4)(),
                totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100),
                totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + this.props.taxRate / 100)
            }));
            // Recalculate totals
            this.props.subtotalNet = this.props.lines.reduce((sum, line) => sum + line.totalNet, 0);
            this.props.totalDiscount = this.props.lines.reduce((sum, line) => sum + (line.quantity * line.unitPrice * line.discount / 100), 0);
            this.props.totalNet = this.props.subtotalNet;
            this.props.totalGross = this.props.lines.reduce((sum, line) => sum + line.totalGross, 0);
        }
        if (props.validUntil !== undefined) {
            this.props.validUntil = props.validUntil ?? undefined;
        }
        if (props.notes !== undefined) {
            this.props.notes = props.notes ?? undefined;
        }
        if (props.status !== undefined) {
            this.validateStatusTransition(this.props.status, props.status);
            this.props.status = props.status;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    send() {
        if (this.props.status !== exports.QuoteStatus.DRAFT) {
            throw new Error('Only draft quotes can be sent');
        }
        this.props.status = exports.QuoteStatus.SENT;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    accept() {
        if (this.props.status !== exports.QuoteStatus.SENT) {
            throw new Error('Only sent quotes can be accepted');
        }
        this.props.status = exports.QuoteStatus.ACCEPTED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    reject() {
        if (this.props.status !== exports.QuoteStatus.SENT) {
            throw new Error('Only sent quotes can be rejected');
        }
        this.props.status = exports.QuoteStatus.REJECTED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    expire() {
        if (this.props.status === exports.QuoteStatus.EXPIRED || this.props.status === exports.QuoteStatus.REJECTED) {
            return; // Already expired or rejected
        }
        this.props.status = exports.QuoteStatus.EXPIRED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    isExpired() {
        return this.props.validUntil < new Date();
    }
    canBeAccepted() {
        return this.props.status === exports.QuoteStatus.SENT && !this.isExpired();
    }
    canBeSent() {
        return this.props.status === exports.QuoteStatus.DRAFT && this.props.lines.length > 0;
    }
    validateStatusTransition(currentStatus, newStatus) {
        const validTransitions = {
            'Draft': ['Sent'],
            'Sent': ['Accepted', 'Rejected', 'Expired'],
            'Accepted': [], // Terminal state
            'Rejected': [], // Terminal state
            'Expired': [] // Terminal state
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
    get quoteNumber() { return this.props.quoteNumber; }
    get lines() { return [...this.props.lines]; }
    get subtotalNet() { return this.props.subtotalNet; }
    get totalDiscount() { return this.props.totalDiscount; }
    get totalNet() { return this.props.totalNet; }
    get totalGross() { return this.props.totalGross; }
    get taxRate() { return this.props.taxRate; }
    get currency() { return this.props.currency; }
    get validUntil() { return this.props.validUntil; }
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
        const { tenantId, ...quoteWithoutTenant } = this.props;
        return quoteWithoutTenant;
    }
}
exports.QuoteEntity = QuoteEntity;
//# sourceMappingURL=quote.js.map