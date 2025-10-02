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
export declare class QueryBuilder<TEntity> {
    private conditions;
    private sort?;
    private limit?;
    private offset?;
    where(field: keyof TEntity, operator: ComparisonOperator, value: QueryValue<TEntity[keyof TEntity]>): this;
    orderBy(field: keyof TEntity, direction?: 'asc' | 'desc'): this;
    limitCount(count: number): this;
    offsetCount(count: number): this;
    build(): QueryDescriptor<TEntity>;
}
export declare const createQueryBuilder: <TEntity>() => QueryBuilder<TEntity>;
//# sourceMappingURL=query-builder.d.ts.map