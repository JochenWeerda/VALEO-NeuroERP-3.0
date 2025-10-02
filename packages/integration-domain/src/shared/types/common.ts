/**
 * Shared type definitions for Integration Domain
 */

export type EntityId = string;
export type Timestamp = Date;

export interface BaseEntity {
  readonly id: string;
  readonly createdAt: Timestamp;
  readonly updatedAt: Timestamp;
}

export interface AuditableEntity extends BaseEntity {
  readonly createdBy: string;
  readonly updatedBy: string;
}

export type EntityStatus = 'active' | 'inactive' | 'pending' | 'error';

export interface PaginationOptions {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface DomainError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
