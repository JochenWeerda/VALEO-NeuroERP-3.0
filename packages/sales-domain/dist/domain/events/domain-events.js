"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DomainEventType = void 0;
// Domain Event Types
exports.DomainEventType = {
    QUOTE_CREATED: 'sales.quote.created',
    QUOTE_SENT: 'sales.quote.sent',
    QUOTE_ACCEPTED: 'sales.quote.accepted',
    QUOTE_REJECTED: 'sales.quote.rejected',
    QUOTE_EXPIRED: 'sales.quote.expired',
    ORDER_CREATED: 'sales.order.created',
    ORDER_CONFIRMED: 'sales.order.confirmed',
    ORDER_INVOICED: 'sales.order.invoiced',
    ORDER_CANCELLED: 'sales.order.cancelled',
    INVOICE_ISSUED: 'sales.invoice.issued',
    INVOICE_PAID: 'sales.invoice.paid',
    INVOICE_OVERDUE: 'sales.invoice.overdue',
    INVOICE_CANCELLED: 'sales.invoice.cancelled',
    CREDIT_NOTE_ISSUED: 'sales.credit_note.issued',
    CREDIT_NOTE_SETTLED: 'sales.credit_note.settled'
};
