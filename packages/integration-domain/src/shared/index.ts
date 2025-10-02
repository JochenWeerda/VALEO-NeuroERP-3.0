/**
 * Shared Layer Exports
 */

// Types
export type {
  BaseEntity,
  AuditableEntity,
  EntityStatus,
  PaginationOptions,
  PaginatedResult,
  Result,
  ValidationError,
  DomainError
} from './types/common.js';

// Utilities
export { generateId, generatePrefixedId, isValidId } from './utils/id-generator.js';
