/**
 * Base Repository Implementation for VALEO NeuroERP 3.0
 * Common repository functionality
 */

import type { EntityId } from '../../domain/value-objects/branded-types.js';
import type { BaseEntity } from '../../domain/entities/base-entity.js';
import type { Repository, QueryBuilder, QueryOperator } from '../../domain/interfaces/repository.js';

export abstract class BaseRepository<T extends BaseEntity> implements Repository<T> {
  protected entities: Map<string, T> = new Map();

  abstract findById(id: EntityId): Promise<T | null>;
  abstract findAll(): Promise<T[]>;
  abstract save(entity: T): Promise<T>;
  abstract update(entity: T): Promise<T>;
  abstract delete(id: EntityId): Promise<void>;

  async exists(id: EntityId): Promise<boolean> {
    const entity = await this.findById(id);
    return entity !== null;
  }

  protected createQueryBuilder(): QueryBuilder<T> {
    return new InMemoryQueryBuilder<T>(this);
  }

  protected generateId(): string {
    return `entity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

// In-Memory Query Builder Implementation
class InMemoryQueryBuilder<T extends BaseEntity> implements QueryBuilder<T> {
  private conditions: Array<{ field: string; operator: QueryOperator; value: unknown; logic: 'AND' | 'OR' }> = [];
  private orderByField?: string;
  private orderByDirection: 'ASC' | 'DESC' = 'ASC';
  private limitCount?: number;
  private offsetCount?: number;

  constructor(private repository: BaseRepository<T>) {}

  where(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T> {
    this.conditions.push({ field, operator, value, logic: 'AND' });
    return this;
  }

  andWhere(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T> {
    this.conditions.push({ field, operator, value, logic: 'AND' });
    return this;
  }

  orWhere(field: string, operator: QueryOperator, value: unknown): QueryBuilder<T> {
    this.conditions.push({ field, operator, value, logic: 'OR' });
    return this;
  }

  orderBy(field: string, direction: 'ASC' | 'DESC'): QueryBuilder<T> {
    this.orderByField = field;
    this.orderByDirection = direction;
    return this;
  }

  limit(count: number): QueryBuilder<T> {
    this.limitCount = count;
    return this;
  }

  offset(count: number): QueryBuilder<T> {
    this.offsetCount = count;
    return this;
  }

  async execute(): Promise<T[]> {
    const allEntities = await this.repository.findAll();
    let filteredEntities = this.applyConditions(allEntities);
    
    if (this.orderByField) {
      filteredEntities = this.applySorting(filteredEntities);
    }
    
    if (this.offsetCount) {
      filteredEntities = filteredEntities.slice(this.offsetCount);
    }
    
    if (this.limitCount) {
      filteredEntities = filteredEntities.slice(0, this.limitCount);
    }
    
    return filteredEntities;
  }

  async count(): Promise<number> {
    const allEntities = await this.repository.findAll();
    const filteredEntities = this.applyConditions(allEntities);
    return filteredEntities.length;
  }

  private applyConditions(entities: T[]): T[] {
    if (this.conditions.length === 0) {
      return entities;
    }

    return entities.filter(entity => {
      let result = true;
      let currentLogic: 'AND' | 'OR' = 'AND';

      for (const condition of this.conditions) {
        const conditionResult = this.evaluateCondition(entity, condition);
        
        if (condition.logic === 'AND') {
          result = result && conditionResult;
        } else {
          result = result || conditionResult;
        }
        
        currentLogic = condition.logic;
      }

      return result;
    });
  }

  private evaluateCondition(entity: T, condition: { field: string; operator: QueryOperator; value: unknown }): boolean {
    const fieldValue = this.getFieldValue(entity, condition.field);
    
    switch (condition.operator) {
      case 'equals':
        return fieldValue === condition.value;
      case 'notEquals':
        return fieldValue !== condition.value;
      case 'greaterThan':
        return (fieldValue as number) > (condition.value as number);
      case 'greaterThanOrEqual':
        return (fieldValue as number) >= (condition.value as number);
      case 'lessThan':
        return (fieldValue as number) < (condition.value as number);
      case 'lessThanOrEqual':
        return (fieldValue as number) <= (condition.value as number);
      case 'like':
        return (fieldValue as string)?.toLowerCase().includes((condition.value as string)?.toLowerCase());
      case 'notLike':
        return !(fieldValue as string)?.toLowerCase().includes((condition.value as string)?.toLowerCase());
      case 'in':
        return Array.isArray(condition.value) && condition.value.includes(fieldValue);
      case 'notIn':
        return Array.isArray(condition.value) && !condition.value.includes(fieldValue);
      case 'isNull':
        return fieldValue === null || fieldValue === undefined;
      case 'isNotNull':
        return fieldValue !== null && fieldValue !== undefined;
      case 'between':
        if (!Array.isArray(condition.value) || condition.value.length !== 2) return false;
        return (fieldValue as number) >= (condition.value[0] as number) && 
               (fieldValue as number) <= (condition.value[1] as number);
      case 'notBetween':
        if (!Array.isArray(condition.value) || condition.value.length !== 2) return true;
        return (fieldValue as number) < (condition.value[0] as number) || 
               (fieldValue as number) > (condition.value[1] as number);
      default:
        return false;
    }
  }

  private getFieldValue(entity: T, field: string): unknown {
    const keys = field.split('.');
    let value: any = entity;
    
    for (const key of keys) {
      value = value?.[key];
    }
    
    return value;
  }

  private applySorting(entities: T[]): T[] {
    if (!this.orderByField) return entities;

    return entities.sort((a, b) => {
      const aValue = this.getFieldValue(a, this.orderByField!);
      const bValue = this.getFieldValue(b, this.orderByField!);

      if (aValue === bValue) return 0;
      
      const comparison = (aValue as any) < (bValue as any) ? -1 : 1;
      return this.orderByDirection === 'ASC' ? comparison : -comparison;
    });
  }
}
