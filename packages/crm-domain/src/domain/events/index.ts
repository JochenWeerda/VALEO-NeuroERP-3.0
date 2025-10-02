// Export all domain events
export * from './domain-events';
export * from './event-factories';

// Re-export commonly used types and constants
export { DomainEventType } from './domain-events';
export type {
  DomainEvent,
  AnyDomainEvent,
  CustomerCreatedEvent,
  CustomerUpdatedEvent,
  CustomerStatusChangedEvent,
  CustomerDeletedEvent,
  ContactCreatedEvent,
  ContactUpdatedEvent,
  ContactDeletedEvent,
  OpportunityCreatedEvent,
  OpportunityUpdatedEvent,
  OpportunityStageChangedEvent,
  OpportunityWonEvent,
  OpportunityLostEvent,
  OpportunityDeletedEvent,
  InteractionCreatedEvent,
  InteractionUpdatedEvent,
  InteractionDeletedEvent
} from './domain-events';

// Re-export event factory functions
export {
  createCustomerCreatedEvent,
  createCustomerUpdatedEvent,
  createCustomerStatusChangedEvent,
  createCustomerDeletedEvent,
  createContactCreatedEvent,
  createContactUpdatedEvent,
  createContactDeletedEvent,
  createOpportunityCreatedEvent,
  createOpportunityUpdatedEvent,
  createOpportunityStageChangedEvent,
  createOpportunityWonEvent,
  createOpportunityLostEvent,
  createOpportunityDeletedEvent,
  createInteractionCreatedEvent,
  createInteractionUpdatedEvent,
  createInteractionDeletedEvent
} from './event-factories';