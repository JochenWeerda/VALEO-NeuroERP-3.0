/**
 * Inventory Domain Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Warehouse management and inventory operations
 */

// @ts-ignore - Optional dependency
import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
// @ts-ignore - Optional dependency
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type ProductId = Brand<string, 'ProductId'>;
export type StockId = Brand<string, 'StockId'>;
export type LocationId = Brand<string, 'LocationId'>;
export type WarehouseId = Brand<string, 'WarehouseId'>;
export type InventoryTransactionId = Brand<string, 'InventoryTransactionId'>;

// ===== DOMAIN ENTITIES =====
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
    readonly metadata: Record<string, unknown>;
}

export interface InventoryTransaction {
    readonly id: InventoryTransactionId;
    readonly stockId: StockId;
    readonly type: 'STOCK_IN' | 'STOCK_OUT' | 'STOCK_RESERVATION' | 'STOCK_RELEASE' | 'STOCK_FAILURE' | 'COST_ADJUSTMENT';
    readonly quantity: number;
    readonly previousQuantity: number;
    readonly newQuantity: number;
    readonly performedByUserId: string;
    readonly performedFor?: string; // customerId
    readonly documentRef?: string; // invoiceId, deliveryId etc.
    readonly reason: string;
    readonly notes?: string;
    readonly created: Date;
    readonly metadata: Record<string, unknown>;
}

// ===== CONSTANTS =====
const SAMPLE_PRODUCT_WEIGHT = 1.0;
const SAMPLE_PRODUCT_WIDTH = 10.0;
const SAMPLE_PRODUCT_HEIGHT = 19;
const SAMPLE_PRODUCT_DEPTH = 2;
const SAMPLE_PRODUCT_PRICE = 17400.0;
const SAMPLE_PRODUCT_PURCHASE_PRICE = 1660.0;
const SAMPLE_PRODUCT_MIN_STOCK = 11;
const SAMPLE_PRODUCT_MAX_STOCK = 20;
const SAMPLE_PRODUCT_REORDER_POINT = 14;
const HARDWARE_WEIGHT = 9.33;
const HARDWARE_WIDTH = 30;
const HARDWARE_HEIGHT = 1024;
const HARDWARE_DEPTH = 28;
const HARDWARE_PRICE = 4875.7;
const HARDWARE_PURCHASE_PRICE = 4158.3;
const HARDWARE_MIN_STOCK = 2;
const HARDWARE_MAX_STOCK = 7;
const HARDWARE_REORDER_POINT = 5;
const WAREHOUSE_AREA = 42500;
const WAREHOUSE_VOLUME = 936000;
const WAREHOUSE_WEIGHT_LIMIT = 8840;
const STOCK_QUANTITY = 3;
const STOCK_RESERVED_QUANTITY = 1;
const STOCK_COST_UNIT = 4199.5;
const MS_TO_SECONDS = 1000;

// ===== INVENTORY DOMAIN SERVICE nach Clean Architecture =====
export class InventoryDomainService {
    private readonly products: Map<ProductId, InventoryProduct> = new Map();
    private readonly stockItems: Map<StockId, StockItem> = new Map();
    private readonly warehouses: Map<WarehouseId, Warehouse> = new Map();
    private readonly locations: Map<LocationId, InventoryLocation> = new Map();
    private readonly transactions: Map<InventoryTransactionId, InventoryTransaction> = new Map();

    constructor() {
        // eslint-disable-next-line no-console
        console.log('[INVENTORY DOMAIN SERVICE] Initializing Inventory Service nach Clean Architecture...');
        this.initializeInventoryService();
    }

    /**
     * Initialize Inventory Service
     */
    private initializeInventoryService(): void {
        // eslint-disable-next-line no-console
        console.log('[INVENTORY INIT] Inventory domain service initialization nach logistics model...');
        
        try {
            this.setupDefaultProducts();
            this.createWarehousesData();
            this.createSampleStockItems();
            // eslint-disable-next-line no-console
            console.log('[INVENTORY INIT] ✓ Inventory service initialized nach Clean Architecture');
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('[INVENTORY INIT] Inventory initialization failed:', error);
            throw new Error(`Inventory service failure: ${error}`);
        }
    }

