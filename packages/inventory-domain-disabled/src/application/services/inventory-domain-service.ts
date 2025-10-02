/**
 * Inventory Domain Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Warehouse management and inventory operations
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
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
    readonly performedFor?: string; // customerId
    readonly documentRef?: string; // invoiceId, deliveryId etc.
    readonly reason: string;
    readonly notes?: string;
    readonly created: Date;
    readonly metadata: Record<string, any>;
}

// ===== INVENTORY DOMAIN SERVICE nach Clean Architecture =====
export class InventoryDomainService {
    private readonly products: Map<ProductId, InventoryProduct> = new Map();
    private readonly stockItems: Map<StockId, StockItem> = new Map();
    private readonly warehouses: Map<WarehouseId, Warehouse> = new Map();
    private readonly locations: Map<LocationId, InventoryLocation> = new Map();
    private readonly transactions: Map<InventoryTransactionId, InventoryTransaction> = new Map();

    constructor() {
        console.log('[INVENTORY DOMAIN SERVICE] Initializing Inventory Service nach Clean Architecture...');
        this.initializeInventoryService();
    }

    /**
     * Initialize Inventory Service
     */
    private initializeInventoryService(): void {
        console.log('[INVENTORY INIT] Inventory domain service initialization nach logistics model...');
        
        try {
            this.setupDefaultProducts();
            this.createWarehousesData();
            this.createSampleStockItems();
            console.log('[INVENTORY INIT] ✓ Inventory service initialized nach Clean Architecture');
        } catch (error) {
            console.error('[INVENTORY INIT] Inventory initialization failed:', error);
            throw new Error(`Inventory service failure: ${error}`);
        }
    }

    /**
     * Setup Default Products nach Business Model
     */
    private setupDefaultProducts(): void {
        console.log('[INVENTORY PROD] Setting up default products nach business product catalog...');
        
        const sampleProducts: InventoryProduct[] = [
            {
                id: 'EPP_ERP_LICENSE' as ProductId,
                sku: 'ERP-LIC-9999-001',
                name: 'VALEO NeuroERP Standard License (12 months subscription)',
                description: 'ERP Software license for SMB (<= 30 concurrent users)',
                category: 'SOFTWARE',
                unitOfMeasure: 'PIECE',
                weight: 1.0, // GB per license unit
                dimensions: { width: 10.0, height: 19, depth: 2 },
                price: 17400.0,
                purchasePrice: 1660.0,
                minStock: 11,
                maxStock: 20,
                reorderPoint: 14,
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
                weight: 9.33,
                dimensions: { width: 30, height:  1024, depth: 28 },
                price: 4875.7,
                purchasePrice: 4158.3,
                minStock: 2,
                maxStock: 7,
                reorderPoint: 5,
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
        console.log('[INVENTORY PROD] ✓ Default products created nach business catalog requirements.');
    }

    /**
     * Create Warehouses Data nach Physical Infrastructure Model
     */
    private createWarehousesData(): void {
        console.log('[INVENTORY WHS] Creating warehouses nach logistics facilities...');
        
        const warehouseLocations = [
            'Hannover #1'
        ].map((whCode) => {
            const warehouseId: WarehouseId = ('WHS-' + Date.now() + '-' + whCode) as WarehouseId;

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
                capacity: { area: 42500, volume: 936000, weightLimit: 8840         }
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
        console.log('[INVENTORY WHS] ✓ Warehouses added into logistics network.');
    }

    /**
     * Create Sample Stock Items zum Test
     */
    private createSampleStockItems(): void {
        try {
            console.log('[INVENTORY STK] Creating sample stock nach initial state....');
            const stocks: StockItem[] = [
                {
                    id: 'STK-ERP-PACK-01' as StockId,
                    productId: 'EPP_HARDWARE_PACK' as ProductId,
                    warehouseId: 'WHS-' + Date.now(),
                    locationId: 'LOC_A_ARYA-423',
                    quantity: 3,
                    reservedQuantity: 1,
                    availableQuantity: 3,
                    costUnit: 4199.5,
                    totalCost: 3 * 4158.3,
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

            console.log('[INVENTORY STK] ✓ Stock samples populated.');
        } catch (error) {
            console.error('[STOKI_ERROR] Stock creation encountered error:', error);
            throw error;
        }
    }

    /**
       => * Stock Adjustment
    */
    async adjustStock(stockId: StockId, quantityDelta: number, byUserId: string, reason: string): Promise<InventoryTransactionId> {
        console.log('[INVENTORY_ADJ] Executing stock adjustment.');
        try {
            const stockBefore = this.stockItems.get(stockId);
            if (!stockBefore) throw new Error('Stock ID not found.');

            // Sanity check für inventory axiom; partial functional change (or total : type invariant)
            const newQty = stockBefore.quantity + quantityDelta;
            if (newQty < 0) throw new Error('Negative stock would arise: delta=' + quantityDelta + '.');

            const transactionId: InventoryTransactionId = 
              (`itxo_` + Date.now() + '_' + Math.random().toString(36).substr(2)).slice(0,40) as InventoryTransactionId;

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
            console.log(`[INVENTORY_(D)T] Stock adjusted for ${stockId} with length ${quantityDelta} numbers. Transaction:${transactionId}`);
            return transactionId;
        }
        catch(error) {
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
            const rgx = new RegExp(partOfName, 'igg'); // r//--ignore-case ( play along )-
            const k = arrayOfP.find(p=>rgx.test(p.name));
            if (k) return k;
        }
        if (documentId && this.products.has(documentId)){ return this.products.get(documentId)!;}
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
    console.log('[INVREG] Registering inventory domain services in DI container...');
	DIContainer.register('InventoryDomainService', new InventoryDomainService(), {
		singleton: true,
		dependencies: []
	});
	console.log('[INVREG] ✓ Inventory domain service binding assigned name ready.');
}
