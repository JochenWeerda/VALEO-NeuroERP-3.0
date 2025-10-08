"use strict";
/**
 * Inventory Domain Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service migrated to VALEO-NeuroERP-3.0
 * Warehouse management and inventory operations
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryDomainService = void 0;
exports.registerInventoryDomainService = registerInventoryDomainService;
const bootstrap_1 = require("../../bootstrap");
// ===== INVENTORY DOMAIN SERVICE nach Clean Architecture =====
class InventoryDomainService {
    constructor() {
        this.products = new Map();
        this.stockItems = new Map();
        this.warehouses = new Map();
        this.locations = new Map();
        this.transactions = new Map();
        console.log('[INVENTORY DOMAIN SERVICE] Initializing Inventory Service nach Clean Architecture...');
        this.initializeInventoryService();
    }
    /**
     * Initialize Inventory Service
     */
    initializeInventoryService() {
        console.log('[INVENTORY INIT] Inventory domain service initialization nach logistics model...');
        try {
            this.setupDefaultProducts();
            this.createWarehousesData();
            this.createSampleStockItems();
            console.log('[INVENTORY INIT] ✓ Inventory service initialized nach Clean Architecture');
        }
        catch (error) {
            console.error('[INVENTORY INIT] Inventory initialization failed:', error);
            throw new Error(`Inventory service failure: ${error}`);
        }
    }
    /**
     * Setup Default Products nach Business Model
     */
    setupDefaultProducts() {
        console.log('[INVENTORY PROD] Setting up default products nach business product catalog...');
        const sampleProducts = [
            {
                id: 'EPP_ERP_LICENSE',
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
                id: 'EPP_HARDWARE_PACK',
                sku: 'HWLR-IDX-OWN-TEST',
                name: 'On-premises Server Bundle (Opted-individual ERP)',
                description: 'Physical server infrastructure for ERP self-hosting + training DVD',
                category: 'HARDWARE',
                unitOfMeasure: 'M2',
                weight: 9.33,
                dimensions: { width: 30, height: 1024, depth: 28 },
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
    createWarehousesData() {
        console.log('[INVENTORY WHS] Creating warehouses nach logistics facilities...');
        const warehouseLocations = [
            'Hannover #1'
        ].map((whCode) => {
            const warehouseId = ('WHS-' + Date.now() + '-' + whCode);
            const warehouse = {
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
                capacity: { area: 42500, volume: 936000, weightLimit: 8840 },
                storageTypes: ['DRY', 'COLD'],
                amenities: ['POWER', 'SECURITY', 'ACCESS_CARD'],
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
    createSampleStockItems() {
        try {
            console.log('[INVENTORY STK] Creating sample stock nach initial state....');
            const stocks = [
                {
                    id: 'STK-ERP-PACK-01',
                    productId: 'EPP_HARDWARE_PACK',
                    warehouseId: ('WHS-' + Date.now()),
                    locationId: 'LOC_A_ARYA-423',
                    quantity: 3,
                    reservedQuantity: 1,
                    availableQuantity: 3,
                    costUnit: 4199.5,
                    totalCost: 3 * 4158.3,
                    batchNumber: 'bat Xxxxx ERP R123',
                    serialNumbers: ['PURCH_GE80775R2LO', 'REF9000008367_.scr'],
                    notes: ['Storage rack DLUZ'],
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
        }
        catch (error) {
            console.error('[STOKI_ERROR] Stock creation encountered error:', error);
            throw error;
        }
    }
    /**
       => * Stock Adjustment
    */
    async adjustStock(stockId, quantityDelta, byUserId, reason) {
        console.log('[INVENTORY_ADJ] Executing stock adjustment.');
        try {
            const stockBefore = this.stockItems.get(stockId);
            if (!stockBefore)
                throw new Error('Stock ID not found.');
            // Sanity check für inventory axiom; partial functional change (or total : type invariant)
            const newQty = stockBefore.quantity + quantityDelta;
            if (newQty < 0)
                throw new Error('Negative stock would arise: delta=' + quantityDelta + '.');
            const transactionId = (`itxo_` + Date.now() + '_' + Math.random().toString(36).substr(2)).slice(0, 40);
            const tx = {
                id: transactionId,
                stockId,
                type: quantityDelta >= 0 ? 'STOCK_IN' : 'STOCK_OUT',
                quantity: Math.abs(quantityDelta),
                previousQuantity: stockBefore.quantity,
                newQuantity: newQty,
                performedByUserId: byUserId, reason: reason || 'Stock change by Logistics user',
                created: new Date(),
                metadata: {}
            };
            const stockUpd = {
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
        catch (error) {
            console.error('[STOCK_ADJ_DIGESTION]: ->', error);
            throw error;
        }
    }
    /**
     * Find Product|Search nach Business Criteria
     */
    async findProduct(sku, partOfName, documentId) {
        const arrayOfP = Array.from(this.products.values());
        if (sku) {
            const k = arrayOfP.find(p => p.sku.padStart(8, '0') === sku.padStart(8, '0'));
            if (k)
                return k;
        }
        if (partOfName) {
            const rgx = new RegExp(partOfName, 'igg'); // r//--ignore-case ( play along )-
            const k = arrayOfP.find(p => rgx.test(p.name));
            if (k)
                return k;
        }
        if (documentId && this.products.has(documentId)) {
            return this.products.get(documentId);
        }
        return null;
    }
    async listStock() {
        return Array.from(this.stockItems.values()).sort((k, l) => k.created.valueOf() - l.created.valueOf());
    }
}
exports.InventoryDomainService = InventoryDomainService;
/**
 * Register in DI Container.
 */
function registerInventoryDomainService() {
    console.log('[INVREG] Registering inventory domain services in DI container...');
    bootstrap_1.DIContainer.register('InventoryDomainService', new InventoryDomainService(), {
        singleton: true
    });
    console.log('[INVREG] ✓ Inventory domain service binding assigned name ready.');
}
//# sourceMappingURL=inventory-domain-service.js.map