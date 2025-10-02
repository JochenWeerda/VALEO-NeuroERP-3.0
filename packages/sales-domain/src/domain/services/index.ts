// Export all services
export * from './quote-service';
export * from './order-service';
export * from './invoice-service';
export * from './credit-note-service';

// Re-export commonly used service classes
export { QuoteService } from './quote-service';
export { OrderService } from './order-service';
export { InvoiceService } from './invoice-service';
export { CreditNoteService } from './credit-note-service';

// Re-export service dependencies interface
export type { QuoteServiceDependencies } from './quote-service';
export type { OrderServiceDependencies } from './order-service';
export type { InvoiceServiceDependencies } from './invoice-service';
export type { CreditNoteServiceDependencies } from './credit-note-service';