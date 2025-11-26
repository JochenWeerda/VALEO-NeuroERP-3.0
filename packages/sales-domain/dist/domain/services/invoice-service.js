"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvoiceService = void 0;
var InvoiceService = /** @class */ (function () {
    function InvoiceService(deps) {
        this.deps = deps;
    }
    InvoiceService.prototype.createInvoice = function (data) {
        return __awaiter(this, void 0, void 0, function () {
            var existingInvoice, _i, _a, line, invoice;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        // Business validation
                        if (data.lines.length === 0) {
                            throw new Error('Invoice must have at least one line item');
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.findByNumber(data.invoiceNumber, data.tenantId)];
                    case 1:
                        existingInvoice = _b.sent();
                        if (existingInvoice) {
                            throw new Error("Invoice number ".concat(data.invoiceNumber, " already exists"));
                        }
                        // Validate line items
                        for (_i = 0, _a = data.lines; _i < _a.length; _i++) {
                            line = _a[_i];
                            if (line.quantity <= 0) {
                                throw new Error('Line item quantity must be positive');
                            }
                            if (line.unitPrice < 0) {
                                throw new Error('Line item unit price cannot be negative');
                            }
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.create(data)];
                    case 2:
                        invoice = _b.sent();
                        return [2 /*return*/, invoice];
                }
            });
        });
    };
    InvoiceService.prototype.getInvoice = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.invoiceRepo.findById(id, tenantId)];
            });
        });
    };
    InvoiceService.prototype.updateInvoice = function (id, data) {
        return __awaiter(this, void 0, void 0, function () {
            var existingInvoice, updatedInvoice;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.invoiceRepo.findById(id, data.tenantId)];
                    case 1:
                        existingInvoice = _a.sent();
                        if (existingInvoice === undefined || existingInvoice === null) {
                            throw new Error("Invoice ".concat(id, " not found"));
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.update(id, data.tenantId, data)];
                    case 2:
                        updatedInvoice = _a.sent();
                        if (updatedInvoice === undefined || updatedInvoice === null) {
                            throw new Error("Failed to update invoice ".concat(id));
                        }
                        return [2 /*return*/, updatedInvoice];
                }
            });
        });
    };
    InvoiceService.prototype.markInvoiceAsPaid = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var invoice, updatedInvoice;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.invoiceRepo.findById(id, tenantId)];
                    case 1:
                        invoice = _a.sent();
                        if (invoice === undefined || invoice === null) {
                            throw new Error("Invoice ".concat(id, " not found"));
                        }
                        if (!invoice.canBePaid()) {
                            throw new Error('Invoice cannot be marked as paid in its current state');
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.updateStatus(id, tenantId, 'Paid')];
                    case 2:
                        updatedInvoice = _a.sent();
                        if (updatedInvoice === undefined || updatedInvoice === null) {
                            throw new Error("Failed to mark invoice as paid");
                        }
                        return [2 /*return*/, updatedInvoice];
                }
            });
        });
    };
    InvoiceService.prototype.markInvoiceAsOverdue = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var invoice, updatedInvoice;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.invoiceRepo.findById(id, tenantId)];
                    case 1:
                        invoice = _a.sent();
                        if (invoice === undefined || invoice === null) {
                            throw new Error("Invoice ".concat(id, " not found"));
                        }
                        if (invoice.isOverdue()) {
                            return [2 /*return*/, invoice]; // Already overdue
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.updateStatus(id, tenantId, 'Overdue')];
                    case 2:
                        updatedInvoice = _a.sent();
                        if (updatedInvoice === undefined || updatedInvoice === null) {
                            throw new Error("Failed to mark invoice as overdue");
                        }
                        return [2 /*return*/, updatedInvoice];
                }
            });
        });
    };
    InvoiceService.prototype.cancelInvoice = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var invoice, updatedInvoice;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.invoiceRepo.findById(id, tenantId)];
                    case 1:
                        invoice = _a.sent();
                        if (invoice === undefined || invoice === null) {
                            throw new Error("Invoice ".concat(id, " not found"));
                        }
                        if (!invoice.canBeCancelled()) {
                            throw new Error('Invoice cannot be cancelled in its current state');
                        }
                        return [4 /*yield*/, this.deps.invoiceRepo.updateStatus(id, tenantId, 'Cancelled')];
                    case 2:
                        updatedInvoice = _a.sent();
                        if (updatedInvoice === undefined || updatedInvoice === null) {
                            throw new Error("Failed to cancel invoice");
                        }
                        return [2 /*return*/, updatedInvoice];
                }
            });
        });
    };
    InvoiceService.prototype.searchInvoices = function (tenantId_1) {
        return __awaiter(this, arguments, void 0, function (tenantId, filters, pagination) {
            if (filters === void 0) { filters = {}; }
            if (pagination === void 0) { pagination = { page: 1, pageSize: 20 }; }
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.invoiceRepo.findAll(tenantId, filters, pagination)];
            });
        });
    };
    InvoiceService.prototype.getInvoicesByCustomer = function (customerId_1, tenantId_1) {
        return __awaiter(this, arguments, void 0, function (customerId, tenantId, filters, pagination) {
            if (filters === void 0) { filters = {}; }
            if (pagination === void 0) { pagination = { page: 1, pageSize: 20 }; }
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.invoiceRepo.findByCustomerId(customerId, tenantId, filters, pagination)];
            });
        });
    };
    InvoiceService.prototype.getOverdueInvoices = function (tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.invoiceRepo.getOverdueInvoices(tenantId)];
            });
        });
    };
    return InvoiceService;
}());
exports.InvoiceService = InvoiceService;
