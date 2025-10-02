"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdatePriceListSchema = exports.CreatePriceListSchema = exports.PriceListSchema = exports.PriceListLineSchema = exports.TierBreakSchema = exports.PriceListStatusEnum = void 0;
const zod_1 = require("zod");
exports.PriceListStatusEnum = zod_1.z.enum([
    'Draft',
    'Active',
    'Archived',
]);
exports.TierBreakSchema = zod_1.z.object({
    minQty: zod_1.z.number().min(0),
    maxQty: zod_1.z.number().optional(),
    price: zod_1.z.number(),
});
exports.PriceListLineSchema = zod_1.z.object({
    sku: zod_1.z.string().min(1, 'SKU is required'),
    commodity: zod_1.z.string().optional(),
    basePrice: zod_1.z.number(),
    uom: zod_1.z.string().default('t'),
    currency: zod_1.z.string().default('EUR'),
    tierBreaks: zod_1.z.array(exports.TierBreakSchema).optional(),
    minQty: zod_1.z.number().optional(),
    description: zod_1.z.string().optional(),
    active: zod_1.z.boolean().default(true),
});
exports.PriceListSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    code: zod_1.z.string().optional(),
    currency: zod_1.z.string().default('EUR'),
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    lines: zod_1.z.array(exports.PriceListLineSchema).min(1, 'At least one line is required'),
    status: exports.PriceListStatusEnum.default('Draft'),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
    updatedBy: zod_1.z.string().optional(),
    activatedAt: zod_1.z.string().datetime().optional(),
    activatedBy: zod_1.z.string().optional(),
});
exports.CreatePriceListSchema = exports.PriceListSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    activatedAt: true,
});
exports.UpdatePriceListSchema = exports.PriceListSchema.partial().omit({
    id: true,
    tenantId: true,
    createdAt: true,
    createdBy: true,
});
//# sourceMappingURL=price-list.js.map