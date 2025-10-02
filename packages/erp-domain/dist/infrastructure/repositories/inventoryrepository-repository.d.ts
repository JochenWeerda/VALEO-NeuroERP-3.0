/**
 * VALEO NeuroERP 3.0 - InventoryRepository Repository Interface
 *
 * Defines the contract for InventoryRepository data access operations.
 * Follows Repository pattern for clean data access abstraction.
 */
export type InventoryRepositoryId = string;
export interface InventoryRepository {
    id: InventoryRepositoryId;
    name: string;
    status?: string;
}
export interface InventoryRepositoryRepository {
    findById(id: InventoryRepositoryId): Promise<InventoryRepository | null>;
    findAll(): Promise<InventoryRepository[]>;
    create(entity: InventoryRepository): Promise<void>;
    update(id: InventoryRepositoryId, entity: InventoryRepository): Promise<void>;
    delete(id: InventoryRepositoryId): Promise<void>;
    exists(id: InventoryRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<InventoryRepository[]>;
    findByStatus(value: string): Promise<InventoryRepository[]>;
}
//# sourceMappingURL=inventoryrepository-repository.d.ts.map