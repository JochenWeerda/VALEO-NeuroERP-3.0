import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);

// Enums
export const WeighingTypeSchema = z.enum(['Vehicle', 'Container', 'Silo', 'Manual']);
export const WeighingStatusSchema = z.enum(['Draft', 'InProgress', 'Completed', 'Cancelled', 'Error']);
export const CommodityTypeSchema = z.enum(['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER', 'OTHER']);
export const WeighingModeSchema = z.enum(['Gross', 'Tare', 'Net']);

// Base schemas
export const WeighingDataContractSchema = z.object({
  weight: z.number().positive().openapi({
    description: 'Weight value',
    example: 50000
  }),
  unit: z.enum(['kg', 't']).openapi({
    description: 'Weight unit',
    example: 'kg'
  }),
  timestamp: z.string().datetime().openapi({
    description: 'Timestamp of weighing',
    example: '2024-01-01T10:00:00.000Z'
  }),
  scaleId: z.string().openapi({
    description: 'Scale identifier',
    example: 'scale-01'
  }),
  operatorId: z.string().uuid().optional().openapi({
    description: 'Operator who performed the weighing',
    example: '550e8400-e29b-41d4-a716-446655440000'
  }),
  notes: z.string().optional().openapi({
    description: 'Additional notes',
    example: 'Clean vehicle, no issues'
  })
}).openapi({
  description: 'Weighing data record'
});

// Line item schema
export const WeighingLineContractSchema = z.object({
  id: z.string().uuid().optional().openapi({
    description: 'Line item ID',
    example: '550e8400-e29b-41d4-a716-446655440001'
  }),
  sku: z.string().openapi({
    description: 'Stock keeping unit',
    example: 'WHEAT-2024'
  }),
  name: z.string().openapi({
    description: 'Product name',
    example: 'Winter Wheat Premium'
  }),
  description: z.string().optional().openapi({
    description: 'Product description',
    example: 'High quality winter wheat'
  }),
  quantity: z.number().positive().openapi({
    description: 'Quantity',
    example: 25.5
  }),
  unitPrice: z.number().positive().openapi({
    description: 'Unit price',
    example: 250.00
  }),
  discount: z.number().min(0).max(100).default(0).openapi({
    description: 'Discount percentage',
    example: 5
  }),
  totalNet: z.number().positive().openapi({
    description: 'Net total',
    example: 6187.50
  }),
  totalGross: z.number().positive().openapi({
    description: 'Gross total',
    example: 7350.00
  })
}).openapi({
  description: 'Weighing ticket line item'
});

// Main ticket schema
export const WeighingTicketContractSchema = z.object({
  id: z.string().uuid().optional().openapi({
    description: 'Ticket ID',
    example: '550e8400-e29b-41d4-a716-446655440002'
  }),
  tenantId: z.string().uuid().openapi({
    description: 'Tenant ID',
    example: '550e8400-e29b-41d4-a716-446655440000'
  }),
  ticketNumber: z.string().openapi({
    description: 'Unique ticket number',
    example: 'WT-2024-001'
  }),
  type: WeighingTypeSchema.openapi({
    description: 'Type of weighing operation',
    example: 'Vehicle'
  }),
  status: WeighingStatusSchema.openapi({
    description: 'Current status',
    example: 'InProgress'
  }),

  // Vehicle/Container Information
  licensePlate: z.string().optional().openapi({
    description: 'Vehicle license plate',
    example: 'B-AB-123'
  }),
  containerNumber: z.string().optional().openapi({
    description: 'Container number',
    example: 'CONT-2024-001'
  }),
  siloId: z.string().optional().openapi({
    description: 'Silo identifier',
    example: 'silo-01'
  }),

  // Commodity Information
  commodity: CommodityTypeSchema.openapi({
    description: 'Commodity type',
    example: 'WHEAT'
  }),
  commodityDescription: z.string().optional().openapi({
    description: 'Commodity description',
    example: 'Winter wheat harvest 2024'
  }),

  // Weights
  grossWeight: WeighingDataContractSchema.optional().openapi({
    description: 'Gross weight measurement'
  }),
  tareWeight: WeighingDataContractSchema.optional().openapi({
    description: 'Tare weight measurement'
  }),
  netWeight: z.number().positive().optional().openapi({
    description: 'Calculated net weight',
    example: 42000
  }),
  netWeightUnit: z.enum(['kg', 't']).optional().openapi({
    description: 'Net weight unit',
    example: 'kg'
  }),

  // Quality & Tolerances
  expectedWeight: z.number().positive().optional().openapi({
    description: 'Expected weight',
    example: 42500
  }),
  tolerancePercent: z.number().min(0).max(20).default(2).openapi({
    description: 'Tolerance percentage',
    example: 2
  }),
  isWithinTolerance: z.boolean().optional().openapi({
    description: 'Whether weight is within tolerance',
    example: true
  }),

  // References
  contractId: z.string().uuid().optional().openapi({
    description: 'Related contract ID',
    example: '550e8400-e29b-41d4-a716-446655440003'
  }),
  orderId: z.string().uuid().optional().openapi({
    description: 'Related order ID',
    example: '550e8400-e29b-41d4-a716-446655440004'
  }),
  deliveryNoteId: z.string().uuid().optional().openapi({
    description: 'Related delivery note ID',
    example: '550e8400-e29b-41d4-a716-446655440005'
  }),

  // ANPR & Automation
  anprRecordId: z.string().uuid().optional().openapi({
    description: 'ANPR record ID',
    example: '550e8400-e29b-41d4-a716-446655440006'
  }),
  autoAssigned: z.boolean().default(false).openapi({
    description: 'Whether ticket was auto-assigned',
    example: true
  }),

  // Gate & Logistics
  gateId: z.string().optional().openapi({
    description: 'Gate identifier',
    example: 'gate-01'
  }),
  slotId: z.string().uuid().optional().openapi({
    description: 'Slot ID',
    example: '550e8400-e29b-41d4-a716-446655440007'
  }),

  // Metadata
  createdAt: z.string().datetime().optional().openapi({
    description: 'Creation timestamp',
    example: '2024-01-01T09:00:00.000Z'
  }),
  updatedAt: z.string().datetime().optional().openapi({
    description: 'Last update timestamp',
    example: '2024-01-01T10:00:00.000Z'
  }),
  completedAt: z.string().datetime().optional().openapi({
    description: 'Completion timestamp',
    example: '2024-01-01T10:30:00.000Z'
  }),
  version: z.number().default(1).openapi({
    description: 'Version number',
    example: 1
  })
}).openapi({
  description: 'Weighing ticket'
});

