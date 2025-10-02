import { z } from 'zod';
import { Address, Money, TimeWindow, UUID } from './shared-schemas';

// Logistics-specific schemas

// Temperature range for cold chain
export const TemperatureRange = z.object({
  minC: z.number(),
  maxC: z.number()
});

export type TemperatureRange = z.infer<typeof TemperatureRange>;

// Payload item for shipments
export const PayloadItem = z.object({
  sscc: z.string().optional(), // Serial Shipping Container Code
  description: z.string().optional(),
  weightKg: z.number().positive(),
  volumeM3: z.number().positive().optional(),
  tempRange: TemperatureRange.optional()
});

export type PayloadItem = z.infer<typeof PayloadItem>;

// Stop type for shipment routes
export const StopType = z.enum(['pickup', 'delivery', 'cross-dock', 'drop-off', 'return']);

export type StopType = z.infer<typeof StopType>;

// Shipment stop
export const ShipmentStop = z.object({
  sequence: z.number().int().positive(),
  type: StopType,
  address: Address,
  window: TimeWindow.optional(),
  contactInfo: z.object({
    name: z.string().optional(),
    phone: z.string().optional(),
    instructions: z.string().optional()
  }).optional()
});

export type ShipmentStop = z.infer<typeof ShipmentStop>;

// Shipment priority levels
export const ShipmentPriority = z.enum(['standard', 'express', 'critical']);

export type ShipmentPriority = z.infer<typeof ShipmentPriority>;

// Incoterm (International Commercial Terms)
export const Incoterm = z.enum([
  'EXW', 'FCA', 'CPT', 'CIP', 'DAT', 'DAP', 'DDP',
  'FAS', 'FOB', 'CFR', 'CIF', 'DES', 'DEQ', 'DDU'
]);

// Main shipment schema
export const Shipment = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  reference: z.string().optional(),

  // Origin and Destination
  origin: Address,
  destination: Address,

  // Route and Stops
  stops: z.array(ShipmentStop),

  // Payload
  payload: z.array(PayloadItem),

  // Business Terms
  priority: ShipmentPriority.default('standard'),
  incoterm: Incoterm.optional(),

  // Status and Tracking
  status: z.enum(['NEW', 'CONFIRMED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED']),
  tracking: z.array(z.object({
    status: z.string(),
    location: Address.optional(),
    timestamp: z.string().datetime(),
    description: z.string().optional()
  })).default([]),

  // Timestamps
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  estimatedDelivery: z.string().datetime().optional(),
  actualDelivery: z.string().datetime().optional()
});

export type Shipment = z.infer<typeof Shipment>;

// Shipment creation DTO (for API requests)
export const CreateShipmentDto = z.object({
  tenantId: z.string().min(1),
  reference: z.string().optional(),
  origin: Address,
  destination: Address,
  priority: ShipmentPriority.default('standard'),
  incoterm: Incoterm.optional(),
  stops: z.array(z.object({
    sequence: z.number().int().positive(),
    type: StopType,
    address: Address,
    window: TimeWindow.optional()
  })),
  payload: z.array(z.object({
    sscc: z.string().optional(),
    description: z.string().optional(),
    weightKg: z.number().positive(),
    volumeM3: z.number().positive().optional(),
    tempRange: TemperatureRange.optional()
  }))
});

// Route plan for shipments
export const RoutePlan = z.object({
  id: UUID,
  shipmentId: UUID,
  tenantId: z.string().min(1),
  status: z.enum(['PLANNING', 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),

  // Route details
  totalDistanceKm: z.number().nonnegative(),
  estimatedDurationMinutes: z.number().positive(),

  // Vehicle and Driver assignment
  vehicleId: z.string().optional(),
  driverId: z.string().optional(),
  trailerId: z.string().optional(),

  // Route legs
  legs: z.array(z.object({
    fromStopId: UUID,
    toStopId: UUID,
    distanceKm: z.number().nonnegative(),
    estimatedDurationMinutes: z.number().positive(),
    etaFrom: z.string().datetime(),
    etaTo: z.string().datetime()
  })),

  // Timestamps
  plannedAt: z.string().datetime(),
  startedAt: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional()
});

export type RoutePlan = z.infer<typeof RoutePlan>;

// Dispatch assignment
export const DispatchAssignment = z.object({
  id: UUID,
  routeId: UUID,
  tenantId: z.string().min(1),

  // Assignment details
  driverId: z.string(),
  vehicleId: z.string(),
  trailerId: z.string().optional(),

  // Status
  status: z.enum(['ASSIGNED', 'EN_ROUTE', 'AT_STOP', 'COMPLETED', 'REASSIGNED']),

  // Timestamps
  assignedAt: z.string().datetime(),
  startedAt: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional()
});

export type DispatchAssignment = z.infer<typeof DispatchAssignment>;

// Yard visit for slot/dock management
export const YardVisit = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  shipmentId: UUID,

  // Location
  gate: z.string(),
  dock: z.string().optional(),

  // Timing
  scheduledWindow: TimeWindow.optional(),
  actualArrival: z.string().datetime().optional(),
  actualDeparture: z.string().datetime().optional(),

  // Status
  status: z.enum(['SCHEDULED', 'CHECKED_IN', 'AT_DOCK', 'LOADING', 'UNLOADING', 'CHECKED_OUT', 'CANCELLED'])
});

