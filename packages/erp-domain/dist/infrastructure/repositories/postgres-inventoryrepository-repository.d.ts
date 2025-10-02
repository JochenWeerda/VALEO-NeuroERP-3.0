/**
 * VALEO NeuroERP 3.0 - Postgres InventoryRepository Repository
 *
 * PostgreSQL implementation of InventoryRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
export type InventoryRepositoryId = string;
export interface InventoryRepository {
    id: InventoryRepositoryId;
    name: string;
    status?: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface PostgresConnection {
    query(query: string, params?: any[]): Promise<any>;
}
import { InventoryRepositoryRepository } from './inventoryrepository-repository';
export declare class PostgresInventoryRepositoryRepository implements InventoryRepositoryRepository {
    private db;
    constructor(db: PostgresConnection);
    findById(id: InventoryRepositoryId): Promise<InventoryRepository | null>;
    findAll(): Promise<InventoryRepository[]>;
    create(entity: InventoryRepository): Promise<void>;
    update(id: InventoryRepositoryId, entity: InventoryRepository): Promise<void>;
    delete(id: InventoryRepositoryId): Promise<void>;
    exists(id: InventoryRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<InventoryRepository[]>;
    findByStatus(value: string): Promise<InventoryRepository[]>;
    private mapRowToEntity;
}
//# sourceMappingURL=postgres-inventoryrepository-repository.d.ts.map