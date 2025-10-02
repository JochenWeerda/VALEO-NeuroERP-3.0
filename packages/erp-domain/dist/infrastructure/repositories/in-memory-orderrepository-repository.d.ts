/**
 * VALEO NeuroERP 3.0 - In-Memory OrderRepository Repository
 *
 * In-memory implementation of OrderRepository repository for testing.
 * Stores data in memory with no persistence.
 */
export type OrderRepositoryId = string;
export interface OrderRepository {
    id: OrderRepositoryId;
    name: string;
    status?: string;
}
import { OrderRepositoryRepository } from './orderrepository-repository';
export declare class InMemoryOrderRepositoryRepository implements OrderRepositoryRepository {
    private storage;
    findById(id: OrderRepositoryId): Promise<OrderRepository | null>;
    findAll(): Promise<OrderRepository[]>;
    create(entity: OrderRepository): Promise<void>;
    update(id: OrderRepositoryId, entity: OrderRepository): Promise<void>;
    delete(id: OrderRepositoryId): Promise<void>;
    exists(id: OrderRepositoryId): Promise<boolean>;
    count(): Promise<number>;
    findByName(value: string): Promise<OrderRepository[]>;
    findByStatus(value: string): Promise<OrderRepository[]>;
    clear(): void;
    seed(data: OrderRepository[]): void;
}
//# sourceMappingURL=in-memory-orderrepository-repository.d.ts.map