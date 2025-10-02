"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FormulaEvaluationResultSchema = exports.UpdateDynamicFormulaSchema = exports.CreateDynamicFormulaSchema = exports.DynamicFormulaSchema = exports.PriceCapsSchema = exports.RoundingConfigSchema = exports.FormulaInputSchema = exports.FormulaInputSourceEnum = void 0;
const zod_1 = require("zod");
exports.FormulaInputSourceEnum = zod_1.z.enum([
    'Index',
    'Futures',
    'Basis',
    'FX',
    'Custom',
    'Static',
]);
exports.FormulaInputSchema = zod_1.z.object({
    key: zod_1.z.string().min(1, 'Key is required'),
    source: exports.FormulaInputSourceEnum,
    sourceRef: zod_1.z.string().optional(),
    fallback: zod_1.z.number().optional(),
    description: zod_1.z.string().optional(),
});
exports.RoundingConfigSchema = zod_1.z.object({
    step: zod_1.z.number().optional(),
    mode: zod_1.z.enum(['up', 'down', 'nearest']).default('nearest'),
});
exports.PriceCapsSchema = zod_1.z.object({
    min: zod_1.z.number().optional(),
    max: zod_1.z.number().optional(),
});
exports.DynamicFormulaSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    expression: zod_1.z.string().min(1, 'Expression is required'),
    inputs: zod_1.z.array(exports.FormulaInputSchema).min(1, 'At least one input is required'),
    rounding: exports.RoundingConfigSchema.optional(),
    caps: exports.PriceCapsSchema.optional(),
    sku: zod_1.z.string().optional(),
    commodity: zod_1.z.string().optional(),
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    active: zod_1.z.boolean().default(true),
    testInputs: zod_1.z.record(zod_1.z.string(), zod_1.z.number()).optional(),
    expectedResult: zod_1.z.number().optional(),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
    updatedBy: zod_1.z.string().optional(),
});
exports.CreateDynamicFormulaSchema = exports.DynamicFormulaSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
exports.UpdateDynamicFormulaSchema = exports.DynamicFormulaSchema.partial().omit({
    id: true,
    tenantId: true,
    createdAt: true,
    createdBy: true,
});
exports.FormulaEvaluationResultSchema = zod_1.z.object({
    formulaId: zod_1.z.string().uuid(),
    result: zod_1.z.number(),
    inputs: zod_1.z.record(zod_1.z.string(), zod_1.z.number()),
    expression: zod_1.z.string(),
    cappedValue: zod_1.z.number().optional(),
    roundedValue: zod_1.z.number(),
    calculatedAt: zod_1.z.string().datetime(),
});
//# sourceMappingURL=dynamic-formula.js.map