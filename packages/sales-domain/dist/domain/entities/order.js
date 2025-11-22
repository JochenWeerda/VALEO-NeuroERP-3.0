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
exports.OrderEntity = exports.UpdateOrderInputSchema = exports.CreateOrderInputSchema = exports.OrderSchema = exports.OrderLineSchema = exports.OrderStatus = void 0;
var zod_1 = require("zod");
var uuid_1 = require("uuid");
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
var OrderEntity = /** @class */ (function () {
    function OrderEntity(props) {
        this.props = props;
    }
    OrderEntity.create = function (props) {
        var now = new Date();
        // Calculate totals from lines
        var lines = props.lines.map(function (line, index) { return (__assign(__assign({}, line), { id: (0, uuid_1.v4)(), totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100), totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100) })); });
        var subtotalNet = lines.reduce(function (sum, line) { return sum + line.totalNet; }, 0);
        var totalDiscount = lines.reduce(function (sum, line) { return sum + (line.quantity * line.unitPrice * line.discount / 100); }, 0);
        var totalNet = subtotalNet;
        var totalGross = lines.reduce(function (sum, line) { return sum + line.totalGross; }, 0);
        var order = __assign(__assign({}, props), { id: (0, uuid_1.v4)(), lines: lines, subtotalNet: subtotalNet, totalDiscount: totalDiscount, totalNet: totalNet, totalGross: totalGross, status: props.status || exports.OrderStatus.DRAFT, createdAt: now, updatedAt: now, version: 1 });
        return new OrderEntity(order);
    };
    OrderEntity.fromPersistence = function (props) {
        var _a, _b;
        return new OrderEntity(__assign(__assign({}, props), { subtotalNet: Number(props.subtotalNet), totalDiscount: Number(props.totalDiscount), totalNet: Number(props.totalNet), totalTax: Number(props.totalTax), totalGross: Number(props.totalGross), lines: props.lines.map(function (line) { return (__assign(__assign({}, line), { unitPrice: Number(line.unitPrice), discount: Number(line.discount), totalNet: Number(line.totalNet), totalGross: Number(line.totalGross) })); }), expectedDeliveryDate: (_a = props.expectedDeliveryDate) !== null && _a !== void 0 ? _a : undefined, notes: (_b = props.notes) !== null && _b !== void 0 ? _b : undefined }));
    };
    OrderEntity.prototype.update = function (props) {
        var _this = this;
        var _a, _b;
        if (props.lines) {
            this.props.lines = props.lines.map(function (line, index) {
                var _a;
                return (__assign(__assign({}, line), { id: ((_a = _this.props.lines[index]) === null || _a === void 0 ? void 0 : _a.id) || (0, uuid_1.v4)(), totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100), totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + _this.props.taxRate / 100) }));
            });
            // Recalculate totals
            this.props.subtotalNet = this.props.lines.reduce(function (sum, line) { return sum + line.totalNet; }, 0);
            this.props.totalDiscount = this.props.lines.reduce(function (sum, line) { return sum + (line.quantity * line.unitPrice * line.discount / 100); }, 0);
            this.props.totalNet = this.props.subtotalNet;
            this.props.totalGross = this.props.lines.reduce(function (sum, line) { return sum + line.totalGross; }, 0);
        }
        if (props.expectedDeliveryDate !== undefined) {
            this.props.expectedDeliveryDate = (_a = props.expectedDeliveryDate) !== null && _a !== void 0 ? _a : undefined;
        }
        if (props.notes !== undefined) {
            this.props.notes = (_b = props.notes) !== null && _b !== void 0 ? _b : undefined;
        }
        if (props.status !== undefined) {
            this.validateStatusTransition(this.props.status, props.status);
            this.props.status = props.status;
        }
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    OrderEntity.prototype.confirm = function () {
        if (this.props.status !== exports.OrderStatus.DRAFT) {
            throw new Error('Only draft orders can be confirmed');
        }
        this.props.status = exports.OrderStatus.CONFIRMED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    OrderEntity.prototype.markAsInvoiced = function () {
        if (this.props.status !== exports.OrderStatus.CONFIRMED) {
            throw new Error('Only confirmed orders can be invoiced');
        }
        this.props.status = exports.OrderStatus.INVOICED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    OrderEntity.prototype.cancel = function () {
        if (this.props.status === exports.OrderStatus.INVOICED) {
            throw new Error('Invoiced orders cannot be cancelled');
        }
        this.props.status = exports.OrderStatus.CANCELLED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    OrderEntity.prototype.canBeConfirmed = function () {
        return this.props.status === exports.OrderStatus.DRAFT && this.props.lines.length > 0;
    };
    OrderEntity.prototype.canBeInvoiced = function () {
        return this.props.status === exports.OrderStatus.CONFIRMED;
    };
    OrderEntity.prototype.canBeCancelled = function () {
        return this.props.status !== exports.OrderStatus.INVOICED;
    };
    OrderEntity.prototype.validateStatusTransition = function (currentStatus, newStatus) {
        var validTransitions = {
            'Draft': ['Confirmed', 'Cancelled'],
            'Confirmed': ['Invoiced', 'Cancelled'],
            'Invoiced': [], // Terminal state
            'Cancelled': [] // Terminal state
        };
        var allowedStatuses = validTransitions[currentStatus];
        if (!(allowedStatuses === null || allowedStatuses === void 0 ? void 0 : allowedStatuses.includes(newStatus))) {
            throw new Error("Cannot change status from ".concat(currentStatus, " to ").concat(newStatus));
        }
    };
    Object.defineProperty(OrderEntity.prototype, "id", {
        // Getters
        get: function () { return this.props.id; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "tenantId", {
        get: function () { return this.props.tenantId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "customerId", {
        get: function () { return this.props.customerId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "orderNumber", {
        get: function () { return this.props.orderNumber; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "lines", {
        get: function () { return __spreadArray([], this.props.lines, true); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "subtotalNet", {
        get: function () { return this.props.subtotalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "totalDiscount", {
        get: function () { return this.props.totalDiscount; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "totalNet", {
        get: function () { return this.props.totalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "totalGross", {
        get: function () { return this.props.totalGross; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "taxRate", {
        get: function () { return this.props.taxRate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "currency", {
        get: function () { return this.props.currency; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "expectedDeliveryDate", {
        get: function () { return this.props.expectedDeliveryDate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "notes", {
        get: function () { return this.props.notes; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "status", {
        get: function () { return this.props.status; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "createdAt", {
        get: function () { return this.props.createdAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "updatedAt", {
        get: function () { return this.props.updatedAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(OrderEntity.prototype, "version", {
        get: function () { return this.props.version; },
        enumerable: false,
        configurable: true
    });
    // Export for persistence
    OrderEntity.prototype.toPersistence = function () {
        return __assign({}, this.props);
    };
    // Export for API responses
    OrderEntity.prototype.toJSON = function () {
        var _a = this.props, tenantId = _a.tenantId, orderWithoutTenant = __rest(_a, ["tenantId"]);
        return orderWithoutTenant;
    };
    return OrderEntity;
}());
exports.OrderEntity = OrderEntity;
