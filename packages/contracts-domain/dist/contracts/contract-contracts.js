"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CancelContractSchema = exports.ActivateContractSchema = exports.ContractListResponseSchema = exports.ContractListQuerySchema = exports.ContractResponseSchema = exports.UpdateContractSchema = exports.CreateContractSchema = exports.DeliveryTermsSchema = exports.PricingTermsSchema = exports.TitleTransferTypeEnum = exports.ShipmentTypeEnum = exports.PricingModeEnum = exports.ContractStatusEnum = exports.CommodityTypeEnum = exports.ContractTypeEnum = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.ContractTypeEnum = zod_1.z.enum(['Buy', 'Sell']);
exports.CommodityTypeEnum = zod_1.z.enum(['WHEAT', 'BARLEY', 'RAPESEED', 'SOYMEAL', 'COMPOUND_FEED', 'FERTILIZER']);
exports.ContractStatusEnum = zod_1.z.enum(['Draft', 'Active', 'PartiallyFulfilled', 'Fulfilled', 'Cancelled', 'Defaulted']);
exports.PricingModeEnum = zod_1.z.enum(['FORWARD_CASH', 'BASIS', 'HTA', 'DEFERRED', 'MIN_PRICE', 'FIXED', 'INDEXED']);
exports.ShipmentTypeEnum = zod_1.z.enum(['Spot', 'Window', 'CallOff']);
exports.TitleTransferTypeEnum = zod_1.z.enum(['AtDelivery', 'AtStorage', 'AtPricing']);
exports.PricingTermsSchema = zod_1.z.object({
    mode: exports.PricingModeEnum,
    referenceMarket: zod_1.z.enum(['CME', 'EURONEXT', 'CASH_INDEX']).optional(),
    futuresMonth: zod_1.z.string().optional(),
    basis: zod_1.z.number().optional(),
    fees: zod_1.z.object({
        elevator: zod_1.z.number().optional(),
        optionPremium: zod_1.z.number().optional(),
    }).optional(),
    fx: zod_1.z.object({
        pair: zod_1.z.string(),
        method: zod_1.z.enum(['SPOT', 'FIXING']),
    }).optional(),
    lastFixingAt: zod_1.z.string().datetime().optional(),
});
exports.DeliveryTermsSchema = zod_1.z.object({
    shipmentType: exports.ShipmentTypeEnum,
    parity: zod_1.z.string().optional(),
    storage: zod_1.z.object({
        allowed: zod_1.z.boolean(),
        tariff: zod_1.z.number().optional(),
        titleTransfer: exports.TitleTransferTypeEnum.optional(),
    }).optional(),
    qualitySpecs: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
});
exports.CreateContractSchema = zod_1.z.object({
    type: exports.ContractTypeEnum,
    commodity: exports.CommodityTypeEnum,
    counterpartyId: zod_1.z.string().uuid(),
    incoterm: zod_1.z.string().optional(),
    deliveryWindow: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    qty: zod_1.z.object({
        unit: zod_1.z.enum(['t', 'mt']),
        contracted: zod_1.z.number().positive(),
        tolerance: zod_1.z.number().min(0).max(20).optional(),
    }),
    pricing: exports.PricingTermsSchema,
    delivery: exports.DeliveryTermsSchema,
});
exports.UpdateContractSchema = zod_1.z.object({
    incoterm: zod_1.z.string().optional(),
    deliveryWindow: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }).optional(),
    qty: zod_1.z.object({
        contracted: zod_1.z.number().positive().optional(),
        tolerance: zod_1.z.number().min(0).max(20).optional(),
    }).optional(),
    pricing: exports.PricingTermsSchema.optional(),
    delivery: exports.DeliveryTermsSchema.optional(),
});
exports.ContractResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    contractNo: zod_1.z.string(),
    type: exports.ContractTypeEnum,
    commodity: exports.CommodityTypeEnum,
    counterpartyId: zod_1.z.string(),
    incoterm: zod_1.z.string().optional(),
    deliveryWindow: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    qty: zod_1.z.object({
        unit: zod_1.z.enum(['t', 'mt']),
        contracted: zod_1.z.number(),
        tolerance: zod_1.z.number().optional(),
    }),
    pricing: exports.PricingTermsSchema,
    delivery: exports.DeliveryTermsSchema,
    status: exports.ContractStatusEnum,
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.ContractListQuerySchema = zod_1.z.object({
    type: exports.ContractTypeEnum.optional(),
    commodity: exports.CommodityTypeEnum.optional(),
    status: exports.ContractStatusEnum.optional(),
    counterpartyId: zod_1.z.string().uuid().optional(),
    deliveryFrom: zod_1.z.string().datetime().optional(),
    deliveryTo: zod_1.z.string().datetime().optional(),
    page: zod_1.z.coerce.number().min(1).default(1),
    pageSize: zod_1.z.coerce.number().min(1).max(100).default(20),
});
exports.ContractListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.ContractResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.ActivateContractSchema = zod_1.z.object({
    notes: zod_1.z.string().optional(),
});
exports.CancelContractSchema = zod_1.z.object({
    reason: zod_1.z.string(),
    notes: zod_1.z.string().optional(),
});
//# sourceMappingURL=contract-contracts.js.map