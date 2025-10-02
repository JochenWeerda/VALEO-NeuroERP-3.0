/**
 * Repository interfaces for CRM Domain
 */
export interface Repository<TEntity, TId> {
    findById(id: TId): Promise<TEntity | null>;
    findOne(query: any): Promise<TEntity | null>;
    findMany(query?: any): Promise<TEntity[]>;
    create(entity: TEntity): Promise<TEntity>;
    update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
    delete(id: TId): Promise<void>;
}
export declare abstract class RepositoryBase<TEntity, TId> implements Repository<TEntity, TId> {
    findOne(query: any): Promise<TEntity | null>;
    abstract findById(id: TId): Promise<TEntity | null>;
    abstract findMany(query?: any): Promise<TEntity[]>;
    abstract create(entity: TEntity): Promise<TEntity>;
    abstract update(id: TId, updates: Partial<TEntity>): Promise<TEntity>;
    abstract delete(id: TId): Promise<void>;
}
export interface Logger {
    debug(message: string, context?: Record<string, unknown>): void;
    info(message: string, context?: Record<string, unknown>): void;
    warn(message: string, context?: Record<string, unknown>): void;
    error(message: string, context?: Record<string, unknown>): void;
}
export interface MetricsRecorder {
    recordCounter(name: string, value?: number, tags?: Record<string, string>): void;
    recordGauge(name: string, value: number, tags?: Record<string, string>): void;
    recordHistogram(name: string, value: number, tags?: Record<string, string>): void;
}
//***REMOVED*** sourceMappingURL=repository.d.ts.map