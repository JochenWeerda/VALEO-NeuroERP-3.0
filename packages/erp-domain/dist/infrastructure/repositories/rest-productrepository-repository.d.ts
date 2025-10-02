/**
 * VALEO NeuroERP 3.0 - REST ProductRepository Repository
 *
 * REST API implementation of ProductRepository repository.
 * Bridges to legacy VALEO-NeuroERP-2.0 APIs during migration.
 */
import { ProductRepository } from '../../core/entities/productrepository';
import { ProductRepositoryId } from '@valero-neuroerp/data-models/branded-types';
import { ProductRepositoryRepository } from './productrepository-repository';
export declare class RestProductRepositoryRepository implements ProductRepositoryRepository {
    private baseUrl;
    private apiToken?;
    constructor(baseUrl: string, apiToken?: string | undefined);
    private request;
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
//# sourceMappingURL=rest-productrepository-repository.d.ts.map