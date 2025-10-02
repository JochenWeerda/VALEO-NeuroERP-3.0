// Export all contract schemas
export * from './customer-contracts';
export * from './contact-contracts';
export * from './opportunity-contracts';
export * from './interaction-contracts';

// Re-export commonly used contract schemas
export {
  CreateCustomerContractSchema,
  UpdateCustomerContractSchema,
  CustomerResponseContractSchema,
  CustomerQueryContractSchema,
  CustomerListResponseContractSchema,
  AddressContractSchema,
  CustomerStatusContractSchema
} from './customer-contracts';

export {
  CreateContactContractSchema,
  UpdateContactContractSchema,
  ContactResponseContractSchema
} from './contact-contracts';

export {
  CreateOpportunityContractSchema,
  UpdateOpportunityContractSchema,
  OpportunityResponseContractSchema,
  OpportunityQueryContractSchema,
  OpportunityListResponseContractSchema,
  OpportunityStageContractSchema
} from './opportunity-contracts';

export {
  CreateInteractionContractSchema,
  UpdateInteractionContractSchema,
  InteractionResponseContractSchema,
  InteractionQueryContractSchema,
  InteractionListResponseContractSchema,
  InteractionTypeContractSchema,
  AttachmentContractSchema
} from './interaction-contracts';