"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WeighingTicketListResponseContractSchema = exports.WeighingTicketResponseContractSchema = exports.WeighingTicketQueryContractSchema = exports.RecordWeightContractSchema = exports.UpdateWeighingTicketContractSchema = exports.CreateWeighingTicketContractSchema = exports.WeighingTicketContractSchema = exports.WeighingLineContractSchema = exports.WeighingDataContractSchema = exports.WeighingModeSchema = exports.CommodityTypeSchema = exports.WeighingStatusSchema = exports.WeighingTypeSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.WeighingTypeSchema = zod_1.z.enum(['Vehicle', 'Container', 'Silo', 'Manual']);
exports.WeighingStatusSchema = zod_1.z.enum(['Draft', 'InProgress', 'Completed', 'Cancelled', 'Error']);
exports.CommodityTypeSchema = zod_1.z.enum(['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER', 'OTHER']);
exports.WeighingModeSchema = zod_1.z.enum(['Gross', 'Tare', 'Net']);
exports.WeighingDataContractSchema = zod_1.z.object({
    weight: zod_1.z.number().positive().openapi({
        description: 'Weight value',
        example: 50000
    }),
    unit: zod_1.z.enum(['kg', 't']).openapi({
        description: 'Weight unit',
        example: 'kg'
    }),
    timestamp: zod_1.z.string().datetime().openapi({
        description: 'Timestamp of weighing',
        example: '2024-01-01T10:00:00.000Z'
    }),
    scaleId: zod_1.z.string().openapi({
        description: 'Scale identifier',
        example: 'scale-01'
    }),
    operatorId: zod_1.z.string().uuid().optional().openapi({
        description: 'Operator who performed the weighing',
        example: '550e8400-e29b-41d4-a716-446655440000'
    }),
    notes: zod_1.z.string().optional().openapi({
        description: 'Additional notes',
        example: 'Clean vehicle, no issues'
    })
}).openapi({
    description: 'Weighing data record'
});
exports.WeighingLineContractSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional().openapi({
        description: 'Line item ID',
        example: '550e8400-e29b-41d4-a716-446655440001'
    }),
    sku: zod_1.z.string().openapi({
        description: 'Stock keeping unit',
        example: 'WHEAT-2024'
    }),
    name: zod_1.z.string().openapi({
        description: 'Product name',
        example: 'Winter Wheat Premium'
    }),
    description: zod_1.z.string().optional().openapi({
        description: 'Product description',
        example: 'High quality winter wheat'
    }),
    quantity: zod_1.z.number().positive().openapi({
        description: 'Quantity',
        example: 25.5
    }),
    unitPrice: zod_1.z.number().positive().openapi({
        description: 'Unit price',
        example: 250.00
    }),
    discount: zod_1.z.number().min(0).max(100).default(0).openapi({
        description: 'Discount percentage',
        example: 5
    }),
    totalNet: zod_1.z.number().positive().openapi({
        description: 'Net total',
        example: 6187.50
    }),
    totalGross: zod_1.z.number().positive().openapi({
        description: 'Gross total',
        example: 7350.00
    })
}).openapi({
    description: 'Weighing ticket line item'
});
exports.WeighingTicketContractSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional().openapi({
        description: 'Ticket ID',
        example: '550e8400-e29b-41d4-a716-446655440002'
    }),
    tenantId: zod_1.z.string().uuid().openapi({
        description: 'Tenant ID',
        example: '550e8400-e29b-41d4-a716-446655440000'
    }),
    ticketNumber: zod_1.z.string().openapi({
        description: 'Unique ticket number',
        example: 'WT-2024-001'
    }),
    type: exports.WeighingTypeSchema.openapi({
        description: 'Type of weighing operation',
        example: 'Vehicle'
    }),
    status: exports.WeighingStatusSchema.openapi({
        description: 'Current status',
        example: 'InProgress'
    }),
    licensePlate: zod_1.z.string().optional().openapi({
        description: 'Vehicle license plate',
        example: 'B-AB-123'
    }),
    containerNumber: zod_1.z.string().optional().openapi({
        description: 'Container number',
        example: 'CONT-2024-001'
    }),
    siloId: zod_1.z.string().optional().openapi({
        description: 'Silo identifier',
        example: 'silo-01'
    }),
    commodity: exports.CommodityTypeSchema.openapi({
        description: 'Commodity type',
        example: 'WHEAT'
    }),
    commodityDescription: zod_1.z.string().optional().openapi({
        description: 'Commodity description',
        example: 'Winter wheat harvest 2024'
    }),
    grossWeight: exports.WeighingDataContractSchema.optional().openapi({
        description: 'Gross weight measurement'
    }),
    tareWeight: exports.WeighingDataContractSchema.optional().openapi({
        description: 'Tare weight measurement'
    }),
    netWeight: zod_1.z.number().positive().optional().openapi({
        description: 'Calculated net weight',
        example: 42000
    }),
    netWeightUnit: zod_1.z.enum(['kg', 't']).optional().openapi({
        description: 'Net weight unit',
        example: 'kg'
    }),
    expectedWeight: zod_1.z.number().positive().optional().openapi({
        description: 'Expected weight',
        example: 42500
    }),
    tolerancePercent: zod_1.z.number().min(0).max(20).default(2).openapi({
        description: 'Tolerance percentage',
        example: 2
    }),
    isWithinTolerance: zod_1.z.boolean().optional().openapi({
        description: 'Whether weight is within tolerance',
        example: true
    }),
    contractId: zod_1.z.string().uuid().optional().openapi({
        description: 'Related contract ID',
        example: '550e8400-e29b-41d4-a716-446655440003'
    }),
    orderId: zod_1.z.string().uuid().optional().openapi({
        description: 'Related order ID',
        example: '550e8400-e29b-41d4-a716-446655440004'
    }),
    deliveryNoteId: zod_1.z.string().uuid().optional().openapi({
        description: 'Related delivery note ID',
        example: '550e8400-e29b-41d4-a716-446655440005'
    }),
    anprRecordId: zod_1.z.string().uuid().optional().openapi({
        description: 'ANPR record ID',
        example: '550e8400-e29b-41d4-a716-446655440006'
    }),
    autoAssigned: zod_1.z.boolean().default(false).openapi({
        description: 'Whether ticket was auto-assigned',
        example: true
    }),
    gateId: zod_1.z.string().optional().openapi({
        description: 'Gate identifier',
        example: 'gate-01'
    }),
    slotId: zod_1.z.string().uuid().optional().openapi({
        description: 'Slot ID',
        example: '550e8400-e29b-41d4-a716-446655440007'
    }),
    createdAt: zod_1.z.string().datetime().optional().openapi({
        description: 'Creation timestamp',
        example: '2024-01-01T09:00:00.000Z'
    }),
    updatedAt: zod_1.z.string().datetime().optional().openapi({
        description: 'Last update timestamp',
        example: '2024-01-01T10:00:00.000Z'
    }),
    completedAt: zod_1.z.string().datetime().optional().openapi({
        description: 'Completion timestamp',
        example: '2024-01-01T10:30:00.000Z'
    }),
    version: zod_1.z.number().default(1).openapi({
        description: 'Version number',
        example: 1
    })
}).openapi({
    description: 'Weighing ticket'
});
exports.CreateWeighingTicketContractSchema = zod_1.z.object({
    type: exports.WeighingTypeSchema,
    licensePlate: zod_1.z.string().optional(),
    containerNumber: zod_1.z.string().optional(),
    siloId: zod_1.z.string().optional(),
    commodity: exports.CommodityTypeSchema,
    commodityDescription: zod_1.z.string().optional(),
    expectedWeight: zod_1.z.number().positive().optional(),
    tolerancePercent: zod_1.z.number().min(0).max(20).optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    deliveryNoteId: zod_1.z.string().uuid().optional(),
    gateId: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional()
}).openapi({
    description: 'Create weighing ticket request'
});
exports.UpdateWeighingTicketContractSchema = zod_1.z.object({
    status: exports.WeighingStatusSchema.optional(),
    commodityDescription: zod_1.z.string().optional(),
    expectedWeight: zod_1.z.number().positive().optional(),
    tolerancePercent: zod_1.z.number().min(0).max(20).optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    deliveryNoteId: zod_1.z.string().uuid().optional(),
    gateId: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional()
}).openapi({
    description: 'Update weighing ticket request'
});
exports.RecordWeightContractSchema = zod_1.z.object({
    mode: exports.WeighingModeSchema,
    weight: zod_1.z.number().positive(),
    unit: zod_1.z.enum(['kg', 't']),
    scaleId: zod_1.z.string(),
    operatorId: zod_1.z.string().uuid().optional(),
    notes: zod_1.z.string().optional()
}).openapi({
    description: 'Record weight measurement'
});
exports.WeighingTicketQueryContractSchema = zod_1.z.object({
    tenantId: zod_1.z.string().uuid().optional(),
    status: exports.WeighingStatusSchema.optional(),
    type: exports.WeighingTypeSchema.optional(),
    commodity: exports.CommodityTypeSchema.optional(),
    licensePlate: zod_1.z.string().optional(),
    gateId: zod_1.z.string().optional(),
    contractId: zod_1.z.string().uuid().optional(),
    orderId: zod_1.z.string().uuid().optional(),
    fromDate: zod_1.z.string().datetime().optional(),
    toDate: zod_1.z.string().datetime().optional(),
    isWithinTolerance: zod_1.z.boolean().optional(),
    page: zod_1.z.string().transform(Number).optional().default('1'),
    pageSize: zod_1.z.string().transform(Number).optional().default('20')
}).openapi({
    description: 'Query parameters for weighing tickets'
});
exports.WeighingTicketResponseContractSchema = exports.WeighingTicketContractSchema.omit({
    tenantId: true
}).openapi({
    description: 'Weighing ticket response'
});
exports.WeighingTicketListResponseContractSchema = zod_1.z.object({
    data: zod_1.z.array(exports.WeighingTicketResponseContractSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number()
    })
}).openapi({
    description: 'Paginated weighing ticket list response'
});
//# sourceMappingURL=weighing-ticket-contracts.js.map