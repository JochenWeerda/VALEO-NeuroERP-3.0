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
exports.QuoteEntity = exports.UpdateQuoteInputSchema = exports.CreateQuoteInputSchema = exports.QuoteSchema = exports.QuoteLineSchema = exports.QuoteStatus = void 0;
var zod_1 = require("zod");
var uuid_1 = require("uuid");
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
var QuoteEntity = /** @class */ (function () {
    function QuoteEntity(props) {
        this.props = props;
    }
    QuoteEntity.create = function (props) {
        var now = new Date();
        // Calculate totals from lines
        var lines = props.lines.map(function (line, index) { return (__assign(__assign({}, line), { id: (0, uuid_1.v4)(), totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100), totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100) })); });
        var subtotalNet = lines.reduce(function (sum, line) { return sum + line.totalNet; }, 0);
        var totalDiscount = lines.reduce(function (sum, line) { return sum + (line.quantity * line.unitPrice * line.discount / 100); }, 0);
        var totalNet = subtotalNet;
        var totalGross = lines.reduce(function (sum, line) { return sum + line.totalGross; }, 0);
        var quote = __assign(__assign({}, props), { id: (0, uuid_1.v4)(), lines: lines, subtotalNet: subtotalNet, totalDiscount: totalDiscount, totalNet: totalNet, totalGross: totalGross, status: props.status || exports.QuoteStatus.DRAFT, createdAt: now, updatedAt: now, version: 1 });
        return new QuoteEntity(quote);
    };
    QuoteEntity.fromPersistence = function (props) {
        var _a;
        return new QuoteEntity(__assign(__assign({}, props), { subtotalNet: Number(props.subtotalNet), totalDiscount: Number(props.totalDiscount), totalNet: Number(props.totalNet), totalTax: Number(props.totalTax), totalGross: Number(props.totalGross), lines: props.lines.map(function (line) { return (__assign(__assign({}, line), { unitPrice: Number(line.unitPrice), discount: Number(line.discount), totalNet: Number(line.totalNet), totalGross: Number(line.totalGross) })); }), notes: (_a = props.notes) !== null && _a !== void 0 ? _a : undefined }));
    };
    QuoteEntity.prototype.update = function (props) {
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
        if (props.validUntil !== undefined) {
            this.props.validUntil = (_a = props.validUntil) !== null && _a !== void 0 ? _a : undefined;
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
    QuoteEntity.prototype.send = function () {
        if (this.props.status !== exports.QuoteStatus.DRAFT) {
            throw new Error('Only draft quotes can be sent');
        }
        this.props.status = exports.QuoteStatus.SENT;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    QuoteEntity.prototype.accept = function () {
        if (this.props.status !== exports.QuoteStatus.SENT) {
            throw new Error('Only sent quotes can be accepted');
        }
        this.props.status = exports.QuoteStatus.ACCEPTED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    QuoteEntity.prototype.reject = function () {
        if (this.props.status !== exports.QuoteStatus.SENT) {
            throw new Error('Only sent quotes can be rejected');
        }
        this.props.status = exports.QuoteStatus.REJECTED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    QuoteEntity.prototype.expire = function () {
        if (this.props.status === exports.QuoteStatus.EXPIRED || this.props.status === exports.QuoteStatus.REJECTED) {
            return; // Already expired or rejected
        }
        this.props.status = exports.QuoteStatus.EXPIRED;
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    QuoteEntity.prototype.isExpired = function () {
        return this.props.validUntil < new Date();
    };
    QuoteEntity.prototype.canBeAccepted = function () {
        return this.props.status === exports.QuoteStatus.SENT && !this.isExpired();
    };
    QuoteEntity.prototype.canBeSent = function () {
        return this.props.status === exports.QuoteStatus.DRAFT && this.props.lines.length > 0;
    };
    QuoteEntity.prototype.validateStatusTransition = function (currentStatus, newStatus) {
        var validTransitions = {
            'Draft': ['Sent'],
            'Sent': ['Accepted', 'Rejected', 'Expired'],
            'Accepted': [], // Terminal state
            'Rejected': [], // Terminal state
            'Expired': [] // Terminal state
        };
        var allowedStatuses = validTransitions[currentStatus];
        if (!(allowedStatuses === null || allowedStatuses === void 0 ? void 0 : allowedStatuses.includes(newStatus))) {
            throw new Error("Cannot change status from ".concat(currentStatus, " to ").concat(newStatus));
        }
    };
    Object.defineProperty(QuoteEntity.prototype, "id", {
        // Getters
        get: function () { return this.props.id; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "tenantId", {
        get: function () { return this.props.tenantId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "customerId", {
        get: function () { return this.props.customerId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "quoteNumber", {
        get: function () { return this.props.quoteNumber; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "lines", {
        get: function () { return __spreadArray([], this.props.lines, true); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "subtotalNet", {
        get: function () { return this.props.subtotalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "totalDiscount", {
        get: function () { return this.props.totalDiscount; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "totalNet", {
        get: function () { return this.props.totalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "totalGross", {
        get: function () { return this.props.totalGross; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "taxRate", {
        get: function () { return this.props.taxRate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "currency", {
        get: function () { return this.props.currency; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "validUntil", {
        get: function () { return this.props.validUntil; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "notes", {
        get: function () { return this.props.notes; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "status", {
        get: function () { return this.props.status; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "createdAt", {
        get: function () { return this.props.createdAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "updatedAt", {
        get: function () { return this.props.updatedAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(QuoteEntity.prototype, "version", {
        get: function () { return this.props.version; },
        enumerable: false,
        configurable: true
    });
    // Export for persistence
    QuoteEntity.prototype.toPersistence = function () {
        return __assign({}, this.props);
    };
    // Export for API responses
    QuoteEntity.prototype.toJSON = function () {
        var _a = this.props, tenantId = _a.tenantId, quoteWithoutTenant = __rest(_a, ["tenantId"]);
        return quoteWithoutTenant;
    };
    return QuoteEntity;
}());
exports.QuoteEntity = QuoteEntity;
