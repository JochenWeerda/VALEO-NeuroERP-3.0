// Export all entities
export * from './customer';
export * from './contact';
export * from './opportunity';
export * from './interaction';

// Re-export commonly used types
export type {
  Customer,
  CreateCustomerInput,
  UpdateCustomerInput,
  Address,
  CustomerStatusType
} from './customer';

export type {
  Contact,
  CreateContactInput,
  UpdateContactInput
} from './contact';

export type {
  Opportunity,
  CreateOpportunityInput,
  UpdateOpportunityInput,
  OpportunityStageType
} from './opportunity';

export type {
  Interaction,
  CreateInteractionInput,
  UpdateInteractionInput,
  Attachment,
  InteractionTypeType
} from './interaction';

// Re-export enums
export { CustomerStatus } from './customer';
export { OpportunityStage } from './opportunity';
export { InteractionType } from './interaction';