"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.QS_DEFAULT_RULES = exports.VLOG_DEFAULT_RULES = exports.UpdateRegulatoryPolicySchema = exports.CreateRegulatoryPolicySchema = exports.RegulatoryPolicySchema = exports.PolicyRuleSchema = exports.PolicyKeyEnum = exports.PolicyScopeEnum = void 0;
const zod_1 = require("zod");
exports.PolicyScopeEnum = zod_1.z.enum([
    'Commodity',
    'Process',
    'Site',
    'Contract',
    'Supplier',
    'Global',
]);
exports.PolicyKeyEnum = zod_1.z.enum([
    'VLOG',
    'QS',
    'REDII',
    'PSM',
    'GMP_PLUS',
    'NON_GMO',
    'ORGANIC',
    'TRACEABILITY',
    'HYGIENE',
    'CUSTOM',
]);
exports.PolicyRuleSchema = zod_1.z.object({
    ruleId: zod_1.z.string(),
    description: zod_1.z.string(),
    type: zod_1.z.enum(['Input', 'Process', 'Documentation', 'Lab', 'Monitoring', 'GHG']),
    criteriaKey: zod_1.z.string(),
    criteriaValue: zod_1.z.any().optional(),
    frequency: zod_1.z.enum(['PerBatch', 'Daily', 'Weekly', 'Monthly', 'Annually', 'OnDemand']).optional(),
    evidenceRequired: zod_1.z.boolean().default(false),
    evidenceType: zod_1.z.string().optional(),
    violationSeverity: zod_1.z.enum(['Minor', 'Major', 'Critical']).default('Major'),
});
exports.RegulatoryPolicySchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    key: exports.PolicyKeyEnum,
    version: zod_1.z.string().default('1.0'),
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    scope: exports.PolicyScopeEnum,
    scopeValue: zod_1.z.string().optional(),
    rules: zod_1.z.array(exports.PolicyRuleSchema).min(1, 'At least one rule is required'),
    active: zod_1.z.boolean().default(true),
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    standardReference: zod_1.z.string().optional(),
    legalBasis: zod_1.z.string().optional(),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
    updatedBy: zod_1.z.string().optional(),
});
exports.CreateRegulatoryPolicySchema = exports.RegulatoryPolicySchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
exports.UpdateRegulatoryPolicySchema = exports.RegulatoryPolicySchema.partial().omit({
    id: true,
    tenantId: true,
    createdAt: true,
    createdBy: true,
});
exports.VLOG_DEFAULT_RULES = [
    {
        ruleId: 'vlog-input-gvo-free',
        description: 'Alle Inputs müssen GVO-frei sein',
        type: 'Input',
        criteriaKey: 'vlog.input.gvo_free',
        criteriaValue: true,
        evidenceRequired: true,
        evidenceType: 'SupplierDeclaration',
        violationSeverity: 'Critical',
    },
    {
        ruleId: 'vlog-separation',
        description: 'Strikte Trennung von GVO/Nicht-GVO Material',
        type: 'Process',
        criteriaKey: 'vlog.process.separation',
        criteriaValue: true,
        evidenceRequired: true,
        evidenceType: 'ProcessDocument',
        violationSeverity: 'Critical',
    },
    {
        ruleId: 'vlog-cleaning',
        description: 'Reinigung zwischen GVO/Nicht-GVO Chargen',
        type: 'Process',
        criteriaKey: 'vlog.process.cleaning',
        criteriaValue: true,
        evidenceRequired: true,
        evidenceType: 'CleaningProtocol',
        violationSeverity: 'Major',
    },
    {
        ruleId: 'vlog-monitoring',
        description: 'GVO-Monitoring-Proben (Frequenz: mind. 1 pro Charge oder 0,5% der Menge)',
        type: 'Monitoring',
        criteriaKey: 'vlog.monitoring.frequency',
        frequency: 'PerBatch',
        evidenceRequired: true,
        evidenceType: 'LabReport',
        violationSeverity: 'Major',
    },
];
exports.QS_DEFAULT_RULES = [
    {
        ruleId: 'qs-mycotoxin-monitoring',
        description: 'Mykotoxin-Monitoring gemäß QS-Leitfaden',
        type: 'Lab',
        criteriaKey: 'qs.monitoring.mycotoxin',
        frequency: 'Monthly',
        evidenceRequired: true,
        evidenceType: 'LabReport',
        violationSeverity: 'Major',
    },
    {
        ruleId: 'qs-pesticide-residue',
        description: 'Rückstandsuntersuchung Pflanzenschutzmittel',
        type: 'Lab',
        criteriaKey: 'qs.monitoring.pesticide_residue',
        frequency: 'Monthly',
        evidenceRequired: true,
        evidenceType: 'LabReport',
        violationSeverity: 'Major',
    },
    {
        ruleId: 'qs-traceability',
        description: 'Rückverfolgbarkeit 1-up/1-down',
        type: 'Documentation',
        criteriaKey: 'qs.traceability.complete',
        criteriaValue: true,
        evidenceRequired: true,
        evidenceType: 'WeighingNote',
        violationSeverity: 'Critical',
    },
];
//# sourceMappingURL=regulatory-policy.js.map