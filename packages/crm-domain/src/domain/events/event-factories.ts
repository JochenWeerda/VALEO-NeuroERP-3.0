import { v4 as uuidv4 } from 'uuid';
import {
  DomainEvent,
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
  InteractionDeletedEvent,
  DomainEventType
} from './domain-events';
import { CustomerEntity, ContactEntity, OpportunityEntity, InteractionEntity } from '../entities';

// Base event creation helper
function createBaseEvent(
  eventType: DomainEvent['eventType'],
  tenantId: string,
  correlationId?: string,
  causationId?: string,
  metadata?: Record<string, any>
): Omit<DomainEvent, 'eventId' | 'eventVersion' | 'occurredAt'> {
  return {
    eventType,
    tenantId,
    correlationId,
    causationId,
    metadata
  } as any;
}

// Customer Event Factories
export function createCustomerCreatedEvent(
  customer: CustomerEntity,
  correlationId?: string,
  causationId?: string
): CustomerCreatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CUSTOMER_CREATED,
    customer.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      customerId: customer.id,
      number: customer.number,
      name: customer.name,
      status: customer.status,
      ownerUserId: customer.ownerUserId
    }
  } as any;
}

export function createCustomerUpdatedEvent(
  customer: CustomerEntity,
  changes: Record<string, any>,
  correlationId?: string,
  causationId?: string
): CustomerUpdatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CUSTOMER_UPDATED,
    customer.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      customerId: customer.id,
      changes
    }
  } as any;
}

export function createCustomerStatusChangedEvent(
  customer: CustomerEntity,
  oldStatus: string,
  correlationId?: string,
  causationId?: string
): CustomerStatusChangedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CUSTOMER_STATUS_CHANGED,
    customer.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      customerId: customer.id,
      oldStatus,
      newStatus: customer.status
    }
  } as any;
}

export function createCustomerDeletedEvent(
  customer: CustomerEntity,
  correlationId?: string,
  causationId?: string
): CustomerDeletedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CUSTOMER_DELETED,
    customer.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      customerId: customer.id
    }
  } as any;
}

// Contact Event Factories
export function createContactCreatedEvent(
  contact: ContactEntity,
  correlationId?: string,
  causationId?: string
): ContactCreatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CONTACT_CREATED,
    contact.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      contactId: contact.id,
      customerId: contact.customerId,
      email: contact.email,
      isPrimary: contact.isPrimary
    }
  } as any;
}

export function createContactUpdatedEvent(
  contact: ContactEntity,
  changes: Record<string, any>,
  correlationId?: string,
  causationId?: string
): ContactUpdatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CONTACT_UPDATED,
    contact.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      contactId: contact.id,
      changes
    }
  } as any;
}

export function createContactDeletedEvent(
  contact: ContactEntity,
  correlationId?: string,
  causationId?: string
): ContactDeletedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.CONTACT_DELETED,
    contact.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      contactId: contact.id,
      customerId: contact.customerId
    }
  } as any;
}

// Opportunity Event Factories
export function createOpportunityCreatedEvent(
  opportunity: OpportunityEntity,
  correlationId?: string,
  causationId?: string
): OpportunityCreatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_CREATED,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id,
      customerId: opportunity.customerId,
      title: opportunity.title,
      stage: opportunity.stage,
      amountNet: opportunity.amountNet,
      probability: opportunity.probability
    }
  } as any;
}

export function createOpportunityUpdatedEvent(
  opportunity: OpportunityEntity,
  changes: Record<string, any>,
  correlationId?: string,
  causationId?: string
): OpportunityUpdatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_UPDATED,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id,
      changes
    }
  } as any;
}

export function createOpportunityStageChangedEvent(
  opportunity: OpportunityEntity,
  oldStage: string,
  correlationId?: string,
  causationId?: string
): OpportunityStageChangedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_STAGE_CHANGED,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id,
      oldStage,
      newStage: opportunity.stage,
      amountNet: opportunity.amountNet,
      probability: opportunity.probability
    }
  } as any;
}

export function createOpportunityWonEvent(
  opportunity: OpportunityEntity,
  correlationId?: string,
  causationId?: string
): OpportunityWonEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_WON,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id,
      customerId: opportunity.customerId,
      amountNet: opportunity.amountNet,
      probability: opportunity.probability
    }
  } as any;
}

export function createOpportunityLostEvent(
  opportunity: OpportunityEntity,
  correlationId?: string,
  causationId?: string
): OpportunityLostEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_LOST,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id,
      customerId: opportunity.customerId,
      amountNet: opportunity.amountNet,
      probability: opportunity.probability
    }
  } as any;
}

export function createOpportunityDeletedEvent(
  opportunity: OpportunityEntity,
  correlationId?: string,
  causationId?: string
): OpportunityDeletedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.OPPORTUNITY_DELETED,
    opportunity.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      opportunityId: opportunity.id
    }
  } as any;
}

// Interaction Event Factories
export function createInteractionCreatedEvent(
  interaction: InteractionEntity,
  correlationId?: string,
  causationId?: string
): InteractionCreatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.INTERACTION_CREATED,
    interaction.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      interactionId: interaction.id,
      customerId: interaction.customerId,
      contactId: interaction.contactId,
      type: interaction.type,
      subject: interaction.subject,
      occurredAt: interaction.occurredAt.toISOString()
    }
  } as any;
}

export function createInteractionUpdatedEvent(
  interaction: InteractionEntity,
  changes: Record<string, any>,
  correlationId?: string,
  causationId?: string
): InteractionUpdatedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.INTERACTION_UPDATED,
    interaction.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      interactionId: interaction.id,
      changes
    }
  } as any;
}

export function createInteractionDeletedEvent(
  interaction: InteractionEntity,
  correlationId?: string,
  causationId?: string
): InteractionDeletedEvent {
  const baseEvent = createBaseEvent(
    DomainEventType.INTERACTION_DELETED,
    interaction.tenantId,
    correlationId,
    causationId
  );

  return {
    ...baseEvent,
    eventId: uuidv4(),
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    payload: {
      interactionId: interaction.id,
      customerId: interaction.customerId
    }
  } as any;
}
