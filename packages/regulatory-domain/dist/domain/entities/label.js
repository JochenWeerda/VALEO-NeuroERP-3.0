"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CreateLabelSchema = exports.LabelEvaluationResultSchema = exports.LabelEvaluateInputSchema = exports.LabelSchema = exports.LabelStatusEnum = exports.LabelCodeEnum = void 0;
const zod_1 = require("zod");
exports.LabelCodeEnum = zod_1.z.enum([
    'VLOG_OGT',
    'QS',
    'GMP_PLUS',
    'NON_GMO',
    'ORGANIC_EU',
    'REDII_COMPLIANT',
    'ISCC',
    'RTRS',
    'RSPO',
    'CUSTOM',
]);
exports.LabelStatusEnum = zod_1.z.enum([
    'Eligible',
    'Ineligible',
    'Conditional',
    'Suspended',
    'Expired',
    'Pending',
]);
exports.LabelSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    code: exports.LabelCodeEnum,
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    targetType: zod_1.z.enum(['Batch', 'Contract', 'Site', 'Commodity', 'Supplier']),
    targetId: zod_1.z.string().min(1, 'Target ID is required'),
    status: exports.LabelStatusEnum.default('Pending'),
    evidenceRefs: zod_1.z.array(zod_1.z.string().uuid()).default([]),
    missingEvidences: zod_1.z.array(zod_1.z.string()).optional(),
    issuedAt: zod_1.z.string().datetime().optional(),
    issuedBy: zod_1.z.string().optional(),
    validFrom: zod_1.z.string().datetime().optional(),
    validTo: zod_1.z.string().datetime().optional(),
    revokedAt: zod_1.z.string().datetime().optional(),
    revokedBy: zod_1.z.string().optional(),
    revokedReason: zod_1.z.string().optional(),
    policyId: zod_1.z.string().uuid().optional(),
    createdAt: zod_1.z.string().datetime().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
});
exports.LabelEvaluateInputSchema = zod_1.z.object({
    targetRef: zod_1.z.object({
        type: zod_1.z.enum(['Batch', 'Contract', 'Site', 'Commodity', 'Supplier']),
        id: zod_1.z.string(),
    }),
    labelCode: exports.LabelCodeEnum,
    context: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
});
exports.LabelEvaluationResultSchema = zod_1.z.object({
    eligible: zod_1.z.boolean(),
    status: exports.LabelStatusEnum,
    missingEvidences: zod_1.z.array(zod_1.z.string()),
    violations: zod_1.z.array(zod_1.z.object({
        ruleId: zod_1.z.string(),
        description: zod_1.z.string(),
        severity: zod_1.z.enum(['Minor', 'Major', 'Critical']),
    })),
    recommendation: zod_1.z.string(),
    confidence: zod_1.z.number().min(0).max(1).optional(),
});
exports.CreateLabelSchema = exports.LabelSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
    issuedAt: true,
    revokedAt: true,
});
//# sourceMappingURL=label.js.map