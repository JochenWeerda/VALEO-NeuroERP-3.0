"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DomainEventType = void 0;
// Domain Event Types
exports.DomainEventType = {
    CUSTOMER_CREATED: 'crm.customer.created',
    CUSTOMER_UPDATED: 'crm.customer.updated',
    CUSTOMER_STATUS_CHANGED: 'crm.customer.status_changed',
    CUSTOMER_DELETED: 'crm.customer.deleted',
    CONTACT_CREATED: 'crm.contact.created',
    CONTACT_UPDATED: 'crm.contact.updated',
    CONTACT_DELETED: 'crm.contact.deleted',
    OPPORTUNITY_CREATED: 'crm.opportunity.created',
    OPPORTUNITY_UPDATED: 'crm.opportunity.updated',
    OPPORTUNITY_STAGE_CHANGED: 'crm.opportunity.stage_changed',
    OPPORTUNITY_WON: 'crm.opportunity.won',
    OPPORTUNITY_LOST: 'crm.opportunity.lost',
    OPPORTUNITY_DELETED: 'crm.opportunity.deleted',
    INTERACTION_CREATED: 'crm.interaction.created',
    INTERACTION_UPDATED: 'crm.interaction.updated',
    INTERACTION_DELETED: 'crm.interaction.deleted'
};
//# sourceMappingURL=domain-events.js.map