// Create ticket schema (without computed fields)
export const CreateWeighingTicketContractSchema = z.object({
  type: WeighingTypeSchema,
  licensePlate: z.string().optional(),
  containerNumber: z.string().optional(),
  siloId: z.string().optional(),
  commodity: CommodityTypeSchema,
  commodityDescription: z.string().optional(),
  expectedWeight: z.number().positive().optional(),
  tolerancePercent: z.number().min(0).max(20).optional(),
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  deliveryNoteId: z.string().uuid().optional(),
  gateId: z.string().optional(),
  notes: z.string().optional()
}).openapi({
  description: 'Create weighing ticket request'
});

// Update ticket schema
export const UpdateWeighingTicketContractSchema = z.object({
  status: WeighingStatusSchema.optional(),
  commodityDescription: z.string().optional(),
  expectedWeight: z.number().positive().optional(),
  tolerancePercent: z.number().min(0).max(20).optional(),
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  deliveryNoteId: z.string().uuid().optional(),
  gateId: z.string().optional(),
  notes: z.string().optional()
}).openapi({
  description: 'Update weighing ticket request'
});

// Weight recording schema
export const RecordWeightContractSchema = z.object({
  mode: WeighingModeSchema,
  weight: z.number().positive(),
  unit: z.enum(['kg', 't']),
  scaleId: z.string(),
  operatorId: z.string().uuid().optional(),
  notes: z.string().optional()
}).openapi({
  description: 'Record weight measurement'
});

// Query parameters
export const WeighingTicketQueryContractSchema = z.object({
  tenantId: z.string().uuid().optional(),
  status: WeighingStatusSchema.optional(),
  type: WeighingTypeSchema.optional(),
  commodity: CommodityTypeSchema.optional(),
  licensePlate: z.string().optional(),
  gateId: z.string().optional(),
  contractId: z.string().uuid().optional(),
  orderId: z.string().uuid().optional(),
  fromDate: z.string().datetime().optional(),
  toDate: z.string().datetime().optional(),
  isWithinTolerance: z.boolean().optional(),
  page: z.string().transform(Number).optional().default('1'),
  pageSize: z.string().transform(Number).optional().default('20')
}).openapi({
  description: 'Query parameters for weighing tickets'
});

// Response schema
export const WeighingTicketResponseContractSchema = WeighingTicketContractSchema.omit({
  tenantId: true
}).openapi({
  description: 'Weighing ticket response'
});

// List response schema
export const WeighingTicketListResponseContractSchema = z.object({
  data: z.array(WeighingTicketResponseContractSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number()
  })
}).openapi({
  description: 'Paginated weighing ticket list response'
});