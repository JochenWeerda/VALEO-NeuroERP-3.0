export type ComparisonOperator = 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'notIn' | 'like' | 'ilike' | 'between';

export type QueryValue<T> = T | T[] | [T, T];

export interface QueryCondition<TEntity> {
  field: keyof TEntity;
  operator: ComparisonOperator;
  value: QueryValue<TEntity[keyof TEntity]>;
}

export interface QuerySort<TEntity> {
  field: keyof TEntity;
  direction: 'asc' | 'desc';
}

export interface QueryDescriptor<TEntity> {
  conditions: QueryCondition<TEntity>[];
  sort?: QuerySort<TEntity>;
  limit?: number;
  offset?: number;
}

export class QueryBuilder<TEntity> {
  private readonly conditions: QueryCondition<TEntity>[] = [];
  private sort?: QuerySort<TEntity>;
  private limit?: number;
  private offset?: number;

  where(field: keyof TEntity, operator: ComparisonOperator, value: QueryValue<TEntity[keyof TEntity]>): this {
    this.conditions.push({ field, operator, value });
    return this;
  }

  orderBy(field: keyof TEntity, direction: 'asc' | 'desc' = 'asc'): this {
    this.sort = { field, direction };
    return this;
  }

  limitCount(count: number): this {
    this.limit = count;
    return this;
  }

  offsetCount(count: number): this {
    this.offset = count;
    return this;
  }

  build(): QueryDescriptor<TEntity> {
    return {
      conditions: this.conditions,
      sort: this.sort,
      limit: this.limit,
      offset: this.offset
    };
  }
}

export const createQueryBuilder = <TEntity>(): QueryBuilder<TEntity> => {
  return new QueryBuilder<TEntity>();
};
