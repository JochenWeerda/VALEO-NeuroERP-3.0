import { z } from 'zod';
export declare const Location: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    code: z.ZodString;
    name: z.ZodString;
    type: z.ZodEnum<["WAREHOUSE", "ZONE", "AISLE", "SHELF", "BIN"]>;
    warehouseId: z.ZodString;
    address: z.ZodOptional<z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>>;
    parentLocationId: z.ZodOptional<z.ZodString>;
    level: z.ZodDefault<z.ZodNumber>;
    maxWeightKg: z.ZodOptional<z.ZodNumber>;
    maxVolumeM3: z.ZodOptional<z.ZodNumber>;
    isActive: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    code: string;
    type: "WAREHOUSE" | "ZONE" | "AISLE" | "SHELF" | "BIN";
    name: string;
    tenantId: string;
    id: string;
    level: number;
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
    warehouseId: string;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    } | undefined;
    maxWeightKg?: number | undefined;
    parentLocationId?: string | undefined;
    maxVolumeM3?: number | undefined;
}, {
    code: string;
    type: "WAREHOUSE" | "ZONE" | "AISLE" | "SHELF" | "BIN";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    warehouseId: string;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    } | undefined;
    level?: number | undefined;
    isActive?: boolean | undefined;
    maxWeightKg?: number | undefined;
    parentLocationId?: string | undefined;
    maxVolumeM3?: number | undefined;
}>;
export type Location = z.infer<typeof Location>;
export declare const InventoryItem: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    sku: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    category: z.ZodOptional<z.ZodString>;
    subcategory: z.ZodOptional<z.ZodString>;
    weightKg: z.ZodNumber;
    volumeM3: z.ZodOptional<z.ZodNumber>;
    dimensions: z.ZodOptional<z.ZodObject<{
        lengthCm: z.ZodNumber;
        widthCm: z.ZodNumber;
        heightCm: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        lengthCm: number;
        widthCm: number;
        heightCm: number;
    }, {
        lengthCm: number;
        widthCm: number;
        heightCm: number;
    }>>;
    standardCost: z.ZodOptional<z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>>;
    standardPrice: z.ZodOptional<z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>>;
    minStockLevel: z.ZodDefault<z.ZodNumber>;
    maxStockLevel: z.ZodOptional<z.ZodNumber>;
    reorderPoint: z.ZodDefault<z.ZodNumber>;
    status: z.ZodEnum<["ACTIVE", "INACTIVE", "DISCONTINUED"]>;
    isTracked: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "ACTIVE" | "INACTIVE" | "DISCONTINUED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    weightKg: number;
    sku: string;
    minStockLevel: number;
    reorderPoint: number;
    isTracked: boolean;
    description?: string | undefined;
    volumeM3?: number | undefined;
    category?: string | undefined;
    subcategory?: string | undefined;
    dimensions?: {
        lengthCm: number;
        widthCm: number;
        heightCm: number;
    } | undefined;
    standardCost?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
    standardPrice?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
    maxStockLevel?: number | undefined;
}, {
    status: "ACTIVE" | "INACTIVE" | "DISCONTINUED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    weightKg: number;
    sku: string;
    description?: string | undefined;
    volumeM3?: number | undefined;
    category?: string | undefined;
    subcategory?: string | undefined;
    dimensions?: {
        lengthCm: number;
        widthCm: number;
        heightCm: number;
    } | undefined;
    standardCost?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
    standardPrice?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
    minStockLevel?: number | undefined;
    maxStockLevel?: number | undefined;
    reorderPoint?: number | undefined;
    isTracked?: boolean | undefined;
}>;
export type InventoryItem = z.infer<typeof InventoryItem>;
export declare const StockLevel: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    itemId: z.ZodString;
    locationId: z.ZodString;
    onHand: z.ZodNumber;
    allocated: z.ZodDefault<z.ZodNumber>;
    available: z.ZodNumber;
    lastCounted: z.ZodOptional<z.ZodString>;
    lastMovement: z.ZodOptional<z.ZodString>;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    id: string;
    updatedAt: string;
    itemId: string;
    locationId: string;
    onHand: number;
    allocated: number;
    available: number;
    lastCounted?: string | undefined;
    lastMovement?: string | undefined;
}, {
    tenantId: string;
    id: string;
    updatedAt: string;
    itemId: string;
    locationId: string;
    onHand: number;
    available: number;
    allocated?: number | undefined;
    lastCounted?: string | undefined;
    lastMovement?: string | undefined;
}>;
export type StockLevel = z.infer<typeof StockLevel>;
export declare const InventoryMovement: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    itemId: z.ZodString;
    fromLocationId: z.ZodOptional<z.ZodString>;
    toLocationId: z.ZodOptional<z.ZodString>;
    quantity: z.ZodNumber;
    type: z.ZodEnum<["RECEIPT", "SALE", "TRANSFER", "ADJUSTMENT", "RETURN", "SCRAP", "CYCLE_COUNT"]>;
    referenceType: z.ZodEnum<["PURCHASE_ORDER", "SALES_ORDER", "WORK_ORDER", "MANUAL"]>;
    referenceId: z.ZodString;
    unitCost: z.ZodOptional<z.ZodObject<{
        amount: z.ZodNumber;
        currency: z.ZodEnum<["EUR", "USD", "GBP", "CHF"]>;
    }, "strip", z.ZodTypeAny, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }, {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    }>>;
    reason: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["PENDING", "COMPLETED", "CANCELLED"]>;
    completedAt: z.ZodOptional<z.ZodString>;
    createdBy: z.ZodString;
    createdAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    type: "RECEIPT" | "SALE" | "TRANSFER" | "ADJUSTMENT" | "RETURN" | "SCRAP" | "CYCLE_COUNT";
    status: "CANCELLED" | "PENDING" | "COMPLETED";
    tenantId: string;
    id: string;
    createdAt: string;
    createdBy: string;
    quantity: number;
    referenceId: string;
    itemId: string;
    referenceType: "PURCHASE_ORDER" | "SALES_ORDER" | "WORK_ORDER" | "MANUAL";
    completedAt?: string | undefined;
    reason?: string | undefined;
    fromLocationId?: string | undefined;
    toLocationId?: string | undefined;
    unitCost?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
}, {
    type: "RECEIPT" | "SALE" | "TRANSFER" | "ADJUSTMENT" | "RETURN" | "SCRAP" | "CYCLE_COUNT";
    status: "CANCELLED" | "PENDING" | "COMPLETED";
    tenantId: string;
    id: string;
    createdAt: string;
    createdBy: string;
    quantity: number;
    referenceId: string;
    itemId: string;
    referenceType: "PURCHASE_ORDER" | "SALES_ORDER" | "WORK_ORDER" | "MANUAL";
    completedAt?: string | undefined;
    reason?: string | undefined;
    fromLocationId?: string | undefined;
    toLocationId?: string | undefined;
    unitCost?: {
        amount: number;
        currency: "EUR" | "USD" | "GBP" | "CHF";
    } | undefined;
}>;
export type InventoryMovement = z.infer<typeof InventoryMovement>;
export declare const Warehouse: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    code: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    address: z.ZodObject<{
        street: z.ZodString;
        city: z.ZodString;
        postalCode: z.ZodString;
        country: z.ZodString;
        coordinates: z.ZodOptional<z.ZodObject<{
            lat: z.ZodNumber;
            lon: z.ZodNumber;
        }, "strip", z.ZodTypeAny, {
            lat: number;
            lon: number;
        }, {
            lat: number;
            lon: number;
        }>>;
        gln: z.ZodOptional<z.ZodString>;
        name: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }, {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    }>;
    type: z.ZodEnum<["MAIN", "REGIONAL", "TRANSIT", "COLD_STORAGE"]>;
    temperatureControlled: z.ZodDefault<z.ZodBoolean>;
    tempRange: z.ZodOptional<z.ZodObject<{
        minC: z.ZodNumber;
        maxC: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        minC: number;
        maxC: number;
    }, {
        minC: number;
        maxC: number;
    }>>;
    totalAreaM2: z.ZodOptional<z.ZodNumber>;
    maxWeightKg: z.ZodOptional<z.ZodNumber>;
    status: z.ZodEnum<["ACTIVE", "INACTIVE", "MAINTENANCE"]>;
    isDefault: z.ZodDefault<z.ZodBoolean>;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    code: string;
    type: "MAIN" | "REGIONAL" | "TRANSIT" | "COLD_STORAGE";
    status: "ACTIVE" | "INACTIVE" | "MAINTENANCE";
    name: string;
    address: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    temperatureControlled: boolean;
    isDefault: boolean;
    description?: string | undefined;
    tempRange?: {
        minC: number;
        maxC: number;
    } | undefined;
    maxWeightKg?: number | undefined;
    totalAreaM2?: number | undefined;
}, {
    code: string;
    type: "MAIN" | "REGIONAL" | "TRANSIT" | "COLD_STORAGE";
    status: "ACTIVE" | "INACTIVE" | "MAINTENANCE";
    name: string;
    address: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        coordinates?: {
            lat: number;
            lon: number;
        } | undefined;
        gln?: string | undefined;
        name?: string | undefined;
    };
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    description?: string | undefined;
    tempRange?: {
        minC: number;
        maxC: number;
    } | undefined;
    maxWeightKg?: number | undefined;
    temperatureControlled?: boolean | undefined;
    totalAreaM2?: number | undefined;
    isDefault?: boolean | undefined;
}>;
export type Warehouse = z.infer<typeof Warehouse>;
export declare const CycleCount: z.ZodObject<{
    id: z.ZodString;
    tenantId: z.ZodString;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    locationIds: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    itemIds: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    scheduledDate: z.ZodString;
    completedDate: z.ZodOptional<z.ZodString>;
    status: z.ZodEnum<["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]>;
    countLines: z.ZodDefault<z.ZodArray<z.ZodObject<{
        itemId: z.ZodString;
        locationId: z.ZodString;
        systemQuantity: z.ZodNumber;
        countedQuantity: z.ZodNumber;
        variance: z.ZodNumber;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        itemId: string;
        locationId: string;
        systemQuantity: number;
        countedQuantity: number;
        variance: number;
        reason?: string | undefined;
    }, {
        itemId: string;
        locationId: string;
        systemQuantity: number;
        countedQuantity: number;
        variance: number;
        reason?: string | undefined;
    }>, "many">>;
    createdBy: z.ZodString;
    createdAt: z.ZodString;
    updatedAt: z.ZodString;
}, "strip", z.ZodTypeAny, {
    status: "CANCELLED" | "COMPLETED" | "IN_PROGRESS" | "SCHEDULED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    scheduledDate: string;
    countLines: {
        itemId: string;
        locationId: string;
        systemQuantity: number;
        countedQuantity: number;
        variance: number;
        reason?: string | undefined;
    }[];
    description?: string | undefined;
    locationIds?: string[] | undefined;
    itemIds?: string[] | undefined;
    completedDate?: string | undefined;
}, {
    status: "CANCELLED" | "COMPLETED" | "IN_PROGRESS" | "SCHEDULED";
    name: string;
    tenantId: string;
    id: string;
    createdAt: string;
    updatedAt: string;
    createdBy: string;
    scheduledDate: string;
    description?: string | undefined;
    locationIds?: string[] | undefined;
    itemIds?: string[] | undefined;
    completedDate?: string | undefined;
    countLines?: {
        itemId: string;
        locationId: string;
        systemQuantity: number;
        countedQuantity: number;
        variance: number;
        reason?: string | undefined;
    }[] | undefined;
}>;
export type CycleCount = z.infer<typeof CycleCount>;
export declare const AvailabilityCheck: z.ZodObject<{
    itemId: z.ZodString;
    tenantId: z.ZodString;
    requestedQuantity: z.ZodNumber;
    locationIds: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    availableQuantity: z.ZodNumber;
    availableLocations: z.ZodArray<z.ZodObject<{
        locationId: z.ZodString;
        availableQuantity: z.ZodNumber;
        eta: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        locationId: string;
        availableQuantity: number;
        eta?: string | undefined;
    }, {
        locationId: string;
        availableQuantity: number;
        eta?: string | undefined;
    }>, "many">;
    isAvailable: z.ZodBoolean;
    shortages: z.ZodDefault<z.ZodArray<z.ZodObject<{
        locationId: z.ZodString;
        shortageQuantity: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        locationId: string;
        shortageQuantity: number;
    }, {
        locationId: string;
        shortageQuantity: number;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    tenantId: string;
    itemId: string;
    requestedQuantity: number;
    availableQuantity: number;
    availableLocations: {
        locationId: string;
        availableQuantity: number;
        eta?: string | undefined;
    }[];
    isAvailable: boolean;
    shortages: {
        locationId: string;
        shortageQuantity: number;
    }[];
    locationIds?: string[] | undefined;
}, {
    tenantId: string;
    itemId: string;
    requestedQuantity: number;
    availableQuantity: number;
    availableLocations: {
        locationId: string;
        availableQuantity: number;
        eta?: string | undefined;
    }[];
    isAvailable: boolean;
    locationIds?: string[] | undefined;
    shortages?: {
        locationId: string;
        shortageQuantity: number;
    }[] | undefined;
}>;
export type AvailabilityCheck = z.infer<typeof AvailabilityCheck>;
//# sourceMappingURL=inventory-schemas.d.ts.map