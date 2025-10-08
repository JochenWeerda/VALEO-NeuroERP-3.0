/**
 * Inventory Domain Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Warehouse management and inventory operations
 */
type Brand<K, T> = K & {
    __brand: T;
};
export type ProductId = Brand<string, 'ProductId'>;
export type StockId = Brand<string, 'StockId'>;
export type LocationId = Brand<string, 'LocationId'>;
export type WarehouseId = Brand<string, 'WarehouseId'>;
export type InventoryTransactionId = Brand<string, 'InventoryTransactionId'>;
export interface InventoryProduct {
    readonly id: ProductId;
    readonly sku: string;
    readonly name: string;
    readonly description: string;
    readonly category: string;
    readonly unitOfMeasure: 'PIECE' | 'KG' | 'L' | 'M' | 'M2' | 'M3';
    readonly weight: number;
    readonly dimensions: {
        width: number;
        height: number;
        depth: number;
    };
    readonly price: number;
    readonly purchasePrice: number;
    readonly minStock: number;
    readonly maxStock: number;
    readonly reorderPoint: number;
    readonly storageConditions: string[];
    readonly barcode?: string;
    readonly isActive: boolean;
    readonly metadata: Record<string, any>;
}
export interface StockItem {
    readonly id: StockId;
    readonly productId: ProductId;
    readonly warehouseId: WarehouseId;
    readonly locationId: LocationId;
    readonly quantity: number;
    readonly reservedQuantity: number;
    readonly availableQuantity: number;
    readonly costUnit: number;
    readonly totalCost: number;
    readonly batchNumber?: string;
    readonly expiryDate?: Date;
    readonly serialNumbers: string[];
    readonly notes: string[];
    readonly isAvailable: boolean;
    readonly metadata: Record<string, any>;
    readonly created: Date;
    readonly updated: Date;
}
export interface Warehouse {
    readonly id: WarehouseId;
    readonly code: string;
    readonly name: string;
    readonly address: Location;
    readonly capacity: {
        area: number;
        volume: number;
        weightLimit: number;
    };
    readonly storageTypes: ('DRY' | 'COLD' | 'FROZEN' | 'DANGEROUS')[];
    readonly amenities: string[];
    readonly operatingHours: {
        openFrom: string;
        closeAt: string;
        workingDays: string[];
    };
    readonly metadata: Record<string, any>;
    readonly isActive: boolean;
}
export interface Location {
    readonly street: string;
    readonly postalCode: string;
    readonly city: string;
    readonly state?: string;
    readonly country: string;
    readonly longitude?: number;
    readonly latitude?: number;
}
export interface InventoryLocation {
    readonly id: LocationId;
    readonly code: string;
    readonly name: string;
    readonly warehouseId: WarehouseId;
    readonly zone: string;
    readonly aisle: string;
    readonly rack: string;
    readonly position: string;
    readonly storageType: 'ROCK_RACK' | 'DLOVE_BIN' | 'BIN';
    readonly maxWeight: number;
    readonly maxVolume: number;
    readonly occupied?: {
        productIds: ProductId[];
        currentWeight: number;
        currentVolume: number;
    };
    readonly isActive: boolean;
    readonly metadata: Record<string, any>;
}
export interface InventoryTransaction {
    readonly id: InventoryTransactionId;
    readonly stockId: StockId;
    readonly type: 'STOCK_IN' | 'STOCK_OUT' | 'STOCK_RESERVATION' | 'STOCK_RELEASE' | 'STOCK_FAILURE' | 'COST_ADJUSTMENT';
    readonly quantity: number;
    readonly previousQuantity: number;
    readonly newQuantity: number;
    readonly performedByUserId: string;
    readonly performedFor?: string;
    readonly documentRef?: string;
    readonly reason: string;
    readonly notes?: string;
    readonly created: Date;
    readonly metadata: Record<string, any>;
}
export declare class InventoryDomainService {
    private readonly products;
    private readonly stockItems;
    private readonly warehouses;
    private readonly locations;
    private readonly transactions;
    constructor();
    /**
     * Initialize Inventory Service
     */
    private initializeInventoryService;
    /**
     * Setup Default Products nach Business Model
     */
    private setupDefaultProducts;
    /**
     * Create Warehouses Data nach Physical Infrastructure Model
     */
    private createWarehousesData;
    /**
     * Create Sample Stock Items zum Test
     */
    private createSampleStockItems;
    /**
       => * Stock Adjustment
    */
    adjustStock(stockId: StockId, quantityDelta: number, byUserId: string, reason: string): Promise<InventoryTransactionId>;
    /**
     * Find Product|Search nach Business Criteria
     */
    findProduct(sku?: string, partOfName?: string, documentId?: ProductId): Promise<InventoryProduct | null>;
    listStock(): Promise<StockItem[]>;
}
/**
 * Register in DI Container.
 */
export declare function registerInventoryDomainService(): void;
export {};
//# sourceMappingURL=inventory-domain-service.d.ts.map