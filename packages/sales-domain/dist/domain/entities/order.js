"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderEntity = exports.UpdateOrderInputSchema = exports.CreateOrderInputSchema = exports.OrderSchema = exports.OrderLineSchema = exports.OrderStatus = void 0;
const zod_1 = require("zod");
const uuid_1 = require("uuid");
// Order Status Enum
exports.OrderStatus = {
    DRAFT: 'Draft',
    CONFIRMED: 'Confirmed',
    INVOICED: 'Invoiced',
    CANCELLED: 'Cancelled'
};
// Order Line Item Schema
exports.OrderLineSchema = zod_1.z.object({
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
// Order Entity Schema
exports.OrderSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string().uuid(),
    customerId: zod_1.z.string().uuid(),
    orderNumber: zod_1.z.string().min(1),
    lines: zod_1.z.array(exports.OrderLineSchema),
    subtotalNet: zod_1.z.number().nonnegative(),
    totalDiscount: zod_1.z.number().nonnegative(),
    totalNet: zod_1.z.number().nonnegative(),
    totalGross: zod_1.z.number().nonnegative(),
    taxRate: zod_1.z.number().min(0).max(100).default(19), // Default 19% VAT
    currency: zod_1.z.string().length(3).default('EUR'),
    expectedDeliveryDate: zod_1.z.date().optional(),
    notes: zod_1.z.string().optional(),
    status: zod_1.z.enum([
        exports.OrderStatus.DRAFT,
        exports.OrderStatus.CONFIRMED,
        exports.OrderStatus.INVOICED,
        exports.OrderStatus.CANCELLED
    ]),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    version: zod_1.z.number().int().nonnegative()
});
// Create Order Input Schema (for API)
exports.CreateOrderInputSchema = exports.OrderSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    version: true,
    subtotalNet: true,
    totalDiscount: true,
    totalNet: true,
    totalGross: true
}).extend({
    lines: zod_1.z.array(exports.OrderLineSchema.omit({ id: true, totalNet: true, totalGross: true }))
});
// Update Order Input Schema (for API)
exports.UpdateOrderInputSchema = zod_1.z.object({
    lines: zod_1.z.array(exports.OrderLineSchema.omit({ id: true, totalNet: true, totalGross: true })).optional(),
    expectedDeliveryDate: zod_1.z.date().nullish(),
    notes: zod_1.z.string().nullish(),
    status: zod_1.z.enum([
        exports.OrderStatus.DRAFT,
        exports.OrderStatus.CONFIRMED,
        exports.OrderStatus.INVOICED,
        exports.OrderStatus.CANCELLED
    ]).optional()
});
// Order Aggregate Root
class OrderEntity {
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
        const order = {
            ...props,
            id: (0, uuid_1.v4)(),
            lines,
            subtotalNet,
            totalDiscount,
            totalNet,
            totalGross,
            status: props.status || exports.OrderStatus.DRAFT,
            createdAt: now,
            updatedAt: now,
            version: 1
        };
        return new OrderEntity(order);
    }
    static fromPersistence(props) {
        return new OrderEntity({
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
            expectedDeliveryDate: props.expectedDeliveryDate ?? undefined,
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
        if (props.expectedDeliveryDate !== undefined) {
            this.props.expectedDeliveryDate = props.expectedDeliveryDate ?? undefined;
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
    confirm() {
        if (this.props.status !== exports.OrderStatus.DRAFT) {
            throw new Error('Only draft orders can be confirmed');
        }
        this.props.status = exports.OrderStatus.CONFIRMED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    markAsInvoiced() {
        if (this.props.status !== exports.OrderStatus.CONFIRMED) {
            throw new Error('Only confirmed orders can be invoiced');
        }
        this.props.status = exports.OrderStatus.INVOICED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    cancel() {
        if (this.props.status === exports.OrderStatus.INVOICED) {
            throw new Error('Invoiced orders cannot be cancelled');
        }
        this.props.status = exports.OrderStatus.CANCELLED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    }
    canBeConfirmed() {
        return this.props.status === exports.OrderStatus.DRAFT && this.props.lines.length > 0;
    }
    canBeInvoiced() {
        return this.props.status === exports.OrderStatus.CONFIRMED;
    }
    canBeCancelled() {
        return this.props.status !== exports.OrderStatus.INVOICED;
    }
    validateStatusTransition(currentStatus, newStatus) {
        const validTransitions = {
            'Draft': ['Confirmed', 'Cancelled'],
            'Confirmed': ['Invoiced', 'Cancelled'],
            'Invoiced': [], // Terminal state
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
    get orderNumber() { return this.props.orderNumber; }
    get lines() { return [...this.props.lines]; }
    get subtotalNet() { return this.props.subtotalNet; }
    get totalDiscount() { return this.props.totalDiscount; }
    get totalNet() { return this.props.totalNet; }
    get totalGross() { return this.props.totalGross; }
    get taxRate() { return this.props.taxRate; }
    get currency() { return this.props.currency; }
    get expectedDeliveryDate() { return this.props.expectedDeliveryDate; }
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
        const { tenantId, ...orderWithoutTenant } = this.props;
        return orderWithoutTenant;
    }
}
exports.OrderEntity = OrderEntity;
//# sourceMappingURL=order.js.map