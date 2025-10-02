"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createCustomerCreatedEvent = createCustomerCreatedEvent;
exports.createCustomerUpdatedEvent = createCustomerUpdatedEvent;
exports.createCustomerStatusChangedEvent = createCustomerStatusChangedEvent;
exports.createCustomerDeletedEvent = createCustomerDeletedEvent;
exports.createContactCreatedEvent = createContactCreatedEvent;
exports.createContactUpdatedEvent = createContactUpdatedEvent;
exports.createContactDeletedEvent = createContactDeletedEvent;
exports.createOpportunityCreatedEvent = createOpportunityCreatedEvent;
exports.createOpportunityUpdatedEvent = createOpportunityUpdatedEvent;
exports.createOpportunityStageChangedEvent = createOpportunityStageChangedEvent;
exports.createOpportunityWonEvent = createOpportunityWonEvent;
exports.createOpportunityLostEvent = createOpportunityLostEvent;
exports.createOpportunityDeletedEvent = createOpportunityDeletedEvent;
exports.createInteractionCreatedEvent = createInteractionCreatedEvent;
exports.createInteractionUpdatedEvent = createInteractionUpdatedEvent;
exports.createInteractionDeletedEvent = createInteractionDeletedEvent;
const uuid_1 = require("uuid");
const domain_events_1 = require("./domain-events");
// Base event creation helper
function createBaseEvent(eventType, tenantId, correlationId, causationId, metadata) {
    return {
        eventType,
        tenantId,
        correlationId,
        causationId,
        metadata
    };
}
// Customer Event Factories
function createCustomerCreatedEvent(customer, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CUSTOMER_CREATED, customer.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            customerId: customer.id,
            number: customer.number,
            name: customer.name,
            status: customer.status,
            ownerUserId: customer.ownerUserId
        }
    };
}
function createCustomerUpdatedEvent(customer, changes, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CUSTOMER_UPDATED, customer.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            customerId: customer.id,
            changes
        }
    };
}
function createCustomerStatusChangedEvent(customer, oldStatus, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CUSTOMER_STATUS_CHANGED, customer.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            customerId: customer.id,
            oldStatus,
            newStatus: customer.status
        }
    };
}
function createCustomerDeletedEvent(customer, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CUSTOMER_DELETED, customer.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            customerId: customer.id
        }
    };
}
// Contact Event Factories
function createContactCreatedEvent(contact, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CONTACT_CREATED, contact.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            contactId: contact.id,
            customerId: contact.customerId,
            email: contact.email,
            isPrimary: contact.isPrimary
        }
    };
}
function createContactUpdatedEvent(contact, changes, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CONTACT_UPDATED, contact.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            contactId: contact.id,
            changes
        }
    };
}
function createContactDeletedEvent(contact, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.CONTACT_DELETED, contact.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            contactId: contact.id,
            customerId: contact.customerId
        }
    };
}
// Opportunity Event Factories
function createOpportunityCreatedEvent(opportunity, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_CREATED, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
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
    };
}
function createOpportunityUpdatedEvent(opportunity, changes, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_UPDATED, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            opportunityId: opportunity.id,
            changes
        }
    };
}
function createOpportunityStageChangedEvent(opportunity, oldStage, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_STAGE_CHANGED, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            opportunityId: opportunity.id,
            oldStage,
            newStage: opportunity.stage,
            amountNet: opportunity.amountNet,
            probability: opportunity.probability
        }
    };
}
function createOpportunityWonEvent(opportunity, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_WON, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            opportunityId: opportunity.id,
            customerId: opportunity.customerId,
            amountNet: opportunity.amountNet,
            probability: opportunity.probability
        }
    };
}
function createOpportunityLostEvent(opportunity, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_LOST, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            opportunityId: opportunity.id,
            customerId: opportunity.customerId,
            amountNet: opportunity.amountNet,
            probability: opportunity.probability
        }
    };
}
function createOpportunityDeletedEvent(opportunity, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.OPPORTUNITY_DELETED, opportunity.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            opportunityId: opportunity.id
        }
    };
}
// Interaction Event Factories
function createInteractionCreatedEvent(interaction, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.INTERACTION_CREATED, interaction.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
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
    };
}
function createInteractionUpdatedEvent(interaction, changes, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.INTERACTION_UPDATED, interaction.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            interactionId: interaction.id,
            changes
        }
    };
}
function createInteractionDeletedEvent(interaction, correlationId, causationId) {
    const baseEvent = createBaseEvent(domain_events_1.DomainEventType.INTERACTION_DELETED, interaction.tenantId, correlationId, causationId);
    return {
        ...baseEvent,
        eventId: (0, uuid_1.v4)(),
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        payload: {
            interactionId: interaction.id,
            customerId: interaction.customerId
        }
    };
}
//# sourceMappingURL=event-factories.js.map