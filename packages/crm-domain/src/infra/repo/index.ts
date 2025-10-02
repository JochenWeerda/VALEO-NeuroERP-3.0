// Export all repositories
export * from './customer-repository';
export * from './contact-repository';
export * from './opportunity-repository';
export * from './interaction-repository';

// Re-export commonly used repository instances
export { CustomerRepository } from './customer-repository';
export { ContactRepository } from './contact-repository';
export { OpportunityRepository } from './opportunity-repository';
export { InteractionRepository } from './interaction-repository';

// Re-export types
export type {
  CustomerFilters,
  PaginationOptions,
  PaginatedResult
} from './customer-repository';

export type {
  ContactFilters
} from './contact-repository';

export type {
  OpportunityFilters
} from './opportunity-repository';

export type {
  InteractionFilters
} from './interaction-repository';