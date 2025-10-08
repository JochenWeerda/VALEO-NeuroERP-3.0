"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LinkEvidenceSchema = exports.CreateEvidenceSchema = exports.EvidenceSchema = exports.EvidenceStatusEnum = exports.EvidenceTypeEnum = void 0;
const zod_1 = require("zod");
exports.EvidenceTypeEnum = zod_1.z.enum([
    'Certificate',
    'LabReport',
    'SupplierDeclaration',
    'AuditReport',
    'WeighingNote',
    'ProcessDocument',
    'CleaningProtocol',
    'ContractClause',
    'InspectionReport',
    'SelfDeclaration',
    'Invoice',
    'TransportDocument',
    'Other',
]);
exports.EvidenceStatusEnum = zod_1.z.enum([
    'Valid',
    'Expired',
    'Pending',
    'Rejected',
    'Archived',
]);
exports.EvidenceSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    type: exports.EvidenceTypeEnum,
    title: zod_1.z.string().min(1, 'Title is required'),
    description: zod_1.z.string().optional(),
    uri: zod_1.z.string().url().optional(),
    hash: zod_1.z.string().optional(),
    mimeType: zod_1.z.string().optional(),
    fileSize: zod_1.z.number().optional(),
    issuedBy: zod_1.z.string().min(1, 'Issued by is required'),
    issuedAt: zod_1.z.string().datetime(),
    validFrom: zod_1.z.string().datetime().optional(),
    validTo: zod_1.z.string().datetime().optional(),
    status: exports.EvidenceStatusEnum.default('Valid'),
    relatedRef: zod_1.z.object({
        type: zod_1.z.enum(['Batch', 'Contract', 'Site', 'Supplier', 'Shipment', 'Sample']),
        id: zod_1.z.string(),
    }).optional(),
    supportingLabels: zod_1.z.array(zod_1.z.string()).default([]),
    supportingPolicies: zod_1.z.array(zod_1.z.string().uuid()).default([]),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
});
exports.CreateEvidenceSchema = exports.EvidenceSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
exports.LinkEvidenceSchema = zod_1.z.object({
    evidenceId: zod_1.z.string().uuid(),
    targetRef: zod_1.z.object({
        type: zod_1.z.enum(['Batch', 'Contract', 'Site', 'Supplier', 'Label']),
        id: zod_1.z.string(),
    }),
});
//# sourceMappingURL=evidence.js.map