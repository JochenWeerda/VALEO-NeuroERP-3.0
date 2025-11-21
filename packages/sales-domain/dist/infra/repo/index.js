"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SalesOfferRepository = exports.CreditNoteRepository = exports.InvoiceRepository = exports.OrderRepository = exports.QuoteRepository = void 0;
// Export all repositories
__exportStar(require("./quote-repository"), exports);
__exportStar(require("./order-repository"), exports);
__exportStar(require("./invoice-repository"), exports);
__exportStar(require("./credit-note-repository"), exports);
__exportStar(require("./sales-offer-repository"), exports);
// Re-export commonly used repository instances
var quote_repository_1 = require("./quote-repository");
Object.defineProperty(exports, "QuoteRepository", { enumerable: true, get: function () { return quote_repository_1.QuoteRepository; } });
var order_repository_1 = require("./order-repository");
Object.defineProperty(exports, "OrderRepository", { enumerable: true, get: function () { return order_repository_1.OrderRepository; } });
var invoice_repository_1 = require("./invoice-repository");
Object.defineProperty(exports, "InvoiceRepository", { enumerable: true, get: function () { return invoice_repository_1.InvoiceRepository; } });
var credit_note_repository_1 = require("./credit-note-repository");
Object.defineProperty(exports, "CreditNoteRepository", { enumerable: true, get: function () { return credit_note_repository_1.CreditNoteRepository; } });
var sales_offer_repository_1 = require("./sales-offer-repository");
Object.defineProperty(exports, "SalesOfferRepository", { enumerable: true, get: function () { return sales_offer_repository_1.SalesOfferRepository; } });
//# sourceMappingURL=index.js.map