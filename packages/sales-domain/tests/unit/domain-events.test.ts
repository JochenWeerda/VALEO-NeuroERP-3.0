import { describe, it, expect } from 'vitest';
import { DomainEventType } from '../../src/domain/events/domain-events';

describe('Domain Events', () => {
  describe('Event Types', () => {
    it('should have all required quote event types', () => {
      expect(DomainEventType.QUOTE_CREATED).toBe('sales.quote.created');
      expect(DomainEventType.QUOTE_SENT).toBe('sales.quote.sent');
      expect(DomainEventType.QUOTE_ACCEPTED).toBe('sales.quote.accepted');
      expect(DomainEventType.QUOTE_REJECTED).toBe('sales.quote.rejected');
      expect(DomainEventType.QUOTE_EXPIRED).toBe('sales.quote.expired');
    });

    it('should have all required order event types', () => {
      expect(DomainEventType.ORDER_CREATED).toBe('sales.order.created');
      expect(DomainEventType.ORDER_CONFIRMED).toBe('sales.order.confirmed');
      expect(DomainEventType.ORDER_INVOICED).toBe('sales.order.invoiced');
      expect(DomainEventType.ORDER_CANCELLED).toBe('sales.order.cancelled');
    });

    it('should have all required invoice event types', () => {
      expect(DomainEventType.INVOICE_ISSUED).toBe('sales.invoice.issued');
      expect(DomainEventType.INVOICE_PAID).toBe('sales.invoice.paid');
      expect(DomainEventType.INVOICE_OVERDUE).toBe('sales.invoice.overdue');
      expect(DomainEventType.INVOICE_CANCELLED).toBe('sales.invoice.cancelled');
    });

    it('should have all required credit note event types', () => {
      expect(DomainEventType.CREDIT_NOTE_ISSUED).toBe('sales.credit_note.issued');
      expect(DomainEventType.CREDIT_NOTE_SETTLED).toBe('sales.credit_note.settled');
    });
  });
});