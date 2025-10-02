/**
 * VALEO NeuroERP 3.0 - Postgres ProductRepository Repository
 *
 * PostgreSQL implementation of ProductRepository repository.
 * Handles database operations with proper error handling and transactions.
 */
export type ProductRepositoryId = string;
export interface ProductRepository {
    id: ProductRepositoryId;
    name: string;
    status?: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface PostgresConnection {
    query(query: string, params?: any[]): Promise<any>;
}
import { ProductRepositoryRepository } from './productrepository-repository';
export declare class PostgresProductRepositoryRepository implements ProductRepositoryRepository {
    private db;
    constructor(db: PostgresConnection);
    findById(id: ProductRepositoryId): Promise<ProductRepository | null>;
    findAll(): Promise<ProductRepository[]>;
    create(entity: ProductRepository): Promise<void>;
    update(id: ProductRepositoryId, entity: ProductRepository): Promise<void>;
    delete(id: ProductRepositoryId): Promise<void>;
    exists(id: ProductRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<ProductRepository[]>;
    findByStatus(value: string): Promise<ProductRepository[]>;
    private mapRowToEntity;
}
//# sourceMappingURL=postgres-productrepository-repository.d.ts.map