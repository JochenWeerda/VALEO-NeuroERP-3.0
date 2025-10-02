"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiResponse = exports.TenantContext = exports.PaginatedResponse = exports.PaginationParams = exports.TimeWindow = exports.ISODateString = exports.Money = exports.Currency = exports.ContactInfo = exports.Address = exports.URL = exports.PhoneNumber = exports.Email = exports.UUID = void 0;
const zod_1 = require("zod");
// Common schemas used across all domains
exports.UUID = zod_1.z.string().uuid();
exports.Email = zod_1.z.string().email();
exports.PhoneNumber = zod_1.z.string().regex(/^\+?[1-9]\d{1,14}$/);
exports.URL = zod_1.z.string().url();
// Address schema (used by multiple domains)
exports.Address = zod_1.z.object({
    street: zod_1.z.string().min(1),
    city: zod_1.z.string().min(1),
    postalCode: zod_1.z.string().min(1),
    country: zod_1.z.string().length(2), // ISO 3166-1 alpha-2
    coordinates: zod_1.z.object({
        lat: zod_1.z.number().min(-90).max(90),
        lon: zod_1.z.number().min(-180).max(180)
    }).optional(),
    gln: zod_1.z.string().optional(), // Global Location Number
    name: zod_1.z.string().optional()
});
// Contact information (used by CRM, Procurement, etc.)
exports.ContactInfo = zod_1.z.object({
    name: zod_1.z.string().min(1),
    email: exports.Email.optional(),
    phone: exports.PhoneNumber.optional(),
    address: exports.Address.optional()
});
// Currency and Money
exports.Currency = zod_1.z.enum(['EUR', 'USD', 'GBP', 'CHF']);
exports.Money = zod_1.z.object({
    amount: zod_1.z.number().nonnegative(),
    currency: exports.Currency
});
// Time and Date
exports.ISODateString = zod_1.z.string().datetime();
exports.TimeWindow = zod_1.z.object({
    from: exports.ISODateString,
    to: exports.ISODateString
});
// Pagination
exports.PaginationParams = zod_1.z.object({
    page: zod_1.z.number().int().positive().default(1),
    limit: zod_1.z.number().int().min(1).max(100).default(20)
});
const PaginatedResponse = (itemSchema) => zod_1.z.object({
    items: zod_1.z.array(itemSchema),
    total: zod_1.z.number().int().nonnegative(),
    page: zod_1.z.number().int().positive(),
    limit: zod_1.z.number().int().positive(),
    hasNext: zod_1.z.boolean(),
    hasPrev: zod_1.z.boolean()
});
exports.PaginatedResponse = PaginatedResponse;
// Tenant context (for multi-tenancy)
exports.TenantContext = zod_1.z.object({
    tenantId: zod_1.z.string().min(1),
    userId: zod_1.z.string().optional(),
    roles: zod_1.z.array(zod_1.z.string()).default([])
});
// Generic response wrapper
const ApiResponse = (dataSchema) => zod_1.z.object({
    success: zod_1.z.boolean(),
    data: dataSchema.optional(),
    error: zod_1.z.object({
        code: zod_1.z.string(),
        message: zod_1.z.string(),
        details: zod_1.z.any().optional()
    }).optional(),
    timestamp: exports.ISODateString,
    requestId: zod_1.z.string().optional()
});
exports.ApiResponse = ApiResponse;
//# sourceMappingURL=shared-schemas.js.map