export type YardVisit = z.infer<typeof YardVisit>;

// Telemetry data for vehicle tracking
export const TelemetryRecord = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  vehicleId: z.string(),

  // Location and movement
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
  speedKph: z.number().nonnegative().optional(),
  heading: z.number().min(0).max(360).optional(),

  // Vehicle state
  temperatureC: z.number().optional(),
  fuelLevelPercent: z.number().min(0).max(100).optional(),

  // Metadata
  recordedAt: z.string().datetime(),
  meta: z.record(z.any()).optional()
});

export type TelemetryRecord = z.infer<typeof TelemetryRecord>;

// Proof of delivery
export const ProofOfDelivery = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  shipmentId: UUID,
  stopId: UUID,

  // Delivery details
  signedBy: z.string(),
  signatureRef: z.string().optional(), // Reference to signature image
  photoRefs: z.array(z.string()).default([]), // References to delivery photos
  scans: z.array(z.string()).default([]), // Barcode scans

  // Exceptions and notes
  exceptions: z.array(z.string()).default([]),
  notes: z.string().optional(),

  // Timestamps
  capturedAt: z.string().datetime(),
  syncedAt: z.string().datetime().optional()
});

export type ProofOfDelivery = z.infer<typeof ProofOfDelivery>;

// Weighing record
export const WeighingRecord = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  shipmentId: UUID,

  // Weights
  grossWeightKg: z.number().positive(),
  tareWeightKg: z.number().positive(),
  netWeightKg: z.number().positive(),

  // Source
  source: z.enum(['bridge', 'sensor', 'manual']),

  // Timestamps
  measuredAt: z.string().datetime(),
  recordedAt: z.string().datetime()
});

export type WeighingRecord = z.infer<typeof WeighingRecord>;

// Freight rate
export const FreightRate = z.object({
  id: UUID,
  tenantId: z.string().min(1),

  // Rate details
  baseAmount: Money,
  surcharges: z.array(z.object({
    type: z.string(),
    amount: Money,
    description: z.string().optional()
  })).default([]),

  // Applicability
  validFrom: z.string().datetime(),
  validTo: z.string().datetime().optional(),

  // Conditions
  minWeightKg: z.number().positive().optional(),
  maxWeightKg: z.number().positive().optional(),
  zones: z.array(z.string()).optional(),

  // Metadata
  rateCardId: z.string().optional(),
  explanation: z.string().optional()
});

export type FreightRate = z.infer<typeof FreightRate>;

// Emission record
export const EmissionRecord = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  shipmentId: UUID,

  // Emission data
  co2eKg: z.number().nonnegative(), // CO2 equivalent in kilograms
  method: z.string(), // Calculation method

  // Factors used
  factors: z.array(z.object({
    factor: z.string(),
    value: z.number(),
    unit: z.string()
  })).default([]),

  // Timestamps
  calculatedAt: z.string().datetime()
});

export type EmissionRecord = z.infer<typeof EmissionRecord>;

// Safety alert
export const SafetyAlert = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  referenceId: UUID, // Shipment, Vehicle, or Driver ID

  // Alert details
  type: z.enum(['dangerous_goods', 'temperature', 'geofence', 'weight', 'speed', 'maintenance']),
  severity: z.enum(['info', 'warning', 'critical']),
  message: z.string(),

  // Location and context
  location: z.object({
    lat: z.number().min(-90).max(90),
    lon: z.number().min(-180).max(180)
  }).optional(),

  // Status
  status: z.enum(['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED']),
  acknowledgedBy: z.string().optional(),
  acknowledgedAt: z.string().datetime().optional(),

  // Timestamps
  raisedAt: z.string().datetime(),
  resolvedAt: z.string().datetime().optional()
});

export type SafetyAlert = z.infer<typeof SafetyAlert>;

// Return order
export const ReturnOrder = z.object({
  id: UUID,
  tenantId: z.string().min(1),
  originalShipmentId: UUID,

  // Return details
  pickupAddress: Address,
  returnReason: z.string(),

  // Items being returned
  items: z.array(z.object({
    originalItemId: z.string(),
    quantity: z.number().int().positive(),
    reason: z.string().optional()
  })),

  // Status
  status: z.enum(['REQUESTED', 'APPROVED', 'SCHEDULED', 'PICKED_UP', 'DELIVERED', 'CANCELLED']),

  // Timestamps
  requestedAt: z.string().datetime(),
  approvedAt: z.string().datetime().optional(),
  scheduledAt: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional()
});

export type ReturnOrder = z.infer<typeof ReturnOrder>;