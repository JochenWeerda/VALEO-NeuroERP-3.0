"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceEntity = exports.UpdateInvoiceInputSchema = exports.CreateInvoiceInputSchema = exports.InvoiceSchema = exports.InvoiceLineSchema = exports.InvoiceStatus = void 0;
var zod_1 = require("zod");
var uuid_1 = require("uuid");
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
var InvoiceEntity = /** @class */ (function () {
    function InvoiceEntity(props) {
        this.props = props;
    }
    InvoiceEntity.create = function (props) {
        var now = new Date();
        // Calculate totals from lines
        var lines = props.lines.map(function (line, index) { return (__assign(__assign({}, line), { id: (0, uuid_1.v4)(), totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100), totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100) })); });
        var subtotalNet = lines.reduce(function (sum, line) { return sum + line.totalNet; }, 0);
        var totalDiscount = lines.reduce(function (sum, line) { return sum + (line.quantity * line.unitPrice * line.discount / 100); }, 0);
        var totalNet = subtotalNet;
        var totalGross = lines.reduce(function (sum, line) { return sum + line.totalGross; }, 0);
        var invoice = __assign(__assign({}, props), { id: (0, uuid_1.v4)(), lines: lines, subtotalNet: subtotalNet, totalDiscount: totalDiscount, totalNet: totalNet, totalGross: totalGross, status: exports.InvoiceStatus.ISSUED, createdAt: now, updatedAt: now, version: 1 });
        return new InvoiceEntity(invoice);
    };
    InvoiceEntity.fromPersistence = function (props) {
        var _a, _b;
        return new InvoiceEntity(__assign(__assign({}, props), { subtotalNet: Number(props.subtotalNet), totalDiscount: Number(props.totalDiscount), totalNet: Number(props.totalNet), totalTax: Number(props.totalTax), totalGross: Number(props.totalGross), lines: props.lines.map(function (line) { return (__assign(__assign({}, line), { unitPrice: Number(line.unitPrice), discount: Number(line.discount), totalNet: Number(line.totalNet), totalGross: Number(line.totalGross) })); }), paidAt: (_a = props.paidAt) !== null && _a !== void 0 ? _a : undefined, notes: (_b = props.notes) !== null && _b !== void 0 ? _b : undefined }));
    };
    InvoiceEntity.prototype.update = function (props) {
        var _a;
        if (props.dueDate !== undefined) {
            this.props.dueDate = props.dueDate;
        }
        if (props.notes !== undefined) {
            this.props.notes = (_a = props.notes) !== null && _a !== void 0 ? _a : undefined;
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
    };
    InvoiceEntity.prototype.markAsPaid = function () {
        if (this.props.status !== exports.InvoiceStatus.ISSUED) {
            throw new Error('Only issued invoices can be marked as paid');
        }
        this.props.status = exports.InvoiceStatus.PAID;
        this.props.paidAt = new Date();
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    InvoiceEntity.prototype.markAsOverdue = function () {
        if (this.props.status !== exports.InvoiceStatus.ISSUED) {
            return; // Only issued invoices can become overdue
        }
        if (this.props.dueDate < new Date()) {
            this.props.status = exports.InvoiceStatus.OVERDUE;
            this.props.updatedAt = new Date();
            this.props.version += 1;
        }
    };
    InvoiceEntity.prototype.cancel = function () {
        if (this.props.status === exports.InvoiceStatus.PAID) {
            throw new Error('Paid invoices cannot be cancelled');
        }
        this.props.status = exports.InvoiceStatus.CANCELLED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    InvoiceEntity.prototype.isOverdue = function () {
        return this.props.status === exports.InvoiceStatus.ISSUED && this.props.dueDate < new Date();
    };
    InvoiceEntity.prototype.canBePaid = function () {
        return this.props.status === exports.InvoiceStatus.ISSUED;
    };
    InvoiceEntity.prototype.canBeCancelled = function () {
        return this.props.status !== exports.InvoiceStatus.PAID;
    };
    InvoiceEntity.prototype.validateStatusTransition = function (currentStatus, newStatus) {
        var validTransitions = {
            'Issued': ['Paid', 'Overdue', 'Cancelled'],
            'Paid': [], // Terminal state
            'Overdue': ['Paid', 'Cancelled'],
            'Cancelled': [] // Terminal state
        };
        var allowedStatuses = validTransitions[currentStatus];
        if (!(allowedStatuses === null || allowedStatuses === void 0 ? void 0 : allowedStatuses.includes(newStatus))) {
            throw new Error("Cannot change status from ".concat(currentStatus, " to ").concat(newStatus));
        }
    };
    Object.defineProperty(InvoiceEntity.prototype, "id", {
        // Getters
        get: function () { return this.props.id; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "tenantId", {
        get: function () { return this.props.tenantId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "customerId", {
        get: function () { return this.props.customerId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "orderId", {
        get: function () { return this.props.orderId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "invoiceNumber", {
        get: function () { return this.props.invoiceNumber; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "lines", {
        get: function () { return __spreadArray([], this.props.lines, true); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "subtotalNet", {
        get: function () { return this.props.subtotalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "totalDiscount", {
        get: function () { return this.props.totalDiscount; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "totalNet", {
        get: function () { return this.props.totalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "totalGross", {
        get: function () { return this.props.totalGross; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "taxRate", {
        get: function () { return this.props.taxRate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "currency", {
        get: function () { return this.props.currency; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "dueDate", {
        get: function () { return this.props.dueDate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "paidAt", {
        get: function () { return this.props.paidAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "notes", {
        get: function () { return this.props.notes; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "status", {
        get: function () { return this.props.status; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "createdAt", {
        get: function () { return this.props.createdAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "updatedAt", {
        get: function () { return this.props.updatedAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(InvoiceEntity.prototype, "version", {
        get: function () { return this.props.version; },
        enumerable: false,
        configurable: true
    });
    // Export for persistence
    InvoiceEntity.prototype.toPersistence = function () {
        return __assign({}, this.props);
    };
    // Export for API responses
    InvoiceEntity.prototype.toJSON = function () {
        var _a = this.props, tenantId = _a.tenantId, invoiceWithoutTenant = __rest(_a, ["tenantId"]);
        return invoiceWithoutTenant;
    };
    return InvoiceEntity;
}());
exports.InvoiceEntity = InvoiceEntity;
