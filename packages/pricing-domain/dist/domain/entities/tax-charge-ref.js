"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.COMMON_TAX_RATES = exports.UpdateTaxChargeRefSchema = exports.CreateTaxChargeRefSchema = exports.TaxChargeRefSchema = exports.TaxChargeMethodEnum = exports.TaxChargeScopeEnum = void 0;
const zod_1 = require("zod");
exports.TaxChargeScopeEnum = zod_1.z.enum([
    'SKU',
    'Commodity',
    'All',
]);
exports.TaxChargeMethodEnum = zod_1.z.enum([
    'ABS',
    'PCT',
]);
exports.TaxChargeRefSchema = zod_1.z.object({
    id: zod_1.z.string().uuid().optional(),
    tenantId: zod_1.z.string().min(1, 'Tenant ID is required'),
    code: zod_1.z.string().min(1, 'Code is required'),
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    type: zod_1.z.enum(['VAT', 'Tax', 'Levy', 'Fee', 'Deposit', 'Surcharge', 'Other']),
    method: exports.TaxChargeMethodEnum,
    rateOrAmount: zod_1.z.number(),
    scope: exports.TaxChargeScopeEnum,
    scopeValue: zod_1.z.string().optional(),
    validFrom: zod_1.z.string().datetime(),
    validTo: zod_1.z.string().datetime().optional(),
    country: zod_1.z.string().default('DE'),
    region: zod_1.z.string().optional(),
    active: zod_1.z.boolean().default(true),
    createdAt: zod_1.z.string().datetime().optional(),
    createdBy: zod_1.z.string().optional(),
    updatedAt: zod_1.z.string().datetime().optional(),
    updatedBy: zod_1.z.string().optional(),
});
exports.CreateTaxChargeRefSchema = exports.TaxChargeRefSchema.omit({
    id: true,
    createdAt: true,
    updatedAt: true,
});
exports.UpdateTaxChargeRefSchema = exports.TaxChargeRefSchema.partial().omit({
    id: true,
    tenantId: true,
    createdAt: true,
    createdBy: true,
});
exports.COMMON_TAX_RATES = {
    VAT_19: { code: 'VAT_19', name: 'USt 19%', type: 'VAT', method: 'PCT', rateOrAmount: 19 },
    VAT_7: { code: 'VAT_7', name: 'USt 7%', type: 'VAT', method: 'PCT', rateOrAmount: 7 },
    VAT_0: { code: 'VAT_0', name: 'USt 0%', type: 'VAT', method: 'PCT', rateOrAmount: 0 },
};
//# sourceMappingURL=tax-charge-ref.js.map