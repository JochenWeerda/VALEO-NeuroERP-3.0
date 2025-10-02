"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PricingFixingSchema = exports.FulfilmentResponseSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.FulfilmentResponseSchema = zod_1.z.object({
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    deliveredQty: zod_1.z.number(),
    pricedQty: zod_1.z.number(),
    invoicedQty: zod_1.z.number(),
    openQty: zod_1.z.number(),
    avgPrice: zod_1.z.number().optional(),
    timeline: zod_1.z.array(zod_1.z.object({
        event: zod_1.z.string(),
        timestamp: zod_1.z.string().datetime(),
        qty: zod_1.z.number().optional(),
        price: zod_1.z.number().optional(),
        notes: zod_1.z.string().optional(),
    })),
    lastUpdated: zod_1.z.string().datetime(),
});
exports.PricingFixingSchema = zod_1.z.object({
    kind: zod_1.z.enum(['BASIS', 'FUTURES', 'MIN_PRICE_DECISION']),
    value: zod_1.z.number(),
    futuresMonth: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional(),
});
//# sourceMappingURL=fulfilment-contracts.js.map