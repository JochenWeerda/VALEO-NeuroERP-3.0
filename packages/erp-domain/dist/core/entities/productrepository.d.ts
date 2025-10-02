import { Brand } from '@valero-neuroerp/data-models';
export type ProductRepositoryId = Brand<string, 'ProductRepositoryId'>;
export interface ProductRepositoryProps {
    id: ProductRepositoryId;
    name: string;
    description?: string;
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export interface ProductRepository extends ProductRepositoryProps {
    toPrimitives(): ProductRepositoryProps;
}
export declare class ProductRepositoryEntity implements ProductRepository {
    readonly id: ProductRepositoryId;
    readonly name: string;
    readonly description?: string;
    readonly isActive: boolean;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(props: ProductRepositoryProps);
    toPrimitives(): ProductRepositoryProps;
    static create(props: Omit<ProductRepositoryProps, 'id' | 'createdAt' | 'updatedAt'>): ProductRepositoryEntity;
}
export type CreateProductRepositoryInput = Omit<ProductRepositoryProps, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateProductRepositoryInput = Partial<CreateProductRepositoryInput>;
//# sourceMappingURL=productrepository.d.ts.map