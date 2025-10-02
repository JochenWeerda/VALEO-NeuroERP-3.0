import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);

// Enums for contracts
export const ContractTypeEnum = z.enum(['Buy', 'Sell']);
export const CommodityTypeEnum = z.enum(['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER']);
export const ContractStatusEnum = z.enum(['Draft', 'Active', 'PartiallyFulfilled', 'Fulfilled', 'Cancelled', 'Defaulted']);
export const PricingModeEnum = z.enum(['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED']);
export const ShipmentTypeEnum = z.enum(['Spot', 'Window', 'CallOff']);
export const TitleTransferTypeEnum = z.enum(['AtDelivery', 'AtStorage', 'AtPricing']);

// Pricing Terms Schema
export const PricingTermsSchema = z.object({
  mode: PricingModeEnum,
  referenceMarket: z.enum(['CME', 'EURONEXT', 'CASH_INDEX']).optional(),
  futuresMonth: z.string().optional(),
  basis: z.number().optional(),
  fees: z.object({
    elevator: z.number().optional(),
    optionPremium: z.number().optional(),
  }).optional(),
  fx: z.object({
    pair: z.string(),
    method: z.enum(['SPOT', 'FIXING']),
  }).optional(),
  lastFixingAt: z.string().datetime().optional(),
});

// Delivery Terms Schema
export const DeliveryTermsSchema = z.object({
  shipmentType: ShipmentTypeEnum,
  parity: z.string().optional(),
  storage: z.object({
    allowed: z.boolean(),
    tariff: z.number().optional(),
    titleTransfer: TitleTransferTypeEnum.optional(),
  }).optional(),
  qualitySpecs: z.record(z.string(), z.any()).optional(),
});

// Contract Create Schema
export const CreateContractSchema = z.object({
  type: ContractTypeEnum,
  commodity: CommodityTypeEnum,
  counterpartyId: z.string().uuid(),
  incoterm: z.string().optional(),
  deliveryWindow: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  qty: z.object({
    unit: z.enum(['t', 'mt']),
    contracted: z.number().positive(),
    tolerance: z.number().min(0).max(20).optional(),
  }),
  pricing: PricingTermsSchema,
  delivery: DeliveryTermsSchema,
});

// Contract Update Schema
export const UpdateContractSchema = z.object({
  incoterm: z.string().optional(),
  deliveryWindow: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }).optional(),
  qty: z.object({
    contracted: z.number().positive().optional(),
    tolerance: z.number().min(0).max(20).optional(),
  }).optional(),
  pricing: PricingTermsSchema.optional(),
  delivery: DeliveryTermsSchema.optional(),
});

// Contract Response Schema
export const ContractResponseSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string(),
  contractNo: z.string(),
  type: ContractTypeEnum,
  commodity: CommodityTypeEnum,
  counterpartyId: z.string(),
  incoterm: z.string().optional(),
  deliveryWindow: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  qty: z.object({
    unit: z.enum(['t', 'mt']),
    contracted: z.number(),
    tolerance: z.number().optional(),
  }),
  pricing: PricingTermsSchema,
  delivery: DeliveryTermsSchema,
  status: ContractStatusEnum,
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
});

// Contract List Query Schema
export const ContractListQuerySchema = z.object({
  type: ContractTypeEnum.optional(),
  commodity: CommodityTypeEnum.optional(),
  status: ContractStatusEnum.optional(),
  counterpartyId: z.string().uuid().optional(),
  deliveryFrom: z.string().datetime().optional(),
  deliveryTo: z.string().datetime().optional(),
  page: z.coerce.number().min(1).default(1),
  pageSize: z.coerce.number().min(1).max(100).default(20),
});

// Contract List Response Schema
export const ContractListResponseSchema = z.object({
  data: z.array(ContractResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Contract Activate Schema
export const ActivateContractSchema = z.object({
  notes: z.string().optional(),
});

// Contract Cancel Schema
export const CancelContractSchema = z.object({
  reason: z.string(),
  notes: z.string().optional(),
});

// Type exports
export type CreateContract = z.infer<typeof CreateContractSchema>;
export type UpdateContract = z.infer<typeof UpdateContractSchema>;
export type ContractResponse = z.infer<typeof ContractResponseSchema>;
export type ContractListQuery = z.infer<typeof ContractListQuerySchema>;
export type ContractListResponse = z.infer<typeof ContractListResponseSchema>;
export type ActivateContract = z.infer<typeof ActivateContractSchema>;
export type CancelContract = z.infer<typeof CancelContractSchema>;