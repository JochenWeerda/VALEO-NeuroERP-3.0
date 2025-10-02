import { v4 as uuidv4 } from 'uuid';
import {
  DomainEvent,
  QuoteCreatedEvent,
  QuoteAcceptedEvent,
  QuoteRejectedEvent,
  QuoteExpiredEvent,
  OrderCreatedEvent,
  OrderConfirmedEvent,
  OrderInvoicedEvent,
  OrderCancelledEvent,
  InvoiceIssuedEvent,
  InvoicePaidEvent,
  InvoiceOverdueEvent,
  InvoiceCancelledEvent,
  CreditNoteIssuedEvent,
  CreditNoteSettledEvent,
  DomainEventType
} from './domain-events';
import { QuoteEntity, OrderEntity, InvoiceEntity, CreditNoteEntity } from '../entities';

// Quote Event Factories
export function createQuoteCreatedEvent(
  quote: QuoteEntity,
  correlationId?: string,
  causationId?: string
): QuoteCreatedEvent {
  const event: QuoteCreatedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.QUOTE_CREATED,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createQuoteAcceptedEvent(
  quote: QuoteEntity,
  correlationId?: string,
  causationId?: string
): QuoteAcceptedEvent {
  const event: QuoteAcceptedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.QUOTE_ACCEPTED,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createQuoteRejectedEvent(
  quote: QuoteEntity,
  correlationId?: string,
  causationId?: string
): QuoteRejectedEvent {
  const event: QuoteRejectedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.QUOTE_REJECTED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: quote.tenantId,
    payload: {
      quoteId: quote.id,
      customerId: quote.customerId,
      quoteNumber: quote.quoteNumber
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createQuoteExpiredEvent(
  quote: QuoteEntity,
  correlationId?: string,
  causationId?: string
): QuoteExpiredEvent {
  const event: QuoteExpiredEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.QUOTE_EXPIRED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: quote.tenantId,
    payload: {
      quoteId: quote.id,
      customerId: quote.customerId,
      quoteNumber: quote.quoteNumber
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Order Event Factories
export function createOrderCreatedEvent(
  order: OrderEntity,
  correlationId?: string,
  causationId?: string
): OrderCreatedEvent {
  const event: OrderCreatedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.ORDER_CREATED,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createOrderConfirmedEvent(
  order: OrderEntity,
  correlationId?: string,
  causationId?: string
): OrderConfirmedEvent {
  const event: OrderConfirmedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.ORDER_CONFIRMED,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createOrderInvoicedEvent(
  order: OrderEntity,
  invoiceId: string,
  invoiceNumber: string,
  correlationId?: string,
  causationId?: string
): OrderInvoicedEvent {
  const event: OrderInvoicedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.ORDER_INVOICED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: order.tenantId,
    payload: {
      orderId: order.id,
      customerId: order.customerId,
      orderNumber: order.orderNumber,
      invoiceId,
      invoiceNumber
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createOrderCancelledEvent(
  order: OrderEntity,
  correlationId?: string,
  causationId?: string
): OrderCancelledEvent {
  const event: OrderCancelledEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.ORDER_CANCELLED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: order.tenantId,
    payload: {
      orderId: order.id,
      customerId: order.customerId,
      orderNumber: order.orderNumber
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Invoice Event Factories
export function createInvoiceIssuedEvent(
  invoice: InvoiceEntity,
  correlationId?: string,
  causationId?: string
): InvoiceIssuedEvent {
  const payload: any = {
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

  const event: InvoiceIssuedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.INVOICE_ISSUED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: invoice.tenantId,
    payload
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createInvoicePaidEvent(
  invoice: InvoiceEntity,
  correlationId?: string,
  causationId?: string
): InvoicePaidEvent {
  const event: InvoicePaidEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.INVOICE_PAID,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: invoice.tenantId,
    payload: {
      invoiceId: invoice.id,
      customerId: invoice.customerId,
      invoiceNumber: invoice.invoiceNumber,
      totalNet: invoice.totalNet,
      totalGross: invoice.totalGross,
      paidAt: invoice.paidAt!.toISOString()
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createInvoiceOverdueEvent(
  invoice: InvoiceEntity,
  correlationId?: string,
  causationId?: string
): InvoiceOverdueEvent {
  const event: InvoiceOverdueEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.INVOICE_OVERDUE,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createInvoiceCancelledEvent(
  invoice: InvoiceEntity,
  correlationId?: string,
  causationId?: string
): InvoiceCancelledEvent {
  const event: InvoiceCancelledEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.INVOICE_CANCELLED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: invoice.tenantId,
    payload: {
      invoiceId: invoice.id,
      customerId: invoice.customerId,
      invoiceNumber: invoice.invoiceNumber
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Credit Note Event Factories
export function createCreditNoteIssuedEvent(
  creditNote: CreditNoteEntity,
  correlationId?: string,
  causationId?: string
): CreditNoteIssuedEvent {
  const event: CreditNoteIssuedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.CREDIT_NOTE_ISSUED,
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

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

export function createCreditNoteSettledEvent(
  creditNote: CreditNoteEntity,
  correlationId?: string,
  causationId?: string
): CreditNoteSettledEvent {
  const event: CreditNoteSettledEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.CREDIT_NOTE_SETTLED,
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
      settledAt: creditNote.settledAt!.toISOString()
    }
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}