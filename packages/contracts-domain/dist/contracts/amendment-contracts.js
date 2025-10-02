"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RejectAmendmentSchema = exports.ApproveAmendmentSchema = exports.AmendmentResponseSchema = exports.CreateAmendmentSchema = exports.AmendmentStatusEnum = exports.AmendmentTypeEnum = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.AmendmentTypeEnum = zod_1.z.enum(['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other']);
exports.AmendmentStatusEnum = zod_1.z.enum(['Pending', 'Approved', 'Rejected', 'Cancelled']);
exports.CreateAmendmentSchema = zod_1.z.object({
    type: exports.AmendmentTypeEnum,
    reason: zod_1.z.string(),
    changes: zod_1.z.record(zod_1.z.any()),
    notes: zod_1.z.string().optional(),
});
exports.AmendmentResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    contractId: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    type: exports.AmendmentTypeEnum,
    reason: zod_1.z.string(),
    changes: zod_1.z.record(zod_1.z.any()),
    approvedBy: zod_1.z.string().optional(),
    approvedAt: zod_1.z.string().datetime().optional(),
    status: exports.AmendmentStatusEnum,
    effectiveAt: zod_1.z.string().datetime().optional(),
    notes: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.ApproveAmendmentSchema = zod_1.z.object({
    notes: zod_1.z.string().optional(),
});
exports.RejectAmendmentSchema = zod_1.z.object({
    reason: zod_1.z.string(),
    notes: zod_1.z.string().optional(),
});
//# sourceMappingURL=amendment-contracts.js.map