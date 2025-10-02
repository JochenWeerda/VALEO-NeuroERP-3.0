import { z } from 'zod';
import { Money, UUID, Address } from './shared-schemas';

// Inventory-specific schemas

// Item/Warehouse location
export const Location = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Location details
  code: z.string(), // e.g., "A1-01-01"
  name: z.string(),
  type: z.enum(['WAREHOUSE', 'ZONE', 'AISLE', 'SHELF', 'BIN']),

  // Physical location
  warehouseId: UUID,
  address: Address.optional(),

  // Hierarchy
  parentLocationId: UUID.optional(),
  level: z.number().int().min(1).max(5).default(1),

  // Capacity
  maxWeightKg: z.number().positive().optional(),
  maxVolumeM3: z.number().positive().optional(),

  // Status
  isActive: z.boolean().default(true),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Location = z.infer<typeof Location>;

// Inventory item/SKU
export const InventoryItem = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Item identification
  sku: z.string(), // Stock Keeping Unit
  name: z.string(),
  description: z.string().optional(),

  // Classification
  category: z.string().optional(),
  subcategory: z.string().optional(),

  // Physical properties
  weightKg: z.number().positive(),
  volumeM3: z.number().positive().optional(),
  dimensions: z.object({
    lengthCm: z.number().positive(),
    widthCm: z.number().positive(),
    heightCm: z.number().positive()
  }).optional(),

  // Financial
  standardCost: Money.optional(),
  standardPrice: Money.optional(),

  // Inventory management
  minStockLevel: z.number().nonnegative().default(0),
  maxStockLevel: z.number().positive().optional(),
  reorderPoint: z.number().nonnegative().default(0),

  // Status
  status: z.enum(['ACTIVE', 'INACTIVE', 'DISCONTINUED']),
  isTracked: z.boolean().default(true),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type InventoryItem = z.infer<typeof InventoryItem>;

// Stock level at specific location
export const StockLevel = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // References
  itemId: UUID,
  locationId: UUID,

  // Quantities
  onHand: z.number().nonnegative(),
  allocated: z.number().nonnegative().default(0),
  available: z.number().nonnegative(),

  // Status
  lastCounted: z.string().datetime().optional(),
  lastMovement: z.string().datetime().optional(),

  // Metadata
  updatedAt: z.string().datetime()
});

export type StockLevel = z.infer<typeof StockLevel>;

// Inventory movement/transaction
export const InventoryMovement = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Movement details
  itemId: UUID,
  fromLocationId: UUID.optional(),
  toLocationId: UUID.optional(),
  quantity: z.number().int(),

  // Movement type
  type: z.enum([
    'RECEIPT', 'SALE', 'TRANSFER', 'ADJUSTMENT',
    'RETURN', 'SCRAP', 'CYCLE_COUNT'
  ]),

  // References
  referenceType: z.enum(['PURCHASE_ORDER', 'SALES_ORDER', 'WORK_ORDER', 'MANUAL']),
  referenceId: z.string(),

  // Additional data
  unitCost: Money.optional(),
  reason: z.string().optional(),

  // Status
  status: z.enum(['PENDING', 'COMPLETED', 'CANCELLED']),
  completedAt: z.string().datetime().optional(),

  // Metadata
  createdBy: z.string(),
  createdAt: z.string().datetime()
});

export type InventoryMovement = z.infer<typeof InventoryMovement>;

// Warehouse
export const Warehouse = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Basic information
  code: z.string(),
  name: z.string(),
  description: z.string().optional(),

  // Location
  address: Address,

  // Configuration
  type: z.enum(['MAIN', 'REGIONAL', 'TRANSIT', 'COLD_STORAGE']),
  temperatureControlled: z.boolean().default(false),
  tempRange: z.object({
    minC: z.number(),
    maxC: z.number()
  }).optional(),

  // Capacity
  totalAreaM2: z.number().positive().optional(),
  maxWeightKg: z.number().positive().optional(),

  // Status
  status: z.enum(['ACTIVE', 'INACTIVE', 'MAINTENANCE']),
  isDefault: z.boolean().default(false),

  // Metadata
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type Warehouse = z.infer<typeof Warehouse>;

// Cycle count
export const CycleCount = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Count details
  name: z.string(),
  description: z.string().optional(),

  // Scope
  locationIds: z.array(UUID).optional(), // All locations if not specified
  itemIds: z.array(UUID).optional(), // All items if not specified

  // Schedule
  scheduledDate: z.string().datetime(),
  completedDate: z.string().datetime().optional(),

  // Status
  status: z.enum(['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),

  // Count results
  countLines: z.array(z.object({
    itemId: UUID,
    locationId: UUID,
    systemQuantity: z.number().nonnegative(),
    countedQuantity: z.number().nonnegative(),
    variance: z.number(),
    reason: z.string().optional()
  })).default([]),

  // Metadata
  createdBy: z.string(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type CycleCount = z.infer<typeof CycleCount>;

// Item availability check
export const AvailabilityCheck = z.object({
  itemId: UUID,
  tenantId: z.string().min(1),

  // Check parameters
  requestedQuantity: z.number().positive(),
  locationIds: z.array(UUID).optional(), // Check specific locations

  // Results
  availableQuantity: z.number().nonnegative(),
  availableLocations: z.array(z.object({
    locationId: UUID,
    availableQuantity: z.number().nonnegative(),
    eta: z.string().datetime().optional()
  })),

  // Status
  isAvailable: z.boolean(),
  shortages: z.array(z.object({
    locationId: UUID,
    shortageQuantity: z.number().positive()
  })).default([])
});

export type AvailabilityCheck = z.infer<typeof AvailabilityCheck>;