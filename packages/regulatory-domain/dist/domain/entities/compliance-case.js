"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdateComplianceCaseSchema = exports.CreateComplianceCaseSchema = exports.ComplianceCaseSchema = exports.ComplianceCaseStatusEnum = exports.ComplianceSeverityEnum = exports.ComplianceCaseTypeEnum = void 0;
const zod_1 = require("zod");
exports.ComplianceCaseTypeEnum = zod_1.z.enum([
    'Violation',
    'AuditFinding',
    'DocMissing',
    'LabelRevocation',
    'Contamination',
    'Expiry',
    'Other',
]);
exports.ComplianceSeverityEnum = zod_1.z.enum([
    'Minor',
    'Major',
    'Critical',
]);
exports.ComplianceCaseStatusEnum = zod_1.z.enum([
    'Open',
    'Investigating',
    'ActionRequired',
    'Resolved',
    'Closed',
    'Escalated',
]);
exports.ComplianceCaseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    caseNumber: zod_1.z.string().min(1, 'Case number is required'),
    type: exports.ComplianceCaseTypeEnum,
    severity: exports.ComplianceSeverityEnum,
    ref: zod_1.z.object({
        type: zod_1.z.enum(['Batch', 'Contract', 'Site', 'Shipment', 'Supplier', 'Process']),
        id: zod_1.z.string(),
    }),
    title: zod_1.z.string().min(1, 'Title is required'),
    description: zod_1.z.string().min(1, 'Description is required'),
    policyId: zod_1.z.string().uuid().optional(),
    labelCode: zod_1.z.string().optional(),
    ruleId: zod_1.z.string().optional(),
    detectedAt: zod_1.z.string().datetime(),
    detectedBy: zod_1.z.string().min(1, 'Detected by is required'),
    detectionMethod: zod_1.z.enum(['Automated', 'Audit', 'Sample', 'Manual']).optional(),
    status: exports.ComplianceCaseStatusEnum.default('Open'),
    immediateAction: zod_1.z.string().optional(),
    capaId: zod_1.z.string().uuid().optional(),
    impactedBatches: zod_1.z.array(zod_1.z.string().uuid()).optional(),
    impactedLabels: zod_1.z.array(zod_1.z.string()).optional(),
    resolvedAt: zod_1.z.string().datetime().optional(),
    resolvedBy: zod_1.z.string().optional(),
    resolution: zod_1.z.string().optional(),
    closedAt: zod_1.z.string().datetime().optional(),
    closedBy: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
});
exports.CreateComplianceCaseSchema = exports.ComplianceCaseSchema.omit({
    id: true,
    caseNumber: true,
    createdAt: true,
    updatedAt: true,
    resolvedAt: true,
    closedAt: true,
});
exports.UpdateComplianceCaseSchema = exports.ComplianceCaseSchema.partial().omit({
    id: true,
    tenantId: true,
    caseNumber: true,
    createdAt: true,
});
//# sourceMappingURL=compliance-case.js.map