"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreatePriceQuoteSchema = exports.PriceQuoteSchema = exports.CalcQuoteInputSchema = exports.PriceComponentSchema = exports.PriceComponentTypeEnum = void 0;
const zod_1 = require("zod");
exports.PriceComponentTypeEnum = zod_1.z.enum([
    'Base',
    'Condition',
    'Dynamic',
    'Charge',
    'Tax',
]);
exports.PriceComponentSchema = zod_1.z.object({
    type: exports.PriceComponentTypeEnum,
    key: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    value: zod_1.z.number(),
    basis: zod_1.z.number().optional(),
    calculatedFrom: zod_1.z.string().optional(),
});
exports.CalcQuoteInputSchema = zod_1.z.object({
    customerId: zod_1.z.string().min(1, 'Customer ID is required'),
    sku: zod_1.z.string().min(1, 'SKU is required'),
    qty: zod_1.z.number().positive('Quantity must be positive'),
    channel: zod_1.z.enum(['Web', 'Mobile', 'BackOffice', 'EDI']).optional(),
    deliveryWindow: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }).optional(),
    siteId: zod_1.z.string().optional(),
    contractRef: zod_1.z.string().optional(),
    context: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
});
exports.PriceQuoteSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    inputs: exports.CalcQuoteInputSchema,
    components: zod_1.z.array(exports.PriceComponentSchema),
    totalNet: zod_1.z.number(),
    totalGross: zod_1.z.number().optional(),
    currency: zod_1.z.string().default('EUR'),
    calculatedAt: zod_1.z.string().datetime().optional(),
    expiresAt: zod_1.z.string().datetime(),
    signature: zod_1.z.string().optional(),
    createdBy: zod_1.z.string().optional(),
});
exports.CreatePriceQuoteSchema = exports.PriceQuoteSchema.omit({
    id: true,
    calculatedAt: true,
    signature: true,
});
//# sourceMappingURL=price-quote.js.map