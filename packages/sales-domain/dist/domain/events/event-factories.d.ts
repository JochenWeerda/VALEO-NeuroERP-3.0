import { QuoteCreatedEvent, QuoteAcceptedEvent, QuoteRejectedEvent, QuoteExpiredEvent, OrderCreatedEvent, OrderConfirmedEvent, OrderInvoicedEvent, OrderCancelledEvent, InvoiceIssuedEvent, InvoicePaidEvent, InvoiceOverdueEvent, InvoiceCancelledEvent, CreditNoteIssuedEvent, CreditNoteSettledEvent } from './domain-events';
import { QuoteEntity, OrderEntity, InvoiceEntity, CreditNoteEntity } from '../entities';
export declare function createQuoteCreatedEvent(quote: QuoteEntity, correlationId?: string, causationId?: string): QuoteCreatedEvent;
export declare function createQuoteAcceptedEvent(quote: QuoteEntity, correlationId?: string, causationId?: string): QuoteAcceptedEvent;
export declare function createQuoteRejectedEvent(quote: QuoteEntity, correlationId?: string, causationId?: string): QuoteRejectedEvent;
export declare function createQuoteExpiredEvent(quote: QuoteEntity, correlationId?: string, causationId?: string): QuoteExpiredEvent;
export declare function createOrderCreatedEvent(order: OrderEntity, correlationId?: string, causationId?: string): OrderCreatedEvent;
export declare function createOrderConfirmedEvent(order: OrderEntity, correlationId?: string, causationId?: string): OrderConfirmedEvent;
export declare function createOrderInvoicedEvent(order: OrderEntity, invoiceId: string, invoiceNumber: string, correlationId?: string, causationId?: string): OrderInvoicedEvent;
export declare function createOrderCancelledEvent(order: OrderEntity, correlationId?: string, causationId?: string): OrderCancelledEvent;
export declare function createInvoiceIssuedEvent(invoice: InvoiceEntity, correlationId?: string, causationId?: string): InvoiceIssuedEvent;
export declare function createInvoicePaidEvent(invoice: InvoiceEntity, correlationId?: string, causationId?: string): InvoicePaidEvent;
export declare function createInvoiceOverdueEvent(invoice: InvoiceEntity, correlationId?: string, causationId?: string): InvoiceOverdueEvent;
export declare function createInvoiceCancelledEvent(invoice: InvoiceEntity, correlationId?: string, causationId?: string): InvoiceCancelledEvent;
export declare function createCreditNoteIssuedEvent(creditNote: CreditNoteEntity, correlationId?: string, causationId?: string): CreditNoteIssuedEvent;
export declare function createCreditNoteSettledEvent(creditNote: CreditNoteEntity, correlationId?: string, causationId?: string): CreditNoteSettledEvent;
//# sourceMappingURL=event-factories.d.ts.map