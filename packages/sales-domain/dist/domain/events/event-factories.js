"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createQuoteCreatedEvent = createQuoteCreatedEvent;
exports.createQuoteAcceptedEvent = createQuoteAcceptedEvent;
exports.createQuoteRejectedEvent = createQuoteRejectedEvent;
exports.createQuoteExpiredEvent = createQuoteExpiredEvent;
exports.createOrderCreatedEvent = createOrderCreatedEvent;
exports.createOrderConfirmedEvent = createOrderConfirmedEvent;
exports.createOrderInvoicedEvent = createOrderInvoicedEvent;
exports.createOrderCancelledEvent = createOrderCancelledEvent;
exports.createInvoiceIssuedEvent = createInvoiceIssuedEvent;
exports.createInvoicePaidEvent = createInvoicePaidEvent;
exports.createInvoiceOverdueEvent = createInvoiceOverdueEvent;
exports.createInvoiceCancelledEvent = createInvoiceCancelledEvent;
exports.createCreditNoteIssuedEvent = createCreditNoteIssuedEvent;
exports.createCreditNoteSettledEvent = createCreditNoteSettledEvent;
var uuid_1 = require("uuid");
var domain_events_1 = require("./domain-events");
// Quote Event Factories
function createQuoteCreatedEvent(quote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.QUOTE_CREATED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: quote.tenantId,
        payload: {
            quoteId: quote.id,
            customerId: quote.customerId,
            quoteNumber: quote.quoteNumber,
            totalNet: quote.totalNet,
            totalGross: quote.totalGross,
            validUntil: quote.validUntil.toISOString()
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createQuoteAcceptedEvent(quote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.QUOTE_ACCEPTED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: quote.tenantId,
        payload: {
            quoteId: quote.id,
            customerId: quote.customerId,
            quoteNumber: quote.quoteNumber,
            totalNet: quote.totalNet,
            totalGross: quote.totalGross
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createQuoteRejectedEvent(quote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.QUOTE_REJECTED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: quote.tenantId,
        payload: {
            quoteId: quote.id,
            customerId: quote.customerId,
            quoteNumber: quote.quoteNumber
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createQuoteExpiredEvent(quote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.QUOTE_EXPIRED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: quote.tenantId,
        payload: {
            quoteId: quote.id,
            customerId: quote.customerId,
            quoteNumber: quote.quoteNumber
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
// Order Event Factories
function createOrderCreatedEvent(order, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.ORDER_CREATED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: order.tenantId,
        payload: {
            orderId: order.id,
            customerId: order.customerId,
            orderNumber: order.orderNumber,
            totalNet: order.totalNet,
            totalGross: order.totalGross
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createOrderConfirmedEvent(order, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.ORDER_CONFIRMED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: order.tenantId,
        payload: {
            orderId: order.id,
            customerId: order.customerId,
            orderNumber: order.orderNumber,
            totalNet: order.totalNet,
            totalGross: order.totalGross
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createOrderInvoicedEvent(order, invoiceId, invoiceNumber, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.ORDER_INVOICED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: order.tenantId,
        payload: {
            orderId: order.id,
            customerId: order.customerId,
            orderNumber: order.orderNumber,
            invoiceId: invoiceId,
            invoiceNumber: invoiceNumber
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createOrderCancelledEvent(order, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.ORDER_CANCELLED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: order.tenantId,
        payload: {
            orderId: order.id,
            customerId: order.customerId,
            orderNumber: order.orderNumber
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
// Invoice Event Factories
function createInvoiceIssuedEvent(invoice, correlationId, causationId) {
    var payload = {
        invoiceId: invoice.id,
        customerId: invoice.customerId,
        invoiceNumber: invoice.invoiceNumber,
        totalNet: invoice.totalNet,
        totalGross: invoice.totalGross,
        dueDate: invoice.dueDate.toISOString()
    };
    if (invoice.orderId) {
        payload.orderId = invoice.orderId;
    }
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.INVOICE_ISSUED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: invoice.tenantId,
        payload: payload
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createInvoicePaidEvent(invoice, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.INVOICE_PAID,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: invoice.tenantId,
        payload: {
            invoiceId: invoice.id,
            customerId: invoice.customerId,
            invoiceNumber: invoice.invoiceNumber,
            totalNet: invoice.totalNet,
            totalGross: invoice.totalGross,
            paidAt: invoice.paidAt.toISOString()
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createInvoiceOverdueEvent(invoice, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.INVOICE_OVERDUE,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: invoice.tenantId,
        payload: {
            invoiceId: invoice.id,
            customerId: invoice.customerId,
            invoiceNumber: invoice.invoiceNumber,
            totalNet: invoice.totalNet,
            totalGross: invoice.totalGross,
            dueDate: invoice.dueDate.toISOString()
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createInvoiceCancelledEvent(invoice, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.INVOICE_CANCELLED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: invoice.tenantId,
        payload: {
            invoiceId: invoice.id,
            customerId: invoice.customerId,
            invoiceNumber: invoice.invoiceNumber
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
// Credit Note Event Factories
function createCreditNoteIssuedEvent(creditNote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.CREDIT_NOTE_ISSUED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: creditNote.tenantId,
        payload: {
            creditNoteId: creditNote.id,
            customerId: creditNote.customerId,
            invoiceId: creditNote.invoiceId,
            creditNumber: creditNote.creditNumber,
            totalNet: creditNote.totalNet,
            totalGross: creditNote.totalGross,
            reason: creditNote.reason
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createCreditNoteSettledEvent(creditNote, correlationId, causationId) {
    var event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.CREDIT_NOTE_SETTLED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: creditNote.tenantId,
        payload: {
            creditNoteId: creditNote.id,
            customerId: creditNote.customerId,
            invoiceId: creditNote.invoiceId,
            creditNumber: creditNote.creditNumber,
            totalNet: creditNote.totalNet,
            totalGross: creditNote.totalGross,
            settledAt: creditNote.settledAt.toISOString()
        }
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
