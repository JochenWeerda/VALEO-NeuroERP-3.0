/**
 * Query builder utilities supporting the 5-Principles architecture.
 *
 * The builder is intentionally persistence-agnostic so it can be consumed
 * by in-memory, SQL, NoSQL or remote repositories without leaking
 * implementation details into the domain layer.
 */
export type ComparisonOperator = 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'notIn' | 'like' | 'ilike' | 'between';
export type SortDirection = 'asc' | 'desc';
export type QueryValue<Value> = Value | Value[] | readonly Value[] | [Value, Value] | readonly [Value, Value];
export interface QueryCondition<TEntity> {
    field: keyof TEntity;
    operator: ComparisonOperator;
    value: QueryValue<TEntity[keyof TEntity]>;
}
export interface QuerySort<TEntity> {
    field: keyof TEntity;
    direction: SortDirection;
}
export interface QueryDescriptor<TEntity> {
    conditions: QueryCondition<TEntity>[];
    sort?: QuerySort<TEntity>;
    limit?: number;
    offset?: number;
}
export declare class QueryBuilder<TEntity> {
    private readonly conditions;
    private sort;
    private limitValue;
    private offsetValue;
    where<Field extends keyof TEntity>(field: Field, operator: ComparisonOperator, value: QueryValue<TEntity[Field]>): this;
    orderBy<Field extends keyof TEntity>(field: Field, direction?: SortDirection): this;
    limit(count: number): this;
    offset(count: number): this;
    clear(): this;
    build(): QueryDescriptor<TEntity>;
}
export declare const createQueryBuilder: <TEntity>() => QueryBuilder<TEntity>;
//***REMOVED*** sourceMappingURL=query-builder.d.ts.map