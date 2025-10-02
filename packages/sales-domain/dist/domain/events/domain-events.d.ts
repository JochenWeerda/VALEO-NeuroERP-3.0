export declare const DomainEventType: {
    readonly QUOTE_CREATED: "sales.quote.created";
    readonly QUOTE_SENT: "sales.quote.sent";
    readonly QUOTE_ACCEPTED: "sales.quote.accepted";
    readonly QUOTE_REJECTED: "sales.quote.rejected";
    readonly QUOTE_EXPIRED: "sales.quote.expired";
    readonly ORDER_CREATED: "sales.order.created";
    readonly ORDER_CONFIRMED: "sales.order.confirmed";
    readonly ORDER_INVOICED: "sales.order.invoiced";
    readonly ORDER_CANCELLED: "sales.order.cancelled";
    readonly INVOICE_ISSUED: "sales.invoice.issued";
    readonly INVOICE_PAID: "sales.invoice.paid";
    readonly INVOICE_OVERDUE: "sales.invoice.overdue";
    readonly INVOICE_CANCELLED: "sales.invoice.cancelled";
    readonly CREDIT_NOTE_ISSUED: "sales.credit_note.issued";
    readonly CREDIT_NOTE_SETTLED: "sales.credit_note.settled";
};
export type DomainEventTypeValue = typeof DomainEventType[keyof typeof DomainEventType];
export interface DomainEvent {
    eventId: string;
    eventType: DomainEventTypeValue;
    eventVersion: number;
    occurredAt: string;
    tenantId: string;
    correlationId?: string;
    causationId?: string;
    metadata?: Record<string, any>;
}
export interface QuoteCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.QUOTE_CREATED;
    payload: {
        quoteId: string;
        customerId: string;
        quoteNumber: string;
        totalNet: number;
        totalGross: number;
        validUntil: string;
    };
}
export interface QuoteAcceptedEvent extends DomainEvent {
    eventType: typeof DomainEventType.QUOTE_ACCEPTED;
    payload: {
        quoteId: string;
        customerId: string;
        quoteNumber: string;
        totalNet: number;
        totalGross: number;
    };
}
export interface QuoteRejectedEvent extends DomainEvent {
    eventType: typeof DomainEventType.QUOTE_REJECTED;
    payload: {
        quoteId: string;
        customerId: string;
        quoteNumber: string;
    };
}
export interface QuoteExpiredEvent extends DomainEvent {
    eventType: typeof DomainEventType.QUOTE_EXPIRED;
    payload: {
        quoteId: string;
        customerId: string;
        quoteNumber: string;
    };
}
export interface OrderCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.ORDER_CREATED;
    payload: {
        orderId: string;
        customerId: string;
        orderNumber: string;
        totalNet: number;
        totalGross: number;
    };
}
export interface OrderConfirmedEvent extends DomainEvent {
    eventType: typeof DomainEventType.ORDER_CONFIRMED;
    payload: {
        orderId: string;
        customerId: string;
        orderNumber: string;
        totalNet: number;
        totalGross: number;
    };
}
export interface OrderInvoicedEvent extends DomainEvent {
    eventType: typeof DomainEventType.ORDER_INVOICED;
    payload: {
        orderId: string;
        customerId: string;
        orderNumber: string;
        invoiceId: string;
        invoiceNumber: string;
    };
}
export interface OrderCancelledEvent extends DomainEvent {
    eventType: typeof DomainEventType.ORDER_CANCELLED;
    payload: {
        orderId: string;
        customerId: string;
        orderNumber: string;
    };
}
export interface InvoiceIssuedEvent extends DomainEvent {
    eventType: typeof DomainEventType.INVOICE_ISSUED;
    payload: {
        invoiceId: string;
        customerId: string;
        orderId?: string;
        invoiceNumber: string;
        totalNet: number;
        totalGross: number;
        dueDate: string;
    };
}
export interface InvoicePaidEvent extends DomainEvent {
    eventType: typeof DomainEventType.INVOICE_PAID;
    payload: {
        invoiceId: string;
        customerId: string;
        invoiceNumber: string;
        totalNet: number;
        totalGross: number;
        paidAt: string;
    };
}
export interface InvoiceOverdueEvent extends DomainEvent {
    eventType: typeof DomainEventType.INVOICE_OVERDUE;
    payload: {
        invoiceId: string;
        customerId: string;
        invoiceNumber: string;
        totalNet: number;
        totalGross: number;
        dueDate: string;
    };
}
export interface InvoiceCancelledEvent extends DomainEvent {
    eventType: typeof DomainEventType.INVOICE_CANCELLED;
    payload: {
        invoiceId: string;
        customerId: string;
        invoiceNumber: string;
    };
}
export interface CreditNoteIssuedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CREDIT_NOTE_ISSUED;
    payload: {
        creditNoteId: string;
        customerId: string;
        invoiceId: string;
        creditNumber: string;
        totalNet: number;
        totalGross: number;
        reason: string;
    };
}
export interface CreditNoteSettledEvent extends DomainEvent {
    eventType: typeof DomainEventType.CREDIT_NOTE_SETTLED;
    payload: {
        creditNoteId: string;
        customerId: string;
        invoiceId: string;
        creditNumber: string;
        totalNet: number;
        totalGross: number;
        settledAt: string;
    };
}
export type AnyDomainEvent = QuoteCreatedEvent | QuoteAcceptedEvent | QuoteRejectedEvent | QuoteExpiredEvent | OrderCreatedEvent | OrderConfirmedEvent | OrderInvoicedEvent | OrderCancelledEvent | InvoiceIssuedEvent | InvoicePaidEvent | InvoiceOverdueEvent | InvoiceCancelledEvent | CreditNoteIssuedEvent | CreditNoteSettledEvent;
//# sourceMappingURL=domain-events.d.ts.map