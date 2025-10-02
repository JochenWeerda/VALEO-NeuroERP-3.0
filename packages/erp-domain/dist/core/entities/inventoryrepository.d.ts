import { Brand } from '@valero-neuroerp/data-models';
export type InventoryRepositoryId = Brand<string, 'InventoryRepositoryId'>;
export interface InventoryRepositoryProps {
    id: InventoryRepositoryId;
    name: string;
    description?: string;
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface InventoryRepository extends InventoryRepositoryProps {
    toPrimitives(): InventoryRepositoryProps;
}
export declare class InventoryRepositoryEntity implements InventoryRepository {
    readonly id: InventoryRepositoryId;
    readonly name: string;
    readonly description?: string;
    readonly isActive: boolean;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(props: InventoryRepositoryProps);
    toPrimitives(): InventoryRepositoryProps;
    static create(props: Omit<InventoryRepositoryProps, 'id' | 'createdAt' | 'updatedAt'>): InventoryRepositoryEntity;
}
export type CreateInventoryRepositoryInput = Omit<InventoryRepositoryProps, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateInventoryRepositoryInput = Partial<CreateInventoryRepositoryInput>;
//# sourceMappingURL=inventoryrepository.d.ts.map