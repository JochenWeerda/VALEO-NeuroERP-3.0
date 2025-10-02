"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.UpdateConditionSetSchema = exports.CreateConditionSetSchema = exports.ConditionSetSchema = exports.ConditionRuleSchema = exports.ChannelEnum = exports.ConditionMethodEnum = exports.ConditionScopeEnum = exports.ConditionTypeEnum = void 0;
const zod_1 = require("zod");
exports.ConditionTypeEnum = zod_1.z.enum([
    'Discount',
    'Markup',
    'Rebate',
    'Surcharge',
]);
exports.ConditionScopeEnum = zod_1.z.enum([
    'SKU',
    'Commodity',
    'All',
]);
exports.ConditionMethodEnum = zod_1.z.enum([
    'ABS',
    'PCT',
]);
exports.ChannelEnum = zod_1.z.enum([
    'Web',
    'Mobile',
    'BackOffice',
    'EDI',
    'All',
]);
exports.ConditionRuleSchema = zod_1.z.object({
    ruleId: zod_1.z.string().optional(),
    type: exports.ConditionTypeEnum,
    scope: exports.ConditionScopeEnum,
    selector: zod_1.z.object({
        sku: zod_1.z.string().optional(),
        commodity: zod_1.z.string().optional(),
    }).optional(),
    method: exports.ConditionMethodEnum,
    value: zod_1.z.number(),
    minQty: zod_1.z.number().optional(),
    maxQty: zod_1.z.number().optional(),
    channel: exports.ChannelEnum.optional(),
    validFrom: zod_1.z.string().datetime().optional(),
    validTo: zod_1.z.string().datetime().optional(),
    stackable: zod_1.z.boolean().default(true),
    description: zod_1.z.string().optional(),
});
exports.ConditionSetSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    key: zod_1.z.string().min(1, 'Key is required'),
    keyType: zod_1.z.enum(['Customer', 'Segment', 'Region', 'PaymentTerm']),
    rules: zod_1.z.array(exports.ConditionRuleSchema).min(1, 'At least one rule is required'),
    priority: zod_1.z.number().int().default(100),
    conflictStrategy: zod_1.z.enum(['FirstWins', 'LastWins', 'MaxWins', 'MinWins', 'Stack']).default('Stack'),
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    active: zod_1.z.boolean().default(true),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
    updatedBy: zod_1.z.string().optional(),
});
exports.CreateConditionSetSchema = exports.ConditionSetSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
exports.UpdateConditionSetSchema = exports.ConditionSetSchema.partial().omit({
    id: true,
    tenantId: true,
    createdAt: true,
    createdBy: true,
});
//# sourceMappingURL=condition-set.js.map