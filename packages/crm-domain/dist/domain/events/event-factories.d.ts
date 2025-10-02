import { CustomerCreatedEvent, CustomerUpdatedEvent, CustomerStatusChangedEvent, CustomerDeletedEvent, ContactCreatedEvent, ContactUpdatedEvent, ContactDeletedEvent, OpportunityCreatedEvent, OpportunityUpdatedEvent, OpportunityStageChangedEvent, OpportunityWonEvent, OpportunityLostEvent, OpportunityDeletedEvent, InteractionCreatedEvent, InteractionUpdatedEvent, InteractionDeletedEvent } from './domain-events';
import { CustomerEntity, ContactEntity, OpportunityEntity, InteractionEntity } from '../entities';
export declare function createCustomerCreatedEvent(customer: CustomerEntity, correlationId?: string, causationId?: string): CustomerCreatedEvent;
export declare function createCustomerUpdatedEvent(customer: CustomerEntity, changes: Record<string, any>, correlationId?: string, causationId?: string): CustomerUpdatedEvent;
export declare function createCustomerStatusChangedEvent(customer: CustomerEntity, oldStatus: string, correlationId?: string, causationId?: string): CustomerStatusChangedEvent;
export declare function createCustomerDeletedEvent(customer: CustomerEntity, correlationId?: string, causationId?: string): CustomerDeletedEvent;
export declare function createContactCreatedEvent(contact: ContactEntity, correlationId?: string, causationId?: string): ContactCreatedEvent;
export declare function createContactUpdatedEvent(contact: ContactEntity, changes: Record<string, any>, correlationId?: string, causationId?: string): ContactUpdatedEvent;
export declare function createContactDeletedEvent(contact: ContactEntity, correlationId?: string, causationId?: string): ContactDeletedEvent;
export declare function createOpportunityCreatedEvent(opportunity: OpportunityEntity, correlationId?: string, causationId?: string): OpportunityCreatedEvent;
export declare function createOpportunityUpdatedEvent(opportunity: OpportunityEntity, changes: Record<string, any>, correlationId?: string, causationId?: string): OpportunityUpdatedEvent;
export declare function createOpportunityStageChangedEvent(opportunity: OpportunityEntity, oldStage: string, correlationId?: string, causationId?: string): OpportunityStageChangedEvent;
export declare function createOpportunityWonEvent(opportunity: OpportunityEntity, correlationId?: string, causationId?: string): OpportunityWonEvent;
export declare function createOpportunityLostEvent(opportunity: OpportunityEntity, correlationId?: string, causationId?: string): OpportunityLostEvent;
export declare function createOpportunityDeletedEvent(opportunity: OpportunityEntity, correlationId?: string, causationId?: string): OpportunityDeletedEvent;
export declare function createInteractionCreatedEvent(interaction: InteractionEntity, correlationId?: string, causationId?: string): InteractionCreatedEvent;
export declare function createInteractionUpdatedEvent(interaction: InteractionEntity, changes: Record<string, any>, correlationId?: string, causationId?: string): InteractionUpdatedEvent;
export declare function createInteractionDeletedEvent(interaction: InteractionEntity, correlationId?: string, causationId?: string): InteractionDeletedEvent;
//# sourceMappingURL=event-factories.d.ts.map