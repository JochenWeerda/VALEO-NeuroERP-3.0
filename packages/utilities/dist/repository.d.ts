import { QueryBuilder, QueryDescriptor } from './query-builder';
export type RepositoryQuery<TEntity> = QueryDescriptor<TEntity>;
export interface Repository<TEntity, TId> {
    findById(id: TId): Promise<TEntity | null>;
    findOne(query: RepositoryQuery<TEntity>): Promise<TEntity | null>;
    findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]>;
    create(entity: TEntity): Promise<TEntity>;
    update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
    delete(id: TId): Promise<void>;
}
export declare abstract class RepositoryBase<TEntity, TId> implements Repository<TEntity, TId> {
    findOne(query: RepositoryQuery<TEntity>): Promise<TEntity | null>;
    abstract findById(id: TId): Promise<TEntity | null>;
    abstract findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]>;
    abstract create(entity: TEntity): Promise<TEntity>;
    abstract update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
    abstract delete(id: TId): Promise<void>;
}
export declare class InMemoryRepository<TEntity extends Record<IdField, TId>, IdField extends keyof TEntity, TId = TEntity[IdField]> extends RepositoryBase<TEntity, TId> {
    private readonly idField;
    private readonly entities;
    constructor(idField: IdField);
    findById(id: TId): Promise<TEntity | null>;
    findMany(query?: RepositoryQuery<TEntity>): Promise<TEntity[]>;
    create(entity: TEntity): Promise<TEntity>;
    update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
    delete(id: TId): Promise<void>;
}
export declare const createQuery: <TEntity>(configure: (builder: QueryBuilder<TEntity>) => QueryBuilder<TEntity>) => RepositoryQuery<TEntity>;
//# sourceMappingURL=repository.d.ts.map