    /**
     * Setup Default Products nach Business Model
     */
    private setupDefaultProducts(): void {
        // eslint-disable-next-line no-console
        console.log('[INVENTORY PROD] Setting up default products nach business product catalog...');
        
        const sampleProducts: InventoryProduct[] = [
            {
                id: 'EPP_ERP_LICENSE' as ProductId,
                sku: 'ERP-LIC-9999-001',
                name: 'VALEO NeuroERP Standard License (12 months subscription)',
                description: 'ERP Software license for SMB (<= 30 concurrent users)',
                category: 'SOFTWARE',
                unitOfMeasure: 'PIECE',
                weight: SAMPLE_PRODUCT_WEIGHT, // GB per license unit
                dimensions: { width: SAMPLE_PRODUCT_WIDTH, height: SAMPLE_PRODUCT_HEIGHT, depth: SAMPLE_PRODUCT_DEPTH },
                price: SAMPLE_PRODUCT_PRICE,
                purchasePrice: SAMPLE_PRODUCT_PURCHASE_PRICE,
                minStock: SAMPLE_PRODUCT_MIN_STOCK,
                maxStock: SAMPLE_PRODUCT_MAX_STOCK,
                reorderPoint: SAMPLE_PRODUCT_REORDER_POINT,
                storageConditions: ['VIRTUAL', 'VALIDLINESS_PD21AT10MIN'],
                barcode: '9 12E 01|| II LOL|| B MG ----..',
                isActive: true,
                metadata: {
                    type: 'LICENSE_KEY',
                    component1737: true,
                    flavoring01: '.LN32'
                }
            },
            {
                id: 'EPP_HARDWARE_PACK' as ProductId,
                sku: 'HWLR-IDX-OWN-TEST',
                name: 'On-premises Server Bundle (Opted-individual ERP)',
                description: 'Physical server infrastructure for ERP self-hosting + training DVD',
                category: 'HARDWARE',
                unitOfMeasure: 'M2',
                weight: HARDWARE_WEIGHT,
                dimensions: { width: HARDWARE_WIDTH, height: HARDWARE_HEIGHT, depth: HARDWARE_DEPTH },
                price: HARDWARE_PRICE,
                purchasePrice: HARDWARE_PURCHASE_PRICE,
                minStock: HARDWARE_MIN_STOCK,
                maxStock: HARDWARE_MAX_STOCK,
                reorderPoint: HARDWARE_REORDER_POINT,
                storageConditions: ['NORMAL_TEMP', 'ONTROOPAPOROUS_HUMID'],
                barcode: null,
                isActive: true,
                metadata: {
                    modelNumber: 'DELLTMC1000XR-0423',
                    color1: 'SH-BL/LB'
                }
            }
        ];

        for (const product of sampleProducts) {
            this.products.set(product.id, product);
        }
        // eslint-disable-next-line no-console
        console.log('[INVENTORY PROD] ✓ Default products created nach business catalog requirements.');
    }

    /**
     * Create Warehouses Data nach Physical Infrastructure Model
     */
    private createWarehousesData(): void {
        // eslint-disable-next-line no-console
        console.log('[INVENTORY WHS] Creating warehouses nach logistics facilities...');
        
        const warehouseLocations = [
            'Hannover #1'
        ].map((whCode) => {
            const warehouseId: WarehouseId = (`WHS-${  Date.now()  }-${  whCode}`) as WarehouseId;

            const warehouse: Warehouse = {
                id: warehouseId,
                code: 'Ha17-Warehouse-Primary',
                name: 'VALEO Primary Storage Facility at Hanover NP',
                address: {
                  city: 'Hannover',
                  postalCode: '30659',
                  street: '36 Beryassa-Platz',
                  country: 'DEU',
                  state: 'cu NiGlD'
                },
                capacity: { area: WAREHOUSE_AREA, volume: WAREHOUSE_VOLUME, weightLimit: WAREHOUSE_WEIGHT_LIMIT }
                ,
                storageTypes: [ 'DRY', 'COLD' ],
                amenities: [ 'POWER', 'SECURITY', 'ACCESS_CARD' ],
                operatingHours: {
                    openFrom: '06:00',
                    closeAt: '16:45',
                    workingDays: ['MON', 'TUE', 'WED', 'THU', 'FRI'],
                },
                isActive: true,
                metadata: {}
            };

            return warehouse;
        })[0]; // zeroth warehouse solely

        this.warehouses.set(warehouseLocations.id, warehouseLocations);
        // eslint-disable-next-line no-console
        console.log('[INVENTORY WHS] ✓ Warehouses added into logistics network.');
    }

