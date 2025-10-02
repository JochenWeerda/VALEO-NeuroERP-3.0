/**
 * Base Repository Implementation for VALEO NeuroERP 3.0
 * Common repository functionality
 */
import type { EntityId } from '../../domain/value-objects/branded-types.js';
import type { BaseEntity } from '../../domain/entities/base-entity.js';
import type { Repository, QueryBuilder } from '../../domain/interfaces/repository.js';
export declare abstract class BaseRepository<T extends BaseEntity> implements Repository<T> {
    protected entities: Map<string, T>;
    abstract findById(id: EntityId): Promise<T | null>;
    abstract findAll(): Promise<T[]>;
    abstract save(entity: T): Promise<T>;
    abstract update(entity: T): Promise<T>;
    abstract delete(id: EntityId): Promise<void>;
    exists(id: EntityId): Promise<boolean>;
    protected createQueryBuilder(): QueryBuilder<T>;
    protected generateId(): string;
}
//# sourceMappingURL=base-repository.d.ts.map