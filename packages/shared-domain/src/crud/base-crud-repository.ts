/**
 * Base CRUD Repository Interface
 * Generic repository pattern for all domain repositories
 */

import {
  CrudFilter,
  CrudSort,
  CrudPagination,
  CrudListResult,
} from './base-crud-service';

/**
 * Base CRUD Repository Interface
 * All domain repositories should implement this interface for consistency
 */
export interface BaseCrudRepository<T> {
  /**
   * Find entity by ID
   */
  findById(id: string): Promise<T | null>;

  /**
   * Find entities with filtering, sorting, and pagination
   */
  findMany(
    filters?: CrudFilter,
    pagination?: CrudPagination,
    sort?: CrudSort
  ): Promise<CrudListResult<T>>;

  /**
   * Search entities by query string
   */
  search(query: string, limit?: number): Promise<T[]>;

  /**
   * Create entity
   */
  create(entity: T): Promise<T>;

  /**
   * Update entity
   */
  update(entity: T): Promise<T>;

  /**
   * Delete entity (hard delete)
   */
  delete(id: string): Promise<void>;

  /**
   * Soft delete entity
   */
  softDelete(id: string, deletedAt: Date, deletedBy: string): Promise<void>;

  /**
   * Restore soft-deleted entity
   */
  restore(id: string, restoredAt: Date, restoredBy: string): Promise<void>;

  /**
   * Check if entity exists
   */
  exists(id: string): Promise<boolean>;

  /**
   * Count entities matching filters
   */
  count(filters?: CrudFilter): Promise<number>;
}

/**
 * Base CRUD Repository Implementation Helper
 * Provides common repository functionality
 */
export abstract class BaseCrudRepositoryHelper<T> {
  /**
   * Apply filters to query
   */
  protected abstract applyFilters(query: any, filters: CrudFilter): any;

  /**
   * Apply sorting to query
   */
  protected abstract applySorting(query: any, sort: CrudSort): any;

  /**
   * Apply pagination to query
   */
  protected abstract applyPagination(
    query: any,
    pagination: CrudPagination
  ): any;

  /**
   * Transform database result to entity
   */
  protected abstract transformToEntity(data: any): T;

  /**
   * Transform entity to database format
   */
  protected abstract transformFromEntity(entity: T): any;
}

