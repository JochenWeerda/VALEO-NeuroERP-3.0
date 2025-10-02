"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MarkDeliveredSchema = exports.CallOffResponseSchema = exports.UpdateCallOffSchema = exports.CreateCallOffSchema = exports.CallOffStatusEnum = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.CallOffStatusEnum = zod_1.z.enum(['Planned', 'Scheduled', 'Delivered', 'Invoiced', 'Cancelled']);
exports.CreateCallOffSchema = zod_1.z.object({
    qty: zod_1.z.number().positive(),
    window: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    site: zod_1.z.string().optional(),
    silo: zod_1.z.string().optional(),
    customerYard: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional(),
});
exports.UpdateCallOffSchema = zod_1.z.object({
    qty: zod_1.z.number().positive().optional(),
    window: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }).optional(),
    site: zod_1.z.string().optional(),
    silo: zod_1.z.string().optional(),
    customerYard: zod_1.z.string().optional(),
    notes: zod_1.z.string().optional(),
});
exports.CallOffResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    qty: zod_1.z.number(),
    window: zod_1.z.object({
        from: zod_1.z.string().datetime(),
        to: zod_1.z.string().datetime(),
    }),
    site: zod_1.z.string().optional(),
    silo: zod_1.z.string().optional(),
    customerYard: zod_1.z.string().optional(),
    status: exports.CallOffStatusEnum,
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.MarkDeliveredSchema = zod_1.z.object({
    actualQty: zod_1.z.number().positive().optional(),
    notes: zod_1.z.string().optional(),
});
//# sourceMappingURL=call-off-contracts.js.map