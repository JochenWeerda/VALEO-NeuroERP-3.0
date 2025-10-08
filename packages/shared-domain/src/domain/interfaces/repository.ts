/**
 * Repository Interfaces for VALEO NeuroERP 3.0
 * Common repository patterns and contracts
 */

import type { EntityId } from '../value-objects/branded-types.js';
import type { BaseEntity } from '../entities/base-entity.js';

// Generic Repository Interface
export interface Repository<T extends BaseEntity> {
  findById(id: EntityId): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  update(entity: T): Promise<T>;
  delete(id: EntityId): Promise<void>;
  exists(id: EntityId): Promise<boolean>;
}

// Query Builder Interface
export interface QueryBuilder<T> {
  where(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T>;
  andWhere(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T>;
  orWhere(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T>;
  orderBy(field: string, direction: 'ASC' | 'DESC'): QueryBuilder<T>;
  limit(count: number): QueryBuilder<T>;
  offset(count: number): QueryBuilder<T>;
  execute(): Promise<T[]>;
  count(): Promise<number>;
}

// Query Operators
export type QueryOperator = 
  | 'equals'
  | 'notEquals'
  | 'greaterThan'
  | 'greaterThanOrEqual'
  | 'lessThan'
  | 'lessThanOrEqual'
  | 'like'
  | 'notLike'
  | 'in'
  | 'notIn'
  | 'isNull'
  | 'isNotNull'
  | 'between'
  | 'notBetween';

// Pagination Interface
export interface PaginationOptions {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortDirection?: 'ASC' | 'DESC';
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// Unit of Work Interface
export interface UnitOfWork {
  start(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  isActive(): boolean;
}

// Transaction Manager Interface
export interface TransactionManager {
  withTransaction<T>(operation: (unitOfWork: UnitOfWork) => Promise<T>): Promise<T>;
}

// Repository Factory Interface
export interface RepositoryFactory {
  createRepository<T extends BaseEntity>(entityType: new (...args: any[]) => T): Repository<T>;
}

// Audit Repository Interface
export interface AuditRepository<T extends BaseEntity> extends Repository<T> {
  findAuditTrail(id: EntityId): Promise<AuditEntry[]>;
  findVersionHistory(id: EntityId): Promise<VersionHistory[]>;
}

// Audit Entry Interface
export interface AuditEntry {
  id: string;
  entityId: EntityId;
  entityType: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  changes: Record<string, { old: unknown; new: unknown }>;
  performedBy: string;
  performedAt: Date;
  metadata?: Record<string, unknown>;
}

// Version History Interface
export interface VersionHistory {
  version: number;
  entityData: Record<string, unknown>;
  createdAt: Date;
  createdBy?: string;
  changes: Record<string, { old: unknown; new: unknown }>;
}


