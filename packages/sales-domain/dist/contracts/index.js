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
exports.CreditNoteStatusContractSchema = exports.CreditNoteLineContractSchema = exports.CreditNoteListResponseContractSchema = exports.CreditNoteQueryContractSchema = exports.CreditNoteResponseContractSchema = exports.UpdateCreditNoteContractSchema = exports.CreateCreditNoteContractSchema = exports.InvoiceStatusContractSchema = exports.InvoiceLineContractSchema = exports.InvoiceListResponseContractSchema = exports.InvoiceQueryContractSchema = exports.InvoiceResponseContractSchema = exports.UpdateInvoiceContractSchema = exports.CreateInvoiceContractSchema = exports.OrderStatusContractSchema = exports.OrderLineContractSchema = exports.OrderListResponseContractSchema = exports.OrderQueryContractSchema = exports.OrderResponseContractSchema = exports.UpdateOrderContractSchema = exports.CreateOrderContractSchema = exports.QuoteStatusContractSchema = exports.QuoteLineContractSchema = exports.QuoteListResponseContractSchema = exports.QuoteQueryContractSchema = exports.QuoteResponseContractSchema = exports.UpdateQuoteContractSchema = exports.CreateQuoteContractSchema = void 0;
// Export all contract schemas
__exportStar(require("./quote-contracts"), exports);
__exportStar(require("./order-contracts"), exports);
__exportStar(require("./invoice-contracts"), exports);
__exportStar(require("./credit-note-contracts"), exports);
// Re-export commonly used contract schemas
var quote_contracts_1 = require("./quote-contracts");
Object.defineProperty(exports, "CreateQuoteContractSchema", { enumerable: true, get: function () { return quote_contracts_1.CreateQuoteContractSchema; } });
Object.defineProperty(exports, "UpdateQuoteContractSchema", { enumerable: true, get: function () { return quote_contracts_1.UpdateQuoteContractSchema; } });
Object.defineProperty(exports, "QuoteResponseContractSchema", { enumerable: true, get: function () { return quote_contracts_1.QuoteResponseContractSchema; } });
Object.defineProperty(exports, "QuoteQueryContractSchema", { enumerable: true, get: function () { return quote_contracts_1.QuoteQueryContractSchema; } });
Object.defineProperty(exports, "QuoteListResponseContractSchema", { enumerable: true, get: function () { return quote_contracts_1.QuoteListResponseContractSchema; } });
Object.defineProperty(exports, "QuoteLineContractSchema", { enumerable: true, get: function () { return quote_contracts_1.QuoteLineContractSchema; } });
Object.defineProperty(exports, "QuoteStatusContractSchema", { enumerable: true, get: function () { return quote_contracts_1.QuoteStatusContractSchema; } });
var order_contracts_1 = require("./order-contracts");
Object.defineProperty(exports, "CreateOrderContractSchema", { enumerable: true, get: function () { return order_contracts_1.CreateOrderContractSchema; } });
Object.defineProperty(exports, "UpdateOrderContractSchema", { enumerable: true, get: function () { return order_contracts_1.UpdateOrderContractSchema; } });
Object.defineProperty(exports, "OrderResponseContractSchema", { enumerable: true, get: function () { return order_contracts_1.OrderResponseContractSchema; } });
Object.defineProperty(exports, "OrderQueryContractSchema", { enumerable: true, get: function () { return order_contracts_1.OrderQueryContractSchema; } });
Object.defineProperty(exports, "OrderListResponseContractSchema", { enumerable: true, get: function () { return order_contracts_1.OrderListResponseContractSchema; } });
Object.defineProperty(exports, "OrderLineContractSchema", { enumerable: true, get: function () { return order_contracts_1.OrderLineContractSchema; } });
Object.defineProperty(exports, "OrderStatusContractSchema", { enumerable: true, get: function () { return order_contracts_1.OrderStatusContractSchema; } });
var invoice_contracts_1 = require("./invoice-contracts");
Object.defineProperty(exports, "CreateInvoiceContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.CreateInvoiceContractSchema; } });
Object.defineProperty(exports, "UpdateInvoiceContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.UpdateInvoiceContractSchema; } });
Object.defineProperty(exports, "InvoiceResponseContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.InvoiceResponseContractSchema; } });
Object.defineProperty(exports, "InvoiceQueryContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.InvoiceQueryContractSchema; } });
Object.defineProperty(exports, "InvoiceListResponseContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.InvoiceListResponseContractSchema; } });
Object.defineProperty(exports, "InvoiceLineContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.InvoiceLineContractSchema; } });
Object.defineProperty(exports, "InvoiceStatusContractSchema", { enumerable: true, get: function () { return invoice_contracts_1.InvoiceStatusContractSchema; } });
var credit_note_contracts_1 = require("./credit-note-contracts");
Object.defineProperty(exports, "CreateCreditNoteContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreateCreditNoteContractSchema; } });
Object.defineProperty(exports, "UpdateCreditNoteContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.UpdateCreditNoteContractSchema; } });
Object.defineProperty(exports, "CreditNoteResponseContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreditNoteResponseContractSchema; } });
Object.defineProperty(exports, "CreditNoteQueryContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreditNoteQueryContractSchema; } });
Object.defineProperty(exports, "CreditNoteListResponseContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreditNoteListResponseContractSchema; } });
Object.defineProperty(exports, "CreditNoteLineContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreditNoteLineContractSchema; } });
Object.defineProperty(exports, "CreditNoteStatusContractSchema", { enumerable: true, get: function () { return credit_note_contracts_1.CreditNoteStatusContractSchema; } });
