/**
 * VALEO NeuroERP 3.0 - REST InventoryRepository Repository
 *
 * REST API implementation of InventoryRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
import { InventoryRepository } from '../../core/entities/inventoryrepository';
import { InventoryRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { InventoryRepositoryRepository } from './inventoryrepository-repository';
export declare class RestInventoryRepositoryRepository implements InventoryRepositoryRepository {
    private baseUrl;
    private apiToken?;
    constructor(baseUrl: string, apiToken?: string | undefined);
    private request;
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
//# sourceMappingURL=rest-inventoryrepository-repository.d.ts.map