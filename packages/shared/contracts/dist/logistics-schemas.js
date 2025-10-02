"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReturnOrder = exports.SafetyAlert = exports.EmissionRecord = exports.FreightRate = exports.WeighingRecord = exports.ProofOfDelivery = exports.TelemetryRecord = exports.YardVisit = exports.DispatchAssignment = exports.RoutePlan = exports.CreateShipmentDto = exports.Shipment = exports.Incoterm = exports.ShipmentPriority = exports.ShipmentStop = exports.StopType = exports.PayloadItem = exports.TemperatureRange = void 0;
const zod_1 = require("zod");
const shared_schemas_1 = require("./shared-schemas");
// Logistics-specific schemas
// Temperature range for cold chain
exports.TemperatureRange = zod_1.z.object({
    minC: zod_1.z.number(),
    maxC: zod_1.z.number()
});
// Payload item for shipments
exports.PayloadItem = zod_1.z.object({
    sscc: zod_1.z.string().optional(), // Serial Shipping Container Code
    description: zod_1.z.string().optional(),
    weightKg: zod_1.z.number().positive(),
    volumeM3: zod_1.z.number().positive().optional(),
    tempRange: exports.TemperatureRange.optional()
});
// Stop type for shipment routes
exports.StopType = zod_1.z.enum(['pickup', 'delivery', 'cross-dock', 'drop-off', 'return']);
// Shipment stop
exports.ShipmentStop = zod_1.z.object({
    sequence: zod_1.z.number().int().positive(),
    type: exports.StopType,
    address: shared_schemas_1.Address,
    window: shared_schemas_1.TimeWindow.optional(),
    contactInfo: zod_1.z.object({
        name: zod_1.z.string().optional(),
        phone: zod_1.z.string().optional(),
        instructions: zod_1.z.string().optional()
    }).optional()
});
// Shipment priority levels
exports.ShipmentPriority = zod_1.z.enum(['standard', 'express', 'critical']);
// Incoterm (International Commercial Terms)
exports.Incoterm = zod_1.z.enum([
    'EXW', 'FCA', 'CPT', 'CIP', 'DAT', 'DAP', 'DDP',
    'FAS', 'FOB', 'CFR', 'CIF', 'DES', 'DEQ', 'DDU'
]);
// Main shipment schema
exports.Shipment = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    reference: zod_1.z.string().optional(),
    // Origin and Destination
    origin: shared_schemas_1.Address,
    destination: shared_schemas_1.Address,
    // Route and Stops
    stops: zod_1.z.array(exports.ShipmentStop),
    // Payload
    payload: zod_1.z.array(exports.PayloadItem),
    // Business Terms
    priority: exports.ShipmentPriority.default('standard'),
    incoterm: exports.Incoterm.optional(),
    // Status and Tracking
    status: zod_1.z.enum(['NEW', 'CONFIRMED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED']),
    tracking: zod_1.z.array(zod_1.z.object({
        status: zod_1.z.string(),
        location: shared_schemas_1.Address.optional(),
        timestamp: zod_1.z.string().datetime(),
        description: zod_1.z.string().optional()
    })).default([]),
    // Timestamps
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    estimatedDelivery: zod_1.z.string().datetime().optional(),
    actualDelivery: zod_1.z.string().datetime().optional()
});
// Shipment creation DTO (for API requests)
exports.CreateShipmentDto = zod_1.z.object({
    tenantId: zod_1.z.string().min(1),
    reference: zod_1.z.string().optional(),
    origin: shared_schemas_1.Address,
    destination: shared_schemas_1.Address,
    priority: exports.ShipmentPriority.default('standard'),
    incoterm: exports.Incoterm.optional(),
    stops: zod_1.z.array(zod_1.z.object({
        sequence: zod_1.z.number().int().positive(),
        type: exports.StopType,
        address: shared_schemas_1.Address,
        window: shared_schemas_1.TimeWindow.optional()
    })),
    payload: zod_1.z.array(zod_1.z.object({
        sscc: zod_1.z.string().optional(),
        description: zod_1.z.string().optional(),
        weightKg: zod_1.z.number().positive(),
        volumeM3: zod_1.z.number().positive().optional(),
        tempRange: exports.TemperatureRange.optional()
    }))
});
// Route plan for shipments
exports.RoutePlan = zod_1.z.object({
    id: shared_schemas_1.UUID,
    shipmentId: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    status: zod_1.z.enum(['PLANNING', 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
    // Route details
    totalDistanceKm: zod_1.z.number().nonnegative(),
    estimatedDurationMinutes: zod_1.z.number().positive(),
    // Vehicle and Driver assignment
    vehicleId: zod_1.z.string().optional(),
    driverId: zod_1.z.string().optional(),
    trailerId: zod_1.z.string().optional(),
    // Route legs
    legs: zod_1.z.array(zod_1.z.object({
        fromStopId: shared_schemas_1.UUID,
        toStopId: shared_schemas_1.UUID,
        distanceKm: zod_1.z.number().nonnegative(),
        estimatedDurationMinutes: zod_1.z.number().positive(),
        etaFrom: zod_1.z.string().datetime(),
        etaTo: zod_1.z.string().datetime()
    })),
    // Timestamps
    plannedAt: zod_1.z.string().datetime(),
    startedAt: zod_1.z.string().datetime().optional(),
    completedAt: zod_1.z.string().datetime().optional()
});
// Dispatch assignment
exports.DispatchAssignment = zod_1.z.object({
    id: shared_schemas_1.UUID,
    routeId: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Assignment details
    driverId: zod_1.z.string(),
    vehicleId: zod_1.z.string(),
    trailerId: zod_1.z.string().optional(),
    // Status
    status: zod_1.z.enum(['ASSIGNED', 'EN_ROUTE', 'AT_STOP', 'COMPLETED', 'REASSIGNED']),
    // Timestamps
    assignedAt: zod_1.z.string().datetime(),
    startedAt: zod_1.z.string().datetime().optional(),
    completedAt: zod_1.z.string().datetime().optional()
});
// Yard visit for slot/dock management
exports.YardVisit = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    shipmentId: shared_schemas_1.UUID,
    // Location
    gate: zod_1.z.string(),
    dock: zod_1.z.string().optional(),
    // Timing
    scheduledWindow: shared_schemas_1.TimeWindow.optional(),
    actualArrival: zod_1.z.string().datetime().optional(),
    actualDeparture: zod_1.z.string().datetime().optional(),
    // Status
    status: zod_1.z.enum(['SCHEDULED', 'CHECKED_IN', 'AT_DOCK', 'LOADING', 'UNLOADING', 'CHECKED_OUT', 'CANCELLED'])
});
// Telemetry data for vehicle tracking
exports.TelemetryRecord = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    vehicleId: zod_1.z.string(),
    // Location and movement
    lat: zod_1.z.number().min(-90).max(90),
    lon: zod_1.z.number().min(-180).max(180),
    speedKph: zod_1.z.number().nonnegative().optional(),
    heading: zod_1.z.number().min(0).max(360).optional(),
    // Vehicle state
    temperatureC: zod_1.z.number().optional(),
    fuelLevelPercent: zod_1.z.number().min(0).max(100).optional(),
    // Metadata
    recordedAt: zod_1.z.string().datetime(),
    meta: zod_1.z.record(zod_1.z.any()).optional()
});
// Proof of delivery
exports.ProofOfDelivery = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    shipmentId: shared_schemas_1.UUID,
    stopId: shared_schemas_1.UUID,
    // Delivery details
    signedBy: zod_1.z.string(),
    signatureRef: zod_1.z.string().optional(), // Reference to signature image
    photoRefs: zod_1.z.array(zod_1.z.string()).default([]), // References to delivery photos
    scans: zod_1.z.array(zod_1.z.string()).default([]), // Barcode scans
    // Exceptions and notes
    exceptions: zod_1.z.array(zod_1.z.string()).default([]),
    notes: zod_1.z.string().optional(),
    // Timestamps
    capturedAt: zod_1.z.string().datetime(),
    syncedAt: zod_1.z.string().datetime().optional()
});
// Weighing record
exports.WeighingRecord = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    shipmentId: shared_schemas_1.UUID,
    // Weights
    grossWeightKg: zod_1.z.number().positive(),
    tareWeightKg: zod_1.z.number().positive(),
    netWeightKg: zod_1.z.number().positive(),
    // Source
    source: zod_1.z.enum(['bridge', 'sensor', 'manual']),
    // Timestamps
    measuredAt: zod_1.z.string().datetime(),
    recordedAt: zod_1.z.string().datetime()
});
// Freight rate
exports.FreightRate = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    // Rate details
    baseAmount: shared_schemas_1.Money,
    surcharges: zod_1.z.array(zod_1.z.object({
        type: zod_1.z.string(),
        amount: shared_schemas_1.Money,
        description: zod_1.z.string().optional()
    })).default([]),
    // Applicability
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    // Conditions
    minWeightKg: zod_1.z.number().positive().optional(),
    maxWeightKg: zod_1.z.number().positive().optional(),
    zones: zod_1.z.array(zod_1.z.string()).optional(),
    // Metadata
    rateCardId: zod_1.z.string().optional(),
    explanation: zod_1.z.string().optional()
});
// Emission record
exports.EmissionRecord = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    shipmentId: shared_schemas_1.UUID,
    // Emission data
    co2eKg: zod_1.z.number().nonnegative(), // CO2 equivalent in kilograms
    method: zod_1.z.string(), // Calculation method
    // Factors used
    factors: zod_1.z.array(zod_1.z.object({
        factor: zod_1.z.string(),
        value: zod_1.z.number(),
        unit: zod_1.z.string()
    })).default([]),
    // Timestamps
    calculatedAt: zod_1.z.string().datetime()
});
// Safety alert
exports.SafetyAlert = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    referenceId: shared_schemas_1.UUID, // Shipment, Vehicle, or Driver ID
    // Alert details
    type: zod_1.z.enum(['dangerous_goods', 'temperature', 'geofence', 'weight', 'speed', 'maintenance']),
    severity: zod_1.z.enum(['info', 'warning', 'critical']),
    message: zod_1.z.string(),
    // Location and context
    location: zod_1.z.object({
        lat: zod_1.z.number().min(-90).max(90),
        lon: zod_1.z.number().min(-180).max(180)
    }).optional(),
    // Status
    status: zod_1.z.enum(['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED']),
    acknowledgedBy: zod_1.z.string().optional(),
    acknowledgedAt: zod_1.z.string().datetime().optional(),
    // Timestamps
    raisedAt: zod_1.z.string().datetime(),
    resolvedAt: zod_1.z.string().datetime().optional()
});
// Return order
exports.ReturnOrder = zod_1.z.object({
    id: shared_schemas_1.UUID,
    tenantId: zod_1.z.string().min(1),
    originalShipmentId: shared_schemas_1.UUID,
    // Return details
    pickupAddress: shared_schemas_1.Address,
    returnReason: zod_1.z.string(),
    // Items being returned
    items: zod_1.z.array(zod_1.z.object({
        originalItemId: zod_1.z.string(),
        quantity: zod_1.z.number().int().positive(),
        reason: zod_1.z.string().optional()
    })),
    // Status
    status: zod_1.z.enum(['REQUESTED', 'APPROVED', 'SCHEDULED', 'PICKED_UP', 'DELIVERED', 'CANCELLED']),
    // Timestamps
    requestedAt: zod_1.z.string().datetime(),
    approvedAt: zod_1.z.string().datetime().optional(),
    scheduledAt: zod_1.z.string().datetime().optional(),
    completedAt: zod_1.z.string().datetime().optional()
});
//# sourceMappingURL=logistics-schemas.js.map