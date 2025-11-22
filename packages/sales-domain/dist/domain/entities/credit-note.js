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
exports.CreditNoteEntity = exports.UpdateCreditNoteInputSchema = exports.CreateCreditNoteInputSchema = exports.CreditNoteSchema = exports.CreditNoteLineSchema = exports.CreditNoteStatus = void 0;
var zod_1 = require("zod");
var uuid_1 = require("uuid");
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
var CreditNoteEntity = /** @class */ (function () {
    function CreditNoteEntity(props) {
        this.props = props;
    }
    CreditNoteEntity.create = function (props) {
        var now = new Date();
        // Calculate totals from lines
        var lines = props.lines.map(function (line, index) { return (__assign(__assign({}, line), { id: (0, uuid_1.v4)(), totalNet: line.quantity * line.unitPrice * (1 - line.discount / 100), totalGross: line.quantity * line.unitPrice * (1 - line.discount / 100) * (1 + props.taxRate / 100) })); });
        var subtotalNet = lines.reduce(function (sum, line) { return sum + line.totalNet; }, 0);
        var totalDiscount = lines.reduce(function (sum, line) { return sum + (line.quantity * line.unitPrice * line.discount / 100); }, 0);
        var totalNet = subtotalNet;
        var totalGross = lines.reduce(function (sum, line) { return sum + line.totalGross; }, 0);
        var creditNote = __assign(__assign({}, props), { id: (0, uuid_1.v4)(), lines: lines, subtotalNet: subtotalNet, totalDiscount: totalDiscount, totalNet: totalNet, totalGross: totalGross, status: exports.CreditNoteStatus.ISSUED, createdAt: now, updatedAt: now, version: 1 });
        return new CreditNoteEntity(creditNote);
    };
    CreditNoteEntity.fromPersistence = function (props) {
        var _a;
        return new CreditNoteEntity(__assign(__assign({}, props), { subtotalNet: Number(props.subtotalNet), totalDiscount: Number(props.totalDiscount), totalNet: Number(props.totalNet), totalGross: Number(props.totalGross), lines: props.lines.map(function (line) { return (__assign(__assign({}, line), { unitPrice: Number(line.unitPrice), discount: Number(line.discount), totalNet: Number(line.totalNet), totalGross: Number(line.totalGross) })); }), settledAt: (_a = props.settledAt) !== null && _a !== void 0 ? _a : undefined }));
    };
    CreditNoteEntity.prototype.update = function (props) {
        var _a;
        if (props.reason !== undefined) {
            this.props.reason = props.reason;
        }
        if (props.notes !== undefined) {
            this.props.notes = (_a = props.notes) !== null && _a !== void 0 ? _a : undefined;
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
    };
    CreditNoteEntity.prototype.settle = function () {
        if (this.props.status !== exports.CreditNoteStatus.ISSUED) {
            throw new Error('Only issued credit notes can be settled');
        }
        this.props.status = exports.CreditNoteStatus.SETTLED;
        this.props.settledAt = new Date();
        this.props.updatedAt = new Date();
        this.props.version += 1;
    };
    CreditNoteEntity.prototype.canBeSettled = function () {
        return this.props.status === exports.CreditNoteStatus.ISSUED;
    };
    CreditNoteEntity.prototype.validateStatusTransition = function (currentStatus, newStatus) {
        var validTransitions = {
            'Issued': ['Settled'],
            'Settled': [] // Terminal state
        };
        var allowedStatuses = validTransitions[currentStatus];
        if (!(allowedStatuses === null || allowedStatuses === void 0 ? void 0 : allowedStatuses.includes(newStatus))) {
            throw new Error("Cannot change status from ".concat(currentStatus, " to ").concat(newStatus));
        }
    };
    Object.defineProperty(CreditNoteEntity.prototype, "id", {
        // Getters
        get: function () { return this.props.id; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "tenantId", {
        get: function () { return this.props.tenantId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "customerId", {
        get: function () { return this.props.customerId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "invoiceId", {
        get: function () { return this.props.invoiceId; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "creditNumber", {
        get: function () { return this.props.creditNumber; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "lines", {
        get: function () { return __spreadArray([], this.props.lines, true); },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "subtotalNet", {
        get: function () { return this.props.subtotalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "totalDiscount", {
        get: function () { return this.props.totalDiscount; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "totalNet", {
        get: function () { return this.props.totalNet; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "totalGross", {
        get: function () { return this.props.totalGross; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "taxRate", {
        get: function () { return this.props.taxRate; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "currency", {
        get: function () { return this.props.currency; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "reason", {
        get: function () { return this.props.reason; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "notes", {
        get: function () { return this.props.notes; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "status", {
        get: function () { return this.props.status; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "settledAt", {
        get: function () { return this.props.settledAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "createdAt", {
        get: function () { return this.props.createdAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "updatedAt", {
        get: function () { return this.props.updatedAt; },
        enumerable: false,
        configurable: true
    });
    Object.defineProperty(CreditNoteEntity.prototype, "version", {
        get: function () { return this.props.version; },
        enumerable: false,
        configurable: true
    });
    // Export for persistence
    CreditNoteEntity.prototype.toPersistence = function () {
        return __assign({}, this.props);
    };
    // Export for API responses
    CreditNoteEntity.prototype.toJSON = function () {
        var _a = this.props, tenantId = _a.tenantId, creditNoteWithoutTenant = __rest(_a, ["tenantId"]);
        return creditNoteWithoutTenant;
    };
    return CreditNoteEntity;
}());
exports.CreditNoteEntity = CreditNoteEntity;
