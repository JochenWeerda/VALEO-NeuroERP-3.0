/**
 * VALEO NeuroERP 3.0 - ProductRepository Repository Interface
 *
 * Defines the contract for ProductRepository data access operations.
 * Follows Repository pattern for clean data access abstraction.
 */
import { ProductRepository } from '../../core/entities/productrepository';
import { ProductRepositoryId } from '@valero-neuroerp/data-models/branded-types';
export interface ProductRepositoryRepository {
    findById(id: ProductRepositoryId): Promise<ProductRepository | null>;
    findAll(): Promise<ProductRepository[]>;
    create(entity: ProductRepository): Promise<void>;
    update(id: ProductRepositoryId, entity: ProductRepository): Promise<void>;
    delete(id: ProductRepositoryId): Promise<void>;
    exists(id: ProductRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<ProductRepository[]>;
    findByStatus(value: string): Promise<ProductRepository[]>;
}
//# sourceMappingURL=productrepository-repository.d.ts.map