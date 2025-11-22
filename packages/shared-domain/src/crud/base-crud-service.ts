/**
 * Base CRUD Service Interface
 * Generic CRUD operations interface for all domain services
 */

export interface CrudFilter {
  [key: string]: any;
}

export interface CrudSort {
  field: string;
  direction: 'asc' | 'desc';
}

export interface CrudPagination {
  page: number;
  pageSize: number;
}

export interface CrudListResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface CrudDeleteOptions {
  reason: string; // Required for audit trail
  softDelete?: boolean; // Default: true
}

export interface CrudCancelOptions {
  reason: string; // Required for audit trail
}

export interface CrudUpdateOptions {
  reason?: string; // Optional reason for significant changes
}

/**
 * Base CRUD Service Interface
 * All domain services should implement this interface for consistency
 */
export interface BaseCrudService<T, CreateInput, UpdateInput> {
  /**
   * Create a new entity
   */
  create(input: CreateInput, userId: string): Promise<T>;

  /**
   * Get entity by ID
   */
  getById(id: string): Promise<T | null>;

  /**
   * List entities with filtering, sorting, and pagination
   */
  list(
    filters?: CrudFilter,
    pagination?: CrudPagination,
    sort?: CrudSort
  ): Promise<CrudListResult<T>>;

  /**
   * Search entities
   */
  search(query: string, limit?: number): Promise<T[]>;

  /**
   * Update entity
   */
  update(
    id: string,
    input: UpdateInput,
    userId: string,
    options?: CrudUpdateOptions
  ): Promise<T>;

  /**
   * Delete entity (soft delete by default)
   */
  delete(id: string, userId: string, options: CrudDeleteOptions): Promise<void>;

  /**
   * Cancel entity (for cancellable entities like orders, contracts)
   */
  cancel(id: string, userId: string, options: CrudCancelOptions): Promise<T>;

  /**
   * Restore soft-deleted entity
   */
  restore(id: string, userId: string, reason: string): Promise<T>;
}

/**
 * Base CRUD Service Implementation Helper
 * Provides common functionality for CRUD operations
 */
export abstract class BaseCrudServiceHelper<T, CreateInput, UpdateInput> {
  /**
   * Validate create input
   */
  protected abstract validateCreateInput(input: CreateInput): void;

  /**
   * Validate update input
   */
  protected abstract validateUpdateInput(input: UpdateInput): void;

  /**
   * Validate delete reason
   */
  protected validateDeleteReason(reason: string): void {
    if (!reason || reason.trim().length === 0) {
      throw new Error('Delete reason is required for audit trail');
    }
    if (reason.trim().length < 10) {
      throw new Error('Delete reason must be at least 10 characters');
    }
  }

  /**
   * Validate cancel reason
   */
  protected validateCancelReason(reason: string): void {
    if (!reason || reason.trim().length === 0) {
      throw new Error('Cancel reason is required for audit trail');
    }
    if (reason.trim().length < 10) {
      throw new Error('Cancel reason must be at least 10 characters');
    }
  }

  /**
   * Get entity type name for audit logging
   */
  protected abstract getEntityType(): string;

  /**
   * Transform create input to entity
   */
  protected abstract transformCreateInput(input: CreateInput, userId: string): T;

  /**
   * Transform update input to entity changes
   */
  protected abstract transformUpdateInput(
    entity: T,
    input: UpdateInput,
    userId: string
  ): T;
}

