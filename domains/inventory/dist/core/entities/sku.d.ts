/**
 * VALEO NeuroERP 3.0 - SKU Entity
 *
 * Represents a Stock Keeping Unit with GS1 compliance and WMS attributes
 */
export interface SkuAttributes {
    sku: string;
    gtin?: string;
    description: string;
    category: string;
    uom: string;
    weight?: number;
    volume?: number;
    dimensions?: {
        length: number;
        width: number;
        height: number;
    };
    tempZone: 'frozen' | 'refrigerated' | 'ambient' | 'heated';
    hazmat: boolean;
    hazmatClass?: string;
    abcClass: 'A' | 'B' | 'C';
    velocityClass: 'X' | 'Y' | 'Z';
    minOrderQty?: number;
    maxOrderQty?: number;
    reorderPoint?: number;
    safetyStock?: number;
    shelfLifeDays?: number;
    serialTracked: boolean;
    lotTracked: boolean;
    active: boolean;
    createdAt: Date;
    updatedAt: Date;
}
export declare class Sku {
    private _attributes;
    constructor(attributes: Omit<SkuAttributes, 'createdAt' | 'updatedAt'>);
    get sku(): string;
    get gtin(): string | undefined;
    get description(): string;
    get category(): string;
    get uom(): string;
    get tempZone(): string;
    get hazmat(): boolean;
    get abcClass(): string;
    get velocityClass(): string;
    get serialTracked(): boolean;
    get lotTracked(): boolean;
    get active(): boolean;
    get attributes(): SkuAttributes;
    isPerishable(): boolean;
    isHighValue(): boolean;
    isFastMoving(): boolean;
    requiresSpecialHandling(): boolean;
    canExpire(expiryDate: Date): boolean;
    update(attributes: Partial<Omit<SkuAttributes, 'sku' | 'createdAt'>>): void;
    deactivate(): void;
    activate(): void;
    private validate;
    private isValidGtin;
    static create(attributes: Omit<SkuAttributes, 'createdAt' | 'updatedAt'>): Sku;
    static fromAttributes(attributes: SkuAttributes): Sku;
}
//# sourceMappingURL=sku.d.ts.map