"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreatePSMProductRefSchema = exports.PSMCheckResultSchema = exports.PSMCheckInputSchema = exports.PSMProductRefSchema = exports.PSMApprovalStatusEnum = void 0;
const zod_1 = require("zod");
exports.PSMApprovalStatusEnum = zod_1.z.enum([
    'Approved',
    'Expired',
    'Withdrawn',
    'Restricted',
    'Pending',
    'Unknown',
]);
exports.PSMProductRefSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    bvlId: zod_1.z.string().optional(),
    name: zod_1.z.string().min(1, 'Name is required'),
    activeSubstances: zod_1.z.array(zod_1.z.string()).default([]),
    approvalStatus: exports.PSMApprovalStatusEnum.default('Unknown'),
    approvalValidTo: zod_1.z.string().datetime().optional(),
    approvalNumber: zod_1.z.string().optional(),
    usageScope: zod_1.z.string().optional(),
    restrictions: zod_1.z.array(zod_1.z.string()).optional(),
    lastCheckedAt: zod_1.z.string().datetime().optional(),
    lastCheckedBy: zod_1.z.string().optional(),
    sourceUrl: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
});
exports.PSMCheckInputSchema = zod_1.z.object({
    items: zod_1.z.array(zod_1.z.object({
        name: zod_1.z.string().min(1, 'PSM name is required'),
        bvlId: zod_1.z.string().optional(),
        useDate: zod_1.z.string().datetime(),
        cropOrUseCase: zod_1.z.string().optional(),
        quantity: zod_1.z.number().optional(),
        unit: zod_1.z.string().optional(),
    })).min(1, 'At least one PSM item is required'),
    batchId: zod_1.z.string().uuid().optional(),
    contractId: zod_1.z.string().uuid().optional(),
});
exports.PSMCheckResultSchema = zod_1.z.object({
    compliant: zod_1.z.boolean(),
    items: zod_1.z.array(zod_1.z.object({
        name: zod_1.z.string(),
        bvlId: zod_1.z.string().optional(),
        status: exports.PSMApprovalStatusEnum,
        approved: zod_1.z.boolean(),
        validUntil: zod_1.z.string().datetime().optional(),
        issues: zod_1.z.array(zod_1.z.string()).default([]),
    })),
    violations: zod_1.z.array(zod_1.z.object({
        name: zod_1.z.string(),
        reason: zod_1.z.string(),
        severity: zod_1.z.enum(['Minor', 'Major', 'Critical']),
    })),
    recommendation: zod_1.z.string(),
});
exports.CreatePSMProductRefSchema = exports.PSMProductRefSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
//# sourceMappingURL=psm-product.js.map