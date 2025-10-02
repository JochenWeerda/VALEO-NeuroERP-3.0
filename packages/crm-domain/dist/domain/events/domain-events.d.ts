export declare const DomainEventType: {
    readonly CUSTOMER_CREATED: "crm.customer.created";
    readonly CUSTOMER_UPDATED: "crm.customer.updated";
    readonly CUSTOMER_STATUS_CHANGED: "crm.customer.status_changed";
    readonly CUSTOMER_DELETED: "crm.customer.deleted";
    readonly CONTACT_CREATED: "crm.contact.created";
    readonly CONTACT_UPDATED: "crm.contact.updated";
    readonly CONTACT_DELETED: "crm.contact.deleted";
    readonly OPPORTUNITY_CREATED: "crm.opportunity.created";
    readonly OPPORTUNITY_UPDATED: "crm.opportunity.updated";
    readonly OPPORTUNITY_STAGE_CHANGED: "crm.opportunity.stage_changed";
    readonly OPPORTUNITY_WON: "crm.opportunity.won";
    readonly OPPORTUNITY_LOST: "crm.opportunity.lost";
    readonly OPPORTUNITY_DELETED: "crm.opportunity.deleted";
    readonly INTERACTION_CREATED: "crm.interaction.created";
    readonly INTERACTION_UPDATED: "crm.interaction.updated";
    readonly INTERACTION_DELETED: "crm.interaction.deleted";
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
export interface CustomerCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CUSTOMER_CREATED;
    payload: {
        customerId: string;
        number: string;
        name: string;
        status: string;
        ownerUserId?: string;
    };
}
export interface CustomerUpdatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CUSTOMER_UPDATED;
    payload: {
        customerId: string;
        changes: Record<string, any>;
    };
}
export interface CustomerStatusChangedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CUSTOMER_STATUS_CHANGED;
    payload: {
        customerId: string;
        oldStatus: string;
        newStatus: string;
    };
}
export interface CustomerDeletedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CUSTOMER_DELETED;
    payload: {
        customerId: string;
    };
}
export interface ContactCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CONTACT_CREATED;
    payload: {
        contactId: string;
        customerId: string;
        email: string;
        isPrimary: boolean;
    };
}
export interface ContactUpdatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CONTACT_UPDATED;
    payload: {
        contactId: string;
        changes: Record<string, any>;
    };
}
export interface ContactDeletedEvent extends DomainEvent {
    eventType: typeof DomainEventType.CONTACT_DELETED;
    payload: {
        contactId: string;
        customerId: string;
    };
}
export interface OpportunityCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_CREATED;
    payload: {
        opportunityId: string;
        customerId: string;
        title: string;
        stage: string;
        amountNet?: number;
        probability: number;
    };
}
export interface OpportunityUpdatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_UPDATED;
    payload: {
        opportunityId: string;
        changes: Record<string, any>;
    };
}
export interface OpportunityStageChangedEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_STAGE_CHANGED;
    payload: {
        opportunityId: string;
        oldStage: string;
        newStage: string;
        amountNet?: number;
        probability: number;
    };
}
export interface OpportunityWonEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_WON;
    payload: {
        opportunityId: string;
        customerId: string;
        amountNet?: number;
        probability: number;
    };
}
export interface OpportunityLostEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_LOST;
    payload: {
        opportunityId: string;
        customerId: string;
        amountNet?: number;
        probability: number;
    };
}
export interface OpportunityDeletedEvent extends DomainEvent {
    eventType: typeof DomainEventType.OPPORTUNITY_DELETED;
    payload: {
        opportunityId: string;
    };
}
export interface InteractionCreatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.INTERACTION_CREATED;
    payload: {
        interactionId: string;
        customerId: string;
        contactId?: string;
        type: string;
        subject: string;
        occurredAt: string;
    };
}
export interface InteractionUpdatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.INTERACTION_UPDATED;
    payload: {
        interactionId: string;
        changes: Record<string, any>;
    };
}
export interface InteractionDeletedEvent extends DomainEvent {
    eventType: typeof DomainEventType.INTERACTION_DELETED;
    payload: {
        interactionId: string;
        customerId: string;
    };
}
export type AnyDomainEvent = CustomerCreatedEvent | CustomerUpdatedEvent | CustomerStatusChangedEvent | CustomerDeletedEvent | ContactCreatedEvent | ContactUpdatedEvent | ContactDeletedEvent | OpportunityCreatedEvent | OpportunityUpdatedEvent | OpportunityStageChangedEvent | OpportunityWonEvent | OpportunityLostEvent | OpportunityDeletedEvent | InteractionCreatedEvent | InteractionUpdatedEvent | InteractionDeletedEvent;
//# sourceMappingURL=domain-events.d.ts.map