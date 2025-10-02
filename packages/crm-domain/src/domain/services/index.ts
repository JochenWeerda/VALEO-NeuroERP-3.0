// Export all services
export * from './customer-service';
export * from './contact-service';
export * from './opportunity-service';
export * from './interaction-service';

// Re-export commonly used service classes
export { CustomerService } from './customer-service';
export { ContactService } from './contact-service';
export { OpportunityService } from './opportunity-service';
export { InteractionService } from './interaction-service';

// Re-export service dependencies interface
export type { CustomerServiceDependencies } from './customer-service';
export type { ContactServiceDependencies } from './contact-service';
export type { OpportunityServiceDependencies } from './opportunity-service';
export type { InteractionServiceDependencies } from './interaction-service';