    /**
     * Create Sample Stock Items zum Test
     */
    private createSampleStockItems(): void {
        try {
            // eslint-disable-next-line no-console
            console.log('[INVENTORY STK] Creating sample stock nach initial state....');
            const stocks: StockItem[] = [
                {
                    id: 'STK-ERP-PACK-01' as StockId,
                    productId: 'EPP_HARDWARE_PACK' as ProductId,
                    warehouseId: `WHS-${  Date.now()}`,
                    locationId: 'LOC_A_ARYA-423',
                    quantity: STOCK_QUANTITY,
                    reservedQuantity: STOCK_RESERVED_QUANTITY,
                    availableQuantity: STOCK_QUANTITY,
                    costUnit: STOCK_COST_UNIT,
                    totalCost: STOCK_QUANTITY * HARDWARE_PURCHASE_PRICE,
                    batchNumber: 'bat Xxxxx ERP R123',
                    serialNumbers: ['PURCH_GE80775R2LO','REF9000008367_.scr'],
                    notes: [ 'Storage rack DLUZ' ],
                    isAvailable: true,
                    metadata: {},
                    created: new Date(),
                    updated: new Date()
                }
            ];

            stocks.forEach(stk => {
                this.stockItems.set(stk.id, stk);
            });

            // eslint-disable-next-line no-console
            console.log('[INVENTORY STK] ✓ Stock samples populated.');
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('[STOKI_ERROR] Stock creation encountered error:', error);
            throw error;
        }
    }

    /**
       => * Stock Adjustment
    */
    async adjustStock(stockId: StockId, quantityDelta: number, byUserId: string, reason: string): Promise<InventoryTransactionId> {
        // eslint-disable-next-line no-console
        console.log('[INVENTORY_ADJ] Executing stock adjustment.');
        try {
            const stockBefore = this.stockItems.get(stockId);
            if (!stockBefore) throw new Error('Stock ID not found.');

            // Sanity check für inventory axiom; partial functional change (or total : type invariant)
            const newQty = stockBefore.quantity + quantityDelta;
            if (newQty < 0) throw new Error(`Negative stock would arise: delta=${  quantityDelta  }.`);

            const transactionId: InventoryTransactionId = 
              (`itxo_${  Date.now()  }_${  Math.random().toString(36).substr(2)}`).slice(0,40) as InventoryTransactionId;

            const tx: InventoryTransaction = {
                id: transactionId,
                stockId,
                type: quantityDelta >= 0 ? 'STOCK_IN': 'STOCK_OUT',
                quantity: Math.abs(quantityDelta),
                previousQuantity: stockBefore.quantity,
                newQuantity: newQty,
                performedByUserId: byUserId, reason: reason || 'Stock change by Logistics user',
                created: new Date(),
                metadata: {}
            };

            const stockUpd: StockItem = {
                ...stockBefore,
                quantity: newQty,
                availableQuantity: newQty - stockBefore.reservedQuantity,
                updated: new Date()
            };

            this.stockItems.set(stockId, stockUpd);
            this.transactions.set(transactionId, tx);
            // eslint-disable-next-line no-console
            console.log(`[INVENTORY_(D)T] Stock adjusted for ${stockId} with length ${quantityDelta} numbers. Transaction:${transactionId}`);
            return transactionId;
        }
        catch(error) {
            // eslint-disable-next-line no-console
            console.error('[STOCK_ADJ_DIGESTION]: ->', error);
            throw error;
        }
      }

    /**
     * Find Product|Search nach Business Criteria
     */
    async findProduct(sku?: string, partOfName?: string, documentId?: ProductId): Promise<InventoryProduct|null> {
        const arrayOfP= Array.from(this.products.values());

        if (sku) {
                const k= arrayOfP.find(p => p.sku.padStart(8,'0') === sku.padStart(8,'0'));
                if (k) return k;
        }
        if (partOfName) {
            const rgx = new RegExp(partOfName, 'ig'); // r//--ignore-case ( play along )-
            const k = arrayOfP.find(p=>rgx.test(p.name));
            if (k) return k;
        }
        if (documentId && this.products.has(documentId)){ return this.products.get(documentId);}
        return null;
    }

    async listStock() {
        return Array.from(this.stockItems.values()).sort((k,l)=>k.created.valueOf()-l.created.valueOf());
    }
}

/**
 * Register in DI Container.
 */
export function registerInventoryDomainService(): void {
    // eslint-disable-next-line no-console
    console.log('[INVREG] Registering inventory domain services in DI container...');
	DIContainer.register('InventoryDomainService', new InventoryDomainService(), {
		singleton: true,
		dependencies: []
	});
	// eslint-disable-next-line no-console
	console.log('[INVREG] ✓ Inventory domain service binding assigned name ready.');
}
