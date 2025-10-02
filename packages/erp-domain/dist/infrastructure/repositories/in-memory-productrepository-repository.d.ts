/**
 * VALEO NeuroERP 3.0 - In-Memory ProductRepository Repository
 *
 * In-memory implementation of ProductRepository repository for testing.
 * Stores data in memory with no persistence.
 */
export type ProductRepositoryId = string;
export interface ProductRepository {
    id: ProductRepositoryId;
    name: string;
    status?: string;
}
import { ProductRepositoryRepository } from './productrepository-repository';
export declare class InMemoryProductRepositoryRepository implements ProductRepositoryRepository {
    private storage;
    findById(id: ProductRepositoryId): Promise<ProductRepository | null>;
    findAll(): Promise<ProductRepository[]>;
    create(entity: ProductRepository): Promise<void>;
    update(id: ProductRepositoryId, entity: ProductRepository): Promise<void>;
    delete(id: ProductRepositoryId): Promise<void>;
    exists(id: ProductRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<ProductRepository[]>;
    findByStatus(value: string): Promise<ProductRepository[]>;
    clear(): void;
    seed(data: ProductRepository[]): void;
}
//# sourceMappingURL=in-memory-productrepository-repository.d.ts.map