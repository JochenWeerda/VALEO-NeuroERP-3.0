"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AvailabilityCheck = exports.CycleCount = exports.Warehouse = exports.InventoryMovement = exports.StockLevel = exports.InventoryItem = exports.Location = void 0;
const zod_1 = require("zod");
const shared_schemas_1 = require("./shared-schemas");
// Inventory-specific schemas
// Item/Warehouse location
exports.Location = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Location details
    code: zod_1.z.string(), // e.g., "A1-01-01"
    name: zod_1.z.string(),
    type: zod_1.z.enum(['WAREHOUSE', 'ZONE', 'AISLE', 'SHELF', 'BIN']),
    // Physical location
    warehouseId: shared_schemas_1.UUID,
    address: shared_schemas_1.Address.optional(),
    // Hierarchy
    parentLocationId: shared_schemas_1.UUID.optional(),
    level: zod_1.z.number().int().min(1).max(5).default(1),
    // Capacity
    maxWeightKg: zod_1.z.number().positive().optional(),
    maxVolumeM3: zod_1.z.number().positive().optional(),
    // Status
    isActive: zod_1.z.boolean().default(true),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Inventory item/SKU
exports.InventoryItem = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Item identification
    sku: zod_1.z.string(), // Stock Keeping Unit
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    // Classification
    category: zod_1.z.string().optional(),
    subcategory: zod_1.z.string().optional(),
    // Physical properties
    weightKg: zod_1.z.number().positive(),
    volumeM3: zod_1.z.number().positive().optional(),
    dimensions: zod_1.z.object({
        lengthCm: zod_1.z.number().positive(),
        widthCm: zod_1.z.number().positive(),
        heightCm: zod_1.z.number().positive()
    }).optional(),
    // Financial
    standardCost: shared_schemas_1.Money.optional(),
    standardPrice: shared_schemas_1.Money.optional(),
    // Inventory management
    minStockLevel: zod_1.z.number().nonnegative().default(0),
    maxStockLevel: zod_1.z.number().positive().optional(),
    reorderPoint: zod_1.z.number().nonnegative().default(0),
    // Status
    status: zod_1.z.enum(['ACTIVE', 'INACTIVE', 'DISCONTINUED']),
    isTracked: zod_1.z.boolean().default(true),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Stock level at specific location
exports.StockLevel = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // References
    itemId: shared_schemas_1.UUID,
    locationId: shared_schemas_1.UUID,
    // Quantities
    onHand: zod_1.z.number().nonnegative(),
    allocated: zod_1.z.number().nonnegative().default(0),
    available: zod_1.z.number().nonnegative(),
    // Status
    lastCounted: zod_1.z.string().datetime().optional(),
    lastMovement: zod_1.z.string().datetime().optional(),
    // Metadata
    updatedAt: zod_1.z.string().datetime()
});
// Inventory movement/transaction
exports.InventoryMovement = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Movement details
    itemId: shared_schemas_1.UUID,
    fromLocationId: shared_schemas_1.UUID.optional(),
    toLocationId: shared_schemas_1.UUID.optional(),
    quantity: zod_1.z.number().int(),
    // Movement type
    type: zod_1.z.enum([
        'RECEIPT', 'SALE', 'TRANSFER', 'ADJUSTMENT',
        'RETURN', 'SCRAP', 'CYCLE_COUNT'
    ]),
    // References
    referenceType: zod_1.z.enum(['PURCHASE_ORDER', 'SALES_ORDER', 'WORK_ORDER', 'MANUAL']),
    referenceId: zod_1.z.string(),
    // Additional data
    unitCost: shared_schemas_1.Money.optional(),
    reason: zod_1.z.string().optional(),
    // Status
    status: zod_1.z.enum(['PENDING', 'COMPLETED', 'CANCELLED']),
    completedAt: zod_1.z.string().datetime().optional(),
    // Metadata
    createdBy: zod_1.z.string(),
    createdAt: zod_1.z.string().datetime()
});
// Warehouse
exports.Warehouse = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Basic information
    code: zod_1.z.string(),
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    // Location
    address: shared_schemas_1.Address,
    // Configuration
    type: zod_1.z.enum(['MAIN', 'REGIONAL', 'TRANSIT', 'COLD_STORAGE']),
    temperatureControlled: zod_1.z.boolean().default(false),
    tempRange: zod_1.z.object({
        minC: zod_1.z.number(),
        maxC: zod_1.z.number()
    }).optional(),
    // Capacity
    totalAreaM2: zod_1.z.number().positive().optional(),
    maxWeightKg: zod_1.z.number().positive().optional(),
    // Status
    status: zod_1.z.enum(['ACTIVE', 'INACTIVE', 'MAINTENANCE']),
    isDefault: zod_1.z.boolean().default(false),
    // Metadata
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Cycle count
exports.CycleCount = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Count details
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    // Scope
    locationIds: zod_1.z.array(shared_schemas_1.UUID).optional(), // All locations if not specified
    itemIds: zod_1.z.array(shared_schemas_1.UUID).optional(), // All items if not specified
    // Schedule
    scheduledDate: zod_1.z.string().datetime(),
    completedDate: zod_1.z.string().datetime().optional(),
    // Status
    status: zod_1.z.enum(['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
    // Count results
    countLines: zod_1.z.array(zod_1.z.object({
        itemId: shared_schemas_1.UUID,
        locationId: shared_schemas_1.UUID,
        systemQuantity: zod_1.z.number().nonnegative(),
        countedQuantity: zod_1.z.number().nonnegative(),
        variance: zod_1.z.number(),
        reason: zod_1.z.string().optional()
    })).default([]),
    // Metadata
    createdBy: zod_1.z.string(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime()
});
// Item availability check
exports.AvailabilityCheck = zod_1.z.object({
    itemId: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Check parameters
    requestedQuantity: zod_1.z.number().positive(),
    locationIds: zod_1.z.array(shared_schemas_1.UUID).optional(), // Check specific locations
    // Results
    availableQuantity: zod_1.z.number().nonnegative(),
    availableLocations: zod_1.z.array(zod_1.z.object({
        locationId: shared_schemas_1.UUID,
        availableQuantity: zod_1.z.number().nonnegative(),
        eta: zod_1.z.string().datetime().optional()
    })),
    // Status
    isAvailable: zod_1.z.boolean(),
    shortages: zod_1.z.array(zod_1.z.object({
        locationId: shared_schemas_1.UUID,
        shortageQuantity: zod_1.z.number().positive()
    })).default([])
});
//# sourceMappingURL=inventory-schemas.js.map