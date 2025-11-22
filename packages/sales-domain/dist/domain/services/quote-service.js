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
exports.QuoteService = void 0;
var QuoteService = /** @class */ (function () {
    function QuoteService(deps) {
        this.deps = deps;
    }
    QuoteService.prototype.createQuote = function (data) {
        return __awaiter(this, void 0, void 0, function () {
            var existingQuote, _i, _a, line, quote;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        // Business validation
                        if (data.lines.length === 0) {
                            throw new Error('Quote must have at least one line item');
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.findByNumber(data.quoteNumber, data.tenantId)];
                    case 1:
                        existingQuote = _b.sent();
                        if (existingQuote) {
                            throw new Error("Quote number ".concat(data.quoteNumber, " already exists"));
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
                        return [4 /*yield*/, this.deps.quoteRepo.create(data)];
                    case 2:
                        quote = _b.sent();
                        return [2 /*return*/, quote];
                }
            });
        });
    };
    QuoteService.prototype.getQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.findById(id, tenantId)];
            });
        });
    };
    QuoteService.prototype.getQuoteByNumber = function (quoteNumber, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.findByNumber(quoteNumber, tenantId)];
            });
        });
    };
    QuoteService.prototype.updateQuote = function (id, data) {
        return __awaiter(this, void 0, void 0, function () {
            var existingQuote, _i, _a, line, updatedQuote;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, data.tenantId)];
                    case 1:
                        existingQuote = _b.sent();
                        if (existingQuote === undefined || existingQuote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        // Business validation
                        if (data.lines) {
                            if (data.lines.length === 0) {
                                throw new Error('Quote must have at least one line item');
                            }
                            for (_i = 0, _a = data.lines; _i < _a.length; _i++) {
                                line = _a[_i];
                                if (line.quantity <= 0) {
                                    throw new Error('Line item quantity must be positive');
                                }
                                if (line.unitPrice < 0) {
                                    throw new Error('Line item unit price cannot be negative');
                                }
                            }
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.update(id, data.tenantId, data)];
                    case 2:
                        updatedQuote = _b.sent();
                        if (updatedQuote === undefined || updatedQuote === null) {
                            throw new Error("Failed to update quote ".concat(id));
                        }
                        return [2 /*return*/, updatedQuote];
                }
            });
        });
    };
    QuoteService.prototype.deleteQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var quote;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, tenantId)];
                    case 1:
                        quote = _a.sent();
                        if (quote === undefined || quote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        // Business rule: only draft quotes can be deleted
                        if (quote.status !== 'Draft') {
                            throw new Error('Only draft quotes can be deleted');
                        }
                        return [2 /*return*/, this.deps.quoteRepo.delete(id, tenantId)];
                }
            });
        });
    };
    QuoteService.prototype.sendQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var quote, updatedQuote;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, tenantId)];
                    case 1:
                        quote = _a.sent();
                        if (quote === undefined || quote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        if (!quote.canBeSent()) {
                            throw new Error('Quote cannot be sent in its current state');
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.updateStatus(id, tenantId, 'Sent')];
                    case 2:
                        updatedQuote = _a.sent();
                        if (updatedQuote === undefined || updatedQuote === null) {
                            throw new Error("Failed to send quote");
                        }
                        return [2 /*return*/, updatedQuote];
                }
            });
        });
    };
    QuoteService.prototype.acceptQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var quote, updatedQuote;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, tenantId)];
                    case 1:
                        quote = _a.sent();
                        if (quote === undefined || quote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        if (!quote.canBeAccepted()) {
                            throw new Error('Quote cannot be accepted in its current state');
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.updateStatus(id, tenantId, 'Accepted')];
                    case 2:
                        updatedQuote = _a.sent();
                        if (updatedQuote === undefined || updatedQuote === null) {
                            throw new Error("Failed to accept quote");
                        }
                        return [2 /*return*/, updatedQuote];
                }
            });
        });
    };
    QuoteService.prototype.rejectQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var quote, updatedQuote;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, tenantId)];
                    case 1:
                        quote = _a.sent();
                        if (quote === undefined || quote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        if (quote.status !== 'Sent') {
                            throw new Error('Only sent quotes can be rejected');
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.updateStatus(id, tenantId, 'Rejected')];
                    case 2:
                        updatedQuote = _a.sent();
                        if (updatedQuote === undefined || updatedQuote === null) {
                            throw new Error("Failed to reject quote");
                        }
                        return [2 /*return*/, updatedQuote];
                }
            });
        });
    };
    QuoteService.prototype.expireQuote = function (id, tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            var quote, updatedQuote;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.deps.quoteRepo.findById(id, tenantId)];
                    case 1:
                        quote = _a.sent();
                        if (quote === undefined || quote === null) {
                            throw new Error("Quote ".concat(id, " not found"));
                        }
                        if (quote.status === 'Expired' || quote.status === 'Rejected' || quote.status === 'Accepted') {
                            return [2 /*return*/, quote]; // Already in terminal state
                        }
                        return [4 /*yield*/, this.deps.quoteRepo.updateStatus(id, tenantId, 'Expired')];
                    case 2:
                        updatedQuote = _a.sent();
                        if (updatedQuote === undefined || updatedQuote === null) {
                            throw new Error("Failed to expire quote");
                        }
                        return [2 /*return*/, updatedQuote];
                }
            });
        });
    };
    QuoteService.prototype.searchQuotes = function (tenantId_1) {
        return __awaiter(this, arguments, void 0, function (tenantId, filters, pagination) {
            if (filters === void 0) { filters = {}; }
            if (pagination === void 0) { pagination = { page: 1, pageSize: 20 }; }
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.findAll(tenantId, filters, pagination)];
            });
        });
    };
    QuoteService.prototype.getQuotesByCustomer = function (customerId_1, tenantId_1) {
        return __awaiter(this, arguments, void 0, function (customerId, tenantId, filters, pagination) {
            if (filters === void 0) { filters = {}; }
            if (pagination === void 0) { pagination = { page: 1, pageSize: 20 }; }
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.findByCustomerId(customerId, tenantId, filters, pagination)];
            });
        });
    };
    QuoteService.prototype.getExpiringSoon = function (tenantId_1) {
        return __awaiter(this, arguments, void 0, function (tenantId, daysAhead) {
            if (daysAhead === void 0) { daysAhead = 7; }
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.getExpiringSoon(tenantId, daysAhead)];
            });
        });
    };
    QuoteService.prototype.getExpiredQuotes = function (tenantId) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.deps.quoteRepo.getExpired(tenantId)];
            });
        });
    };
    return QuoteService;
}());
exports.QuoteService = QuoteService;
