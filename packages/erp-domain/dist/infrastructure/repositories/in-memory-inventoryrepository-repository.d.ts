/**
 * VALEO NeuroERP 3.0 - In-Memory InventoryRepository Repository
 *
 * In-memory implementation of InventoryRepository repository for testing.
 * Stores data in memory with no persistence.
 */
export type InventoryRepositoryId = string;
export interface InventoryRepository {
    id: InventoryRepositoryId;
    name: string;
    status?: string;
}
import { InventoryRepositoryRepository } from './inventoryrepository-repository';
export declare class InMemoryInventoryRepositoryRepository implements InventoryRepositoryRepository {
    private storage;
    findById(id: InventoryRepositoryId): Promise<InventoryRepository | null>;
    findAll(): Promise<InventoryRepository[]>;
    create(entity: InventoryRepository): Promise<void>;
    update(id: InventoryRepositoryId, entity: InventoryRepository): Promise<void>;
    delete(id: InventoryRepositoryId): Promise<void>;
    exists(id: InventoryRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<InventoryRepository[]>;
    findByStatus(value: string): Promise<InventoryRepository[]>;
    clear(): void;
    seed(data: InventoryRepository[]): void;
}
//# sourceMappingURL=in-memory-inventoryrepository-repository.d.ts.map